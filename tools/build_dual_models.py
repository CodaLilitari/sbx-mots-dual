"""Build local SBX player variants with native retail left-hilt geometry.

Consumes owned/user-supplied mod resources. Does not ship any base archive.
The original 0..17 animated skeleton is preserved. Empty SBX anchors 18/19
become left/right grip anchors, only in variants used by the dual puppet.
"""
from pathlib import Path
import argparse, copy, json, re, math
import jk_formats as fmt
from archive_io import digest

def parsed(data):
    # Historical SBX files use both C++-style and hash inline comments.
    clean=re.sub(rb'//[^\r\n]*',b'',data.rstrip(b'\x1a'))
    return fmt.read_3do(clean)

def hilt_from_saber(model):
    mesh=copy.deepcopy(model['meshes'][0])
    # Supplied JK31 saber: luminous faces use WHITE/GREENANIM/DGREEN/CLEAR;
    # the hilt uses the named ordinary metal/handle textures below.
    allowed={'bowpprt2.mat','kysaber1.mat','bowpbar2.mat','kysaber2.mat'}
    faces=[f for f in mesh['faces'] if model['materials'][f['material']].lower() in allowed]
    if not faces: raise ValueError('No hilt faces found')
    vs=sorted({i for f in faces for i in f['vertices']})
    us=sorted({i for f in faces for i in f['uvs']})
    mats=sorted({f['material'] for f in faces})
    vi={n:i for i,n in enumerate(vs)};ui={n:i for i,n in enumerate(us)};mi={n:i for i,n in enumerate(mats)}
    mesh['vertices']=[mesh['vertices'][i] for i in vs]
    mesh['uvs']=[mesh['uvs'][i] for i in us]
    mesh['normals']=[mesh['normals'][i] for i in vs]
    for f in faces:
        f['vertices']=[vi[i] for i in f['vertices']]
        f['uvs']=[ui[i] for i in f['uvs']]
        f['material']=mi[f['material']]
    mesh['faces']=faces;mesh['name']='sbxd_lhilt'
    return mesh,[model['materials'][i] for i in mats]

def fist_center(model,meshes,hand):
    points=meshes[model['nodes'][hand]['mesh']]['vertices']
    return (min(v[1] for v in points)+max(v[1] for v in points))/2

def grip(model,meshes,hand,hilt):
    low=min(v[1] for v in hilt['vertices'])
    if low>=0:raise ValueError('Unexpected hilt axis')
    center=fist_center(model,meshes,hand)
    return max(low,min(-low,center-low/2))

def reverse_grip(model,meshes,hand,hilt):
    """Dual Sabers 17's reverse grip: the hilt turned end over end about the
    middle of the fist (half a turn about the hand's up axis), as OpenJKDF2's
    jkPlayer_GripMatrix does. Returns the anchor's position along the hand's
    forward axis; its rotation is yaw 180."""
    return 2*fist_center(model,meshes,hand)-grip(model,meshes,hand,hilt)

def reverse_grip_anchors(data,hilt):
    """Reverse-grip anchor positions (left node18, right node19) for one
    player model, from its first geoset, as the upper loop key carries them."""
    model=parsed(data);meshes=fmt.model_geosets(model)[0]
    return reverse_grip(model,meshes,6,hilt),reverse_grip(model,meshes,12,hilt)

