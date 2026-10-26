"""Behavioral packaging tests: precedence, closure, isolation, determinism."""
from pathlib import Path
import json
import tempfile
import unittest
from archive_io import read_gob, write_gob
from build_standalone import build

class StandaloneTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sbx-standalone-test-')
        self.root = Path(self.temp.name)
        self.base = self.archive('base.goo', {'misc/pup/body.pup': b'walk existing.key\n',
            '3do/key/existing.key': b'base walk', '3do/mat/color.mat': b'base material',
            'patchinfo.txt': b'Original SBX attribution'})
        self.overlay = self.archive('overlay.goo', {'3do/key/existing.key': b'retimed walk',
            'misc/pup/dual.pup': b'walk owned.key\n'})
        self.res = self.archive('stock-res.goo', {'3do/key/owned.key': b'owned native key',
            '3do/key/unneeded.key': b'do not package retail wholesale'})
        self.snd = self.archive('stock-snd.goo', {})
    def tearDown(self):
        self.temp.cleanup()
    def archive(self, name, entries):
        path = self.root / name
        write_gob(entries, path)
        return path
    def pack(self, name='out', **kwargs):
        return build(self.base, self.overlay, self.res, self.snd, self.root / name, **kwargs)
    def test_flattens_winners_preserves_attribution_without_copying_game_archives(self):
        result = self.pack()
        packed = read_gob(self.root / 'out/accelerated/SBX-MotS-Dual.goo')
        self.assertEqual(packed, read_gob(self.base) | read_gob(self.overlay))
        self.assertNotIn('3do/key/owned.key', packed)
        self.assertFalse(result['variants']['accelerated']['separate_sbx_runtime_archives_required'])
        self.assertEqual(result['variants']['accelerated']['introduced_missing_resources'], [])
    def test_archive_bytes_deterministic_across_input_order_and_output_location(self):
        self.pack('one')
        write_gob(dict(reversed(list(read_gob(self.base).items()))), self.base)
        self.pack('two')
        self.assertEqual((self.root / 'one/accelerated/SBX-MotS-Dual.goo').read_bytes(),
                         (self.root / 'two/accelerated/SBX-MotS-Dual.goo').read_bytes())
    def test_software_is_complete_independent_archive(self):
        software = self.archive('software.goo', {'3do/mat/color.mat': b'indexed material'})
        self.pack(software=software)
        normal = read_gob(self.root / 'out/accelerated/SBX-MotS-Dual.goo')
        indexed = read_gob(self.root / 'out/software/SBX-MotS-Dual.goo')
        self.assertEqual(indexed, normal | read_gob(software))
        self.assertEqual(indexed['patchinfo.txt'], b'Original SBX attribution')
    def test_missing_new_dependency_fails_with_receipt(self):
        self.overlay = self.archive('bad.goo', {'misc/pup/dual.pup': b'walk absent.key\n'})
        with self.assertRaisesRegex(ValueError, 'Missing resources'):
            self.pack()
        receipt = json.loads((self.root / 'out/accelerated/PACKAGE-MANIFEST.json').read_text())
        self.assertFalse(receipt['passed'])
        self.assertEqual(receipt['introduced_missing_resources'], [['misc/pup/dual.pup', 'absent.key']])
    def test_inherited_missing_dependency_also_fails(self):
        self.base = self.archive('inherited.goo', read_gob(self.base) | {'misc/pup/unused.pup': b'walk absent.key\n'})
        with self.assertRaisesRegex(ValueError, 'Missing resources'):
            self.pack()
        receipt = json.loads((self.root / 'out/accelerated/PACKAGE-MANIFEST.json').read_text())
        self.assertEqual(receipt['inherited_missing_resources'], [['misc/pup/unused.pup', 'absent.key']])
    def test_existing_output_preserved(self):
        out = self.root / 'out'; out.mkdir()
        marker = out / 'keep.txt'; marker.write_text('existing work')
        with self.assertRaises(FileExistsError): self.pack()
        self.assertEqual(marker.read_text(), 'existing work')
    def test_full_builder_rejects_git_ancestor_before_creating_output(self):
        from types import SimpleNamespace
        from build_overlay import build as full_build
        (self.root / '.git').mkdir()
        output = self.root / 'bulk-build'
        with self.assertRaisesRegex(ValueError, 'outside Git'):
            full_build(SimpleNamespace(output=str(output)))
        self.assertFalse(output.exists())
    def test_software_cannot_change_gameplay_scripts(self):
        software = self.archive('software.goo', {'cog/changed.cog': b'not a material'})
        with self.assertRaisesRegex(ValueError, 'only material'): self.pack(software=software)

if __name__ == '__main__': unittest.main()
