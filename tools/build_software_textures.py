"""Build an optional private 8-bit MotS software-renderer texture override.

Reads a complete SBX MotS base plus overlay, leaving both immutable. Converts
every winning mod-path RGB565 MAT, preserving all cells, texture dimensions,
present mip levels and color-key masks. Two hash-pinned historical truncated
mip chains are completed with box-filtered lower levels. Standard library only.
"""
from pathlib import Path
import argparse
import collections
import json
import math
import struct

from archive_io import digest, read_gob, write_gob, extract


RGB565 = (1, 16, 5, 6, 5, 11, 5, 0, 3, 2, 3, 0, 0, 0)
INDEXED8 = (0, 8)+(0,)*12
KNOWN_MISSING_MIPS = {
    '3do/mat/mwdchest.mat': '99e2c05287f2dcf164b767e97b64a7741dad1bda6cbd8f9db3f2bce3ba2a2866',
    '3do/mat/mwdback.mat': '7fb7628f2c29dd9a4db6b7a97759e4260745bf392a1a53dea70f74c8ab07e20c',
}
# The static dark-blue companions and animated cells share blade/fan model
# roles. The same color must not change merely because one path is animated.
EMISSIVE_MATERIALS = {'blueanim.mat', 'lukeblueanim.mat', 'dblue.mat', 'lukedblue.mat'}
BAYER4 = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))


def read_layer(path):
    path = Path(path)
    if path.is_file():
        return read_gob(path)
    if not path.is_dir():
        raise FileNotFoundError(path)
    result = {}
    for member in sorted(path.rglob('*')):
        if member.is_file():
            name = member.relative_to(path).as_posix().lower()
            if name in result:
                raise ValueError('Case-colliding overlay resource: '+name)
            result[name] = member.read_bytes()
    return result


