"""Assemble review candidates; never modifies a game installation."""
from pathlib import Path
import argparse,json,re
from archive_io import digest,extract,read_gob,write_gob

def preload(text,section,names):
    match=re.search(r'(?ims)(^Section:\s*'+section+r'\b.*?)(^end\s*$)',text)
    if not match:raise ValueError('Missing static section '+section)
    part=match.group(1)
    rows=re.findall(r'(?m)^\s*(\d+):\s+(\S+)',part)
    known={name.lower() for index,name in rows};index=max([int(i) for i,n in rows],default=-1)+1
    for name in sorted(set(names)):
        if name.lower() in known:continue
        part+=f'{index}: {name}\n';index+=1;known.add(name.lower())
    capacity=re.search(r'(?im)^world\s+\S+\s+(\d+)',part)
    if capacity and index>int(capacity[1]):raise ValueError('Static capacity exceeded: '+section)
    return text[:match.start()]+part+match.group(2)+text[match.end():]

def assemble(root,out,models,controller,reconciled=None,jk_res=None,mots_res=None):
    root=Path(root);out=Path(out);models=Path(models);controller=Path(controller)
    entries={};origins={}
    def add(name,data,reason):entries[name]=data;origins[name]=reason
    def tree(folder,reason):
        for p in Path(folder).rglob('*'):
            if p.is_file() and p.suffix.lower() in {'.cog','.3do','.mat','.snd','.wav','.key','.pup','.dat','.jkl','.uni','.bm','.sft','.ai','.spr','.par'}:
                add(p.relative_to(folder).as_posix().lower(),p.read_bytes(),reason)
    if reconciled:tree(reconciled,'JK31/MotS reconciliation')
    tree(root/'generated/dual-scripts','MotS dual integration')
    for p in (root/'generated-animation-exact-local-03/3do/key').glob('*.key'):add('3do/key/'+p.name,p.read_bytes(),'Exact upstream converter, locally derived owned JK animation')
    tree(models,'Locally generated base-skin hilt variant')
    tree(controller,'Native presentation controller and model lookups')
    visuals=root/'generated/dual-visuals'
    if not visuals.is_dir():raise FileNotFoundError('Native dual visual assets were not generated')
    tree(visuals,'Locally derived native dual blade materials and right hilt')
    if reconciled:
        from reconcile_sbx import transform_actor,transform_items,transform_static
        for name in ['cog/kyle_m.cog','cog/mara_m.cog','cog/luke_m.cog']:
            if name in entries:
                text=entries[name].decode('latin1').replace('\r\n','\n')
                add(name,transform_actor(text).replace('\n','\r\n').encode('latin1'),'MotS class logic, native dual blocking and compatible JK31 actor features')
    dual=root/'sources/dual';jk=root/'sources/jk31';base=root/'sources/mots30'
    # Native SBX con0 lists two nonexistent, unused material slots. Preserve
    # its indices and every geometric byte, substituting its existing white
    # material for only those unused entries so static preloading is complete.
    from build_dual_models import parsed
    con=entries.get('3do/con0.3do',(base/'3do/con0.3do').read_bytes())
    con_model=parsed(con)
    for index in (1,3):
        assert not any(face['material']==index for geo in con_model.get('geosets',[con_model['meshes']]) for mesh in geo for face in mesh['faces'])
    assert con.count(b'1: red.mat')==con.count(b'3: green1.mat')==1
    con=con.replace(b'1: red.mat',b'1: white.mat').replace(b'3: green1.mat',b'3: white.mat')
    assert con.count(b'0: 0x0 0x1 0 -1 1 -1 0 ')==1
    con=con.replace(b'0: 0x0 0x1 0 -1 1 -1 0 ',b'0: 0x0 0x1 0 -1 -1 -1 0 ')
    add('3do/con0.3do',con,'Repair inherited unused material slots red/green1 to existing white and nonexistent root child1 to-1; no geometry or used material changes')
    # Dual Sabers 17 also ships 0.01 s stand-ins (rt_*.key) for the keys it
    # makes at load, for games that cannot make them, and the reverse grip's
    # idle (rg_antidle.key), which is only the source of rt_rg*.key. Retail
    # gets the prepared keys above instead: copy only the add-on's attacks.
    for p in sorted((dual/'3do/key').glob('*.key')):
        if p.name.startswith('rt_') or p.name=='rg_antidle.key':continue
        add('3do/key/'+p.name,p.read_bytes(),'Supplied Dual Sabers attack, preserved')
    footsteps=root/'generated/footsteps'
    if footsteps.is_dir():tree(footsteps,"SBX walk with Dual Sabers 17's footstep markers (misc/keymarkers.dat)")
    items=entries.get('misc/items.dat',(base/'misc/items.dat').read_bytes()).decode('latin1')
    if reconciled:items=transform_items(items)
    itemrows=(controller/'controller-items.txt').read_text()
    at=items.lower().rfind('end');items=items[:at]+'\n# Native dual presentation helpers; no added hotkeys.\n'+itemrows+'\n'+items[at:]
    add('misc/items.dat',items.encode('latin1'),'MotS bins retained, four non-hotkey helper COGs')
    static=entries.get('jkl/static.jkl',(base/'jkl/static.jkl').read_bytes()).decode('latin1')
    if reconciled:static=transform_static(static)
    registry=json.loads((models/'dual-models.json').read_text())
    model_names={row[key] for row in registry['models'] for key in ['source','variant']}
    model_names.update(Path(n).name for n in entries if n.endswith('.3do'))
    static=preload(static,'MODELS',model_names)
    static=preload(static,'KEYFRAMES',[Path(n).name for n in entries if n.endswith('.key')])
    static=preload(static,'ANIMCLASS',['ky_bo.pup','ky_rg.pup','ky_rgd.pup'])
    # All registered skins now load together for native model lookup. Their
    # 1600+ distinct materials exceed SBX3.0's 1000 static-material slots.
    static=re.sub(r'(?im)^(World materials)\s+1000\s*$',r'\1 4096',static)
    add('jkl/static.jkl',static.encode('latin1'),'Preserve MotS tables; preload source/dual models and keys outside per-level capacities; static material capacity4096')
    # Dependencies of the namespaced/new models: existing MotS assets take
    # precedence, adding a JK31 material only if neither base nor retail has it.
    stock=read_gob(mots_res)
    jk_stock=read_gob(jk_res)
    available=set(stock)|{p.relative_to(base).as_posix().lower() for p in base.rglob('*') if p.is_file()}|set(entries)
    # Preloading base skins and weapons also makes their inherited material
    # omissions relevant. Resolve the entire static model table, including
    # unchanged base members such as con0.3do, not merely overlay models.
    model_section=re.search(r'(?ims)^Section:\s*MODELS\b(.*?)^end\s*$',static)
    all_models=set(re.findall(r'(?im)^\s*\d+:\s+(\S+\.3do)',model_section[1]))
    for filename in sorted(all_models):
        name='3do/'+filename.lower()
        data=entries.get(name)
        if data is None and (base/name).is_file():data=(base/name).read_bytes()
        if data is None:data=stock.get(name)
        if data is None:raise FileNotFoundError('Static model missing: '+name)
        text=data.decode('latin1');match=re.search(r'(?ims)^MATERIALS\s+\d+\s*\n(.*?)(?=^SECTION:)',text)
        if match is None:raise ValueError('Missing model material table: '+name)
        for mat in re.findall(r'(?im)^\s*\d+:\s+(\S+\.mat)',match.group(1)):
            mat=mat.lower()
            if any(p in available for p in ['3do/mat/'+mat,'mat/'+mat]):continue
            found=next((jk/q for q in ['3do/mat/'+mat,'mat/'+mat] if (jk/q).is_file()),None)
            dest='3do/mat/'+mat
            if found is not None:
                add(dest,found.read_bytes(),'Missing model material dependency from JK31')
            else:
                owned=next((jk_stock[q] for q in ['3do/mat/'+mat,'mat/'+mat] if q in jk_stock),None)
                if owned is None:raise FileNotFoundError(f'{name} needs {mat}')
                add(dest,owned,'Locally copied owned JK retail material; excluded from portable distribution')
            available.add(dest)
    # Complete two proven truncated original RGB565 mip tails as well as the
    # optional indexed conversion. Preserve every existing byte and all full
    # resolution artwork, including for accelerated rendering.
    from build_software_textures import KNOWN_MISSING_MIPS,parse_mat
    mip_repairs=[]
    for name,source_hash in sorted(KNOWN_MISSING_MIPS.items()):
        raw=entries.get(name,(base/name).read_bytes())
        if digest(raw)!=source_hash:raise ValueError('Unexpected original mip repair source: '+name)
        parsed_mat=parse_mat(raw,name,True)
        fixed=raw+b''.join(level['pixels'] for texture in parsed_mat['textures'] for level in texture['levels'] if level['reconstructed'])
        parse_mat(fixed,name,False)
        assert fixed.startswith(raw) and len(fixed)>len(raw)
        add(name,fixed,'Repair pinned truncated RGB565 mip tail by box reduction; retain all original bytes and full-resolution artwork')
        mip_repairs.append({'path':name,'source_sha256':source_hash,'sha256':digest(fixed),'repairs':parsed_mat['repairs'],'original_bytes_preserved':True})
    # A layered package must omit all byte-identical base members.
    entries={n:b for n,b in entries.items() if not (base/n).is_file() or (base/n).read_bytes()!=b}
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True)
    extract(entries,out/'overlay')
    write_gob(entries,out/'SBX-MotS-Dual-Overlay.goo')
    report={'status':'candidate_not_runtime_accepted','base_archive_sha256':digest((root/'sources/mots30-zip/sbx-mots v3.goo').read_bytes()),'overlay_sha256':digest((out/'SBX-MotS-Dual-Overlay.goo').read_bytes()),'entries':[{'path':n,'bytes':len(b),'sha256':digest(b),'reason':origins[n]} for n,b in sorted(entries.items())]}
    (out/'native-mip-repairs.json').write_text(json.dumps(mip_repairs,indent=2)+'\n')
    (out/'manifest.json').write_text(json.dumps(report,indent=2));return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--out',required=True);p.add_argument('--models',required=True);p.add_argument('--controller',required=True);p.add_argument('--reconciled');p.add_argument('--jk-res',required=True);p.add_argument('--mots-res',required=True);a=p.parse_args();r=assemble(a.root,a.out,a.models,a.controller,a.reconciled,a.jk_res,a.mots_res);print(json.dumps({'entries':len(r['entries']),'sha256':r['overlay_sha256']},indent=2))
