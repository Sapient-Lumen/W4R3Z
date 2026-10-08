# Revision rev0254 — promotion readiness and Linux-native export posture

This revision extends the route/promotion planner with an explicit `promotion_readiness` surface.

## Added

- `plan-project --json` now emits:
  - `promotion_readiness`
  - `promotion_readiness_summary`
- Human-readable `vhk plan-project` now shows a **Promotion readiness** table.
- `gen-promotion-pack` now incorporates readiness into:
  - `docs/VHK_PROMOTION_PLAN.md`
  - `docs/VHK_PROMOTION_FIXUPS.md`
  - `docs/VHK_PROMOTION_PLAN.json`

## Why

The repo already knew which Linux-native surface each macro or project *wanted*. It did not yet say whether those promotions were actually ready to ship on the current Linux posture.

This revision adds a thin but explicit posture layer:

- `ready`
- `review`
- `blocked`

That posture is derived from:

- route fit
- backend shape (`x11` vs `wayland`)
- session capability signals when available
- helper/capture/pointer constraints that should not be hidden behind generic parity claims

## Product stance reinforced

- Text automation is a first-class product lane, but Wayland text/package behavior still deserves explicit review.
- Remapper exports are real, but app-context scope remains desktop-sensitive enough that promotion should not be treated as automatic parity.
- Helper-sensitive flows should stay dossiers/contracts until their session capabilities are honestly satisfied.
