"""Package complete SBX MotS GOO editions; original SBX archives are build inputs only."""
from pathlib import Path
import argparse
import json
from archive_io import digest, read_gob, write_gob
from validate_candidate import reachable_missing


def save_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def package_variant(base, overlay, stock, folder, sources, software=None):
    expected = base | overlay
    if software is not None:
        if any(not name.endswith('.mat') for name in software):
            raise ValueError('The software layer must contain only material overrides')
        expected |= software
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=False)
    archive = folder / 'SBX-MotS-Dual.goo'
    write_gob(expected, archive)
    packed = read_gob(archive)
    if packed != expected:
        raise ValueError('Standalone archive differs from the effective input layers')
    # All packed entries are roots, including unchanged base resources.
    missing, count = reachable_missing(stock | packed, packed)
    prior, _ = reachable_missing(stock | base, base)
    members = []
    for name, raw in sorted(packed.items()):
        origin = ('software' if software is not None and name in software else
                  'overlay' if name in overlay else 'sbx_mots_base')
        member = {'path': name, 'bytes': len(raw), 'sha256': digest(raw), 'origin': origin}
        if name in base and raw != base[name]:
            member['replaced_base_sha256'] = digest(base[name])
        members.append(member)
    result = {
        'schema': 'sbx-standalone-package-v1',
        'status': 'PACKAGED_AND_STATIC_CHECKED' if not missing else 'FAILED_RESOURCE_CLOSURE',
        'archive': archive.name, 'archive_sha256': digest(archive.read_bytes()),
        'archive_bytes': archive.stat().st_size, 'member_count': len(packed),
        'runtime_prerequisites': ['Owned retail Mysteries of the Sith installation'],
        'separate_sbx_runtime_archives_required': False, 'engine_executable_modified': False,
        'renderer': 'software' if software is not None else 'accelerated',
        'precedence': ['sbx_mots_base', 'overlay'] + (['software'] if software is not None else []),
        'sources': sources, 'exact_effective_resource_bytes_verified': packed == expected,
        'reachable_resources_checked': count, 'inherited_missing_resources': sorted(missing & prior),
        'introduced_missing_resources': sorted(missing - prior), 'passed': not missing,
        'method': 'All packed roots resolve against this GOO plus owned MotS archives only. No separate SBX archive participates. Both inherited and introduced missing references fail acceptance.',
        'runtime_validation': 'Not performed by this packer.', 'members': members,
    }
    save_json(folder / 'PACKAGE-MANIFEST.json', result)
    (folder / 'SHA256SUMS.txt').write_text(result['archive_sha256'] + '  ' + archive.name + '\n', encoding='ascii')
    if missing:
        raise ValueError('Missing resources; inspect PACKAGE-MANIFEST.json')
    return result


def build(base, overlay, mots_res, mots_snd, output, software=None):
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError('Choose a new standalone output directory')
    if any((p / '.git').exists() for p in [output, *output.parents]):
        raise ValueError('Put generated standalone packages outside Git checkouts')
    paths = {'sbx_mots_base': Path(base), 'overlay': Path(overlay),
             'mots_resources': Path(mots_res), 'mots_sounds': Path(mots_snd)}
    if software is not None:
        paths['software'] = Path(software)
    for path in paths.values():
        if not path.is_file():
            raise FileNotFoundError(path)
    contents = {name: read_gob(path) for name, path in paths.items()}
    sources = {name: {'sha256': digest(path.read_bytes()), 'entries': len(contents[name])}
               for name, path in paths.items()}
    output.mkdir(parents=True)
    stock = contents['mots_resources'] | contents['mots_sounds']
    variants = {'accelerated': package_variant(contents['sbx_mots_base'], contents['overlay'], stock,
                                               output / 'accelerated', sources)}
    if software is not None:
        variants['software'] = package_variant(contents['sbx_mots_base'], contents['overlay'], stock,
                                               output / 'software', sources, contents['software'])
    report = {
        'schema': 'sbx-standalone-build-v1', 'status': 'PACKAGED_AND_STATIC_CHECKED',
        'variants': {name: {k: v for k, v in row.items() if k != 'members'} for name, row in variants.items()},
        'installation': 'Choose one renderer directory. Copy its SBX-MotS-Dual.goo alone into an empty expansions/SBX-Dual folder. Start JKM.EXE -path expansions/SBX-Dual. Do not install both renderer archives or any separate SBX 3.0/3.1 archive.',
        'build_inputs': 'Original mod archives remain necessary only for reproducible rebuilding, not for playing the finished GOO.',
        'redistribution': 'Original authors retain rights and credits. This local build may contain resources derived from owned game inputs; publication is a separate reviewed action.',
    }
    save_json(output / 'STANDALONE-RESULT.json', report)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for tag in ['base', 'overlay', 'mots-res', 'mots-snd', 'output']:
        parser.add_argument('--' + tag, required=True)
    parser.add_argument('--software', help='Optional generated material-only GOO')
    args = parser.parse_args()
    print(json.dumps(build(args.base, args.overlay, args.mots_res, args.mots_snd, args.output, args.software), indent=2))
