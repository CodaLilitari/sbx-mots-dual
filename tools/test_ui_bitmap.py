from pathlib import Path
import json,struct,tempfile,unittest
from archive_io import read_gob,write_gob
from native_ui_bitmap import parse,validate_replacement,encode_png,SIZE
from build_special_edition import apply

class MenuBitmapTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='sbx-menu-test-');self.root=Path(self.temp.name)
        h=[0]*32;h[0]=struct.unpack('<I',b'BM  ')[0];h[1]=70;h[3]=2;h[4]=1;h[9]=8
        palette=bytes(v for i in range(256) for v in (i,i,i))
        self.raw=struct.pack('<32I',*h)+struct.pack('<II',640,480)+bytes([12])*(640*480)+palette
    def tearDown(self): self.temp.cleanup()
    def test_rejects_geometry_and_palette_changes(self):
        with self.assertRaises(ValueError):parse(self.raw[:-1])
        b=bytearray(self.raw);struct.pack_into('<I',b,128,641)
        with self.assertRaises(ValueError):validate_replacement(self.raw,bytes(b))
        b=bytearray(self.raw);b[-1]^=1
        with self.assertRaisesRegex(ValueError,'palette'):validate_replacement(self.raw,bytes(b))
    def test_pixel_bounds_and_unchanged_regions(self):
        b=bytearray(self.raw);b[136+80*640+463]=15
        result=validate_replacement(self.raw,bytes(b))
        self.assertEqual(result['changed_pixels'],1);self.assertEqual(result['changed_bbox_xyxy'],[463,80,464,81])
    def test_encoding_preserves_duplicate_palette_indices(self):
        from PIL import Image
        b=bytearray(self.raw);b[-768+13*3:-768+13*3+3]=bytes([12,12,12]);b[136]=13
        bm=bytes(b);p=parse(bm);im=Image.frombytes('P',(640,480),p['pixels']);im.putpalette(p['palette']);png=self.root/'identical.png';im.convert('RGB').save(png)
        self.assertEqual(encode_png(bm,png),bm)
    def test_hook_changes_only_bitmap_and_preserves_gameplay(self):
        source=self.root/'source';(source/'assets/ui').mkdir(parents=True)
        b=bytearray(self.raw);b[136+80*640+463]=15;(source/'assets/ui/bkmain.bm').write_bytes(b)
        base=self.root/'base.goo';write_gob({'ui/bm/bkmain.bm':self.raw},base)
        candidate=self.root/'candidate';candidate.mkdir();write_gob({'cog/check.cog':b'original script'},candidate/'SBX-MotS-Dual-Overlay.goo')
        (candidate/'manifest.json').write_text(json.dumps({'entries':[{'path':'cog/check.cog','reason':'test'}]}))
        apply(candidate,base,source)
        entries=read_gob(candidate/'SBX-MotS-Dual-Overlay.goo');self.assertEqual(entries['cog/check.cog'],b'original script');self.assertEqual(set(entries),{'cog/check.cog','ui/bm/bkmain.bm'})
    def test_hook_rejects_art_changes_outside_title(self):
        source=self.root/'source';(source/'assets/ui').mkdir(parents=True)
        b=bytearray(self.raw);b[136+200*640+100]=15;(source/'assets/ui/bkmain.bm').write_bytes(b)
        base=self.root/'base.goo';write_gob({'ui/bm/bkmain.bm':self.raw},base)
        candidate=self.root/'candidate';candidate.mkdir();write_gob({},candidate/'SBX-MotS-Dual-Overlay.goo')
        with self.assertRaisesRegex(ValueError,'title block'):apply(candidate,base,source)

if __name__=='__main__':unittest.main()
