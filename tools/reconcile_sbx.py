"""Reconcile SBX JK 3.1 assets onto native SBX MotS 3.0, without copying the base.

The original archives remain authoritative. Every emitted member has a disposition.
This module owns only generated/reconciled; dual weapon/controller code is separate.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STOCK = Path(r'C:\Users\Andrei\Documents\ChatGPT\Starweird-JKDF2-Lab\private-tests\retail-readiness\stock-mots\resource\JKMRES.GOO')
DEFAULT_JK_SOUNDS = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Star Wars Jedi Knight\Resource\Res1hi.gob')
DEFAULT_JK_RES = DEFAULT_JK_SOUNDS.with_name('Res2.gob')
TALISMAN_ITEM = 'sbxd_talisman 153 0 1 0x010 cog=sbxd_talisman.cog'
TALISMAN_TEMPLATE = 'sbxd_talisman _powerupx model3d=vestl.3do cog=sbxd_tal_pick.cog'
OBJECT_THROW_ITEM = 'objthrow 154 1 4 0x022 cog=sbxd_objthrow.cog'
DESTRUCTION_TEMPLATES = '''+sbxd_destcloud none orient=(0/0/0) type=particle timer=.119 typeflags=0x3f material=dstructparts.mat range=.05 rate=64 maxthrust=40 elementsize=.01 count=64
+sbxd_dest1 _explosionx thingflags=0x1 light=.1 timer=.4 sprite=destruct8.spr soundclass=exp_dest.snd creatething=+sbxd_destcloud typeflags=0x13 damage=15 damageclass=0x8 blasttime=.3 force=100 maxlight=.5 range=.5
+sbxd_dest2 _explosionx thingflags=0x1 light=.2 timer=.6 sprite=destruct8.spr soundclass=exp_dest.snd creatething=+sbxd_destcloud typeflags=0x13 damage=30 damageclass=0x8 blasttime=.4 force=200 maxlight=.6 range=1
+sbxd_dest3 _explosionx thingflags=0x1 light=.3 timer=.8 sprite=destruct8.spr soundclass=exp_dest.snd creatething=+sbxd_destcloud typeflags=0x13 damage=45 damageclass=0x8 blasttime=.5 force=300 maxlight=.7 range=1.5
+sbxd_dest4 _explosionx thingflags=0x1 light=.4 timer=1 sprite=destruct8.spr soundclass=exp_dest.snd creatething=+sbxd_destcloud typeflags=0x13 damage=60 damageclass=0x8 blasttime=.6 force=400 maxlight=.8 range=2
+sbxd_destp1 _weaponx thingflags=0x20000401 light=.4 sprite=forcedstruct_150.spr cog=00_desttrail.cog vel=(0/7/0) explode=+sbxd_dest1 fleshhit=+sbxd_dest1 damage=20 typeflags=0xd
+sbxd_destp2 +sbxd_destp1 explode=+sbxd_dest2 fleshhit=+sbxd_dest2
+sbxd_destp3 +sbxd_destp1 explode=+sbxd_dest3 fleshhit=+sbxd_dest3
+sbxd_destp4 +sbxd_destp1 explode=+sbxd_dest4 fleshhit=+sbxd_dest4'''

OBJECT_THROW_COG = '''# Force Throw (objects), native MotS selectable inventory item154.
# Based on LucasArts/YB FORCE_THROW.COG and ShadowX SBX JK3.1 changes.
# Native adaptation by Coda collaborating with Andrei, 2026-10-23.
# Hold Inventory Use to aim; release to throw visible debris. No new hotkey.
# Rank follows native Jedi rank, capped4; costs30/50/80/80. Native powers kept.
symbols
thing player local
thing potential local
thing debris local
thing victim=-1 local
flex mana local
flex maxDot local
flex dot local
flex cost=80 local
flex readyAt=0 local
int rank local
int active=0 local
int inbubble=0 local
vector dir local
sound throwSound=ForceThrow01.wav local
message startup
message activated
message deactivated
message pulse
message newplayer
message killed
message deselected
message selected
message enterbubble
message exitbubble
message user1
message user2
message user3
message shutdown
end
code
startup:
   player = GetLocalPlayerThing();
   active = 0;
   inbubble = 0;
   Return;
activated:
   if(active || inbubble) Return;
   if(GetThingHealth(player) <= 0) Return;
   if(GetActorFlags(player) & 0x800) Return;
   if(GetCurWeapon(player) == 10) Return;
   if(GetGameTime() < readyAt) Return;
   rank = GetInv(player, 20);
   if(rank <= 0)
   {
      Print("Force Throw requires Jedi potential");
      Return;
   }
   if(rank > 4) rank = 4;
   if(rank == 1) cost = 30;
   else if(rank == 2) cost = 50;
   else cost = 80;
   mana = GetInv(player, 14);
   if(mana < cost) Return;
   active = 1;
   victim = -1;
   SetInvActivated(player, 154, 1);
   call find_target;
   SetPulse(0.1);
   Return;
pulse:
   if(!active) Return;
   if(inbubble || (GetThingHealth(player) <= 0) || (GetActorFlags(player) & 0x800) || (GetCurWeapon(player) == 10))
   {
      call stop_power;
      Return;
   }
   call find_target;
   Return;
find_target:
   victim = -1;
   maxDot = 0;
   potential = FirstThingInView(player, 50 + 10 * rank, 7, 0x404);
   while(potential != -1)
   {
      if(HasLOS(player, potential) && (potential != player) &&
         (GetThingHealth(potential) > 0) &&
         (VectorDist(GetThingPos(player), GetThingPos(potential)) <= 4) &&
         !(GetThingFlags(potential) & 0x200) &&
         !((jkGetFlags(potential) & 0x20) && !IsInvActivated(player, 23)))
      {
         dot = ThingViewDot(player, potential);
         if(dot > maxDot)
         {
            victim = potential;
            maxDot = dot;
         }
      }
      potential = NextThingInView();
   }
   if(victim != -1)
   {
      jkSetTargetColors(6, 7, 8);
      jkSetTarget(victim);
   }
   else jkEndTarget();
   Return;
deactivated:
   if(!active) Return;
   if(inbubble || (GetThingHealth(player) <= 0) || (GetActorFlags(player) & 0x800) || (GetCurWeapon(player) == 10))
   {
      call stop_power;
      Return;
   }
   call find_target;
   mana = GetInv(player, 14);
   if((victim != -1) && (mana >= cost))
   {
      PlayMode(player, 24);
      PlaySoundThing(throwSound, player, 1.0, -1, -1, 0x80);
      if(GetInv(player, 64) != 1) ChangeInv(player, 14, -cost);
      readyAt = GetGameTime() + 2;
      SetBinWait(player, 154, 2);
      if(!IsMulti()) SendMessageExRadius(GetThingPos(player), cost, 0x4, splash, 154, 0, 0, 0);
      debris = FirstThingInView(player, 40 + 20 * rank, 3 + rank, 0x010);
      while(debris != -1)
      {
         if(HasLOS(player, debris))
         {
            dir = VectorScale(VectorNorm(VectorSub(GetThingPos(victim), GetThingPos(debris))), 200);
            DetachThing(debris);
            ApplyForce(debris, dir);
         }
         debris = NextThingInView();
      }
   }
   call stop_power;
   Return;
selected:
   jkPrintUNIString(player, 154);
   Return;
killed:
   if(GetSenderRef() != player) Return;
   call stop_power;
   Return;
enterbubble:
user2:
   inbubble = 1;
   call stop_power;
   Return;
exitbubble:
user3:
   inbubble = 0;
   Return;
newplayer:
   inbubble = 0;
   readyAt = 0;
   call stop_power;
   Return;
deselected:
user1:
shutdown:
   call stop_power;
   Return;
stop_power:
   SetPulse(0);
   SetInvActivated(player, 154, 0);
   active = 0;
   victim = -1;
   jkEndTarget();
   Return;
end
'''

TALISMAN_COG = '''# Sith Talisman, optional native MotS inventory helper.
# Original concept/behavior: ShadowX SBX JK3.1; LucasArts/YB pickup precedent.
# MotS adaptation: Coda collaborating with Andrei, 2026-10-23.
# Bin153 is independent of native Super Shield62. No map pickup is replaced.
symbols
thing player local
int active=0 local
int inheritedSeal=0 local
int warnings=0 local
sound outsnd=SCAlarm.wav local
message startup
message user0
message user1
message pulse
message timer
message newplayer
message killed
message shutdown
end
code
startup:
   player = GetLocalPlayerThing();
   Return;
user0:
   player = GetLocalPlayerThing();
   if(GetThingHealth(player) <= 0) Return;
   if(!active) inheritedSeal = (GetThingFlags(player) & 4) && !IsInvActivated(player, 62);
   active = 1;
   SetInv(player, 153, 1);
   SetInvActivated(player, 153, 1);
   SetThingFlags(player, 4);
   SetInv(player, 14, 0);
   KillTimerEx(153);
   KillTimerEx(154);
   warnings = 0;
   SetTimerEx(15, 153, 0, 0);
   SetTimerEx(12, 154, 0, 0);
   SetPulse(0.5);
   jkPrintUNIString(player, 153);
   Return;
pulse:
   if(!active) Return;
   if(GetThingHealth(player) <= 0)
   {
      call stop_power;
      Return;
   }
   SetInv(player, 14, 0);
   SetThingFlags(player, 4);
   Return;
timer:
   if(GetSenderId() == 153)
   {
      call stop_power;
      Return;
   }
   if((GetSenderId() == 154) && active)
   {
      PlaySoundLocal(outsnd, 1.0, 0.0, 0);
      warnings = warnings + 1;
      if(warnings < 3) SetTimerEx(1, 154, 0, 0);
   }
   Return;
killed:
   if(GetSenderRef() != player) Return;
   call stop_power;
   Return;
newplayer:
user1:
shutdown:
   call stop_power;
   Return;
stop_power:
   SetPulse(0);
   KillTimerEx(153);
   KillTimerEx(154);
   if(active && !inheritedSeal && !IsInvActivated(player, 62)) ClearThingFlags(player, 4);
   active = 0;
   inheritedSeal = 0;
   if(player >= 0)
   {
      SetInv(player, 153, 0);
      SetInvActivated(player, 153, 0);
   }
   Return;
end
'''

TALISMAN_PICKUP_COG = '''# Optional Sith Talisman pickup for native MotS.
# Based on ShadowX/YB SBX JK3.1 pow_supershield.cog behavior.
# MotS adaptation by Coda collaborating with Andrei; stock Super Shield retained.
symbols
thing player local
thing powerup local
sound pickupsnd=forceabsorb02.wav local
sound respawnsnd=Activate01.wav local
message touched
message taken
message respawn
end
code
touched:
   player = GetSourceRef();
   powerup = GetSenderRef();
   TakeItem(powerup, player);
   Return;
taken:
   player = GetSourceRef();
   powerup = GetSenderRef();
   PlaySoundThing(pickupsnd, powerup, 1.0, -1, -1, 0);
   if(player == GetLocalPlayerThing())
   {
      AddDynamicTint(player, 0.2, 0.0, 0.0);
      SendMessage(GetInvCog(player, 153), user0);
   }
   Return;
respawn:
   powerup = GetSenderRef();
   PlaySoundThing(respawnsnd, powerup, 0.6, 5.0, 10.0, 0);
   Return;
end
'''

def transform_actor(text):
    """Apply after dual edits to each of kyle_m, mara_m, and luke_m."""
    if '# SBXD TALISMAN DAMAGE' in text:
        return text
    pattern = r'(damageType\s*=\s*GetParam\(1\);\s*damage\s*=\s*GetParam\(0\);)'
    addition = '''
   // # SBXD TALISMAN DAMAGE: native Super Shield62 remains independent.
   if(IsInvActivated(player, 153) && (damageType & 8))
   {
      ReturnEx(0);
      Return;
   }
'''
    text,count=re.subn(pattern,lambda m:m.group(1)+addition,text,count=1)
    assert count == 1, 'Missing native MotS damage initialization'
    pos=text.index('\nskill:')
    head,tail=text[:pos],text[pos:]
    pattern=r'(bin\s*=\s*GetParam\(0\);\s*rank\s*=\s*GetParam\(1\);)'
    addition='''
   // # SBXD TALISMAN SKILL: reject Force effects, including MotS chain lightning.
   // Carbonite, flash bombs and other weapon skills keep native behavior.
   if(IsInvActivated(player, 153) && ((bin == 24) || (bin == 25) ||
      (bin == 27) || (bin == 31) || (bin == 34) || (bin == 38) || (bin == 39)))
   {
      ReturnEx(0);
      Return;
   }
'''
    tail,count=re.subn(pattern,lambda m:m.group(1)+addition,tail,count=1)
    assert count == 1, 'Missing native MotS skill initialization'
    text=head+tail
    for label in ('killed','newplayer'):
        # Defer the killed cleanup until after the native local-player guard.
        pattern=(r'(\nkilled:\s*if\s*\(player\s*!=\s*GetSenderRef\(\)\)\s*Return;)' if label=='killed'
                 else r'(\nnewplayer:)')
        text,count=re.subn(pattern,lambda m:m.group(1)+'\n   SendMessage(GetInvCog(player, 153), user1);\n   SendMessage(GetInvCog(player, 154), user1);\n',text,count=1)
        assert count == 1, f'Missing native {label} cleanup insertion'
    # Native bubble iteration dispatches only flag0x8 Force bins. The new item
    # intentionally lacks that flag; bridge class events through ordinary user
    # messages because native SendMessage disallows event numbers45/46.
    for label,event in (('enterbubble','user2'),('exitbubble','user3')):
        pattern=r'(\n'+label+r':)'
        text,count=re.subn(pattern,lambda m:m.group(1)+f'\n   SendMessage(GetInvCog(player, 154), {event});\n',text,count=1)
        assert count == 1, f'Missing native {label} forwarding insertion'
    before='newColorEffect(0, 0, 0, 0, 0, 0, 200 + 8 * rank, 210 + 10 * rank, 200 + 8 * rank, 1.0)'
    assert text.count(before) == 1
    text=text.replace(before,'newColorEffect(0, 0, 0, 0, 0, 0, 252, 270, 252, 1.0)')
    before='SetTimerEx(4 * rank * jkGetMultiParam (31) * defenseFactor, 27, player, 0);'
    assert text.count(before) == 1
    text=text.replace(before,'SetTimerEx((4 + rank) * jkGetMultiParam (31) * defenseFactor, 27, player, 0);')
    return text

def transform_items(text):
    """Add Talisman153 and inventory-only ObjectThrow154 without base changes."""
    for row in (TALISMAN_ITEM,OBJECT_THROW_ITEM):
        name,number=row.split()[:2]
        if re.search(r'(?im)^\s*'+name+r'\s+'+number+r'\s',text):
            continue
        assert not re.search(r'(?im)^\s*\S+\s+'+number+r'\s',text), 'Inventory bin occupied: '+number
        match=list(re.finditer(r'(?im)^\s*end\s*$',text))[-1]
        text=text[:match.start()]+row+'\n'+text[match.start():]
    return text

def transform_static(text):
    """Expose a new template; never replace a map's original super-shield item."""
    match=re.search(r'(?ims)(^Section:\s*templates\b.*?)(^end\s*$)',text)
    assert match and re.search(r'(?im)^\s*_powerupx\s',match.group(1))
    part=match.group(1)
    additions=[row for row in [TALISMAN_TEMPLATE,*DESTRUCTION_TEMPLATES.splitlines()]
               if not re.search(r'(?im)^\s*'+re.escape(row.split()[0])+r'\s',part)]
    if not additions:
        return text
    count=re.search(r'(?im)^(\s*world\s+templates\s+)(\d+)',part)
    if count:
        part=part[:count.start(2)]+str(int(count.group(2))+len(additions))+part[count.end(2):]
    return text[:match.start()]+part+'\n'+'\n'.join(additions)+'\n'+match.group(2)+text[match.end():]