def variant(data,hilt,materials):
    model=parsed(data);before=copy.deepcopy(model)
    if len(model['nodes'])!=20:raise ValueError('Expected existing SBX 20-node skeleton')
    nodes=model['nodes']
    if nodes[6]['name'].lower()!='k_lhand' or nodes[12]['name'].lower()!='k_rhand':raise ValueError('Unexpected hand mapping')
    spare=nodes[19]['mesh']
    if nodes[18]['mesh']!=-1 or spare<0:raise ValueError('SBX spare anchors unavailable')
    remap=[]
    for material in materials:
        table=[x.lower() for x in model['materials']]
        if material.lower() not in table:model['materials'].append(material)
        remap.append([x.lower() for x in model['materials']].index(material.lower()))
    offsets=[];reverse=[]
    for meshes in fmt.model_geosets(model):
        if meshes[spare]['vertices'] or meshes[spare]['faces']:raise ValueError('Spare mesh is not empty')
        offsets.append((grip(model,meshes,6,hilt),grip(model,meshes,12,hilt)))
        reverse.append((reverse_grip(model,meshes,6,hilt),reverse_grip(model,meshes,12,hilt)))
        mesh=copy.deepcopy(hilt)
        for face in mesh['faces']:face['material']=remap[face['material']]
        meshes[spare]=mesh
    left,right=offsets[0]
    for idx,parent,offset,mesh,name,typ in [(18,6,left,spare,'sbxd_left_grip',2),(19,12,right,-1,'sbxd_right_grip',4)]:
        nodes[idx].update(parent=parent,mesh=mesh,position=[0,offset,0],rotation=[0,0,0],pivot=[0,0,0],name=name,type=typ)
    # Every source animated node, mesh, UV, face and material assignment is unchanged.
    assert nodes[:18]==before['nodes'][:18]
    for orig,new in zip(fmt.model_geosets(before),fmt.model_geosets(model)):
        for i,(a,b) in enumerate(zip(orig,new)):
            if i!=spare:assert a==b
    # Child links are regenerated from the preserved parent graph plus the two
    # deliberately repurposed anchors. They are not animation transforms.
    for node in nodes:
        for field in ('child','sibling','numChildren'):node.pop(field,None)
    return model,{'left_grip_offset':left,'right_grip_offset':right,'left_reverse_anchor':reverse[0][0],'right_reverse_anchor':reverse[0][1],'reused_empty_mesh':spare,'lods':len(offsets),'source_sha256':digest(data)}

def serialize_variant(raw,model,spare):
    """Surgical edit: preserve every original visible mesh and its normals."""
    text=raw.rstrip(b'\x1a').decode('ascii').replace('\r\n','\n')
    def vec(v):return ' '.join(format(x,'.9g') for x in v)
    materials='MATERIALS %d\n'%len(model['materials'])+'\n'.join(f'{i}: {m}' for i,m in enumerate(model['materials']))+'\n\n'
    text,n=re.subn(r'(?ims)^MATERIALS\s+\d+\s*\n.*?(?=^SECTION:\s*GEOMETRYDEF)',materials,text)
    assert n==1
    geos=iter(fmt.model_geosets(model))
    def replace_mesh(match):
        mesh=next(geos)[spare]
        radius=max(math.sqrt(sum(c*c for c in v)) for v in mesh['vertices'])
        lines=[f'MESH {spare}','NAME '+mesh['name'],f'RADIUS {radius:.9g}',f"GEOMETRYMODE {mesh['geometrymode']}",f"LIGHTINGMODE {mesh['lightingmode']}",f"TEXTUREMODE {mesh['texturemode']}",f"VERTICES {len(mesh['vertices'])}"]
        lines += [f'{i}: {vec(v)} 0' for i,v in enumerate(mesh['vertices'])]
        lines += [f"TEXTURE VERTICES {len(mesh['uvs'])}"]+[f'{i}: {vec(v)}' for i,v in enumerate(mesh['uvs'])]
        lines += ['VERTEX NORMALS']+[f'{i}: {vec(v)}' for i,v in enumerate(mesh['normals'])]
        lines += [f"FACES {len(mesh['faces'])}"]
        for i,f in enumerate(mesh['faces']):
            pairs=' '.join(f'{a},{b}' for a,b in zip(f['vertices'],f['uvs']))
            lines.append(f"{i}: {f['material']} 0x{f['flags']:x} {f['geometrymode']} {f['lightingmode']} {f['texturemode']} {f['extralight']:.9g} {len(f['vertices'])} {pairs}")
        lines += ['FACE NORMALS']+[f"{i}: {vec(fmt._normal(mesh['vertices'],f['vertices']))}" for i,f in enumerate(mesh['faces'])]
        return '\n'.join(lines)+'\n\n'
    text,n=re.subn(rf'(?ims)^MESH\s+{spare}\s*\n.*?(?=^MESH\s+\d+\s*$|^SECTION:\s*HIERARCHYDEF)',replace_mesh,text)
    assert n==len(fmt.model_geosets(model))
    at=text.upper().index('SECTION: HIERARCHYDEF');prefix=text[:at];hier=text[at:]
    children,siblings=fmt._links(model['nodes'])
    # Regenerate every link from the parent graph. Some historical source
    # skins have stale child pointers (notably plorobe's head -> node19).
    # Only links change here; transforms and visible source meshes stay exact.
    for i in range(len(model['nodes'])):
        node=model['nodes'][i];ch=children[i]
        line=f"{i}: 0x{node['flags']:x} 0x{node['type']:x} {node['mesh']} {node['parent']} {ch[0] if ch else -1} {siblings[i]} {len(ch)} {vec(node['position'])} {vec(node['rotation'])} {vec(node['pivot'])} {node['name']}"
        hier,count=re.subn(rf'(?m)^\s*{i}:.*$',line,hier)
        assert count==1
    result=(prefix+hier).replace('\n','\r\n').encode('ascii')
    check=parsed(result);before=parsed(raw)
    for a,b in zip(fmt.model_geosets(before),fmt.model_geosets(check)):
        for i,(am,bm) in enumerate(zip(a,b)):
            if i!=spare:assert am==bm,('Unexpected visible source mesh change',i)
    for i in range(18):
        for key in ('mesh','parent','position','rotation','pivot','type','flags'):
            assert before['nodes'][i][key]==check['nodes'][i][key],(i,key)
    return result

