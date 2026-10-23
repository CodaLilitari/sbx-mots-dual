# SBX native MotS reconciliation audit

Static source reconciliation; not retail execution or connected multiplayer proof.

- Registry: 676 preserved rows plus 52 added rows = 728; 165 native unique models become 178.
- All native row order, sound choices and class roles are retained; textual index typos are repaired without reordering.
- Imported plorobe.3do keeps the JK3.1 revision with one hierarchy repair: head node15 child19 becomes-1, matching its zero children and the native MotS source. Every other model byte is retained.
- MotS-only resources preserved: 208. No base-only file is deleted.
- JK3.0 removals in3.1: 30 individually accounted for; native copies, exact relocated materials, native extended-saber equivalent, and retained original Force Halt audio.
- Reconciliation emits 355 changed/additional members. Local retail dependencies: 40 owned JK audio clips, 2 owned JK icons, and 1 adapted owned MotS COG. The portable builder derives these from the user's installation instead of distributing their bytes.
- Resource dependency closure: 0 unresolved references (models/materials/soundclasses with MotS resource and sound archives checked).

## Added skins

- adigalliac.3do
- angel.3do
- angel2.3do
- bartender.3do
- callista.3do
- hal.3do
- luuz.3do
- mara.3do
- jkcmikos.3do
- obiwan2c.3do
- tokohikaru.3do
- yarah.3do
- yoda.3do

## Feature dispositions

| Feature | Disposition |
| --- | --- |
| Copyright date, multiplayer background, general hotkey wording | Preserve MotS interface; original JK3.1 documentation retained. |
| Move field light/goggles/saber controls to inventory | JK-specific control budget workaround; preserve native MotS controls and bins. |
| Neutral bonus Push/Throw; restore Speed and object Throw | Native MotS Push, saber Throw and Speed retained with native class/rank contract. Object Throw added as inventory item154 without a new hotkey; native powers remain assigned. |
| Sith Talisman | Included as optional sbxd_talisman pickup and bin153; native Super Shield62 remains available. Actor/item/template hooks must be called by assembly. |
| Dark/Light Surge only refill mana; Power Boost15seconds | Preserve MotS native Surge and30secondPowerBoost balance; JK balance reductions remove existing capability and are not applied globally. |
| 13missing skins and29shared revised skins, texture mipmap repairs | Included; all676native registry rows preserved plus52new class-tagged rows. Solomon remains alongside Mikos. Imported plorobe head child link repaired to native -1; all other source bytes retained. |
| Sith and single-saber audio, hit audio, soundclass variety | Included actual JK3.0-to3.1 asset differences; missing retail sound dependencies derived locally. |
| Explosion06/07 retouch | Preserve different MotS-specific explosion originals rather than silently replace target-specific audio. |
| Force Push rumble / Jump slowing cue | Native Jump sound updated; native Push logic retained. Shared sound/forcepush.wav is already in MotS SBX3. |
| Force Throw rapid-fire/cost change | Ported as bin154 inventory-only object Throw, press/release targeting, native Jedi rank capped4, cost30/50/80/80,2secondcooldown, bubble/EWEB/death cancellation. Own JK icons derived locally. |
| Inventory and Saber Throw icons | JK bin-specific interface assets retained in source; native MotS control layout preserved. |
| Force Destruction self damage | Native MotS explosion flags0x53 become0x13, clearing only no-shooter-damage0x40. Native damage/radii0.5/1/1.5/2 retained. Namespaced projectile/explosion/cloud templates and COG references avoid map-definition precedence. |
| Stronger/shorter Blinding | transform_actor ports252/270/252effect and4+rankduration while retaining native MotS server and defense multipliers. |
| Sith blocking trails, disabled-trails throwing, quicksave stance repairs, saber priorities | Weapon/controller deltas delegated to main dual builder; not claimed complete by this module. |
| MotS Force Defense inversion | Fixed from rank*.25 to1-rank*.25; exact stock source independently supports decreasing-damage direction, original stock strength is.125. |
| MotS Bryar autoselection | Fixed incorrect inventory bin2 lookup to GetWeaponBin(2), which is bin122 in native MotS; priority and all other behavior preserved. |
| JK3.1 IR goggles brightness | Port EnableIRMode brightness0.3to1.0; native controls, battery and newplayer cleanup preserved. |
| JK3.1 Force Push deltas | Port Jedi-potential costs30/50/60, invulnerable-actor exclusion and Dark/Light Surge cost exemptions. Native bin38, Force-power rank, range,120*rank force and actor/player-only target scope retained. Explicit player/Talisman immunity and single-step iteration repair prevent rejected targets from bypassing the filter. |

## JK3.0 content removed from JK3.1

