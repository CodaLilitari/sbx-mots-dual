"""Bake retail native dual-saber KEYs with the pinned upstream retarget algorithm.

Only explicit user-owned JK/SBX resources are read. Generated keys contain owned
JK animation and must remain local; the distributable is this tool plus recipe,
source and its independently built headless adapter. No game or UI is launched.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import subprocess
import sys
from archive_io import read_gob

HERE = Path(__file__).resolve().parent
UPSTREAM_COMMIT = '8ccc356c5733a41688982e8e5bcd95bb5826c654'
UPSTREAM_SHA256 = 'c2d51fd268673ee1881b8ec9324fdf8c08188ef1a313b767a291a5745e43532e'
UPPER = {1,5,6,7,11,12,13,15,16,17}
LOWER = set(range(18)) - UPPER


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_recipe(raw):
    """Dual Sabers 17's recipe: 23 keys converted from Boc (section:
    retarget), then 14 made from the reverse grip's own idle (section: own).
    Each rule is returned with its section."""
    rules=[]
    in_keys=False;section=None
    for line in raw.decode('ascii').splitlines():
        words=line.split('#')[0].split()
        if not words:continue
        if words[0]=='section:':section=words[1] if len(words)>1 else None;continue
        if words[0]=='keys':in_keys=True;continue
        if words[0]=='end':in_keys=False
        if in_keys:rules.append((section,words))
    counts={name:sum(1 for sec,w in rules if sec==name) for name in ('retarget','own')}
    if counts!={'retarget':23,'own':14} or len(rules)!=37:raise ValueError('Expected supplied 23+14-key recipe')
    return rules

# The reverse grip's idle loop also holds both grip anchors (nodes 18 and
# 19) turned end over end about the fist: OpenJKDF2 does this in the engine
# (jk flag 0x200), which retail does not have.
ANCHOR_NODES=((18,'sbxd_left_grip'),(19,'sbxd_right_grip'))


def add_reverse_anchors(raw,anchors):
    text=raw.decode('ascii')
    nodes=re.search(r'(?m)^NODES (\d+)$',text)
    if nodes is None or 'NODE 18\n' in text or 'NODE 19\n' in text:raise ValueError('Unexpected upper loop key layout')
    text=text[:nodes.start()]+'NODES %d'%(int(nodes[1])+2)+text[nodes.end():]
    for (node,name),y in zip(ANCHOR_NODES,anchors):
        text+=f'NODE {node}\nMESH NAME {name}\nENTRIES 1\n0: 0 0x0000 0 {y:.9g} 0 0 180 0\n0 0 0 0 0 0\n'
    return text.encode('ascii')


def read_key(raw):
    lines=[line.split('#')[0].strip() for line in raw.decode('ascii').splitlines()]
    lines=[line for line in lines if line]
    result={'nodes':{},'markers':[]}
    current=None;i=0
    while i<len(lines):
        words=lines[i].split();lead=words[0].upper()
        if lead in ('FLAGS','TYPE','FRAMES','FPS','JOINTS','NODES'):
            result['node_count' if lead=='NODES' else lead.lower()]=float(words[1]) if lead=='FPS' else int(words[1],0)
        elif lead=='MARKERS':
            for _ in range(int(words[1])):
                i+=1;frame,marker=lines[i].split();result['markers'].append((float(frame),int(marker)))
        elif lead=='NODE':
            current=int(words[1])
            if current in result['nodes']:raise ValueError('Duplicate native KEY node')
            result['nodes'][current]=[]
        elif words[0].endswith(':') and words[0][:-1].isdigit():
            if current is None or len(words)!=9:raise ValueError('Malformed native KEY pose')
            entry_index=int(words[0][:-1]);entries=result['nodes'][current]
            if entry_index!=len(entries):raise ValueError('KEY entry index mismatch')
            i+=1;velocity=list(map(float,lines[i].split()))
            if len(velocity)!=6:raise ValueError('Malformed native KEY velocity')
            entries.append((float(words[1]),int(words[2],16),list(map(float,words[3:])),velocity))
        i+=1
    if len(result['nodes'])!=result['node_count']:raise ValueError('KEY node count mismatch')
    for node,entries in result['nodes'].items():
        if not 0<=node<result['joints'] or not entries:raise ValueError('KEY node outside allocation')
        if any(a[0]>b[0] for a,b in zip(entries,entries[1:])):raise ValueError('KEY time order')
        for frame,flags,values,velocity in entries:
            if not math.isfinite(frame) or not all(map(math.isfinite,values+velocity)):raise ValueError('Nonfinite KEY entry')
    return result


def sample_entry(entries,frame):
    entry=entries[0]
    for candidate in entries:
        if candidate[0]>frame:break
        entry=candidate
    t,flags,values,velocity=entry
    return [v+(frame-t)*velocity[a] if flags&(1 if a<3 else 2) else v for a,v in enumerate(values)]


def build(jk_res,sbx_root,recipe_path,output,adapter=None,dual_root=None):
    output=Path(output).resolve()
    if output.exists():raise FileExistsError('Use a new output directory; originals are preserved')
    source=HERE/'vendor/sithKeyRetarget.c'
    if sha(source.read_bytes())!=UPSTREAM_SHA256:raise ValueError('Pinned upstream retarget source hash differs')
    adapter=Path(adapter or HERE/'dual-key-baker.exe').resolve()
    receipt_path=HERE/'dual-key-baker-build.json'
    receipt=json.loads(receipt_path.read_text())
    if sha(adapter.read_bytes())!=receipt['adapter_sha256']:raise ValueError('Adapter executable hash differs from build receipt')
    owned=read_gob(jk_res)
    sbx_root=Path(sbx_root)
    base=read_gob(sbx_root) if sbx_root.is_file() else None
    recipe_raw=Path(recipe_path).read_bytes();sections=read_recipe(recipe_raw)
    rules=[words for section,words in sections]
    own_rules={words[0] for section,words in sections if section=='own'}
    dual_root=Path(dual_root) if dual_root else Path(recipe_path).parent.parent
    def get_dual(name):
        path=dual_root/name
        return path.read_bytes() if path.is_file() else None
    stage=output/'local-input-staging';key_dir=output/'3do/key'
    inputs={}
    def put(kind,name,raw):
        name=name.replace('\\','/').lower()
        if not re.fullmatch(r'[a-z0-9_./-]+',name) or '..' in name:raise ValueError('Unsafe staging member')
        path=stage/kind/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        inputs[kind+'/'+name]={'sha256':sha(raw),'bytes':len(raw)}
    def get_sbx(name):
        if base is not None:return base.get(name)
        path=sbx_root/name
        return path.read_bytes() if path.is_file() else None
    put('overlay','misc/keyretarget.dat',recipe_raw)
    # Dual Sabers 17's footstep markers for SBX 3.1's walks: the converter
    # gives them to the legs under the dual and reverse-grip walks.
    markers_raw=get_dual('misc/keymarkers.dat')
    if markers_raw is None:raise FileNotFoundError('misc/keymarkers.dat')
    put('overlay','misc/keymarkers.dat',markers_raw)
    for name in ('3do/bo.3do','3do/ky.3do'):put('retail',name,owned[name])
    for rule in rules:
        name='3do/key/'+rule[1].lower()
        if rule[0] in own_rules:
            # The reverse grip's idle is the add-on's own key
            candidate=get_dual(name)
            if candidate is None:raise FileNotFoundError(name)
            put('overlay',name,candidate)
            continue
        candidate=get_sbx(name)
        put('overlay' if candidate is not None else 'retail',name,candidate if candidate is not None else owned[name])
        if 'legs' in rule:
            name='3do/key/'+rule[rule.index('legs')+1].lower()
            candidate=get_sbx(name)
            put('overlay' if candidate is not None else 'retail',name,candidate if candidate is not None else owned[name])
    # Where the reverse grip holds each hilt: worked out on SBX's Kyle, the
    # skeleton these keys are made for. Every prepared skin's own value is
    # in generated/models/dual-models.json.
    from build_dual_models import parsed,hilt_from_saber,reverse_grip_anchors
    hilt,_=hilt_from_saber(parsed(get_sbx('3do/sabg-g.3do')))
    anchors=reverse_grip_anchors(get_sbx('3do/ky.3do'),hilt)
    key_dir.mkdir(parents=True)
    process=subprocess.run([str(adapter),str(stage),str(key_dir)],capture_output=True,text=True,check=False)
    (output/'adapter-log.txt').write_text(process.stdout+process.stderr)
    if process.returncode:raise RuntimeError('Headless retarget adapter failed; inspect adapter-log.txt')
    expected={rule[0] for rule in rules}|{'rt_boupper.key','rt_rgupper.key'}
    actual={path.name for path in key_dir.glob('*.key')}
    if actual!=expected:raise AssertionError('Generated KEY set differs')
    outputs={};checks=[]
    for name in sorted(expected):
        raw=(key_dir/name).read_bytes();key=read_key(raw)
        rule=next((r for r in rules if r[0]==name),None)
        if name=='rt_boupper.key':
            assert set(key['nodes'])==UPPER and key['type']==15
            assert key['frames']==83 and key['fps']==15 and key['markers']==[(0.,4)]
        elif name=='rt_rgupper.key':
            idle=read_key(get_dual('3do/key/rg_antidle.key'))
            assert set(key['nodes'])==UPPER and key['type']==15
            assert key['frames']==idle['frames'] and key['fps']==idle['fps'] and key['markers']==[(0.,4)]
        elif 'legs' in rule:
            assert set(key['nodes'])==LOWER
            legname='3do/key/'+rule[rule.index('legs')+1].lower()
            legraw=get_sbx(legname)
            leg=read_key(legraw if legraw is not None else owned[legname])
            assert key['frames']==leg['frames'] and key['fps']==leg['fps']
            # Source adapter samples integer leg frames, then emits short-arc
            # velocities. Verify integer pose identity (angles modulo360).
            for node in LOWER:
                if node not in leg['nodes']:continue
                for frame in range(key['frames']):
                    a=sample_entry(key['nodes'][node],frame);b=sample_entry(leg['nodes'][node],frame)
                    assert max(abs(x-y) for x,y in zip(a[:3],b[:3]))<2e-6,(name,node,frame,'translation')
                    assert max(abs((x-y+180)%360-180) for x,y in zip(a[3:],b[3:]))<2e-3,(name,node,frame,'rotation')
        assert key['joints']==20 and key['markers'][0]==(0.,4)
        assert not ({18,19}&set(key['nodes']))
        assert not any(m in (5,14) for f,m in key['markers'])
        if rule and 'upper' in rule:assert not any(m in (11,12) for f,m in key['markers'])
        if name=='rt_rgupper.key':
            raw=add_reverse_anchors(raw,anchors);(key_dir/name).write_bytes(raw)
            key=read_key(raw)
            assert set(key['nodes'])==UPPER|{18,19}
            for node,_ in ANCHOR_NODES:
                (frame,flags,values,velocity),=key['nodes'][node]
                assert frame==0 and flags==0 and velocity==[0.]*6
                assert values[0]==values[2]==values[3]==values[5]==0 and values[4]==180 and abs(values[1]-anchors[node-18])<1e-8
        outputs['3do/key/'+name]={'sha256':sha(raw),'bytes':len(raw),'nodes':sorted(key['nodes']),'frames':key['frames'],'fps':key['fps'],'markers':key['markers']}
    report={'schema':'sbx-upstream-native-key-adapter-v1','status':'GENERATED_AND_STATIC_CHECKED_NOT_RUNTIME_VERIFIED',
            'upstream_commit':UPSTREAM_COMMIT,'upstream_source_sha256':UPSTREAM_SHA256,
            'source_transform':'Only include directives removed for concatenation; retarget function bodies unchanged.',
            'adapter_sha256':sha(adapter.read_bytes()),'wrapper_sha256':sha(Path(__file__).read_bytes()),
            'jk_archive_sha256':sha(Path(jk_res).read_bytes()),'recipe_sha256':sha(recipe_raw),
            'input_staging_private':True,'inputs':inputs,'outputs':outputs,
            'reverse_grip_anchors':{'left_node18':anchors[0],'right_node19':anchors[1],'yaw':180,'model':'3do/ky.3do (SBX-JK 3.1)'},
            'checks':['39 ordinary KEY files parsed with finite native entries and exact expected set.',
                      'Upper loops contain only nodes of type 0xF; root0 and hip2 excluded; torso dummy1 retained. The reverse-grip loop adds only grip anchors 18 and 19, constant, yaw 180.',
                      '25 locomotion files contain only root/hip/leg nodes; SBX timing and integer poses checked.',
                      'Damage-on marker0 preserved; damage-off/reset omitted; upper jump markers omitted; walk footstep markers from misc/keymarkers.dat.'],
            'retail_adaptation':'Locomotion drops extension upper clock tracks. rt_boupper.key and rt_rgupper.key preserve those exact generated loops for the independent PlayKey controller; rt_rgupper.key also turns the grip anchors for the reverse grip. Non-locomotion generated keys serialize upstream objects.',
            'limits':['No browser-only quaternion turn blending in retail; transition visual parity unproved.',
                      'Retail independent-track priority, movement, attacks, blocking, death, respawn and multiplayer require execution tests.',
                      'Original source upper semantics assign key type0xF but retain lower entries; low-priority blending follows ordinary retail engine.',
                      'Owned JK-derived outputs and input-staging must stay local; distribute the builder only.']}
    (output/'animation-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jk-res',type=Path,required=True)
    parser.add_argument('--sbx-root',type=Path,required=True,help='Extracted SBX root or GOB/GOO archive')
    parser.add_argument('--recipe',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--adapter',type=Path)
    parser.add_argument('--dual-root',type=Path,help='Extracted Dual Sabers root (default: two levels above the recipe)')
    args=parser.parse_args()
    report=build(args.jk_res,args.sbx_root,args.recipe,args.output,args.adapter,args.dual_root)
    print(json.dumps({'output':str(args.output),'keys':len(report['outputs']),'status':report['status']}))

if __name__=='__main__':main()
