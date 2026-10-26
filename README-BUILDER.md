# SBX Dual Sabers for retail MotS — local overlay builder

This package builds a minimal local overlay for **Saber Battle X: Mysteries of the Sith v3.0** from the four specified mod releases and your owned Jedi Knight/MotS resources. The delivered resources passed static validation and a bounded original-executable test under Wine/Xvfb. See [RETAIL-VALIDATION.md](RETAIL-VALIDATION.md) for observed behavior and remaining limits. A successful rebuild establishes matching resources and static checks; it does not independently rerun gameplay tests.

This Builder ZIP contains build tools and documentation; the ready-to-install overlay is a separate download. It does not contain a complete SBX mod or a prebuilt collection of owned game data. The generated overlay contains only changed/additional files relative to SBX-MotS v3.0, while the separate local runnable folder also contains your unchanged base mod archive.

## Requirements

- 64-bit Windows with Python **3.11 or later**. The example uses the Windows Python launcher, `py -3`; check `py -3 --version` first. An explicit path to a suitable `python.exe` works too.
- The complete builder package, including its `tools` directory, pinned retarget source, supplied `dual-key-baker.exe`, its build receipt, and license files. Keep this layout intact.
- The four original mod ZIPs listed below, or the exact audited GOB/GOO payload from each ZIP.
- Your owned retail Jedi Knight `Res2.gob` and `Res1hi.gob`, and owned MotS `JKMRES.GOO` and `JKMSNDLO.GOO`.
- A new output directory. The builder refuses to overwrite an existing build directory.

Once these local inputs and Python are available, the build is offline. It requires no API key, network service, third-party Python package, installed C compiler, or game launch. It runs the included local headless animation helper; it does not alter a game executable. The helper is already built, so WSL and a compiler are not prerequisites for this procedure.

| Argument | Input |
| --- | --- |
| `--dual` | **SBX Dual Sabers 17**: `SBX Dual Sabers.gob` (SHA-256 `b0ad90b06fc76efd6641d286ff11a27c7f66b94db05c4b33a53fb1287f9e97e6`), or a ZIP holding exactly that GOB. v1.0.0 took the 22 October release instead. |
| `--jk30` | **SBX-JK v3.0**, downloaded as `1871-sbxjkv3.zip` |
| `--jk31` | **SBX-JK v3.1**, downloaded as `1887-sbxjkv31.zip` |
| `--mots30` | **SBX-MotS v3.0**, downloaded as `1866-sbx-motsv3.zip` |
| `--jk-res` | Jedi Knight `Resource\Res2.gob` — owned models/animations and other resources |
| `--jk-snd` | Jedi Knight `Resource\Res1hi.gob` — owned audio and UI dependencies |
| `--mots-res` | MotS `Resource\JKMRES.GOO` |
| `--mots-snd` | MotS `Resource\JKMSNDLO.GOO` |
| `--output` | A new directory for your local build |

The four mod payloads are checked against pinned SHA-256 values. ZIP filenames may differ, but each ZIP must contain exactly one GOB/GOO, and its payload must match the audited release. Renaming another version does not make it compatible. The game archive arguments are explicit; the builder does not search your computer for installations.

## Build in PowerShell

Open PowerShell in the unpacked builder directory. Replace the example paths with the locations of your files. Use a new output directory for each attempt.

```powershell
py -3 --version

$buildArgs = @(
    '--dual',     'C:\ModInputs\SBX Dual Sabers.gob',
    '--jk30',     'C:\ModInputs\1871-sbxjkv3.zip',
    '--jk31',     'C:\ModInputs\1887-sbxjkv31.zip',
    '--mots30',   'C:\ModInputs\1866-sbx-motsv3.zip',
    '--jk-res',   'C:\Games\Jedi Knight\Resource\Res2.gob',
    '--jk-snd',   'C:\Games\Jedi Knight\Resource\Res1hi.gob',
    '--mots-res', 'C:\Games\MotS\Resource\JKMRES.GOO',
    '--mots-snd', 'C:\Games\MotS\Resource\JKMSNDLO.GOO',
    '--output',   'C:\ModBuilds\SBX-Dual-local-01'
)
py -3 '.\tools\build_overlay.py' @buildArgs
```

