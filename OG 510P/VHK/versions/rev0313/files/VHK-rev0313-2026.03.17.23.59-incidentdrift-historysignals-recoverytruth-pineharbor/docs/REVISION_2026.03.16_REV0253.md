# Revision rev0253 — promotion waves and executable promotion review

This revision keeps pushing VHK toward a Linux-native composition model instead of a fake single-backend story.

## What changed

- `vhk plan-project --json` now emits `promotion_waves` alongside `route_portfolio` and `export_promotion_plan`.
- Human-readable `vhk plan-project` now shows a **Promotion waves** table.
- New command: `vhk gen-promotion-pack`.
  - writes `docs/VHK_PROMOTION_PLAN.md`
  - writes `docs/VHK_PROMOTION_FIXUPS.md`
  - writes `docs/VHK_PROMOTION_PLAN.json`
  - writes `scripts/vhk_review_promotion_plan.sh`

## Why this matters

Previous revisions could explain which lane a macro belonged to and which export surface looked plausible. This revision turns that into staged project-level work:

- which promotions belong in the immediate specialist-export wave
- which ones are helper/conditional clean-up work
- which ones are later auxiliary shipping refinements

That makes VHK's Linux-native direction more operational: reviewable, scriptable, and easier to hand off.