def rgb565(value):
    return (((value >> 11)*255+15)//31, (((value >> 5)&63)*255+31)//63,
            ((value&31)*255+15)//31)


def encode565(rgb):
    r,g,b = rgb
    return ((r*31+127)//255 << 11) | ((g*63+127)//255 << 5) | ((b*31+127)//255)


def lower_mip(previous, width, height, transparent, key):
    """Rebuild only an absent tail; use an explicit 2x2 box/cutout rule."""
    values = [v[0] for v in struct.iter_unpack('<H', previous)]
    result = bytearray()
    for y in range(height//2):
        for x in range(width//2):
            block = [values[(2*y+dy)*width+2*x+dx] for dy in (0,1) for dx in (0,1)]
            opaque = [v for v in block if not transparent or v != key]
            if transparent and len(opaque) <= 2:
                value = key
            else:
                colors = [rgb565(v) for v in opaque]
                average = tuple((sum(c[i] for c in colors)+len(colors)//2)//len(colors) for i in range(3))
                value = encode565(average)
                if transparent and value == key:
                    value = key ^ 1
            result.extend(struct.pack('<H', value))
    return bytes(result)


def parse_mat(raw, name='', repair_missing=False):
    if len(raw) < 76:
        raise ValueError('Truncated MAT header: '+name)
    header = struct.unpack_from('<4s18I', raw)
    if header[:2] != (b'MAT ',50):
        raise ValueError('Unsupported MAT magic/revision: '+name)
    kind, cells, textures = header[2:5]
    if kind & 1:
        raise ValueError('Embedded MAT palettes are outside this native conversion: '+name)
    if header[5:7] not in ((1,16),(0,8)):
        raise ValueError('Unsupported MAT color format: '+name)
    bpp = header[6]
    if bpp == 16 and header[5:] != RGB565:
        raise ValueError('Only the observed native RGB565 layout is supported: '+name)
    if not 1 <= cells <= 256 or not 0 <= textures <= 256:
        raise ValueError('Invalid cell/texture count: '+name)
    cursor = 76
    infos = []
    for _ in range(cells):
        row = struct.unpack_from('<6I',raw,cursor)
        start = cursor
        cursor += 24
        if row[0] & 8:
            ext = struct.unpack_from('<4I',raw,cursor)
            cursor += 16
            if ext[3] >= textures:
                raise ValueError('Texture cell index out of range: '+name)
        else:
            ext = None
        infos.append(dict(raw=raw[start:cursor], values=row, texture=ext[3] if ext else None))
    result = []
    repairs = []
    authorized_repair = (repair_missing and bpp == 16 and
                         KNOWN_MISSING_MIPS.get(name) == digest(raw))
    for index in range(textures):
        values = struct.unpack_from('<6I',raw,cursor)
        cursor += 24
        width,height,alpha,unused,key,count = values
        if any(d < 1 or d&(d-1) for d in (width,height)) or not 1 <= count <= 4:
            raise ValueError('Invalid native texture dimensions/mips: '+name)
        if alpha not in (0,1):
            raise ValueError('Unsupported transparency flags: '+name)
        levels = []
        for level in range(count):
            w,h = width >> level,height >> level
            if min(w,h) < 1:
                raise ValueError('Mip dimensions underflow: '+name)
            length = w*h*(bpp//8)
            if cursor+length <= len(raw):
                pixels = raw[cursor:cursor+length]
                cursor += length
                reconstructed = False
            elif authorized_repair and index == textures-1 and cursor == len(raw) and levels:
                pixels = lower_mip(levels[-1]['pixels'],w*2,h*2,alpha&1,key)
                reconstructed = True
                repairs.append(dict(texture=index,mip=level,width=w,height=h,
                                    method='2x2 RGB565 box reduction from preceding complete mip; declared level retained'))
            else:
                raise ValueError(f'Truncated texture or unknown missing mip: {name}, texture{index}, mip{level}')
            levels.append(dict(width=w,height=h,pixels=pixels,reconstructed=reconstructed))
        result.append(dict(header=values,levels=levels))
    if cursor != len(raw):
        raise ValueError('Unexpected MAT trailing bytes: '+name)
    return dict(header=header,infos=infos,textures=result,repairs=repairs)


def palette_profiles(stock):
    members = sorted(n for n in stock if n.startswith('misc/cmp/') and n.endswith('.cmp')
                     and n != 'misc/cmp/uicolormap.cmp')
    if 'misc/cmp/dflt.cmp' not in members:
        raise ValueError('Native default CMP is missing')
    for name in members:
        if stock[name][:4] != b'CMP ' or len(stock[name]) < 832+64*256:
            raise ValueError('Invalid native map CMP: '+name)
    reference = stock['misc/cmp/dflt.cmp']
    palette = [tuple(reference[64+i*3:67+i*3]) for i in range(256)]
    stable = [i for i in range(1,256)
              if len({stock[n][64+i*3:67+i*3] for n in members}) == 1]
    # Avoid assigning diffuse art to indices whose palette light-table column
    # remains a nonblack constant through all 64 illumination levels.
    fullbright = [i for i in stable if palette[i] != (0,0,0) and any(
        len({stock[n][832+level*256+i] for level in range(64)}) == 1 for n in members)]
    def deduplicate(indices):
        seen=set();result=[]
        for i in indices:
            if palette[i] not in seen:
                seen.add(palette[i]);result.append(i)
        return result
    diffuse = deduplicate(i for i in stable if i not in fullbright)
    emissive = deduplicate(stable)
    return palette, dict(diffuse=diffuse,emissive=emissive), dict(
        reference_member='misc/cmp/dflt.cmp',reference_rgb_sha256=digest(reference[64:832]),
        checked_map_palettes=[dict(path=n,sha256=digest(stock[n])) for n in members],
        stable_nontransparent_indices=stable,fullbright_indices_excluded_for_diffuse=fullbright,
        diffuse_indices=diffuse,emissive_indices=emissive,
        limits='Stable RGB entries only. Custom maps with different palettes are not certified. Diffuse colors avoid permanently self-lit entries; this restricts saturated color fidelity.')


class Quantizer:
    def __init__(self,palette,indices):
        self.palette=palette
        self.choices=[(i,*palette[i]) for i in indices]
        self.cache={}

    def nearest(self,rgb):
        cached=self.cache.get(rgb)
        if cached is not None:
            return cached
        r,g,b=rgb
        # A fixed weighted RGB metric and ascending-index tie break make the
        # result reproducible. It is not a perceptual/color-managed transform.
        best=min(self.choices,key=lambda c:2*(r-c[1])**2+3*(g-c[2])**2+(b-c[3])**2)[0]
        self.cache[rgb]=best
        return best


def convert(raw,name,quantizer,dither='ordered',repair_missing=True):
    source=parse_mat(raw,name,repair_missing)
    if source['header'][6] != 16:
        raise ValueError('Conversion input is not 16-bit: '+name)
    header=list(source['header']);header[5:]=INDEXED8
    output=bytearray(struct.pack('<4s18I',*header))
    for info in source['infos']:
        cell=bytearray(info['raw'])
        if info['texture'] is None:
            value=quantizer.nearest(rgb565(info['values'][1]&65535))
            struct.pack_into('<I',cell,4,value)
        output.extend(cell)
    level_reports=[]
    total_squared=total_absolute=total_samples=maximum_squared=0
    for texture_index,texture in enumerate(source['textures']):
        width,height,alpha,unused,key,count=texture['header']
        output.extend(struct.pack('<6I',width,height,alpha,unused,0,count))
        for mip,level in enumerate(texture['levels']):
            w,h=level['width'],level['height']
            # Fixed small ordered offsets for ordinary diffuse texture detail.
            # No dithering for animated cells, emissive art, or tiny mip levels.
            ordered=(dither=='ordered' and source['header'][3]==1 and
                     Path(name).name not in EMISSIVE_MATERIALS and min(w,h)>=16)
            pixels=bytearray();transparent_pixels=0
            squared=absolute=samples=max_squared=0
            for pos,(value,) in enumerate(struct.iter_unpack('<H',level['pixels'])):
                if alpha&1 and value==key:
                    pixels.append(0);transparent_pixels+=1;continue
                color=rgb565(value)
                target=color
                if ordered:
                    delta=2*BAYER4[(pos//w)&3][pos&3]-15
                    target=tuple(max(0,min(255,(2*c+delta+1)//2)) for c in color)
                index=quantizer.nearest(target)
                assert index != 0
                pixels.append(index)
                errors=[color[c]-quantizer.palette[index][c] for c in range(3)]
                error_squared=sum(e*e for e in errors)
                squared+=error_squared;absolute+=sum(abs(e) for e in errors);samples+=1
                max_squared=max(max_squared,error_squared)
            output.extend(pixels)
            total_squared+=squared;total_absolute+=absolute;total_samples+=samples
            maximum_squared=max(maximum_squared,max_squared)
            level_reports.append(dict(texture=texture_index,mip=mip,width=w,height=h,
                reconstructed=level['reconstructed'],transparency_mask_preserved=True,
                transparent_pixels=transparent_pixels,opaque_pixels=samples,
                dither='ordered-4x4-channel-offset-max8' if ordered else 'nearest',
                rgb_rmse=round(math.sqrt(squared/(3*samples)),4) if samples else 0,
                rgb_mae=round(absolute/(3*samples),4) if samples else 0))
    result=bytes(output)
    check=parse_mat(result,name)
    assert check['header'][3:5]==source['header'][3:5]
    assert check['header'][5:]==INDEXED8
    for before,after in zip(source['infos'],check['infos']):
        assert before['texture']==after['texture']
        if before['texture'] is not None:assert before['raw']==after['raw']
    for before,after in zip(source['textures'],check['textures']):
        assert before['header'][:4]==after['header'][:4]
        assert before['header'][5]==after['header'][5]
        for old,new in zip(before['levels'],after['levels']):
            values=[v[0] for v in struct.iter_unpack('<H',old['pixels'])]
            assert len(values)==len(new['pixels'])
            assert all((bool(before['header'][2]&1) and a==before['header'][4]) == (b==0)
                       for a,b in zip(values,new['pixels']))
    return result,dict(cells=header[3],textures=header[4],mips=level_reports,repairs=source['repairs'],
                      rgb_error=dict(opaque_pixels=total_samples,
                         rmse=round(math.sqrt(total_squared/(3*total_samples)),4) if total_samples else 0,
                         mean_absolute=round(total_absolute/(3*total_samples),4) if total_samples else 0,
                         max_euclidean=round(math.sqrt(maximum_squared),4),
                         squared_sum=total_squared,absolute_sum=total_absolute),
                      structures_and_transparency_verified=True)


def build(overlay,base,mots_res,out,dither='ordered'):
    if dither not in ('ordered','none'):
        raise ValueError('Dither must be ordered or none')
    out=Path(out)
    if out.exists():
        raise FileExistsError('Choose a new software-texture output directory')
    stock=read_gob(mots_res);base_members=read_layer(base);overlay_members=read_layer(overlay)
    mod=base_members|overlay_members
    palette,profiles,palette_report=palette_profiles(stock)
    quantizers={name:Quantizer(palette,indices) for name,indices in profiles.items()}
    targets={};inventory=[]
    for name,raw in sorted(mod.items()):
        if not name.endswith('.mat'):continue
        if len(raw)<76 or raw[:4]!=b'MAT ':
            raise ValueError('Invalid active mod MAT: '+name)
        header=struct.unpack_from('<4s18I',raw)
        inventory.append(dict(path=name,bpp=header[6],cells=header[3],textures=header[4],
                              source='overlay' if name in overlay_members else 'sbx-mots30',sha256=digest(raw)))
        if header[6]==16:targets[name]=raw
        elif header[6]!=8:raise ValueError('Unexpected active mod material depth: '+name)
    if not targets:
        raise ValueError('No active 16-bit mod materials found; check base/overlay inputs')
    generated={};rows=[]
    for name,raw in targets.items():
        profile='emissive' if Path(name).name in EMISSIVE_MATERIALS else 'diffuse'
        converted,receipt=convert(raw,name,quantizers[profile],dither)
        generated[name]=converted
        rows.append(dict(path=name,source='overlay' if name in overlay_members else 'sbx-mots30',
                         source_sha256=digest(raw),sha256=digest(converted),source_bytes=len(raw),
                         output_bytes=len(converted),palette_profile=profile,**receipt))
    # Every original 16-bit mod path is superseded; other active mod bytes stay
    # identical. The native stock MAT library is not bulk copied or converted.
    assert set(generated)==set(targets)
    merged=mod|generated
    assert all(struct.unpack_from('<I',raw,24)[0]==8 for name,raw in merged.items() if name.endswith('.mat'))
    extract(generated,out/'overlay')
    archive=out/'SBX-MotS-Software-Textures.goo';write_gob(generated,archive)
    sums=[r['rgb_error'] for r in rows]
    samples=sum(r['opaque_pixels'] for r in sums)
    report=dict(schema='sbx-mots-software-textures-v1',
        status='GENERATED_AND_STRUCTURALLY_CHECKED_NOT_RETAIL_ACCEPTED',
        scope='Optional texture-only local override; authentic accelerated textures remain unchanged in the main overlay.',
        material_count=len(rows),texture_count=sum(r['textures'] for r in rows),
        animated_materials=[r['path'] for r in rows if r['cells']>1],
        reconstruction_repairs=[dict(path=r['path'],levels=r['repairs']) for r in rows if r['repairs']],
        default_dither=dither,palette=palette_report,inventory=inventory,materials=rows,
        all_active_mod_materials_indexed_after_override=True,all_cells_mips_and_transparency_checked=True,
        aggregate_rgb_error=dict(opaque_pixels=samples,
            rmse=round(math.sqrt(sum(r['squared_sum'] for r in sums)/(3*samples)),4),
            mean_absolute=round(sum(r['absolute_sum'] for r in sums)/(3*samples),4)),
        generated_archive_sha256=digest(archive.read_bytes()),
        quality_limits='8-bit palette conversion loses RGB565 color precision. Stable normally shaded colors restrict saturated diffuse hues. Ordered dithering can add fine grain; animated/small textures use nearest mapping. Error metrics are source RGB comparisons, not perceptual quality or native rendering tests.',
        distribution='Private local derivation from owned/user-supplied resources. Distribute this source builder, not generated texture data.')
    (out/'software-textures.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('overlay','base','mots-res','out'):parser.add_argument('--'+name,required=True,type=Path)
    parser.add_argument('--dither',choices=('ordered','none'),default='ordered')
    args=parser.parse_args();report=build(args.overlay,args.base,args.mots_res,args.out,args.dither)
    print(json.dumps({k:report[k] for k in ('status','material_count','texture_count','animated_materials','reconstruction_repairs','aggregate_rgb_error','generated_archive_sha256')},indent=2))
