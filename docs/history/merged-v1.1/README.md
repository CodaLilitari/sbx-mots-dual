# SBX Dual Sabers for Mysteries of the Sith

**A retail-compatible add-on for SBX-MotS v3.0, converted and reconciled by Coda (Codex Lily) and Andrei.**

This brings the supplied SBX Dual Sabers add-on to original Mysteries of the Sith and carries compatible additions and fixes from SBX-JK 3.1 into the MotS version. It installs on top of **SBX-MotS v3.0**. You need your own MotS installation and the original `sbx-mots v3.goo`; the complete base mod and retail game archives are not included.

The main overlay contains 602 changed or additional game resources. It adds the dual/Boc stance through the existing Lightsaber Stance action, with two native glowing blades, ten colors and prepared dual variants for all 178 merged player models. The reconciliation retains MotS-only content, adds 13 missing skins and carries 29 shared model revisions. It also brings over compatible saber cleanup, trail, goggles and Force changes while preserving MotS's own weapon and Force contracts.

## v1.1.0: SBX Dual Sabers 17 (not packaged yet)

The tools in this repository's `tools/` folder now build v1.1.0 from **SBX Dual Sabers 17**. It adds a fourth Sith-saber stance, the **reverse grip** (both sabers blade-down, with its own stand, attacks, a hop and spin, and a dash), through the same Lightsaber Stance action: **staff → Sariss → dual/Boc → reverse grip → staff**. It also brings Dual Sabers 17's retimed attacks, its second heavy-cut fix and footstep sounds when walking in SBX's stances. The main overlay grows to 651 game resources. JKM.EXE has no engine support for the reverse grip, so the blades are turned by the stance's own idle animation; nothing else is added. See [CHANGES.md](CHANGES.md). v1.1.0 has run in OpenJKDF2's MotS mode but **not yet in the original JKM.EXE**; see [RETAIL-VALIDATION.md](RETAIL-VALIDATION.md). The downloads below are v1.0.0.

## Downloads

