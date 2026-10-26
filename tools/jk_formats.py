"""Small, standalone JKDF2/MotS 3DO 2.1 and MAT RGB565/indexed exporter.

No legacy executable or proprietary SDK is needed. Pillow is the sole optional
dependency (used for MAT images only). All numeric binary fields are little-endian.

Model schema: name, materials (MAT basenames), meshes, nodes. Each mesh contains
name, vertices (local XYZ), uvs (PIXEL/TEXEL coordinates, top-left origin), faces.
Each face contains vertices and uvs index lists plus material index; flags,
geometrymode, lightingmode, texturemode and extralight are optional. Each node
contains name, mesh index (-1 for dummy), parent index (-1 for root), type,
position (parent-relative XYZ), rotation (pitch/yaw/roll DEGREES), pivot (XYZ).
Nodes need not be in parent-first order. Vertices use JK's Z-up, Y-forward frame.

This validates format structure, not successful loading/animation in the game.
Sources: https://www.massassi.net/jkspecs/3do.htm and /mat.htm;
https://github.com/shinyquagsire23/OpenJKDF2/blob/master/src/Primitives/rdModel3.c
https://github.com/shinyquagsire23/OpenJKDF2/blob/master/src/Engine/rdMaterial.c
https://github.com/shinyquagsire23/OpenJKDF2/blob/master/src/types.h
https://github.com/bahstrike/Matt/blob/main/Material.cs
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import tempfile

MAX_VERTICES = 512
MAX_UVS = 768
MAX_FACES = 512
MAX_FACE_VERTICES = 24
MAX_MIPMAPS = 4  # rdTexture.texture_struct[4] -- NOT a complete chain to 1x1.


def _xyz(value):
    value = tuple(float(x) for x in value)
    if len(value) != 3 or not all(math.isfinite(x) for x in value):
        raise ValueError(f"Invalid finite XYZ: {value}")
    return value


def _length(v):
    return math.sqrt(sum(x*x for x in v))


def _normal(vertices, indices):
    # Newell's method also handles planar quads with a collinear first triple.
    n = [0., 0., 0.]
    points = [vertices[i] for i in indices]
    for p, q in zip(points, points[1:] + points[:1]):
        n[0] += (p[1]-q[1])*(p[2]+q[2])
        n[1] += (p[2]-q[2])*(p[0]+q[0])
        n[2] += (p[0]-q[0])*(p[1]+q[1])
    length = _length(n)
    if length <= 1e-15:
        raise ValueError(f"Degenerate face {indices}")
    return [x/length for x in n]


def _links(nodes):
    children = [[] for _ in nodes]
    roots = []
    for i, node in enumerate(nodes):
        p = int(node.get('parent', -1))
        if p == -1:
            roots.append(i)
        elif 0 <= p < len(nodes) and p != i:
            children[p].append(i)
        else:
            raise ValueError(f"Invalid parent {p} on node {i}")
    if len(roots) != 1 or roots[0] != 0:
        raise ValueError("One root at node zero is required")
    seen = set()
    def walk(i):
        if i in seen:
            raise ValueError("Cyclic node hierarchy")
        seen.add(i)
        for ch in children[i]:
            walk(ch)
    walk(0)
    if len(seen) != len(nodes):
        raise ValueError("Unreachable or cyclic node hierarchy")
    siblings = [-1 for _ in nodes]
    for group in children:
        for a, b in zip(group, group[1:]):
            siblings[a] = b
    return children, siblings


def _validate_single_model(model, material_dir=None):
    """Raise on unsafe geometry/indices; return a JSON-ready structure report."""
    materials = model['materials']
    meshes, nodes = model['meshes'], model['nodes']
    for material in materials:
        if Path(material).name != material or not re.fullmatch(r'[A-Za-z0-9_$.-]+\.mat', material, re.I):
            raise ValueError(f"Material must be a safe MAT basename: {material}")
        if len(material) > 31:
            raise ValueError(f"Material filename exceeds 31 bytes: {material}")
        if material_dir is not None and not (Path(material_dir)/material).is_file():
            raise ValueError(f"Missing material {material}")
    children, siblings = _links(nodes)
    used_meshes = []
    for i, node in enumerate(nodes):
        mesh = int(node.get('mesh', -1))
        if mesh < -1 or mesh >= len(meshes):
            raise ValueError(f"Node {i} mesh index out of bounds: {mesh}")
        if mesh >= 0:
            used_meshes.append(mesh)
        for key in ('position', 'rotation', 'pivot'):
            _xyz(node.get(key, (0, 0, 0)))
        if not re.fullmatch(r'[\w$.-]{1,31}', node['name'], re.ASCII):
            raise ValueError(f"Invalid node name {node['name']}")
        if 'child' in node:
            # Sibling order is not semantically tied to the node index order;
            # source files can use an alternate valid linked-list ordering.
            ch = node['child']
            chain = []
            while ch != -1:
                if not (0 <= ch < len(nodes)) or ch in chain:
                    raise ValueError(f"Invalid child/sibling chain at node {i}")
                chain.append(ch)
                ch = nodes[ch].get('sibling', -1)
            if set(chain) != set(children[i]):
                raise ValueError(f"Wrong child links at node {i}")
            if node.get('numChildren', len(chain)) != len(chain):
                raise ValueError(f"Wrong child count at node {i}")
    if set(used_meshes) != set(range(len(meshes))):
        raise ValueError("Every mesh must be referenced by the node hierarchy")
    report = []
    for mi, mesh in enumerate(meshes):
        vertices = [_xyz(v) for v in mesh['vertices']]
        uvs, faces = mesh['uvs'], mesh['faces']
        if not re.fullmatch(r'[\w$.-]{1,31}', mesh['name'], re.ASCII):
            raise ValueError(f"Invalid mesh name {mesh['name']}")
        if len(vertices) > MAX_VERTICES or len(uvs) > MAX_UVS or len(faces) > MAX_FACES:
            raise ValueError(f"Mesh {mesh['name']} exceeds JK loader limits: {len(vertices)} v, {len(uvs)} uv, {len(faces)} faces")
        for uv in uvs:
            if len(uv) != 2 or not all(math.isfinite(float(x)) for x in uv):
                raise ValueError(f"Mesh {mi} has invalid UV")
        tris = 0
        for fi, face in enumerate(faces):
            ids, tids = face['vertices'], face['uvs']
            if not 3 <= len(ids) <= MAX_FACE_VERTICES or len(ids) != len(tids):
                raise ValueError(f"Invalid vertex count on {mi}:{fi}")
            if any(i < 0 or i >= len(vertices) for i in ids):
                raise ValueError(f"Invalid vertex index on {mi}:{fi}")
            if any(i < 0 or i >= len(uvs) for i in tids):
                raise ValueError(f"Invalid UV index on {mi}:{fi}")
            if not 0 <= face['material'] < len(materials):
                raise ValueError(f"Invalid material index on {mi}:{fi}")
            _normal(vertices, ids)
            tris += len(ids)-2
        if 'normals' in mesh:
            if len(mesh['normals']) != len(vertices):
                raise ValueError(f'Mesh {mi} vertex normal count mismatch')
            used_vertices={index for face in faces for index in face['vertices']}
            for index, normal in enumerate(mesh['normals']):
                length=_length(_xyz(normal))
                if index in used_vertices and abs(length-1.0)>1e-4:
                    raise ValueError(f'Mesh {mi} vertex {index} normal is not unit length: {length}')
        report.append({'name': mesh['name'], 'vertices': len(vertices), 'uvs': len(uvs), 'faces': len(faces), 'triangles': tris})
    return {'meshes': len(meshes), 'nodes': len(nodes), 'materials': len(materials),
            'vertices': sum(x['vertices'] for x in report), 'faces': sum(x['faces'] for x in report),
            'triangles': sum(x['triangles'] for x in report), 'mesh_details': report,
            'validation_scope': 'Format, indices, finite geometry, hierarchy reachability, documented loader limits; no in-engine proof.'}


def model_geosets(model):
    """Accept original parser lists and authoring {meshes:[...]} geosets."""
    geosets = model.get('geosets', [model['meshes']])
    return [geo['meshes'] if isinstance(geo, dict) else geo for geo in geosets]


def validate_model(model, material_dir=None):
    geosets = model_geosets(model)
    if not 1 <= len(geosets) <= 4:
        raise ValueError('3DO storage supports one to four geosets')
    if len(model['nodes']) > 64:
        raise ValueError('Animated package exceeds the 64-node Puppet track budget')
    names = [mesh['name'] for mesh in geosets[0]]
    reports = []
    for meshes in geosets:
        if [mesh['name'] for mesh in meshes] != names:
            raise ValueError('Every LOD must retain mesh count, names and order')
        reports.append(_validate_single_model({**model, 'meshes': meshes}, material_dir))
    result = dict(reports[0])
    result['geosets'] = len(reports)
    result['lods'] = reports
    return result


def _write_single_3do(path, model):
    report = _validate_single_model(model)
    children, siblings = _links(model['nodes'])
    def vec(v):
        return ' '.join(f'{x:.9f}' for x in _xyz(v))
    radii = [max((_length(v) for v in mesh['vertices']), default=0.) for mesh in model['meshes']]
    # Conservative bound, valid even when a hierarchy has bind rotations.
    bounds = []
    for node in model['nodes']:
        b = radii[node['mesh']] if node.get('mesh', -1) >= 0 else 0.
        cursor = node
        while True:
            b += _length(cursor.get('position', (0,0,0))) + _length(cursor.get('pivot', (0,0,0)))
            if cursor.get('parent', -1) == -1:
                break
            cursor = model['nodes'][cursor['parent']]
        bounds.append(b)
    # Fitted stock rigs contain cancelling dummy transforms. Their verified
    # explicit radius must not be expanded by summing translation magnitudes.
    radius = float(model['radius']) if 'radius' in model else max(bounds, default=0)
    if not math.isfinite(radius) or radius <= 0:
        raise ValueError('Model radius must be finite and positive')
    out = [f"# Original model {model.get('name', Path(path).stem)}; generated by jk_formats.py", '',
           'SECTION: HEADER', '3DO 2.1', '', 'SECTION: MODELRESOURCE', f"MATERIALS {len(model['materials'])}"]
    out += [f'{i}: {name}' for i, name in enumerate(model['materials'])]
    out += ['', 'SECTION: GEOMETRYDEF', f'RADIUS {radius:.9f}',
            'INSERT OFFSET '+vec(model.get('insert_offset', (0,0,0))), 'GEOSETS 1', 'GEOSET 0', f"MESHES {len(model['meshes'])}"]
    for mi, mesh in enumerate(model['meshes']):
        vs = mesh['vertices']
        fns = [_normal(vs, f['vertices']) for f in mesh['faces']]
        vns = [[0.,0.,0.] for _ in vs]
        for face, normal in zip(mesh['faces'], fns):
            for i in face['vertices']:
                vns[i] = [a+b for a,b in zip(vns[i],normal)]
        vns = [[x/(_length(v) or 1.) for x in v] for v in vns]
        if 'normals' in mesh:
            if len(mesh['normals']) != len(vs):
                raise ValueError('Vertex normal count mismatch')
            vns = mesh['normals']
        out += ['', f'MESH {mi}', 'NAME '+mesh['name'], f'RADIUS {radii[mi]:.9f}',
                f"GEOMETRYMODE {mesh.get('geometrymode',4)}", f"LIGHTINGMODE {mesh.get('lightingmode',3)}",
                f"TEXTUREMODE {mesh.get('texturemode',0)}", f'VERTICES {len(vs)}']
        out += [f'{i}: {vec(v)} 0.000000000' for i,v in enumerate(vs)]
        out += [f"TEXTURE VERTICES {len(mesh['uvs'])}"]
        out += [f'{i}: {uv[0]:.9f} {uv[1]:.9f}' for i,uv in enumerate(mesh['uvs'])]
        out += ['VERTEX NORMALS'] + [f'{i}: {vec(n)}' for i,n in enumerate(vns)]
        out += [f"FACES {len(mesh['faces'])}"]
        for fi,face in enumerate(mesh['faces']):
            indices = ' '.join(f'{v},{uv}' for v,uv in zip(face['vertices'],face['uvs']))
            out.append(f"{fi}: {face['material']} 0x{face.get('flags',0):04x} {face.get('geometrymode',4)} {face.get('lightingmode',3)} {face.get('texturemode',0)} {face.get('extralight',0.):.9f} {len(face['vertices'])} {indices}")
        out += ['FACE NORMALS'] + [f'{i}: {vec(n)}' for i,n in enumerate(fns)]
    out += ['', 'SECTION: HIERARCHYDEF', f"HIERARCHY NODES {len(model['nodes'])}",
            '# num flags type mesh parent child sibling numChildren x y z pitch yaw roll pivotx pivoty pivotz name']
    for i,node in enumerate(model['nodes']):
        ch = children[i]
        out.append(f"{i}: 0x{node.get('flags',0):04x} 0x{node.get('type',1):05x} {node.get('mesh',-1)} {node.get('parent',-1)} {ch[0] if ch else -1} {siblings[i]} {len(ch)} {vec(node.get('position',(0,0,0)))} {vec(node.get('rotation',(0,0,0)))} {vec(node.get('pivot',(0,0,0)))} {node['name']}")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(('\r\n'.join(out)+'\r\n').encode('ascii'))
    loaded = read_3do(path)
    validate_model(loaded)
    report.update(path=str(path), bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    return report


def write_3do(path, model):
    """Export all LODs with shared material table and animated hierarchy."""
    report = validate_model(model)
    geosets = model_geosets(model)
    sections = []
    with tempfile.TemporaryDirectory(prefix='lccoda-3do-') as directory:
        for index, meshes in enumerate(geosets):
            temporary = Path(directory)/f'lod{index}.3do'
            single = {key:value for key,value in model.items() if key != 'geosets'}
            single['meshes'] = meshes
            _write_single_3do(temporary, single)
            sections.append(temporary.read_text(encoding='ascii'))
    first = sections[0]
    prefix = first[:first.index('GEOSETS 1')]
    hierarchy = first[first.index('SECTION: HIERARCHYDEF'):]
    geometry = []
    for index, section in enumerate(sections):
        block = section[section.index('GEOSET 0'):section.index('SECTION: HIERARCHYDEF')]
        geometry.append(block.replace('GEOSET 0', f'GEOSET {index}', 1))
    output = prefix + f'GEOSETS {len(geosets)}\n' + ''.join(geometry) + hierarchy
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(output.replace('\r\n','\n').replace('\n','\r\n').encode('ascii'))
    loaded = read_3do(path)
    loaded_report = validate_model(loaded)
    if [r['triangles'] for r in loaded_report['lods']] != [r['triangles'] for r in report['lods']]:
        raise AssertionError('LOD triangle counts changed during export')
    normal_error=0.0;normal_meshes=0
    for original,returned in zip(geosets,model_geosets(loaded)):
        for source_mesh,parsed_mesh in zip(original,returned):
            if 'normals' not in source_mesh:continue
            normal_meshes+=1
            for source_normal,parsed_normal in zip(source_mesh['normals'],parsed_mesh['normals']):
                normal_error=max(normal_error,max(abs(float(a)-float(b)) for a,b in zip(source_normal,parsed_normal)))
    if normal_error>5.01e-10:raise AssertionError('Supplied vertex normals changed beyond 9-decimal serialization')
    report['normal_preservation']={'supplied_meshes_across_lods':normal_meshes,'max_component_error':normal_error,'passed':True}
    report.update(path=str(path), bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    return report


def read_3do(path_or_bytes):
    """Read text 3DO 2.1, including multi-geoset original files."""
    data = path_or_bytes if isinstance(path_or_bytes, bytes) else Path(path_or_bytes).read_bytes()
    lines = [' '.join(line.split('#',1)[0].split()) for line in data.decode('ascii').splitlines()]
    lines = [line for line in lines if line]
    cursor = 0
    def take(prefix=None):
        nonlocal cursor
        if cursor >= len(lines):
            raise ValueError('Unexpected end of 3DO')
        line = lines[cursor]; cursor += 1
        if prefix is not None:
            if not line.lower().startswith(prefix.lower()):
                raise ValueError(f'Expected {prefix}, got {line}')
            return line[len(prefix):].strip()
        return line
    def indexed(count, dimensions, extra=False):
        result=[]
        for i in range(count):
            row=take().split(':',1)
            if int(row[0]) != i:
                raise ValueError('Nonsequential table index')
            values=[float(x) for x in row[1].split()]
            if len(values) != dimensions+(1 if extra else 0):
                raise ValueError('Incorrect vector column count')
            result.append(values[:dimensions])
        return result
    take('SECTION: HEADER')
    version=take('3DO ')
    if version != '2.1':
        raise ValueError(f'Only 3DO 2.1 supported, got {version}')
    take('SECTION: MODELRESOURCE')
    count=int(take('MATERIALS '))
    materials=[]
    for i in range(count):
        row=take().split(':',1)
        if int(row[0]) != i:
            raise ValueError('Nonsequential material index')
        materials.append(row[1].strip())
    take('SECTION: GEOMETRYDEF')
    radius=float(take('RADIUS '))
    insert=[float(x) for x in take('INSERT OFFSET ').split()]
    geosets=[]
    for gi in range(int(take('GEOSETS '))):
        if int(take('GEOSET ')) != gi:
            raise ValueError('Nonsequential geoset')
        meshes=[]
        for mi in range(int(take('MESHES '))):
            if int(take('MESH ')) != mi:
                raise ValueError('Nonsequential mesh')
            mesh={'name':take('NAME '), 'radius':float(take('RADIUS '))}
            for key in ('geometrymode','lightingmode','texturemode'):
                mesh[key]=int(take(key+' '))
            mesh['vertices']=indexed(int(take('VERTICES ')),3,True)
            mesh['uvs']=indexed(int(take('TEXTURE VERTICES ')),2)
            take('VERTEX NORMALS')
            mesh['normals']=indexed(len(mesh['vertices']),3)
            faces=[]
            for fi in range(int(take('FACES '))):
                row=take().split(':',1)
                if int(row[0]) != fi:
                    raise ValueError('Nonsequential face')
                cols=row[1].split(None,7)
                pairs=re.findall(r'(-?\d+)\s*,\s*(-?\d+)',cols[7])
                if len(pairs) != int(cols[6]):
                    raise ValueError('Face index pair count mismatch')
                faces.append({'material':int(cols[0]),'flags':int(cols[1],16),'geometrymode':int(cols[2]),
                              'lightingmode':int(cols[3]),'texturemode':int(cols[4]),'extralight':float(cols[5]),
                              'vertices':[int(v) for v,u in pairs],'uvs':[int(u) for v,u in pairs]})
            mesh['faces']=faces
            take('FACE NORMALS')
            mesh['face_normals']=indexed(len(faces),3)
            meshes.append(mesh)
        geosets.append(meshes)
    take('SECTION: HIERARCHYDEF')
    nodes=[]
    for ni in range(int(take('HIERARCHY NODES '))):
        row=take().split(':',1)
        if int(row[0]) != ni:
            raise ValueError('Nonsequential hierarchy index')
        cols=row[1].split()
        if len(cols) != 17:
            raise ValueError('Incorrect hierarchy column count')
        nodes.append({'flags':int(cols[0],16),'type':int(cols[1],16),'mesh':int(cols[2]),
                      'parent':int(cols[3]),'child':int(cols[4]),'sibling':int(cols[5]),'numChildren':int(cols[6]),
                      'position':[float(x) for x in cols[7:10]],'rotation':[float(x) for x in cols[10:13]],
                      'pivot':[float(x) for x in cols[13:16]],'name':cols[16]})
    if cursor != len(lines):
        raise ValueError('Unexpected trailing 3DO records')
    return {'name':'parsed_model','materials':materials,'radius':radius,'insert_offset':insert,
            'meshes':geosets[0], 'geosets':geosets, 'nodes':nodes}


def gob_read(path, member):
    """Read ONE exact member from a JK GOB/GOO; never writes to the archive."""
    member=member.replace('/','\\').lower()
    with Path(path).open('rb') as f:
        magic, first_size, count_offset = struct.unpack('<4sII',f.read(12))
        if magic != b'GOB ':
            raise ValueError('Not a Jedi Knight GOB')
        f.seek(count_offset)
        count=struct.unpack('<I',f.read(4))[0]
        if count > 1000000:
            raise ValueError('Implausible GOB count')
        for _ in range(count):
            offset,length,name=struct.unpack('<II128s',f.read(136))
            name=name.split(b'\0',1)[0].decode('ascii').replace('/','\\').lower()
            if name == member:
                f.seek(offset)
                data=f.read(length)
                if len(data) != length:
                    raise ValueError('Truncated GOB member')
                return data
    raise FileNotFoundError(member)


def cmp_palette(path_or_bytes):
    data=path_or_bytes if isinstance(path_or_bytes,bytes) else Path(path_or_bytes).read_bytes()
    if data[:4] != b'CMP ' or len(data) < 64+768:
        raise ValueError('Invalid JK CMP file')
    return data[64:64+768]


def write_mat(path, image, format='rgb565', mipmaps=True, palette=None):
    """Write one opaque image cel, four mip levels by default. No image flip.

    indexed8 requires exact 768-byte RGB palette from the TARGET LEVEL CMP.
    The palette is used for quantization but is not embedded or redistributed.
    This does not claim general software-renderer compatibility of rgb565.
    """
    from PIL import Image
    if not isinstance(image, Image.Image):
        image=Image.open(image)
    if image.mode in ('RGBA','LA') and image.getextrema()[-1][0] != 255:
        raise ValueError('Opaque-only writer: flatten transparency intentionally before export')
    image=image.convert('RGB')
    w,h=image.size
    if any(d < 1 or d&(d-1) for d in (w,h)):
        raise ValueError('MAT dimensions must be powers of two')
    if format == 'rgb565':
        fmt=[1,16,5,6,5,11,5,0,3,2,3,0,0,0]
    elif format == 'indexed8':
        if palette is None or len(palette) != 768:
            raise ValueError('indexed8 requires the exact target CMP palette (768 RGB bytes)')
        fmt=[0,8]+[0]*12
    else:
        raise ValueError('Supported MAT formats: rgb565 and indexed8')
    count = (MAX_MIPMAPS if mipmaps is True else 1 if mipmaps is False else int(mipmaps))
    count=min(count,1+int(math.log2(min(w,h))))
    if not 1 <= count <= MAX_MIPMAPS:
        raise ValueError('JK materials support one through four mip levels')
    chunks=[struct.pack('<4s18I', b'MAT ',50,2,1,1,*fmt),
            struct.pack('<10I',8,0,0x3f800000,0x3f800000,0x3f800000,0x3f800000,0,0,0xbff78482,0),
            struct.pack('<6I',w,h,0,0,0,count)]
    for level in range(count):
        im=image if level == 0 else image.resize((w>>level,h>>level),Image.Resampling.BOX)
        if format == 'rgb565':
            raw=bytearray()
            for r,g,b in im.getdata():
                raw.extend(struct.pack('<H',((r>>3)<<11)|((g>>2)<<5)|(b>>3)))
            chunks.append(bytes(raw))
        else:
            pal=Image.new('P',(1,1)); pal.putpalette(palette)
            chunks.append(im.quantize(palette=pal,dither=Image.Dither.FLOYDSTEINBERG).tobytes())
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(b''.join(chunks))
    result=validate_mat(path)
    result['palette_sha256']=hashlib.sha256(palette).hexdigest() if palette is not None else None
    return result


def read_mat(path, palette=None):
    """Strict readback for the single-cel opaque formats emitted here."""
    from PIL import Image
    data=Path(path).read_bytes()
    if len(data) < 140:
        raise ValueError('MAT shorter than single-cel header')
    hdr=struct.unpack_from('<4s18I',data)
    if hdr[:5] != (b'MAT ',50,2,1,1):
        raise ValueError('Expected revision 50, texture, one material, one texture')
    fmt=hdr[5:]
    if fmt not in [(1,16,5,6,5,11,5,0,3,2,3,0,0,0),(0,8,0,0,0,0,0,0,0,0,0,0,0,0)]:
        raise ValueError('Unsupported color format')
    record=struct.unpack_from('<10I',data,76)
    if record[0] != 8 or record[-1] != 0:
        raise ValueError('Invalid texture record')
    w,h,alpha,unused,key,count=struct.unpack_from('<6I',data,116)
    if alpha or not 1 <= count <= 4 or any(d < 1 or d&(d-1) for d in (w,h)):
        raise ValueError('Unsupported texture header')
    bpp=fmt[1]; offset=140; images=[]; sizes=[]
    for level in range(count):
        mw,mh=w>>level,h>>level
        if min(mw,mh) < 1:
            raise ValueError('Mip dimension underflows to zero')
        size=mw*mh*(bpp//8)
        raw=data[offset:offset+size]
        if len(raw) != size:
            raise ValueError('Truncated MAT pixels')
        if bpp == 16:
            pixels=[]
            for val, in struct.iter_unpack('<H',raw):
                pixels.append((((val>>11)&31)<<3,((val>>5)&63)<<2,(val&31)<<3))
            im=Image.new('RGB',(mw,mh)); im.putdata(pixels)
        else:
            im=Image.frombytes('P',(mw,mh),raw)
            if palette is not None:
                im.putpalette(palette); im=im.convert('RGB')
        images.append(im); sizes.append([mw,mh]); offset+=size
    if offset != len(data):
        raise ValueError('Unexpected trailing MAT bytes')
    return {'width':w,'height':h,'bpp':bpp,'format':'rgb565' if bpp==16 else 'indexed8',
            'mipmap_count':count,'mip_dimensions':sizes,'bytes':len(data),'images':images,
            'sha256':hashlib.sha256(data).hexdigest()}


def validate_mat(path):
    result=read_mat(path)
    del result['images']
    return result


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file',type=Path)
    parser.add_argument('--materials',type=Path)
    args=parser.parse_args()
    result=validate_mat(args.file) if args.file.suffix.lower()=='.mat' else validate_model(read_3do(args.file),args.materials)
    print(json.dumps(result,indent=2))
