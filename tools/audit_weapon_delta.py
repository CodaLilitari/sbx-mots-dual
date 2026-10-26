"""Record source-level JK3.0 -> JK3.1 weapon/class delta dispositions.

This report is deliberately separate from native execution acceptance.
It records exact source hashes, line excerpts and full diffs, including deltas
that preserve a different native MotS behavior instead of silently replacing it.
"""
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import re


def audit(root):
    root = Path(root)
    out = root / 'audit'
    diffs = out / 'jk30-jk31-weapon-diffs'
    diffs.mkdir(parents=True, exist_ok=True)
    files = {}

    def text(path):
        data = (root / path).read_bytes()
        files[path] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
        return data.decode('latin1').replace('\r\n', '\n')

    def evidence(path, needle, radius=1):
        lines = text(path).splitlines()
        indices = [i for i, line in enumerate(lines) if needle in line]
        if not indices:
            raise ValueError(f'Missing evidence in {path}: {needle}')
        i = indices[0]
        a, b = max(0, i-radius), min(len(lines), i+radius+1)
        return {'path': path, 'line_start': a+1, 'line_end': b, 'excerpt': '\n'.join(lines[a:b])}

    pairs = [('weap_saber.cog','weap_saber.cog'),
             ('weap_sithsaber.cog','weap_sithsaber.cog'),
             ('weap_extsaber.cog','weap_longsaber.cog'),
             ('saberstance.cog','saberstance.cog'),('kyle.cog','kyle.cog'),
             ('force_blinding.cog','force_blinding.cog'),
             ('client_weapons.cog','client_weapons.cog')]
    pair_results = []

    def code_only(value):
        # Used only to identify comment-only changes. The full byte-level text
        # diff is saved separately and remains the audit's primary input.
        return [re.sub(r'\s+', '', line.split('//')[0]) for line in value.splitlines()
                if line.strip() and not line.lstrip().startswith(('#','//'))]

    for old, new in pairs:
        a, b = f'sources/jk30/cog/{old}', f'sources/jk31/cog/{new}'
        aa, bb = text(a), text(b)
        diff = ''.join(difflib.unified_diff(aa.splitlines(True), bb.splitlines(True), a, b))
        filename = f'{old}--{new}.diff'
        (diffs / filename).write_text(diff, encoding='utf8')
        pair_results.append({'jk30': a, 'jk31': b, 'text_identical': aa == bb,
                             'code_without_comments_identical': code_only(aa) == code_only(bb),
                             'diff': f'audit/jk30-jk31-weapon-diffs/{filename}'})

    rows = []
    def row(feature, delta, disposition, status, refs):
        rows.append({'feature':feature, 'actual_delta':delta, 'mots_disposition':disposition,
                     'status':status, 'evidence':[evidence(*ref) for ref in refs]})

    j30='sources/jk30/cog/'
    j31='sources/jk31/cog/'
    gen='generated/dual-scripts/cog/'
    mot='sources/mots30/cog/'
    row('Disabled-trails Saber Throw and cleanup',
        'JK31 gates the changing Fan1/Fan2 mesh only; timer cleanup and steady blade restoration remain unconditional.',
        'Remove MotS30 broad allowfans wrappers around timer bodies; gate only changing fan meshes. Attack/throw cleanup executes even with trails disabled.',
        'implemented-source; native execution acceptance separate',
        [(j31+'weap_saber.cog','if(allowfans == 1) jkSetWeaponMesh(player, Fan1[color]);'),
         ('tools/build_dual_scripts.py','def unwrap_fan_gates',12),
         (gen+'weap_saber_m.cog','if(allowfans) jkSetWeaponMesh(player, Fan1[color]);')])
    row('Instant trail toggle',
        'JK31 restores the steady saber mesh in user5 when the current active saber changes trail preference.',
        'All three MotS weapon scripts restore their current steady mesh immediately; staff uses the dual-aware setblade helper.',
        'implemented-source; native execution acceptance separate',
        [(j31+'weap_saber.cog','allowfans=(1-allowfans);',6),
         (gen+'weap_saber_m.cog','allowfans=(1-allowfans);',3),
         (gen+'weap_sithsaber_m.cog','allowfans=(1-allowfans);',3)])
    row('Staff blocking without owning the single saber',
        'JK31 changes three erroneous staff timer ownership guards from single saber bin10 to staff bin5.',
        'Native MotS staff guards already use staff inventory bin125, and are retained. No dependency on MotS single-saber bin10 is introduced.',
        'already-native; preserved',
        [(j30+'weap_sithsaber.cog','if(GetInv(player, 10) == 0) Return;'),
         (j31+'weap_sithsaber.cog','if(GetInv(player, 5) == 0) Return;'),
         (gen+'weap_sithsaber_m.cog','if(GetInv(player, 125) == 0) Return;')])
    row('Startup hum channel reset',
        'JK31 initializes humChannel to -1 during startup.',
        'All three native MotS weapon startup handlers now initialize humChannel to -1.',
        'implemented-source; native execution acceptance separate',
        [(j31+'weap_saber.cog','humChannel = -1;'),
         (gen+'weap_saber_m.cog','humChannel = -1;')])
    row('Saved/uninitialized stance fallback',
        'JK31 adds -1 stance recovery in activation and stance rebroadcast handlers.',
        'Supplied dual stance includes the recovery for all three saber families; port retains it with native ordinals11/5/19 and staff inventory125.',
        'implemented-source; save/load acceptance separate',
        [(j31+'saberstance.cog','if(saberStance == -1)',4),
         (j31+'saberstance.cog','if(saberStance == -1) SendTrigger'),
         (gen+'saberstance.cog','if(saberStance == -1)',4),
         (gen+'saberstance.cog','if(extSaberStance == -1) SendTrigger')])
    row('Ignition stance item availability and handle',
        'JK31 grants and enables stance item144 on saber ignition.',
        'Grant and enable native MotS stance item143 on ignition, and re-fetch its COG handle to avoid retaining a stale saved handle.',
        'implemented-source; save/load acceptance separate',
        [(j31+'weap_saber.cog','SetInv(player, 144, 1);',2),
         (gen+'weap_saber_m.cog','SetInv(player, 143, 1);',3),
         (gen+'weap_sithsaber_m.cog','SetInv(player, 143, 1);',3),
         (gen+'weap_extsaber_m.cog','SetInv(player, 143, 1);',3)])
    row('Saving with a lit saber',
        'JK31 documentation explicitly still requires saving with saber off; active damage and stance reset remain known upstream limitations.',
        'Do not claim the ignition/fallback changes fix saving while lit. Keep the save-with-saber-off limitation until native save/load testing proves a further repair.',
        'known upstream limitation; not claimed fixed',
        [('sources/jk31-document-extracted.txt','Loading quick saves',0)])
    row('Saber auto-selection order',
        'JK31 gives single1000, staff900, long800, above its guns.',
        'Native MotS has concussion800, so long850/staff900/single1000 preserves the JK31 order above all native guns. Keep selected staff at1001 to prevent the dual pose being deselected by engine auto-selection.',
        'implemented-source; native execution acceptance separate',
        [(j31+'weap_saber.cog','ReturnEx(1000.0);'),
         (j31+'weap_sithsaber.cog','ReturnEx(900.0);'),
         (j31+'weap_longsaber.cog','ReturnEx(800.0);'),
         (gen+'weap_saber_m.cog','ReturnEx(1000.0);'),
         (gen+'weap_sithsaber_m.cog','ReturnEx(1001.0);'),
         (gen+'weap_extsaber_m.cog','ReturnEx(850.0);')])
    row('Force Saber Throw inventory relocation',
        'JK31 relocates Saber Throw activation from22 to37 and stance from118 to144.',
        'Retain native MotS Saber Throw37 and stance143. Keep Evasion142, staff125, native Projection and AI notifications; do not transplant JK inventory indices wholesale.',
        'native adaptation',
        [(j31+'weap_saber.cog','IsInvActivated(player, 37)',5),
         (gen+'weap_saber_m.cog','IsInvActivated(player, 37)',11)])
    row('Force Saber Throw cost balance',
        'JK31 uses Jedi level20 with30/70/100 cost; JK30 uses the old power-rank costs.',
        'Retain native MotS power rank37 and130/120/100/80 cost, including its full-mana exception, native force-disturbance message and existing class contracts. This JK31 balance change is not mirrored.',
        'intentional native-balance preservation; disclosed difference',
        [(j31+'weap_saber.cog','rank = GetInv(player, 20);',7),
         (gen+'weap_saber_m.cog','rank = GetInv(player, 37);',10)])
    row('Force Blinding strength and duration',
        'Actual class receiver changes from rank-dependent200/210/200 color to252/270/252, and4*rank to4+rank seconds.',
        'reconcile_sbx.transform_actor applies these exact values after dual actor integration while preserving MotS server and defense multipliers. Its assembly hook is required.',
        'implemented in reconciliation transform; final assembly acceptance separate',
        [(j30+'kyle.cog','blindingEffectHandle = newColorEffect',4),
         (j31+'kyle.cog','blindingEffectHandle = newColorEffect',4),
         ('tools/reconcile_sbx.py','before=\'newColorEffect',6)])
    row('Flash bomb versus Force Blinding',
        'JK31 Force Blinding differs in the class receiver. Its pre-existing flash-damage AddDynamicTint formula remains rank-dependent; force_blinding.cog itself changes comments only.',
        'Preserve native MotS flash-bomb behavior. No separate flash-bomb improvement is claimed from JK31.',
        'no relevant JK31 flash-bomb code change',
        [(j30+'kyle.cog','AddDynamicTint(player, 200 + 8 * rank'),
         (j31+'kyle.cog','AddDynamicTint(player, 200 + 8 * rank')])
    row('Talisman immunity and neutral power/control changes',
        'JK31 class adds Talisman immunity gates, bonus Push/Throw availability and item controls.',
        'Owned by reconcile_sbx: optional Talisman153 and object Throw154 retain native MotS powers and Super Shield. Do not duplicate its actor transformation in the dual builder.',
        'see reconciliation.md and final assembly; separate owner',
        [(j31+'kyle.cog','SetInv(player, 37, 4.0);',8),
         ('audit/reconciliation.md','| Sith Talisman |',0),
         ('audit/reconciliation.md','| Force Throw rapid-fire/cost change |',0)])
    row('Native resource-reference capacity repair',
        'Not a JK31 feature: inherited MotS single/long COGs declare131 resource references, above native128. Final COG handles would be ignored by original parser.',
        'Remove only five legacy sound declarations proven unused in executable code. Retain all used sounds and contiguous arrays. New counts126/123/126 preserve class/Projection/stance COG references.',
        'implemented-source; native128 cap independently proven from disassembly and runtime crash',
        [('tools/build_dual_scripts.py',"for symbol in ('hitSound01'",4),
         ('tools/build_dual_scripts.py','def cog_budget',11)])
    row('Dual track-pressure and hit-list safety adaptation',
        'Supplied browser extension overlaps dual attacks at75% of animation duration and depends on enhanced runtime generation.',
        'Exact locally baked native KEYs; four-track adaptation waits full duration, uses UNIQUE/NOLOOP end-removal, rejects failed allocation before hit-list reset, and does not retain attack handles that could later target reused tracks.',
        'implemented-source; retail animation/damage acceptance separate',
        [(gen+'weap_sithsaber_m.cog','if(dualResult == -1)',11),
         (gen+'weap_sithsaber_m.cog','Full-duration cooldown',3)])

    report={'scope':'Source reconciliation only; not original-retail execution, save/load or multiplayer proof.',
            'pairs':pair_results, 'features':rows, 'files':files,
            'native_script_budgets':json.loads(text('generated/dual-scripts/script-build.json'))}
    (out/'weapon-class-feature-matrix.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    md=['# JK3.0 to JK3.1 weapon and class feature matrix','',report['scope'],'',
        'The JSON companion contains source hashes and exact line excerpts. The `jk30-jk31-weapon-diffs` directory contains complete source diffs.','',
        '| Feature | Actual JK3.0 to JK3.1 delta | MotS disposition and status | Evidence |',
        '| --- | --- | --- | --- |']
    for r in rows:
        refs='; '.join(f"`{e['path']}:{e['line_start']}`" for e in r['evidence'])
        md.append(f"| {r['feature']} | {r['actual_delta']} | {r['mots_disposition']} **{r['status']}.** | {refs} |")
    md+=['','## Direct pair checks','']
    for pair in pair_results:
        md.append(f"- `{pair['jk30']}` -> `{pair['jk31']}`: identical text={pair['text_identical']}; identical executable tokens ignoring whitespace/comments={pair['code_without_comments_identical']}.")
    (out/'weapon-class-feature-matrix.md').write_text('\n'.join(md)+'\n',encoding='utf8')
    return {'features':len(rows),'diff_pairs':len(pairs),'report':str(out/'weapon-class-feature-matrix.json')}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',required=True)
    args=parser.parse_args();print(json.dumps(audit(args.root),indent=2))
