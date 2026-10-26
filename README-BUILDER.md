# SBX MotS Dual Sabers — Special Edition v1.2.0 builder

This produces two complete single-GOO editions from explicit historical mods and owned JK/MotS data. Those archives are build inputs only: a player needs the finished GOO and ordinary MotS, with no separate SBX 3.0/3.1 installation.

Current gameplay acceptance belongs to `STANDALONE-VALIDATION.md`. The builder performs static checks, not gameplay tests. Generated workload must live outside Git checkouts.

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

The bundled `assets/ui/bkmain.bm` is embedded unchanged. Pillow and image generation are not ordinary build requirements. Optional `--ui-bitmap` accepts a prepared native replacement subject to the same header, palette and title-region checks. `tools/native_ui_bitmap.py` is an artwork-authoring tool requiring Pillow, not part of ordinary rebuilding. Keep the bundled asset and encoding receipt in place.

## Output and installation

- `standalone/accelerated/SBX-MotS-Dual.goo`: complete original-texture edition.
- `standalone/software/SBX-MotS-Dual.goo`: complete indexed-texture alternative.
- Each edition has `PACKAGE-MANIFEST.json` and `SHA256SUMS.txt`, recording member origins/hashes, effective-layer equality and full-package file-reference closure against stock MotS alone.
- `standalone/STANDALONE-RESULT.json`: packaging/install receipt.
- `local-mod/SBX-Dual/SBX-MotS-Dual.goo`: convenience copy of the complete accelerated edition; no separate SBX archive or loose overlay.
- `ready/` and `ready-software-textures/`: intermediate overlay archives and source/generation reports.
- `sources/`, `generated/` and `audit/`: reproduction inputs/intermediates; not the installation or public delivery.

Create a fresh empty `<MotS game folder>/expansions/SBX-Dual` and copy the selected edition's **single GOO** into it. Run `JKM.EXE -path expansions/SBX-Dual` from the game directory. Do not stack editions or add old SBX archives/loose overlays. Preserve old installs separately. To change renderer editions, use a fresh folder with the other complete GOO.

The accelerated edition retains original textures. The software edition folds in 193 indexed MAT overrides; native lighting can shift hues in dim sectors. Neither edition modifies the executable or includes complete retail game archives. The release ZIPs retain original companion documents; full conversion inputs and private runtime fixtures are excluded.

## Features and controls

- **Dual sabers:** equip the Sith lightsaber and use SBX's existing **Lightsaber Stance** action. The cycle is **staff → Sariss → dual/Boc → reverse grip → staff**. No twenty-first action key is added. The retail conversion uses locally prepared KEY files and player-model variants instead of requiring the browser engine's runtime conversion.
- **Reverse grip (v1.1.0):** both sabers blade-down, each blade leaving the little-finger side of the fist. Its stand, attacks (standing, moving forward, left, right and back, and turning fast), second-fire hop and spin, and dash come from SBX Dual Sabers 17, prepared locally like Boc's. The original executable can't turn a hilt round, so the stance's persistent upper idle (`rt_rgupper.key`) also turns both grip anchors end over end about the hilt's middle; positions come from SBX Kyle and fit 175 of the 178 models within 0.0001 units (the other three within 0.000708).
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

Every multiplayer participant should use the same complete GOO edition and version. Connected multiplayer, host/client synchronization, respawn, custom skins outside the merged registry, custom episodes, and compatibility with other resource-changing mods are separate acceptance cases. The supplied browser add-on's statements about joining an unmodified SBX game do not establish that behavior for this retail MotS conversion.

**Current QA:** see `STANDALONE-VALIDATION.md`. Historical v1.0/v1.1 results are preserved separately and are not fresh validation of this edition.
