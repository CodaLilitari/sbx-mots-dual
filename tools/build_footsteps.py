"""Give SBX's walks their footsteps back, as Dual Sabers 17 does at load.

SBX 3.1's walk, walk-back and strafe keys replaced the original game's
footstep markers (1 left foot, 2 right) with saber damage markers, so every
stance walks silently. SBX-MotS 3.0 ships the same 23 keys byte for byte.
Dual Sabers 17 lists the frames where each key's feet land in
misc/keymarkers.dat, which OpenJKDF2 applies as a key loads. Original MotS
cannot read that file, so this writes the marked copies ahead of time.

Same rules as OpenJKDF2's sithKeyRetarget_AddMarkers (8ccc356c): a key of
another length, or one that already has a marker of a listed type, is left
as it is; the added markers go in frame order among the key's own, eight at
most. Nothing else in a key changes.
"""
from pathlib import Path
import argparse, json, re
from archive_io import digest


def read_table(raw):
    rows={}
    in_keys=False
    for line in raw.decode('ascii').splitlines():
        words=line.split('#')[0].split()
        if not words:continue
        if words[0]=='keys':in_keys=True;continue
        if words[0]=='end':in_keys=False;continue
        if in_keys:
            if len(words)<4 or len(words)%2:raise ValueError('Malformed keymarkers row: '+line)
            frames=int(words[1]);pairs=[(float(words[i]),int(words[i+1])) for i in range(2,len(words),2)]
            if any(not 0<=f<frames for f,t in pairs):raise ValueError('Marker outside key: '+line)
            rows[words[0].lower()]=(frames,pairs)
    if len(rows)!=23:raise ValueError('Expected the 23 SBX walk keys')
    return rows


def frame_count(text):
    match=re.search(r'(?im)^\s*FRAMES\s+(\d+)\s*$',text)
    if match is None:raise ValueError('KEY without FRAMES')
    return int(match[1])


def own_markers(text):
    match=re.search(r'(?ims)^SECTION:\s*MARKERS\s*$(.*?)(?=^#*\s*SECTION:|^SECTION:)',text)
    if match is None:return None,[]
    body=[line.split('#')[0].split() for line in match[1].splitlines()]
    body=[w for w in body if w]
    if not body or body[0][0].upper()!='MARKERS':raise ValueError('Malformed MARKERS section')
    count=int(body[0][1]);pairs=[(float(w[0]),int(w[1])) for w in body[1:1+count]]
    if len(pairs)!=count:raise ValueError('MARKERS count mismatch')
    return match,pairs


def add(raw,frames,added):
    text=raw.decode('latin1')
    newline='\r\n' if '\r\n' in text else '\n'
    if frame_count(text)!=frames:return None,'length differs'
    match,pairs=own_markers(text)
    if any(t==a for f,t in pairs for _,a in added):return None,'already has footstep markers'
    merged=[];i=j=0
    while (i<len(pairs) or j<len(added)) and len(merged)<8:
        if j>=len(added) or (i<len(pairs) and pairs[i][0]<=added[j][0]):merged.append(pairs[i]);i+=1
        else:merged.append(added[j]);j+=1
    section=newline.join(['SECTION: MARKERS','',f'MARKERS {len(merged)}','']+[f'{f:.6f} {t}' for f,t in merged]+['','',''])
    if match is not None:
        start=text.upper().rindex('SECTION:',0,match.end(0))
        text=text[:start]+section+text[match.end(0):]
    else:
        nodes=re.search(r'(?im)^SECTION:\s*KEYFRAME NODES',text)
        if nodes is None:raise ValueError('KEY without KEYFRAME NODES')
        hashes=text.rfind('###############',0,nodes.start())
        cut=hashes if hashes!=-1 and text[hashes:nodes.start()].strip('#\r\n ')=='' else nodes.start()
        text=text[:cut]+'###############'+newline+section+text[cut:]
    out=text.encode('latin1')
    check,result=own_markers(out.decode('latin1'))
    if result!=merged or frame_count(out.decode('latin1'))!=frames:raise AssertionError('Marker rewrite failed')
    return out,'footstep markers added'


def build(table_path,key_roots,out):
    table=read_table(Path(table_path).read_bytes())
    roots=[Path(p) for p in key_roots];out=Path(out)
    rows=[]
    for name,(frames,added) in sorted(table.items()):
        source=next((root/'3do/key'/name for root in roots if (root/'3do/key'/name).is_file()),None)
        if source is None:raise FileNotFoundError('3do/key/'+name)
        raw=source.read_bytes();new,why=add(raw,frames,added)
        row={'path':'3do/key/'+name,'source_sha256':digest(raw),'reason':why}
        if new is not None:
            dest=out/'3do/key'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(new)
            row['sha256']=digest(new);row['markers_added']=added
        rows.append(row)
    report={'schema':'sbx-walk-footsteps-v1','table_sha256':digest(Path(table_path).read_bytes()),'keys':rows,
            'scope':'Marker sections only; every pose entry is unchanged. Not runtime verified.'}
    out.mkdir(parents=True,exist_ok=True);(out/'footsteps.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--table',required=True);ap.add_argument('--keys',action='append',required=True,help='Root(s) holding 3do/key, first wins');ap.add_argument('--out',required=True)
    a=ap.parse_args();r=build(a.table,a.keys,a.out);print(json.dumps({'marked':sum('sha256' in k for k in r['keys']),'keys':len(r['keys'])},indent=2))