The final console result should report `BUILT_AND_STATIC_CHECKED`. Check `BUILD-RESULT.json` and `ready\static-validation.json` in the output. If the build stops, retain its reports and resolve the reported input or validation problem before installing anything. Use another new output name for the next attempt; an incomplete directory is not a finished package.

## What the output contains

| Path under your output directory | Purpose |
| --- | --- |
| `ready\overlay\` | Minimal loose overlay: changed/additional files only; byte-identical SBX-MotS base members are omitted |
| `ready\SBX-MotS-Dual-Overlay.goo` | A generated archive of that same overlay, retained for inspection; the installation below uses loose files |
| `ready\manifest.json` | Member hashes and assembly reasons |
| `ready\static-validation.json` | Static acceptance report for this assembled candidate |
| `ready-software-textures\overlay\` | Optional indexed-color MAT overrides for the original software renderer; apply after the main overlay |
| `ready-software-textures\software-textures.json` | Per-texture source/output hashes, conversion details and repaired mip chains |
| `local-mod\SBX-Dual\` | Convenience folder containing the loose overlay **and your unchanged SBX-MotS v3.0 GOO**, ready for a local installation |
| `input-receipt.json` and `BUILD-RESULT.json` | Input identities and final build status |
| `audit\`, `generated\`, `sources\` | Source reconciliation, generation receipts, intermediate resources and extracted local inputs |

**The complete build tree is not the public release.** The separately packaged main overlay and optional texture layer contain only their defined changed/additional resources; the Builder ZIP contains tools and documentation. Keep source archives, extracted inputs, private runtime fixtures and the convenience folder's unchanged full base mod out of release packages. Copied or adapted assets retain their source attribution; see [CREDITS.md](CREDITS.md) and the unmodified original documents for provenance and permission statements. The public documentation edition preserves the tested tools byte-for-byte. Historical workstation fallback paths in internal tools are retained for source identity; the documented command supplies all game inputs explicitly.

## Install the local build

1. Use a separate, initially empty mod folder: `<MotS game folder>\expansions\SBX-Dual`.
2. Copy the contents of your completed `local-mod\SBX-Dual` folder into it. Alternatively, copy the original SBX-MotS v3.0 GOO into that empty folder, then copy the contents of `ready\overlay` alongside the GOO.
3. Confirm that the GOO sits beside the loose `cog`, `3do`, `misc`, `jkl`, and other generated directories. Do not create an extra `overlay` directory between the mod folder and those resources.
4. Start MotS from its game directory with this path:

```powershell
Set-Location -LiteralPath 'C:\Games\MotS'
& '.\JKM.EXE' -path 'expansions/SBX-Dual'
```

The loose resources provide the override layer above the unchanged base GOO. This layout avoids depending on ordering between two GOO archives. Do not also copy `SBX-MotS-Dual-Overlay.goo` into this loose-file installation, and do not mix the original JK Dual Sabers GOB or unrelated mod overrides into it. The builder itself does not install files into your game directory.

For **software rendering**, copy the contents of `ready-software-textures\overlay` into that same mod folder last. These overrides convert the winning 16-bit SBX textures to indexed color using entries shared by the stock MotS map palettes, including animated materials and mipmaps. The main overlay retains the original textures for accelerated rendering, with append-only repairs to two incomplete mip chains. Native indexed lighting can shift hues in dark sectors; for example, Yoda's olive tones become browner under the original MotS lighting table. This patch fixes software-format corruption without recoloring the original artwork or changing level colormaps. To return to the original textures, assemble a fresh empty mod folder from the unchanged base GOO and the main overlay; this avoids accidentally leaving software overrides in place.

To play without this mod, launch MotS without this `-path` argument. Keep the generated build separate from your game installation so its receipts and hashes remain available for diagnosis.

## Features and controls

- **Dual sabers:** equip the Sith lightsaber and use SBX's existing **Lightsaber Stance** action. The cycle is **staff → Sariss → dual/Boc → reverse grip → staff**. No twenty-first action key is added. The retail conversion uses locally prepared KEY files and player-model variants instead of requiring the browser engine's runtime conversion.
- **Reverse grip (v1.1.0):** both sabers blade-down, each blade leaving the little-finger side of the fist. Its stand, attacks (standing, moving forward, left, right and back, and turning fast), second-fire hop and spin, and dash come from SBX Dual Sabers 17, prepared locally like Boc's. The original executable can't turn a hilt round, so the stance's persistent upper idle (`rt_rgupper.key`) also turns both grip anchors end over end about the hilt's middle; positions come from SBX Kyle and fit 175 of the 178 models within 0.0001 units (the other three within 0.0007).
- **Footsteps (v1.1.0):** SBX's 23 walk, walk-back and strafe keys get the original game's footstep markers back from Dual Sabers 17's `misc/keymarkers.dat`, as do the walks prepared for both two-saber stances. Only marker sections change.
- **View:** use third-person view to see the two separate sabers. The first-person weapon view retains the existing staff presentation.
- **Retail blade rendering:** dual mode uses two visible native saber polylines and separate hilts. The browser extension's duplicated mesh glow/fan is unavailable in the original executable, so dual mode has the native blade appearance and no mesh fan trails. The original staff, single and long saber mesh fans remain. Seven dual colors use original MotS materials; light-blue, dark-purple and silver use documented palette remaps.
- **Attacks:** primary fire uses the supplied stance and movement-dependent attacks; secondary fire uses the heavy cut. Retail permits only a limited number of simultaneous animation tracks, so the conversion waits for an attack's **full key duration** before another attack. It also checks failed animation allocation before resetting a hit list. This intentionally differs from the browser add-on's overlapping attacks at 75% of the duration; the original executable was exercised with both attack buttons, but every attack on every skin has not been tested.
- **Skins:** the merge retains all original MotS registry rows and class roles, adds **13 missing JK3.1 skins**, and brings forward **29 shared revised skins**. Solomon remains available alongside Mikos. The registry grows from 676 to 728 rows, with 178 unique models. The imported Plo Koon robe model includes a one-field repair to its inconsistent head-child link; its other JK3.1 bytes are preserved.
- **Force Throw (objects):** select this item with ordinary **Inventory Next/Previous**, hold **Inventory Use** to aim at a living target, then release to throw visible nearby debris. It has no added hotkey and does not replace native MotS Force powers. It requires Jedi potential and mana, uses costs of 30/50/80/80 by capped rank, and has a two-second cooldown. Bubble, EWEB, blindness and death handling are included in the source adaptation.
- **Sith Talisman:** the optional `sbxd_talisman` pickup provides the 15-second Force-immunity/magnetic-seal effect and drains mana; physical objects thrown with Force Throw remain a threat. It is exposed for explicit spawning or custom-map placement. Existing stock-map Super Shield pickups are **not replaced**; Super Shield remains available. The template's availability does not mean it has been placed into a campaign map.
- **Preserved MotS systems:** native weapons, Force powers, ranks, classes, inventory assignments and campaign-specific scripts remain the base. Compatible JK3.1 audio, model and script improvements are merged selectively. Native Surge/Power Boost behavior is preserved rather than globally applying JK3.1's shorter balance settings. Source decisions, reverse removals and individual inclusions are recorded in `audit\reconciliation.json`.

The build also repairs the SBX MotS Force Defense multiplier direction and Bryar autoselection inventory lookup, and provides namespaced native Destruction templates that allow shooter self-damage. These are source-level changes documented in the audit; they are not a claim that every resulting interaction has passed original-retail testing.

## Save/load and compatibility limits

The SBX3.1 documentation reports that saving with a saber ignited can restore the default stance and leave damage inactive on load. Preserve the established precaution: **turn the saber off before saving**. If a loaded saber lacks damage, turn it off and on again. This conversion retains that inherited precaution; save/load validation for the new stance has not been completed.

Every multiplayer participant should use the same assembled overlay and base release. Connected multiplayer, host/client synchronization, respawn, custom skins outside the merged registry, custom episodes, and compatibility with other resource-changing mods are separate acceptance cases. The supplied browser add-on's statements about joining an unmodified SBX game do not establish that behavior for this retail MotS conversion.

**QA status (v1.1.0):** the tools here rebuild the same v1.1.0 overlay from the same inputs and pass the static checks; v1.1.0 has run in OpenJKDF2's MotS mode but not yet in the original executable (see `RETAIL-VALIDATION.md`). **QA status (v1.0.0):** public documentation edition of the final tested delivery, with bounded native-executable validation. The exact final archive was reproduced from the portable builder. Static receipts, runtime scope, and untested cases are retained in `RETAIL-VALIDATION.md` and `docs/audit/`. Connected multiplayer and complete campaign acceptance remain unverified.
