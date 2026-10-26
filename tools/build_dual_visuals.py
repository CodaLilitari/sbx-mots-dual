"""Build private native MotS dual-blade MAT pairs and one right hilt model.

Standard library only. Seven blade pairs are exact owned MotS resources;
three pairs are palette-index remaps of those resources, preserving every
header byte and all transparent pixels. No source archive is modified.
"""
from pathlib import Path
import argparse
import collections
import copy
import json
import math
import struct

from archive_io import digest, read_gob
from build_dual_models import parsed, hilt_from_saber
import jk_formats as fmt


COLORS = (
    ('orange', 'orange', None),
    ('purple', 'purple', None),
    ('dark-purple', 'purple', 'dark-purple'),
    ('blue', 'blue', None),
    ('light-blue', 'blue', 'light-blue'),
    ('red', 'red', None),
    ('dark-red', 'dred', None),
    ('yellow', 'yellow', None),
    ('green', 'green', None),
    ('silver', 'blue', 'silver'),
)
PALETTE_MEMBER = 'misc/cmp/dflt.cmp'


def inspect_mat(data):
    """Validate the native single-cel indexed texture layout without Pillow."""
    if len(data) < 140:
        raise ValueError('Truncated MAT')
    header = struct.unpack_from('<4s18I', data)
    if header[:5] != (b'MAT ', 50, 2, 1, 1):
        raise ValueError('Expected native revision50 one-cel texture MAT')
    # Native indexed files retain nonzero unused color-format words. Only
    # the indexed-mode and bit-depth fields govern this lane; preserve the rest.
    if header[5:7] != (0, 8):
        raise ValueError('Expected native indexed8 color format')
    record = struct.unpack_from('<10I', data, 76)
    if record[0] != 8 or record[-1] != 0:
        raise ValueError('Unexpected native MAT texture record')
    width, height, transparent, unused, key, mips = struct.unpack_from('<6I', data, 116)
    if transparent not in (0, 1) or key != 0 or mips not in range(1, 5):
        raise ValueError('Unexpected transparency/mip contract')
    if any(n < 1 or n & (n-1) for n in (width, height)):
        raise ValueError('Expected power-of-two texture dimensions')
    length = sum((width >> i)*(height >> i) for i in range(mips))
    if len(data) != 140+length:
        raise ValueError('Unexpected MAT pixel length')
    histogram = collections.Counter(data[140:])
    if not any(index != 0 for index in histogram):
        raise ValueError('Blade MAT is fully index-zero')
    return dict(width=width, height=height, bpp=8, mips=mips,
                transparent=transparent, color_key=key,
                transparent_pixel_count=histogram.get(0, 0),
                nonzero_pixel_count=length-histogram.get(0, 0),
                indices=sorted(histogram))


def remap_for(kind, palette):
    table = list(range(256))
    if kind == 'light-blue':
        # Brighten the native blue ramp by two rungs. Index18 is omitted as a
        # destination because its RGB differs among stock MotS map palettes.
        # Keep the white core16 and the lightest colored rung17 unchanged.
        ladder = [143, 142, 141, 140, 139, 138, 137, 136, 20, 19, 17]
        for pos, index in enumerate(ladder):
            table[index] = ladder[min(pos+2, len(ladder)-1)]
        table[18] = 17
    elif kind == 'dark-purple':
        # Move the colored purple glow one rung darker, retaining white16.
        # The native purple pair includes yellow104 and red8 pixels; bring
        # those into the purple ramp for this new, deliberately distinct tint.
        for index in range(184, 192):
            table[index] = min(index+1, 191)
        table[104] = 184
        table[8] = 191
    elif kind == 'silver':
        # Preserve source luminance using stable native grayscale entries.
        # White16 remains white; never map an opaque source pixel to index0.
        grays = [16, *range(33, 63)]
        for index in range(1, 256):
            r, g, b = palette[index*3:index*3+3]
            luminance = (2126*r+7152*g+722*b)/10000
            table[index] = min(grays, key=lambda i: (abs(palette[i*3]-luminance), i))
    else:
        raise ValueError('Unknown derived color: '+kind)
    table[0] = 0
    table[16] = 16
    return bytes(table)


def derived_mat(source, kind, palette):
    before = inspect_mat(source)
    table = remap_for(kind, palette)
    result = source[:140]+source[140:].translate(table)
    after = inspect_mat(result)
    assert result[:140] == source[:140]
    assert all((a == 0) == (b == 0) for a, b in zip(source[140:], result[140:]))
    assert before['transparent_pixel_count'] == after['transparent_pixel_count']
    assert result != source, 'Derived material did not change'
    return result, {str(i):table[i] for i in before['indices']}


