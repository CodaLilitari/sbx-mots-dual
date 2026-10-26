"""Strict BM codec preserving menu headers, palette, and unchanged pixel indices."""
from pathlib import Path
import argparse, struct
WIDTH, HEIGHT = 640, 480
PIXELS = WIDTH * HEIGHT
PIXEL_START = 136
SIZE = PIXEL_START + PIXELS + 768

def parse(raw):
    if len(raw) != SIZE: raise ValueError('Expected one 640x480 indexed BM with embedded palette')
    f = struct.unpack('<32I', raw[:128])
    if raw[:4] != b'BM  ' or f[1] != 70: raise ValueError('Invalid native BM signature/version')
    if f[3] != 2 or f[4] != 1 or f[8:10] != (0, 8): raise ValueError('Expected opaque single-frame 8-bit BM')
    if struct.unpack_from('<II', raw, 128) != (WIDTH, HEIGHT): raise ValueError('Menu bitmap must remain640x480')
    return {'header': raw[:PIXEL_START], 'pixels': raw[PIXEL_START:PIXEL_START+PIXELS], 'palette': raw[-768:]}

def validate_replacement(original, replacement):
    a,b = parse(original),parse(replacement)
    if a['header'] != b['header']: raise ValueError('Preserve original BM header and dimensions')
    if a['palette'] != b['palette']: raise ValueError('Preserve original menu palette')
    changed=[i for i,(x,y) in enumerate(zip(a['pixels'],b['pixels'])) if x!=y]
    bbox=None if not changed else [min(i%WIDTH for i in changed),min(i//WIDTH for i in changed),max(i%WIDTH for i in changed)+1,max(i//WIDTH for i in changed)+1]
    return {'changed_pixels':len(changed),'changed_bbox_xyxy':bbox,'header_unchanged':True,'palette_unchanged':True,'width':WIDTH,'height':HEIGHT}

def encode_png(original,image_path):
    # Optional authoring dependency only; the ordinary builder embeds a ready BM.
    from PIL import Image
    source=parse(original)
    with Image.open(image_path) as image:
        if image.size!=(WIDTH,HEIGHT): raise ValueError('Provide final artwork at exactly640x480')
        if 'A' in image.getbands() and image.getchannel('A').getextrema()!=(255,255): raise ValueError('Flatten transparency before encoding')
        rgb=image.convert('RGB');pal=Image.new('P',(1,1));pal.putpalette(source['palette'])
        indexed=rgb.quantize(palette=pal,dither=Image.Dither.NONE)
        target=rgb.tobytes();indices=indexed.tobytes();pixels=bytearray(source['pixels'])
        for i,index in enumerate(source['pixels']):
            if target[i*3:i*3+3]!=source['palette'][index*3:index*3+3]: pixels[i]=indices[i]
    encoded=source['header']+pixels+source['palette'];validate_replacement(original,encoded);return encoded

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reference-bm',required=True);p.add_argument('--png',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();out=Path(a.output)
    if out.exists(): raise FileExistsError(out)
    out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(encode_png(Path(a.reference_bm).read_bytes(),a.png))