- [SBX-MotS-Dual-Overlay.zip](https://gitlab.com/api/v4/projects/codalilitari%2Fsbx-mots-dual/packages/generic/sbx-mots-dual/1%2E0%2E0/SBX-MotS-Dual-Overlay%2Ezip) — the ready-to-install add-on; requires SBX-MotS v3.0.
- [SBX-MotS-Software-Texture-Fix.zip](https://gitlab.com/api/v4/projects/codalilitari%2Fsbx-mots-dual/packages/generic/sbx-mots-dual/1%2E0%2E0/SBX-MotS-Software-Texture-Fix%2Ezip) — optional indexed-color overrides for the original software renderer. Install after the main overlay. Accelerated rendering and the browser's WebGL renderer should use the main overlay's original textures.
- [SBX-MotS-Dual-Builder.zip](https://gitlab.com/api/v4/projects/codalilitari%2Fsbx-mots-dual/packages/generic/sbx-mots-dual/1%2E0%2E0/SBX-MotS-Dual-Builder%2Ezip) — reproducible offline tools, pinned retarget implementation, helper, documentation and evidence. Building requires the specified source mods and your own game resources; these inputs are not included.

These are public documentation editions of the tested delivery. Their game resources and builder tools are unchanged; release notes, path references and package manifests have been updated for distribution. [SHA256SUMS.txt](https://gitlab.com/api/v4/projects/codalilitari%2Fsbx-mots-dual/packages/generic/sbx-mots-dual/1%2E0%2E0/SHA256SUMS%2Etxt) and [public-edition-receipt.json](https://gitlab.com/api/v4/projects/codalilitari%2Fsbx-mots-dual/packages/generic/sbx-mots-dual/1%2E0%2E0/public-edition-receipt%2Ejson) identify the exact public archives and their relationship to the tested originals.

## Retail installation and controls

1. Create an empty `expansions\SBX-Dual` folder inside your MotS installation.
2. Copy your original **SBX-MotS v3.0** `sbx-mots v3.goo` into it. The JK version of SBX is not a substitute.
3. Extract [SBX-MotS-Dual-Overlay.zip](https://gitlab.com/api/v4/projects/codalilitari%2Fsbx-mots-dual/packages/generic/sbx-mots-dual/1%2E0%2E0/SBX-MotS-Dual-Overlay%2Ezip) into the same folder. Its `3do`, `cog`, `jkl`, `mat`, `misc`, `sound`, `voice` and `ui` folders must sit directly beside the base GOO.
4. If using the original software renderer, extract the optional texture ZIP there **last**, replacing matching MAT files.
5. Start from the MotS game directory with `JKM.EXE -path expansions/SBX-Dual`.

Equip the Sith lightsaber and use the existing **Lightsaber Stance** action: **staff → Sariss → dual/Boc → staff**. Use third-person view to see both separate sabers; first person retains the staff presentation. Primary and alternate attacks use the twin-saber moves. No extra action hotkey is required.

Object Force Throw is available through Inventory Next/Previous and Inventory Use: hold to target a living actor, then release to throw nearby debris. The optional `sbxd_talisman` pickup is provided for custom-map placement; existing campaign pickups are preserved.

Keep SBX's save precaution: **turn the saber off before saving**. If a loaded saber loses damage, switch it off and on again.

## Browser MotS

Source inspection indicates that the overlay should also work in the MotS mode of [tristamus/OpenJKDF2](https://github.com/tristamus/OpenJKDF2). Load the MotS 3.0 base and put this overlay above it in the browser mod list so the overlay wins. The browser supports loose-folder/ZIP mods. Do **not** additionally load the original JK/browser Dual Sabers add-on: its runtime retarget recipe can override the prepared animations.

This exact overlay has **not been run in the browser**, and browser multiplayer is unverified. The supplied animations are ordinary native KEY files; there is no runtime retarget recipe, and the model attachment names avoid the browser's automatic extra-hilt branch. The optional software texture patch is not needed for WebGL.

## Validation and differences

The resources passed dependency, model, native COG contract and deterministic rebuild checks. Bounded tests used the original unmodified MotS executable under Wine/Xvfb, including both blades, real primary/alternate input, color changes, stance/lightsaber lifecycle, damage to a test actor, brighter goggles and representative software texture checks. Accelerated tests used llvmpipe rather than a physical GPU.

Retail dual mode uses native blade glows and full-duration attack cooldowns. It does not reproduce the browser add-on's extra mesh fans or overlapping attacks at 75% duration. Indexed software textures trade color precision for compatibility and can show dithering or native palette shifts in dim areas.

Connected multiplayer, complete campaign playthroughs, save/load, every skin/attack combination and every Force interaction remain unverified. Push activation and timer reset were observed, but its revised costs and physical effect were source-checked rather than demonstrated against an accepted runtime target. See `RETAIL-VALIDATION.md` for the exact evidence and remaining limits.

## Credits

MotS conversion, reconciliation, integration, tools and validation: **Coda (Codex Lily) and Andrei**. **ShadowX** created SBX; the supplied Dual Sabers readme credits **EAH_CL0wN's Sith Sabers** for several attack animations and states they were used with permission. That readme does not separately name its own add-on author, so we have not invented an attribution. **OpenJKDF2 contributors**, including the implementation recovered from **tristamus/OpenJKDF2**, supplied the pinned retarget code used by the offline baker. **LucasArts/Lucasfilm** and the original creators retain credit for the underlying games, Boc and source game assets.

The full SBX contributor credits, original readmes, permission statements and OpenJKDF2 license are included in every package. Their attribution and permission claims are preserved; this conversion does not claim new authorship or a blanket license over their work. This modification is not made, distributed or supported by LucasArts Entertainment Company.

## Repository contents

This repository contains release documentation, original attribution documents, curated validation evidence and, in `tools/`, the offline conversion tools and pinned helper (v1.1.0; the first commit adding them is v1.0.0's, byte for byte). The v1.0.0 tools are also in the [Builder ZIP](https://gitlab.com/api/v4/projects/codalilitari%2Fsbx-mots-dual/packages/generic/sbx-mots-dual/1%2E0%2E0/SBX-MotS-Dual-Builder%2Ezip). No retail game archive or complete SBX base mod is stored here. See [full credits](CREDITS.md) and [retail validation](RETAIL-VALIDATION.md). There is no new blanket license over inherited mod/game resources.

Release: **v1.0.0**, public documentation edition of the tested 2026-10-23 resources. [Standalone release writeup](https://gitlab.com/api/v4/projects/codalilitari%2Fsbx-mots-dual/packages/generic/sbx-mots-dual/1%2E0%2E0/release-writeup%2Emd).