def transform_strings(text):
    """Merge only new UI labels, incrementing the original MSGS allocation."""
    additions=[]
    for key,value in (('COG_00153','Sith Talisman'),('COG_00154','Force Throw (objects)')):
        if not re.search(r'(?im)^\s*"'+key+r'"\s',text):
            additions.append(f'   "{key}" 0 "{value}"')
    if not additions:
        return text
    match=re.search(r'(?im)^(MSGS\s+)(\d+)',text)
    assert match
    text=text[:match.start(2)]+str(int(match.group(2))+len(additions))+text[match.end(2):]
    end=list(re.finditer(r'(?im)^\s*END\b',text))[-1]
    return text[:end.start()]+'\n# Native SBX overlay additions\n'+'\n'.join(additions)+'\n'+text[end.start():]

def sha(data):
    return hashlib.sha256(data).hexdigest()

def read_tree(path):
    return {p.relative_to(path).as_posix().lower(): p.read_bytes()
            for p in sorted(path.rglob('*')) if p.is_file()}

def stock_index(path):
    with path.open('rb') as f:
        magic, version, table = struct.unpack('<4sII', f.read(12))
        assert magic == b'GOB ' and version == 20
        f.seek(table)
        count, = struct.unpack('<I', f.read(4))
        result = {}
        for _ in range(count):
            offset, size, raw = struct.unpack('<II128s', f.read(136))
            name = raw.split(b'\0')[0].decode('latin1').replace('\\', '/').lower().lstrip('/')
            result[name] = (offset, size)
    return result