def build(source_roots,out,registry):
    roots=[Path(p) for p in source_roots];out=Path(out);out.mkdir(parents=True,exist_ok=True)
    def read(name):
        for root in roots:
            p=root/name
            if p.is_file():return p.read_bytes()
        raise FileNotFoundError(name)
    # The JK31 donor is intentionally namespaced by the main builder.
    hilt,mats=hilt_from_saber(parsed(read('3do/sbxd_donor.3do')))
    names=sorted(set(re.findall(r'^\s*\d+:\s+(\S+\.3do)',Path(registry).read_text(encoding='latin1'),re.M|re.I))|{'ky.3do','mj.3do'})
    rows=[];errors=[]
    for i,name in enumerate(names):
        try:
            data=read('3do/'+name.lower());model,receipt=variant(data,hilt,mats)
            dest='3do/dx%03d.3do'%i
            (out/dest).parent.mkdir(parents=True,exist_ok=True)
            (out/dest).write_bytes(serialize_variant(data,model,receipt['reused_empty_mesh']))
            check=parsed((out/dest).read_bytes())
            for a,b in zip(check['nodes'][:18],model['nodes'][:18]):
                assert all(a[k]==v for k,v in b.items())
            rows.append({'source':name.lower(),'variant':Path(dest).name,**receipt,'sha256':digest((out/dest).read_bytes())})
        except (ValueError,FileNotFoundError,AssertionError) as e:errors.append({'source':name,'reason':str(e)})
    report={'models':rows,'unsupported':errors,'scope':'Generated local variants only; retail runtime not established by this report.'}
    (out/'dual-models.json').write_text(json.dumps(report,indent=2))
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',action='append',required=True);ap.add_argument('--out',required=True);ap.add_argument('--registry',required=True);a=ap.parse_args()
    result=build(a.source,a.out,a.registry);print(json.dumps({'built':len(result['models']),'unsupported':result['unsupported']},indent=2))
