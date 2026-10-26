"""Reproduce the minimal MotS overlay from explicitly supplied local archives."""
from pathlib import Path
import argparse, json, shutil, zipfile
from archive_io import digest, extract, read_gob

EXPECTED={
 # SBX Dual Sabers 17 (25 October 2026): reverse grip, retimed attacks,
 # second heavy-cut fix, walk footsteps. v1.0.0 used the 22 October release
 # (eb34c78521be8fc2e7c6472e63ab7590b3f9b642e21fc5c47ec0b552e5ebf0e8).
 'dual':'b0ad90b06fc76efd6641d286ff11a27c7f66b94db05c4b33a53fb1287f9e97e6',
 'jk31':'ad3df02e7bb2270ffb7997b57158e3d39f85b0bbabfaec43447cfc5f3f176833',
 'jk30':'2f858fd1b2a43f656935677db6de49fef94a293e4bde7725d532e719f6a57ecf',
 'mots30':'49c2d136cffb6b6108ea29165d1245262713a7ff9ace472654768ee0e3e0c449'}

def source(path,tag,root):
    path=Path(path).resolve()
    if path.suffix.lower()=='.zip':
        with zipfile.ZipFile(path) as archive:
            members=[n for n in archive.namelist() if Path(n).suffix.lower() in ('.goo','.gob')]
            if len(members)!=1:raise ValueError(f'{tag}: ZIP must contain exactly one GOB/GOO')
            raw=archive.read(members[0])
    else:raw=path.read_bytes()
    if digest(raw)!=EXPECTED[tag]:raise ValueError(f'{tag}: source archive differs from the audited release')
    archive=root/'sources'/(tag+'-zip')/('sbx-mots v3.goo' if tag=='mots30' else tag+'.gob')
    archive.parent.mkdir(parents=True,exist_ok=True);archive.write_bytes(raw)
    entries=read_gob(archive);extract(entries,root/'sources'/tag)
    return {'archive_sha256':digest(raw),'entries':len(entries),'input_path':str(path)}

def build(args):
    root=Path(args.output).resolve()
    if root.exists():raise FileExistsError('Choose a new build directory; existing work is never overwritten')
    for name in ['dual','jk30','jk31','mots30','jk_res','jk_snd','mots_res','mots_snd']:
        if not Path(getattr(args,name)).is_file():raise FileNotFoundError(getattr(args,name))
    root.mkdir(parents=True)
    receipts={tag:source(getattr(args,tag),tag,root) for tag in EXPECTED}
    (root/'input-receipt.json').write_text(json.dumps(receipts,indent=2)+'\n')
    from reconcile_sbx import build as reconcile
    from build_dual_scripts import build as scripts
    from build_dual_models import build as models
    from build_dual_controller import build as controller
    from build_dual_visuals import build as visuals
    from bake_dual_keys import build as keys
    from assemble_candidate import assemble
    from validate_candidate import validate
    from build_software_textures import build as software_textures
    from build_footsteps import build as footsteps
    reconciled=root/'generated/reconciled'
    reconcile(root,reconciled,args.mots_res,args.jk_res,args.jk_snd,args.mots_snd)
    scripts(root,root/'generated/dual-scripts')
    visuals(root/'sources/jk31',args.mots_res,root/'generated/dual-visuals')
    keys(args.jk_res,root/'sources/jk31',root/'sources/dual/misc/keyretarget.dat',root/'generated-animation-exact-local-03')
    footsteps(root/'sources/dual/misc/keymarkers.dat',[reconciled,root/'sources/mots30',root/'sources/jk31'],root/'generated/footsteps')
    donor=root/'generated/asset-input/3do/sbxd_donor.3do';donor.parent.mkdir(parents=True)
    shutil.copyfile(root/'sources/jk31/3do/sabg-g.3do',donor)
    model_root=root/'generated/models'
    model_report=models([donor.parent.parent,reconciled,root/'sources/mots30',root/'sources/jk31'],model_root,reconciled/'misc/models.dat')
    if model_report['unsupported']:raise ValueError('Unsupported player models; inspect generated/models/dual-models.json')
    control=root/'generated/controller'
    controller(model_root/'dual-models.json',control)
    candidate=root/'ready'
    assemble(root,candidate,model_root,control,reconciled,args.jk_res,args.mots_res)
    qa=validate(candidate,root/'sources/mots30-zip/sbx-mots v3.goo',args.mots_res,args.mots_snd)
    if not qa['passed']:raise ValueError('Static validation failed; inspect ready/static-validation.json')
    software=software_textures(candidate/'overlay',root/'sources/mots30-zip/sbx-mots v3.goo',args.mots_res,root/'ready-software-textures')
    # This local runnable folder is not the redistributable archive. Loose
    # resources override its unchanged base GOO without archive-order guessing.
    mod=root/'local-mod/SBX-Dual'
    shutil.copytree(candidate/'overlay',mod)
    shutil.copyfile(root/'sources/mots30-zip/sbx-mots v3.goo',mod/'sbx-mots v3.goo')
    result={'status':'BUILT_AND_STATIC_CHECKED','overlay_sha256':qa['archive_sha256'],'members':qa['members'],'models':len(model_report['models']),
            'software_texture_members':software['material_count'],'software_texture_sha256':software['generated_archive_sha256'],
            'local_mod':str(mod),'private_generated_files':True,'note':'Only the source builder package is intended for redistribution. Generated files include locally derived owned game animation.'}
    (root/'BUILD-RESULT.json').write_text(json.dumps(result,indent=2)+'\n');return result

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    for tag in ['dual','jk30','jk31','mots30']:ap.add_argument('--'+tag,required=True,help='Audited local ZIP or GOB/GOO')
    for tag in ['jk-res','jk-snd','mots-res','mots-snd','output']:ap.add_argument('--'+tag,required=True)
    args=ap.parse_args();print(json.dumps(build(args),indent=2))