def stock_member(path, index, name):
    offset, size = index[name]
    with path.open('rb') as f:
        f.seek(offset)
        return f.read(size)

def parse_models(data):
    rows = []
    for line in data.decode('latin1').splitlines():
        m = re.match(r'\s*(\d+):\s+(\S+)\s+(\S+)(?:\s+(\d+))?\s*(.*)', line)
        if m:
            i, model, sound, personality, comment = m.groups()
            rows.append(dict(source_label=int(i), model=model.lower(), sound=sound.lower(),
                             personality=int(personality) if personality is not None else None,
                             comment=comment))
    expected = int(re.search(rb'(?i)nummodels:\s*(\d+)', data).group(1))
    assert len(rows) == expected
    return rows

def reconcile(root=ROOT, out=None, stock=DEFAULT_STOCK, jk_sounds=DEFAULT_JK_SOUNDS, mots_sounds=None, jk_res=DEFAULT_JK_RES):
    root = Path(root).resolve()
    out = Path(out).resolve() if out else root/'generated/reconciled'
    assert out.is_relative_to(root), 'Output must stay in this task'
    sources = {name: read_tree(root/'sources'/name) for name in ('mots30','jk30','jk31')}
    base, old, new = (sources[k] for k in ('mots30','jk30','jk31'))
    stock = Path(stock)
    index = stock_index(stock)
    sound_archive = Path(mots_sounds) if mots_sounds else stock.with_name('JKMSNDLO.GOO')
    assert sound_archive.is_file(), 'Owned MotS sound archive is required for dependency verification'
    available_stock = set(index) | set(stock_index(sound_archive))
    jk_sounds = Path(jk_sounds)
    jk_sound_index = stock_index(jk_sounds)
    generated = {}
    manifest = {}
    def emit(name, data, reason, source):
        if base.get(name) == data:
            return
        generated[name] = data
        manifest[name] = dict(path=name, reason=reason, source=source, sha256=sha(data),
                              base_sha256=sha(base[name]) if name in base else None)

    # Preserve every native row, class and sound choice. Append missing skins for
    # each of the four native non-team classes, following the SBX MotS contract.
    base_rows = parse_models(base['misc/models.dat'])
    jk_rows = parse_models(new['misc/models.dat'])
    existing = {row['model'] for row in base_rows}
    missing = [row for row in jk_rows if row['model'] not in existing]
    assert len({r['model'] for r in missing}) == len(missing)
    rows = [dict(row) for row in base_rows]
    for personality in (1,2,3,4):
        rows.extend({**row, 'personality':personality} for row in missing)
    lines = ['# SBX MotS 3.0 registry with missing SBX JK 3.1 skins.',
             '# Original content by ShadowX and credited contributors; reconciliation by Coda with Andrei.',
             '# Existing row order, sound choices and personality roles are preserved.',
             f'numModels: {len(rows)}', '']
    for i,row in enumerate(rows):
        lines.append(f"{i}:\t{row['model']}\t{row['sound']}\t{row['personality']}  {row['comment']}")
    emit('misc/models.dat', ('\r\n'.join(lines)+'\r\n').encode('latin1'),
         'Preserve all native rows; append missing JK3.1 skins in classes 1-4; repair duplicate textual row labels without reordering.', 'merge')

    delta = {name for name,data in new.items() if old.get(name) != data}
    dispositions = []
    art_prefixes = ('3do/', 'mat/', 'sound/', 'misc/snd/')
    preserved_conflicts = {'sound/expl_06.wav','sound/expl_07.wav'}
    for name in sorted(delta):
        if name in preserved_conflicts:
            decision, reason = 'preserve-mots', 'MotS-specific explosion audio differs from both JK versions; preserve native sound.'
        elif name.startswith(art_prefixes):
            emit(name,new[name],'True JK3.0-to-3.1 asset addition/update; shared MotS bytes are JK3.0 where applicable.','jk31')
            decision,reason = 'include-asset', 'Bring forward actual 3.1 media improvements and additions.'
        elif name == 'misc/models.dat':
            decision,reason = 'merge-registry','Append missing skins while preserving native personality roles and all MotS-only rows.'
        elif name.startswith('ui/'):
            decision,reason = 'preserve-mots-interface','JK menu/label/icon replacement is tied to its different inventory scheme; retain native MotS control names and layout.'
        elif name == 'misc/items.dat':
            decision,reason = 'preserve-mots-inventory','JK inventory and hotkey renumbering cannot replace native MotS bins, classes, powers and weapon ordinals.'
        elif name == 'jkl/static.jkl':
            decision,reason = 'delegated-template-merge','Native MotS template graph retained; compatible weapon delta integration belongs to main builder.'
        elif name.startswith('cog/'):
            decision,reason = 'reviewed-target-specific','See feature dispositions and COG notes; do not overwrite MotS COGs with JK variants.'
        else:
            decision,reason = 'preserve-attribution-separately','Historical JK package metadata retained as source documentation, not installed over MotS.'
        dispositions.append(dict(path=name,change='added' if name not in old else 'changed',disposition=decision,reason=reason))

    # JK3.1 accidentally links the head to the right-hand saber node, despite
    # declaring no head children. Restore only that link to the native MotS
    # value; all JK3.1 geometry, transforms and other hierarchy fields survive.
    plorobe = new['3do/plorobe.3do']
    bad_link = b'15: 0x0 0x8 13 16 19 -1 0 '
    good_link = b'15: 0x0 0x8 13 16 -1 -1 0 '
    assert plorobe.count(bad_link) == 1
    repaired_plorobe = plorobe.replace(bad_link, good_link)
    emit('3do/plorobe.3do',repaired_plorobe,
         'JK3.1 skin update with native hierarchy repair: head node15 child19 becomes-1; child count0 and right-hand parent12 of node19 retained.',
         'jk31-native-hierarchy-repair')
    for disposition in dispositions:
        if disposition['path'] == '3do/plorobe.3do':
            disposition.update(disposition='include-asset-repaired',reason='Include JK3.1 revision; repair the inconsistent head child19 link to native MotS -1 without changing any other bytes.')

    reverse_dispositions=[]
    for name in sorted(set(old)-set(new)):
        if name in base:
            decision='preserved-native-base'
            reason='Still supplied by SBX MotS3.0; overlay does not remove it.'
        elif name in available_stock:
            decision='preserved-native-retail'
            reason='Native MotS resource/sound archive supplies this path; retain target UI/audio.'
        elif name in ('mat/clear.mat','mat/sblack.mat'):
            relocated='3do/'+name
            assert new[relocated]==old[name]
            decision='preserved-relocated-identical'
            reason='Exact same bytes are provided at '+relocated+'; both are standard material lookup locations.'
        elif name=='cog/weap_extsaber.cog':
            assert 'cog/weap_extsaber_m.cog' in base
            decision='preserved-native-equivalent'
            reason='Native MotS extended-saber COG retained and updated by weapon builder; JK bin variant is not installed.'
        else:
            emit(name,old[name],'JK3.0-only content absent from both JK3.1 and native MotS resources.','jk30-retained')
            decision='include-jk30-only'
            reason='Preserve removed3.0resource as additional optional content without assigning it over3.1orMotS.'
        reverse_dispositions.append(dict(path=name,disposition=decision,reason=reason))

    # Make every newly registered skin resolve. Existing native definitions remain
    # authoritative for unchanged model names and their sound choices.
    for row in missing:
        for name in ('3do/'+row['model'],'misc/snd/'+row['sound']):
            if name not in base and name not in generated and name not in available_stock:
                assert name in new or name in old, f'Missing registered resource {name}'
                emit(name,new.get(name,old.get(name)), 'Dependency of newly registered JK3.1 skin.', 'jk31' if name in new else 'jk30')

    # Resolve inherited sound classes too: kybobafett.snd uses an owned JK
    # voice line absent from the MotS archives, despite being unchanged here.
    unresolved = []
    checked = set()
    pending = list(generated) + [n for n in base if n.endswith('.snd')]
    while pending:
        name = pending.pop()
        if name in checked:
            continue
        checked.add(name)
        data = generated.get(name,base.get(name))
        if name.endswith('.3do'):
            refs = re.findall(r'(?im)^\s*\d+:\s+(\S+\.mat)\s*$',data.decode('latin1'))
            refs = [('3do/mat/'+ref.lower(),'mat/'+ref.lower()) for ref in refs]
        elif name.endswith('.snd'):
            refs = [('sound/'+ref.lower(),'voice/'+ref.lower()) for ref in re.findall(r'(?i)\b([^\s#]+\.wav)\b', data.decode('latin1'))]
        else:
            refs = []
        for alternatives in refs:
            if any(ref in generated or ref in base or ref in available_stock for ref in alternatives):
                continue
            found = next((ref for ref in alternatives if ref in new or ref in old),None)
            if found:
                emit(found,new.get(found,old.get(found)), f'Dependency closure for {name}.', 'jk31' if found in new else 'jk30')
                pending.append(found)
            else:
                owned = next((ref for ref in alternatives if ref in jk_sound_index),None)
                if owned:
                    emit(owned,stock_member(jk_sounds,jk_sound_index,owned),
                         f'Locally derived owned JK sound dependency for {name}; omit bytes from portable distribution.',
                         'owned-jk-retail-local-only')
                else:
                    unresolved.append(dict(owner=name, alternatives=alternatives))

    # Full standalone closure exposes an inherited MotS omission: the male
    # pedestrian's third response names cm60142.wav, which shipped neither in
    # MotS nor SBX. Use the same response's original JK voice, explicitly as a
    # fallback (not a claim to recover the missing MotS recording).
    pedestrian = base['cog/actor_mn.cog']
    needle = b'mind=cm60142.wav'
    assert pedestrian.count(needle) == 1
    jk_resources = Path(jk_res)
    jk_resource_index = stock_index(jk_resources)
    original_pedestrian = stock_member(jk_resources, jk_resource_index, 'cog/actor_mn.cog')
    assert b'mind=i00mn13z.wav' in original_pedestrian
    voice_name = 'voice/i00mn13z.wav'
    emit('cog/actor_mn.cog', pedestrian.replace(needle, b'mind=i00mn13z.wav'),
         'Replace inherited missing MotS mind-response sound with the source-equivalent original JK response; all other actor bytes preserved.',
         'mots30-voice-fallback')
    emit(voice_name, stock_member(jk_sounds, jk_sound_index, voice_name),
         'Original JK actor_mn mind response, bundled as an explicit fallback for absent cm60142.wav, not a recovered MotS voice.',
         'owned-jk-retail-local-only')

    # SBX accidentally inverted native Force Defense. Stock source independently
    # establishes subtraction (1-rank*.125); retain SBX's intended .25 strength.
    stock_defense = stock_member(stock,index,'cog/force_defense.cog')
    assert b'damage = damage * (1 - rank * 0.125);' in stock_defense
    defense = base['cog/force_defense.cog']
    needle = b'damage = damage * (rank * 0.25);'
    assert defense.count(needle) == 1
    emit('cog/force_defense.cog', defense.replace(needle,b'damage = damage * (1 - rank * 0.25);'),
         'Restore native decreasing-damage direction while retaining SBX 25-percent-per-rank balance.', 'mots30-corrected')
    bryar=base['cog/weap_bryar_m.cog']
    needle=b'GetInv(player, 2)'
    assert bryar.count(needle)==1
    emit('cog/weap_bryar_m.cog',bryar.replace(needle,b'GetInv(player, GetWeaponBin(2))'),
         'Repair MotS Bryar autoselection: test native weapon bin122 via GetWeaponBin(2), preserving original priority200 and all other behavior.','mots30-corrected')

    # JK3.1 changed the slowing/Push rumble. Port only the sound choice into the
    # native MotS Jump implementation; its bin, EWEB and bubble logic stay intact.
    jump = base['cog/force_jump.cog']
    assert jump.lower().count(b'slowsound=fpush.wav') == 1
    jump = re.sub(rb'slowSound=fpush\.wav',b'slowSound=forcepush.wav',jump,flags=re.I)
    emit('cog/force_jump.cog',jump,'Port JK3.1 Force Push/slowfall sound choice; retain native MotS Jump lifecycle and bins.','mots30-merged')
    if 'sound/forcepush.wav' not in base and 'sound/forcepush.wav' not in available_stock:
        assert 'sound/forcepush.wav' in new
        emit('sound/forcepush.wav',new['sound/forcepush.wav'],'Sound dependency for updated slowfall cue.','jk31')

    goggles=base['cog/item_irgoggles.cog']
    assert goggles.count(b'EnableIRMode(0.3, 1)')==1
    emit('cog/item_irgoggles.cog',goggles.replace(b'EnableIRMode(0.3, 1)',b'EnableIRMode(1.0, 1)'),
         'Port JK3.1 brighter IR effect; retain native goggles controls, battery and newplayer cleanup.','mots30-merged')
    push=base['cog/force_push.cog'].decode('latin1').replace('\r\n','\n')
    assert push.count('message     startup')==1
    push=push.replace('message     startup','int level local\nint eligible local\n\nmessage     startup')
    needle='   rank = GetInv(player, 38);'
    assert push.count(needle)==1
    push=push.replace(needle,needle+'''
   level = GetInv(player, 20);
   if(level == 1) cost = 30;
   else if(level == 2) cost = 50;
   else cost = 60;''')
    begin=push.index('\npulse:');end=push.index('\nselected:',begin)
    push=push[:begin]+'''
pulse:
   if(!active) Return;
   // Retain native MotS actor/player scope, power rank, reach and force.
   // Exactly one iterator advance prevents a rejected target from making
   // the next target bypass immunity/visibility checks (an inherited bug).
   victim = FirstThingInView(player, 20 + 15 * rank, rank / 3, 0x404);
   while(victim != -1)
   {
      eligible = 1;
      if(GetThingType(victim) == 10)
      {
         if(IsInvActivated(victim, 153)) eligible = 0;
      }
      if(eligible && HasLOS(player, victim) && (victim != player) &&
         (VectorDist(GetThingPos(player), GetThingPos(victim)) <= (rank / 4)) &&
         !(GetThingFlags(victim) & 0x200) && !(GetThingFlags(victim) & 0x2) &&
         !(GetActorFlags(victim) & 8) && !(jkGetFlags(victim) & 0x20))
      {
         mana = GetInv(player, 14);
         if(mana >= cost)
         {
            PlayKey(player, push, 0, 0x38);
            PlaySoundThing(pushSound, player, 1.0, -1, -1, 0x80);
            DetachThing(victim);
            ApplyForce(victim, VectorScale(VectorNorm(VectorSub(GetThingPos(victim), GetThingPos(player))), 120 * rank));
            if((GetInv(player, 64) != 1) && (GetInv(player, 65) != 1)) ChangeInv(player, 14, -cost);
            SetBinWait(player, 38, 1.5);
         }
      }
      victim = NextThingInView();
   }
   SetPulse(0);
   Return;

# ........................................................................................
''' + push[end:]
    emit('cog/force_push.cog',push.replace('\n','\r\n').encode('latin1'),
         'Port JK3.1 Jedi-potential cost30/50/60, actor invulnerability exclusion and either-Surge mana exemption. Preserve native bin38/rank/reach/force120/actor-player scope/bubble handling; enforce Talisman immunity and repair iterator filter bypass.','mots30-merged')

    emit('cog/sbxd_talisman.cog',TALISMAN_COG.replace('\n','\r\n').encode('ascii'),
         'Optional 15-second Sith Talisman lifecycle, separate bin153, magnetic seal and mana drain.','authored-native-adaptation')
    emit('cog/sbxd_tal_pick.cog',TALISMAN_PICKUP_COG.replace('\n','\r\n').encode('ascii'),
         'Optional Talisman pickup; no original MotS pickup or powerup is replaced.','authored-native-adaptation')
    native_shield=stock_member(stock,index,'cog/pow_supershield.cog')
    shield=native_shield.decode('latin1').replace('\r','')
    for target in ('GetParam(0)','player'):
        needle=f'ClearThingFlags({target}, 4);'
        assert shield.count(needle)==1
        shield=shield.replace(needle,f'if(!IsInvActivated({target}, 153)) '+needle)
    emit('cog/pow_supershield.cog',shield.replace('\n','\r\n').encode('latin1'),
         'Locally derived native Super Shield with two seal-clear guards so overlap never cancels active Talisman; native duration/invulnerability/shieldbonus unchanged.','owned-mots-retail-derived-local-only')
    emit('ui/jkstrings.uni',transform_strings(base['ui/jkstrings.uni'].decode('latin1').replace('\r\n','\n')).replace('\n','\r\n').encode('latin1'),
         'Merge COG_00153/154 labels and increment original MSGS allocation by2; preserve native strings.','mots30-merged')
    emit('cog/sbxd_objthrow.cog',OBJECT_THROW_COG.replace('\n','\r\n').encode('ascii'),
         'JK3.1 object Throw adapted to inventory-only bin154, native MotS eligibility/bubbles/EWEB, true2secondcooldown.','authored-native-adaptation')
    for bits in (8,16):
        name=f'ui/bm/icf_thr{bits}.bm'
        assert name in jk_sound_index
        emit(f'ui/bm/icobjth{bits}.bm',stock_member(jk_sounds,jk_sound_index,name),
             'Locally derived owned JK Force Throw icon, renamed for inventory name objthrow; no hotkey.','owned-jk-retail-local-only')
    destruction=base['cog/force_destruction.cog']
    for rank in range(1,5):
        oldname=f'=+force_dest_p{rank}'.encode('ascii')
        assert destruction.count(oldname)==1
        destruction=destruction.replace(oldname,f'=+sbxd_destp{rank}'.encode('ascii'))
    emit('cog/force_destruction.cog',destruction,
         'Use namespaced native MotS projectile/explosion clones, clearing only explosion no-shooter-damage0x40. Avoid map override precedence.','mots30-merged')
    emit('cog/luke_m.cog',transform_actor(base['cog/luke_m.cog'].decode('latin1').replace('\r\n','\n')).replace('\n','\r\n').encode('latin1'),
         'Native Luke gains Talisman checks and JK3.1 blindness while preserving MotS defense/server multipliers.','mots30-merged')

    for name,data in generated.items():
        target = out/name
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
    # Exact ownership directory only; reject stale outputs so callers never pick
    # up an accidentally retained member from an older reconciliation.
    stale = set(read_tree(out))-set(generated)
    assert not stale, f'Stale reconciliation members: {sorted(stale)}'
    report = dict(schema=1, scope='Static source reconciliation; not retail execution or connected multiplayer proof.',
                  base_registry_rows=len(base_rows), merged_registry_rows=len(rows),
                  base_unique_models=len(existing), merged_unique_models=len({r['model'] for r in rows}),
                  added_models=missing, class_counts=dict(Counter(str(r['personality']) for r in rows)),
                  preserved_original_rows=True, preserved_mots_only_resources=len(set(base)-set(new)),
                  original_duplicate_labels=[dict(ordinal=i,label=r['source_label']) for i,r in enumerate(base_rows) if i!=r['source_label']],
                  stock_defense_evidence=dict(archive=str(stock),member='cog/force_defense.cog',sha256=sha(stock_defense),
                                              formula='damage * (1 - rank * 0.125)',
                                              sbx_original='damage * (rank * 0.25)', corrected='damage * (1 - rank * 0.25)',
                                              returned_fraction_by_rank=[1,.75,.5,.25,0]),
                  native_shield_evidence=dict(member='cog/pow_supershield.cog',sha256=sha(native_shield),
                                              duration_seconds=20,actor_invulnerability_flag=8,thing_magnetic_flag=4,
                                              changes='Guard only two magnetic-bit clears against active bin153; Talisman cleanup separately guards active bin62.'),
                  delta_dispositions=dispositions, reverse_removal_dispositions=reverse_dispositions,
                  emitted_members=list(manifest.values()),
                  dependency_unresolved=unresolved,
                  local_owned_dependencies=dict(
                     jk_audio=sum(m['source']=='owned-jk-retail-local-only' and m['path'].endswith('.wav') for m in manifest.values()),
                     jk_icons=sum(m['source']=='owned-jk-retail-local-only' and m['path'].endswith('.bm') for m in manifest.values()),
                     mots_derived_cogs=sum(m['source']=='owned-mots-retail-derived-local-only' for m in manifest.values())),
                  native_model_repairs=[dict(path='3do/plorobe.3do',source_sha256=sha(plorobe),output_sha256=sha(repaired_plorobe),
                     change='Hierarchy node15 (k_head) child19 -> -1 only; all other bytes unchanged.',
                     evidence='Node15 declares zero children; node19 parent is12 (k_rhand), whose child is19. MotS3.0 node15 child is-1.')],
                  integration_hooks=dict(actors='Call transform_actor after dual edits for kyle_m.cog and mara_m.cog. luke_m.cog is emitted here.',
                     items='Call transform_items on final MotS items.dat (adds Talisman153 and inventory-only ObjectThrow154).',
                     static='Call transform_static on final MotS static.jkl (adds optional Talisman and namespaced native Destruction templates).',
                     strings='Call transform_strings if dual UI modifications supersede this module; it adds only COG_00153/154 labels and increments MSGS allocation.'),
                  feature_dispositions=[
                    dict(feature='Copyright date, multiplayer background, general hotkey wording',disposition='Preserve MotS interface; original JK3.1 documentation retained.'),
                    dict(feature='Move field light/goggles/saber controls to inventory',disposition='JK-specific control budget workaround; preserve native MotS controls and bins.'),
                    dict(feature='Neutral bonus Push/Throw; restore Speed and object Throw',disposition='Native MotS Push, saber Throw and Speed retained with native class/rank contract. Object Throw added as inventory item154 without a new hotkey; native powers remain assigned.'),
                    dict(feature='Sith Talisman',disposition='Included as optional sbxd_talisman pickup and bin153; native Super Shield62 remains available. Actor/item/template hooks must be called by assembly.'),
                    dict(feature='Dark/Light Surge only refill mana; Power Boost15seconds',disposition='Preserve MotS native Surge and30secondPowerBoost balance; JK balance reductions remove existing capability and are not applied globally.'),
                    dict(feature='13missing skins and29shared revised skins, texture mipmap repairs',disposition='Included; all676native registry rows preserved plus52new class-tagged rows. Solomon remains alongside Mikos. Imported plorobe head child link repaired to native -1; all other source bytes retained.'),
                    dict(feature='Sith and single-saber audio, hit audio, soundclass variety',disposition='Included actual JK3.0-to3.1 asset differences; missing retail sound dependencies derived locally.'),
                    dict(feature='Explosion06/07 retouch',disposition='Preserve different MotS-specific explosion originals rather than silently replace target-specific audio.'),
                    dict(feature='Force Push rumble / Jump slowing cue',disposition='Native Jump sound updated; native Push logic retained. Shared sound/forcepush.wav is already in MotS SBX3.'),
                    dict(feature='Force Throw rapid-fire/cost change',disposition='Ported as bin154 inventory-only object Throw, press/release targeting, native Jedi rank capped4, cost30/50/80/80,2secondcooldown, bubble/EWEB/death cancellation. Own JK icons derived locally.'),
                    dict(feature='Inventory and Saber Throw icons',disposition='JK bin-specific interface assets retained in source; native MotS control layout preserved.'),
                    dict(feature='Force Destruction self damage',disposition='Native MotS explosion flags0x53 become0x13, clearing only no-shooter-damage0x40. Native damage/radii0.5/1/1.5/2 retained. Namespaced projectile/explosion/cloud templates and COG references avoid map-definition precedence.'),
                    dict(feature='Stronger/shorter Blinding',disposition='transform_actor ports252/270/252effect and4+rankduration while retaining native MotS server and defense multipliers.'),
                    dict(feature='Sith blocking trails, disabled-trails throwing, quicksave stance repairs, saber priorities',disposition='Weapon/controller deltas delegated to main dual builder; not claimed complete by this module.'),
                    dict(feature='MotS Force Defense inversion',disposition='Fixed from rank*.25 to1-rank*.25; exact stock source independently supports decreasing-damage direction, original stock strength is.125.'),
                    dict(feature='MotS Bryar autoselection',disposition='Fixed incorrect inventory bin2 lookup to GetWeaponBin(2), which is bin122 in native MotS; priority and all other behavior preserved.'),
                    dict(feature='JK3.1 IR goggles brightness',disposition='Port EnableIRMode brightness0.3to1.0; native controls, battery and newplayer cleanup preserved.'),
                    dict(feature='JK3.1 Force Push deltas',disposition='Port Jedi-potential costs30/50/60, invulnerable-actor exclusion and Dark/Light Surge cost exemptions. Native bin38, Force-power rank, range,120*rank force and actor/player-only target scope retained. Explicit player/Talisman immunity and single-step iteration repair prevent rejected targets from bypassing the filter.'),
                  ])
    audit = root/'audit'
    audit.mkdir(parents=True,exist_ok=True)
    (audit/'reconciliation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    owned=[m for m in manifest.values() if m['source']=='owned-jk-retail-local-only']
    md=['# SBX native MotS reconciliation audit','',report['scope'],'',
        f'- Registry: {len(base_rows)} preserved rows plus {len(rows)-len(base_rows)} added rows = {len(rows)}; {len(existing)} native unique models become {report["merged_unique_models"]}.',
        '- All native row order, sound choices and class roles are retained; textual index typos are repaired without reordering.',
        '- Imported plorobe.3do keeps the JK3.1 revision with one hierarchy repair: head node15 child19 becomes-1, matching its zero children and the native MotS source. Every other model byte is retained.',
        f'- MotS-only resources preserved: {report["preserved_mots_only_resources"]}. No base-only file is deleted.',
        f'- JK3.0 removals in3.1: {len(reverse_dispositions)} individually accounted for; native copies, exact relocated materials, native extended-saber equivalent, and retained original Force Halt audio.',
        f'- Reconciliation emits {len(generated)} changed/additional members. Local retail dependencies: {report["local_owned_dependencies"]["jk_audio"]} owned JK audio clips, {report["local_owned_dependencies"]["jk_icons"]} owned JK icons, and {report["local_owned_dependencies"]["mots_derived_cogs"]} adapted owned MotS COG. The portable builder derives these from the user\'s installation instead of distributing their bytes.',
        f'- Resource dependency closure: {len(unresolved)} unresolved references (models/materials/soundclasses with MotS resource and sound archives checked).','',
        '## Added skins','']
    md.extend('- '+row['model'] for row in missing)
    md.extend(['','## Feature dispositions','','| Feature | Disposition |','| --- | --- |'])
    md.extend(f'| {f["feature"]} | {f["disposition"]} |' for f in report['feature_dispositions'])
    md.extend(['','## JK3.0 content removed from JK3.1','','| Resource | Disposition |','| --- | --- |'])
    md.extend(f'| {f["path"]} | {f["disposition"]}: {f["reason"]} |' for f in reverse_dispositions)
    md.extend(['','## Assembly contract','','`build(root, out, stock, jk_res, jk_snd, mots_snd)` writes this layer. The root builder must call `transform_actor` for Kyle/Mara after its dual edits, `transform_items` on final inventory, `transform_static` on final templates, and `transform_strings` if later UI changes replace this module\'s table. Luke is already emitted with the actor changes.',
               '', 'The optional Talisman lasts 15 seconds, drains mana, applies magnetic sealing and blocks the listed Force effects. Its inventory helper keeps each local player\'s lifecycle separate from pickup ownership. Two minimal native Super Shield guards preserve magnetic sealing when the effects overlap; Talisman cleanup retains an active Super Shield and pre-existing non-shield sealing. Original retail behavior, save/load ownership and connected multiplayer remain runtime acceptance items.',
               '', 'Object Throw is selected with normal Inventory Next/Previous and activated by holding Inventory Use to aim, then releasing to throw visible debris at the highlighted actor. It has no new hotkey. Native Jedi rank is capped at four for its strength, with costs of 30/50/80/80 mana and a two-second cooldown. Native bubble events reach this inventory-only helper through the actor bridge; EWEB, blindness and death cancel or prevent activation.',
               '', 'Force Destruction uses namespaced projectile/explosion templates, retaining native MotS damage and radii while clearing only the explosion no-shooter-damage bit (0x40). This avoids relying on an override of episode-local template names. The original definitions were identical in 39 maps across the four owned MotS episode archives; see `reconciliation-destruction-evidence.json`.','',
               'Force Defense stock evidence: `cog/force_defense.cog` SHA-256 `'+sha(stock_defense)+'`; stock formula `1-rank*0.125`, SBX original `rank*0.25`, corrected `1-rank*0.25`. This is an explicit preservation of SBX strength with native direction, not an unmodified stock restoration.',''])
    (audit/'reconciliation.md').write_text('\n'.join(md),encoding='utf-8')
    assert not unresolved, f'Unresolved asset dependencies: {unresolved}'
    return report

def build(root, out, stock=DEFAULT_STOCK, jk_res=None, jk_snd=DEFAULT_JK_SOUNDS, mots_snd=None):
    """Portable builder entry point; stock is used for verification, never copied."""
    return reconcile(root,out,stock,jk_snd,mots_snd,jk_res or DEFAULT_JK_RES)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--out',type=Path)
    parser.add_argument('--stock',type=Path,default=DEFAULT_STOCK)
    parser.add_argument('--jk-sounds',type=Path,default=DEFAULT_JK_SOUNDS)
    args=parser.parse_args()
    report=reconcile(args.root,args.out,args.stock,args.jk_sounds)
    print(json.dumps({k:report[k] for k in ('base_registry_rows','merged_registry_rows','merged_unique_models','class_counts')}))
    print('Emitted',len(report['emitted_members']),'members; dependencies unresolved',len(report['dependency_unresolved']))

if __name__ == '__main__':
    main()