| Resource | Disposition |
| --- | --- |
| 3do/jkcsolomon.3do | preserved-native-base: Still supplied by SBX MotS3.0; overlay does not remove it. |
| 3do/mat/adihdfr.mat | preserved-native-base: Still supplied by SBX MotS3.0; overlay does not remove it. |
| 3do/mat/bensab1.mat | preserved-native-base: Still supplied by SBX MotS3.0; overlay does not remove it. |
| 3do/mat/draghdfr.mat | preserved-native-base: Still supplied by SBX MotS3.0; overlay does not remove it. |
| 3do/mat/kothchest.mat | preserved-native-base: Still supplied by SBX MotS3.0; overlay does not remove it. |
| 3do/mat/kunfacef.mat | preserved-native-base: Still supplied by SBX MotS3.0; overlay does not remove it. |
| 3do/mat/mcwchest.mat | preserved-native-base: Still supplied by SBX MotS3.0; overlay does not remove it. |
| 3do/mat/mcwfoot.mat | preserved-native-base: Still supplied by SBX MotS3.0; overlay does not remove it. |
| 3do/mat/mcwhip.mat | preserved-native-base: Still supplied by SBX MotS3.0; overlay does not remove it. |
| 3do/mat/mcwleg.mat | preserved-native-base: Still supplied by SBX MotS3.0; overlay does not remove it. |
| 3do/mat/mcwthigh.mat | preserved-native-base: Still supplied by SBX MotS3.0; overlay does not remove it. |
| 3do/mat/mwdarm.mat | preserved-native-base: Still supplied by SBX MotS3.0; overlay does not remove it. |
| 3do/mat/mwdback.mat | preserved-native-base: Still supplied by SBX MotS3.0; overlay does not remove it. |
| 3do/mat/mwdchest.mat | preserved-native-base: Still supplied by SBX MotS3.0; overlay does not remove it. |
| 3do/mat/mwdhip.mat | preserved-native-base: Still supplied by SBX MotS3.0; overlay does not remove it. |
| 3do/mat/mwdleg.mat | preserved-native-base: Still supplied by SBX MotS3.0; overlay does not remove it. |
| 3do/mat/mwdthigh.mat | preserved-native-base: Still supplied by SBX MotS3.0; overlay does not remove it. |
| 3do/mat/plorbchest.mat | preserved-native-base: Still supplied by SBX MotS3.0; overlay does not remove it. |
| 3do/mat/yunfacesd.mat | preserved-native-base: Still supplied by SBX MotS3.0; overlay does not remove it. |
| cog/weap_extsaber.cog | preserved-native-equivalent: Native MotS extended-saber COG retained and updated by weapon builder; JK bin variant is not installed. |
| mat/clear.mat | preserved-relocated-identical: Exact same bytes are provided at 3do/mat/clear.mat; both are standard material lookup locations. |
| mat/sblack.mat | preserved-relocated-identical: Exact same bytes are provided at 3do/mat/sblack.mat; both are standard material lookup locations. |
| sound/forcehalt.wav | include-jk30-only: Preserve removed3.0resource as additional optional content without assigning it over3.1orMotS. |
| sound/ltsaberhit03.wav | preserved-native-base: Still supplied by SBX MotS3.0; overlay does not remove it. |
| sound/ltsaberhit07.wav | preserved-native-base: Still supplied by SBX MotS3.0; overlay does not remove it. |
| sound/ltsaberhit14.wav | preserved-native-base: Still supplied by SBX MotS3.0; overlay does not remove it. |
| sound/theforce.wav | preserved-native-base: Still supplied by SBX MotS3.0; overlay does not remove it. |
| ui/bm/fospeed.bm | preserved-native-retail: Native MotS resource/sound archive supplies this path; retain target UI/audio. |
| ui/bm/icf_spe16.bm | preserved-native-retail: Native MotS resource/sound archive supplies this path; retain target UI/audio. |
| ui/bm/icf_spe8.bm | preserved-native-retail: Native MotS resource/sound archive supplies this path; retain target UI/audio. |

## Assembly contract

`build(root, out, stock, jk_res, jk_snd, mots_snd)` writes this layer. The root builder must call `transform_actor` for Kyle/Mara after its dual edits, `transform_items` on final inventory, `transform_static` on final templates, and `transform_strings` if later UI changes replace this module's table. Luke is already emitted with the actor changes.

The optional Talisman lasts 15 seconds, drains mana, applies magnetic sealing and blocks the listed Force effects. Its inventory helper keeps each local player's lifecycle separate from pickup ownership. Two minimal native Super Shield guards preserve magnetic sealing when the effects overlap; Talisman cleanup retains an active Super Shield and pre-existing non-shield sealing. Original retail behavior, save/load ownership and connected multiplayer remain runtime acceptance items.

Object Throw is selected with normal Inventory Next/Previous and activated by holding Inventory Use to aim, then releasing to throw visible debris at the highlighted actor. It has no new hotkey. Native Jedi rank is capped at four for its strength, with costs of 30/50/80/80 mana and a two-second cooldown. Native bubble events reach this inventory-only helper through the actor bridge; EWEB, blindness and death cancel or prevent activation.

Force Destruction uses namespaced projectile/explosion templates, retaining native MotS damage and radii while clearing only the explosion no-shooter-damage bit (0x40). This avoids relying on an override of episode-local template names. The original definitions were identical in 39 maps across the four owned MotS episode archives; see `reconciliation-destruction-evidence.json`.

Force Defense stock evidence: `cog/force_defense.cog` SHA-256 `27d065075417c0216f54677c00fec63af2fcb82ccd7e01accfbb068eb39b6ae3`; stock formula `1-rank*0.125`, SBX original `rank*0.25`, corrected `1-rank*0.25`. This is an explicit preservation of SBX strength with native direction, not an unmodified stock restoration.
