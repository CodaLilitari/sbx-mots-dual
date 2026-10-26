"""Apply one maintained Special Edition main-menu bitmap to the overlay."""
from pathlib import Path
import json
from archive_io import digest,read_gob,write_gob
from native_ui_bitmap import validate_replacement
UI_PATH='ui/bm/bkmain.bm'
def apply(candidate,base_archive,source_root,bitmap=None):
    candidate,source_root=Path(candidate),Path(source_root)
    bitmap=Path(bitmap) if bitmap else source_root/'assets/ui/bkmain.bm'
    if not bitmap.is_file(): raise FileNotFoundError('Special Edition requires assets/ui/bkmain.bm')
    base=read_gob(base_archive);archive=candidate/'SBX-MotS-Dual-Overlay.goo';entries=read_gob(archive)
    original=entries.get(UI_PATH,base[UI_PATH]);replacement=bitmap.read_bytes();report=validate_replacement(original,replacement)
    bbox=report['changed_bbox_xyxy']
    if bbox is None or not (bbox[0]>=450 and bbox[1]>=0 and bbox[2]<=616 and bbox[3]<=97):
        raise ValueError('Special Edition pixels must stay inside the approved right title block')
    report.update({'schema':'sbx-special-edition-ui-v1','resource':UI_PATH,'original_sha256':digest(original),'replacement_sha256':digest(replacement),'method':'Prepared native BM; header, palette, pixels outside the right title block and all other game-resource bytes preserved.'})
    before=dict(entries);entries[UI_PATH]=replacement;write_gob(entries,archive)
    dest=candidate/'overlay'/UI_PATH;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(replacement)
    assert all(entries[n]==raw for n,raw in before.items() if n!=UI_PATH)
    mp=candidate/'manifest.json';manifest=json.loads(mp.read_text());rows={row['path']:row for row in manifest['entries']}
    rows[UI_PATH]={'path':UI_PATH,'bytes':len(replacement),'sha256':digest(replacement),'reason':'Special Edition subtitle; original palette, artwork outside the right title block and controls preserved'}
    manifest['entries']=[rows[n] for n in sorted(rows)];manifest['overlay_sha256']=digest(archive.read_bytes());mp.write_text(json.dumps(manifest,indent=2)+'\n')
    report['non_ui_game_resources_unchanged']=True;(candidate/'special-edition-ui.json').write_text(json.dumps(report,indent=2)+'\n');return report