def build(jk31_root, mots_res, out):
    """Generate 21 resources plus a provenance report into a new directory."""
    jk31_root, mots_res, out = map(Path, (jk31_root, mots_res, out))
    if out.exists():
        raise FileExistsError('Choose a new dual-visuals output directory')
    resources = read_gob(mots_res)
    cmp_data = resources[PALETTE_MEMBER]
    if cmp_data[:4] != b'CMP ' or len(cmp_data) < 832:
        raise ValueError('Invalid native default palette')
    palette = cmp_data[64:832]
    map_palettes = {n:b[64:832] for n,b in resources.items()
                    if n.startswith('misc/cmp/') and n.endswith('.cmp')
                    and n != 'misc/cmp/uicolormap.cmp'}
    out.mkdir(parents=True)
    rows = []
    for index, (color, source_color, derivative) in enumerate(COLORS):
        for suffix, role, stem in [(1, 'side', 'dxbs'), (0, 'tip', 'dxbt')]:
            member = f'mat/saber{source_color}{suffix}.mat'
            source = resources[member]
            if derivative:
                raw, index_map = derived_mat(source, derivative, palette)
            else:
                raw, index_map = source, None
            properties = inspect_mat(raw)
            if role == 'side':
                assert (properties['width'], properties['height']) == (32, 256)
            else:
                assert (properties['width'], properties['height']) == (32, 32)
                assert properties['transparent'] == 1
                assert properties['transparent_pixel_count'] == 228
            path = f'mat/{stem}{index}.mat'
            target = out/path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            used = properties['indices']
            unstable = [i for i in used if len({p[i*3:i*3+3] for p in map_palettes.values()}) != 1]
            # Newly chosen colors use only palette-stable indices. Existing
            # native pairs retain their exact bytes, including native index18.
            if derivative:
                assert not unstable, ('Derived palette varies across native maps', unstable)
            rows.append(dict(path=path, color_index=index, color=color, role=role,
                             source_member=member, source_sha256=digest(source), sha256=digest(raw),
                             method=derivative or 'exact-owned-native-copy', index_map=index_map,
                             native_header_preserved=True, zero_mask_preserved=True,
                             palette_rgb={str(i):list(palette[i*3:i*3+3]) for i in used},
                             variable_native_palette_indices=unstable, **properties))

    donor_path = jk31_root/'3do/sabg-g.3do'
    donor_raw = donor_path.read_bytes()
    donor = parsed(donor_raw)
    if len(donor['nodes']) != 1 or donor['nodes'][0]['mesh'] != 0:
        raise ValueError('Unexpected JK3.1 saber donor hierarchy')
    hilt, materials = hilt_from_saber(donor)
    hilt['name'] = 'sbxd_rhilt'
    # Historical donor normals are non-unit; normalize only their magnitude.
    # Positions, faces, texture coordinates and the model origin are unchanged.
    normalized = 0
    for i, normal in enumerate(hilt['normals']):
        length = math.sqrt(sum(c*c for c in normal))
        if length == 0:
            raise ValueError('Zero-length donor hilt normal')
        if abs(length-1) > 1e-8:
            normalized += 1
        hilt['normals'][i] = [c/length for c in normal]
    model = copy.deepcopy(donor)
    model.update(name='dxrhilt', materials=materials, meshes=[hilt], geosets=[[hilt]])
    # Keep the donor origin, insert offset, node transform and original vertices.
    # The right-hand attachment path already establishes its native placement.
    model_path = out/'3do/dxrhilt.3do'
    model_report = fmt.write_3do(model_path, model)
    checked = parsed(model_path.read_bytes())
    assert len(checked['meshes']) == len(checked['nodes']) == 1
    assert checked['nodes'] == donor['nodes']
    assert checked['insert_offset'] == donor['insert_offset']
    for key in ('vertices', 'uvs', 'faces'):
        assert checked['meshes'][0][key] == hilt[key], ('Hilt geometry changed', key)
    assert all(abs(a-b) < 1e-8 for before,after in zip(hilt['normals'], checked['meshes'][0]['normals'])
               for a,b in zip(before,after))
    hilt_report = dict(path='3do/dxrhilt.3do', source_member='3do/sabg-g.3do',
                       source_sha256=digest(donor_raw), sha256=digest(model_path.read_bytes()),
                       method='build_dual_models.hilt_from_saber; retain only four named ordinary hilt materials',
                       materials=materials, vertices=len(hilt['vertices']), faces=len(hilt['faces']),
                       vertex_normals_normalized=normalized,
                       original_node_transform_and_origin_preserved=True,
                       format_validation=model_report)
    report = dict(schema='sbx-retail-dual-visuals-v1',
                  scope='Private locally derived resources; structural checks only, not native rendered/gameplay acceptance.',
                  palette_member=PALETTE_MEMBER, palette_sha256=digest(palette),
                  map_palettes_checked=sorted(map_palettes), color_order=[c[0] for c in COLORS],
                  blade_materials=rows, right_hilt=hilt_report,
                  generated_resource_count=len(rows)+1,
                  distribution='Do not redistribute generated resources. Share the builder and derive from owned local inputs.')
    (out/'dual-visuals.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jk31-root', required=True, type=Path)
    parser.add_argument('--mots-res', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    result = build(args.jk31_root, args.mots_res, args.out)
    print(json.dumps(dict(resources=result['generated_resource_count'], color_order=result['color_order'],
                          right_hilt_sha256=result['right_hilt']['sha256'])))
