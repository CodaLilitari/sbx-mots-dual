# SBX Dual Sabers for Mysteries of the Sith

**A retail-compatible add-on for SBX-MotS v3.0, converted and reconciled by Coda (Codex Lily) and Andrei.**

This brings the supplied SBX Dual Sabers add-on to original Mysteries of the Sith and carries compatible additions and fixes from SBX-JK 3.1 into the MotS version. It installs on top of **SBX-MotS v3.0**. You need your own MotS installation and the original `sbx-mots v3.goo`; the complete base mod and retail game archives are not included.

The v1.1.0 main overlay contains 651 changed or additional game resources. It adds two stances to the Sith lightsaber through the existing Lightsaber Stance action, Boc's dual sabers and the reverse grip from SBX Dual Sabers 17, with two native glowing blades, ten colors and prepared dual variants for all 178 merged player models. The reconciliation retains MotS-only content, adds 13 missing skins and carries 29 shared model revisions. It also brings over compatible saber cleanup, trail, goggles and Force changes while preserving MotS's own weapon and Force contracts.

## Downloads

- **SBX-MotS-Dual-Overlay.zip** — the ready-to-install add-on; requires SBX-MotS v3.0.
- **SBX-MotS-Software-Texture-Fix.zip** — optional indexed-color overrides for the original software renderer. Install after the main overlay. Accelerated rendering and the browser's WebGL renderer should use the main overlay's original textures.
- **SBX-MotS-Dual-Builder.zip** — reproducible offline tools, pinned retarget implementation, helper, documentation and evidence. Building requires the specified source mods and your own game resources; these inputs are not included.

The v1.0.0 packages were public documentation editions of the tested delivery, with their game resources and builder tools unchanged. `SHA256SUMS.txt` and `public-edition-receipt.json` identify the exact public archives and their relationship to the tested originals.

## Retail installation and controls

1. Create an empty `expansions\SBX-Dual` folder inside your MotS installation.
2. Copy your original **SBX-MotS v3.0** `sbx-mots v3.goo` into it. The JK version of SBX is not a substitute.
3. Extract **SBX-MotS-Dual-Overlay.zip** into the same folder. Its `3do`, `cog`, `jkl`, `mat`, `misc`, `sound`, `voice` and `ui` folders must sit directly beside the base GOO.
4. If using the original software renderer, extract the optional texture ZIP there **last**, replacing matching MAT files.
5. Start from the MotS game directory with `JKM.EXE -path expansions/SBX-Dual`.

Equip the Sith lightsaber and use the existing **Lightsaber Stance** action: **staff → Sariss → dual/Boc → reverse grip → staff**. Use third-person view to see both separate sabers; first person retains the staff presentation. Primary and alternate attacks use the twin-saber moves. In the reverse grip both sabers are held blade-down: primary attacks depend on how you move, alternate fire is a hop with a whole turn in the air, and running flat out for about half a second breaks into a dash. No extra action hotkey is required.

Object Force Throw is available through Inventory Next/Previous and Inventory Use: hold to target a living actor, then release to throw nearby debris. The optional `sbxd_talisman` pickup is provided for custom-map placement; existing campaign pickups are preserved.

Keep SBX's save precaution: **turn the saber off before saving**. If a loaded saber loses damage, switch it off and on again.

## Browser MotS

Source inspection indicates that the overlay should also work in the MotS mode of [tristamus/OpenJKDF2](https://github.com/tristamus/OpenJKDF2). Load the MotS 3.0 base and put this overlay above it in the browser mod list so the overlay wins. The browser supports loose-folder/ZIP mods. Do **not** additionally load the original JK/browser Dual Sabers add-on: its runtime retarget recipe can override the prepared animations.

v1.1.0 ran in the site's OpenJKDF2 MotS mode (8ccc356c) for the checks in `RETAIL-VALIDATION.md`; browser multiplayer is unverified. The supplied animations are ordinary native KEY files; there is no runtime retarget recipe, and the model attachment names avoid the browser's automatic extra-hilt branch. The optional software texture patch is not needed for WebGL.

## Validation and differences

v1.1.0 passed the same static and deterministic rebuild checks and ran in OpenJKDF2's MotS mode, but **has not yet been run in the original executable**. For v1.0.0, the resources passed dependency, model, native COG contract and deterministic rebuild checks, and bounded tests used the original unmodified MotS executable under Wine/Xvfb, including both blades, real primary/alternate input, color changes, stance/lightsaber lifecycle, damage to a test actor, brighter goggles and representative software texture checks. Accelerated tests used llvmpipe rather than a physical GPU.

Retail dual mode uses native blade glows and full-duration attack cooldowns. It does not reproduce the browser add-on's extra mesh fans or overlapping attacks at 75% duration. Indexed software textures trade color precision for compatibility and can show dithering or native palette shifts in dim areas.

Connected multiplayer, complete campaign playthroughs, save/load, every skin/attack combination and every Force interaction remain unverified. Push activation and timer reset were observed, but its revised costs and physical effect were source-checked rather than demonstrated against an accepted runtime target. See `RETAIL-VALIDATION.md` for the exact evidence and remaining limits.

## Credits

MotS conversion, reconciliation, integration, tools and validation: **Coda (Codex Lily) and Andrei**. **ShadowX** created SBX; the supplied Dual Sabers readme credits **EAH_CL0wN's Sith Sabers** for several attack animations and states they were used with permission. That readme does not separately name its own add-on author, so we have not invented an attribution. **OpenJKDF2 contributors**, including the implementation recovered from **tristamus/OpenJKDF2**, supplied the pinned retarget code used by the offline baker. **LucasArts/Lucasfilm** and the original creators retain credit for the underlying games, Boc and source game assets.

The full SBX contributor credits, original readmes, permission statements and OpenJKDF2 license are included in every package. Their attribution and permission claims are preserved; this conversion does not claim new authorship or a blanket license over their work. This modification is not made, distributed or supported by LucasArts Entertainment Company.
