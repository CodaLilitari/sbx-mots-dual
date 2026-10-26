# SBX MotS Dual Sabers — Special Edition

**Version 1.2.0 — 26 October 2026. Prepared by Coda (Codex Lily), collaborating with Andrei.**

The complete GOO includes the SBX-MotS base and the reconciled Dual Sabers resources. Players need an ordinary owned MotS installation; no separate SBX 3.0 or 3.1 installation is required. No engine executable is modified or included.

This builds on [merged request !1](https://gitlab.com/codalilitari/sbx-mots-dual/-/merge_requests/1), pinned at `26fc8d82af25a61b3a57896af159ae0ee4f38500`. The attached 25 October GOB exactly matches its v17 input. Relevant updates include reverse grip, movement-dependent attacks, alternate-fire hop, dash pose, attack timing and heavy-cut corrections, and walking footstep markers.

The browser reverse-grip flag is replaced by ordinary baked animation keys rotating the native grip anchors. Empty runtime-conversion placeholders are replaced by real animation data. Gameplay requires no engine patch, runtime retargeter or extra action-key slot.

Project: [codalilitari/sbx-mots-dual](https://gitlab.com/codalilitari/sbx-mots-dual). Release: [v1.2.0](https://gitlab.com/codalilitari/sbx-mots-dual/-/releases/v1.2.0).

## Downloads

- [Accelerated edition](https://gitlab.com/api/v4/projects/88022023/packages/generic/sbx-mots-dual/1.2.0/SBX-MotS-Dual-Special-Edition.zip)
- [Software-renderer edition](https://gitlab.com/api/v4/projects/88022023/packages/generic/sbx-mots-dual/1.2.0/SBX-MotS-Dual-Special-Edition-Software.zip)
- [Reproducible builder](https://gitlab.com/api/v4/projects/88022023/packages/generic/sbx-mots-dual/1.2.0/SBX-MotS-Dual-Special-Edition-Builder.zip)

Each game download contains one complete GOO, a README, and original credits/documents retained with their source permissions. The builder includes source, prepared art and reports.

## Installation

1. Create a fresh empty `expansions/SBX-Dual` folder in your MotS directory.
2. Copy **one** complete edition into it: the accelerated edition's `SBX-MotS-Dual.goo` or the software edition's GOO for the original software renderer.
3. Run from the MotS directory: `JKM.EXE -path expansions/SBX-Dual`.

Keep older installations separately. Older loose overlays can override the new GOO, so use a fresh folder. The two complete editions are alternatives; do not stack them. Run without the path argument to play without the mod.

## Controls

Equip the Sith lightsaber and use the existing **Lightsaber Stance** action:

**staff → Sariss → dual/Boc → reverse grip → staff**.

Third person shows both separate blades; first person retains SBX's staff. Primary attacks depend on movement. Reverse-grip alternate fire hops and spins; running flat out for about half a second changes to a dash pose without a speed boost.

Retail uses full-duration attack cooldowns to respect its four animation tracks and native blade glows instead of browser mesh fan trails. The package preserves MotS weapon/Force/class contracts and prepares 178 player models. The inherited save precaution remains: extinguish the saber before saving; switch it off/on if a loaded saber loses damage.

## Review and provenance

Current original-JKM results and UI previews belong to `STANDALONE-VALIDATION.md`. Historical overlay documentation is preserved under `docs/history/merged-v1.1/`; its results do not establish this edition's acceptance. Special Edition retains the inherited artwork and native button regions. Its main title adds a small Special Edition subtitle, with the existing logo moved upward 17 pixels without resampling. The original embedded palette and all pixels outside the right title block remain unchanged.

The complete-package audit found one sound already absent from stock MotS: `actor_mn.cog` refers to `cm60142.wav`. This edition explicitly reuses the already bundled same-response original JK voice, `i00mn13z.wav`. This is a source-supported fallback, not recovery of the missing MotS recording; the actor's other bytes are retained.

SBX is by ShadowX. Antonio Aiello / tristamus submitted the v17 merge and retail reverse-grip adaptation. Sith Sabers contributions are credited to EAH_CL0wN. See `CREDITS.md` and unchanged source documents under `docs/original/` for full attribution, permission testimony and upstream licenses.

## Rebuilding

The builder takes explicit historical SBX archives and owned JK/MotS data as conversion inputs. Those inputs are required to reproduce the conversion, but are not separate play-time requirements. See `README-BUILDER.md`; the build's `standalone/` output contains the finished archives and member/closure reports.
