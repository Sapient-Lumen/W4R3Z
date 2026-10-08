# VHK revision 0257 — promotion evidence, proof posture, and checked-in release truth

This revision adds a new planner/pack/lint layer: **promotion evidence**.

## What changed

- `plan-project --json` now includes:
  - `promotion_evidence`
  - `promotion_evidence_summary`
- Human-readable `vhk plan-project` now shows a **Promotion evidence** table.
- `gen-promotion-pack` now writes:
  - `docs/VHK_PROMOTION_EVIDENCE.md`
- `lint-project` now emits:
  - `PROMOTION_EVIDENCE_MISSING`
  - `PROMOTION_EVIDENCE_PARTIAL`

## Why this mattered

The repo already knew:

- which lane each macro belongs to
- which export surfaces the project wants
- which surfaces are ready/review/blocked
- which promotion gates are passing or failing
- which queued backlog tasks should happen next

The missing question was: **what proof should exist in the repo before those surfaces and gates count as release-ready knowledge instead of planner suggestions?**

This revision answers that by attaching explicit checked-in proof requirements to each promotion surface and gate.

## Current proof model

Examples of required artifacts now include:

- `docs/VHK_SETUP_GUIDE.md`
- `docs/VHK_VERIFICATION_GUIDE.md`
- `docs/VHK_CLAIM_GUIDE.md`
- `docs/VHK_TARGET_CLAIMS.yaml`
- `docs/VHK_ROUTE_SELECTION.md`
- `docs/VHK_TARGET_ROUTE_MATRIX.md`
- `docs/VHK_HOST_REQUIREMENTS.md`

The planner now marks each evidence entry as:

- `complete`
- `partial`
- `missing`

That same posture now flows into promotion-pack docs and project lint warnings.

## Why this is Linux-native

On Linux, “works” often depends on session family, compositor behavior, portal backend routing, helper daemons, and explicit host setup. The planner should not stop at route ownership or release gates; it should also say what proof a project ought to check in before shipping stronger support language.

This revision keeps VHK pointed at a more honest product shape:

- text/remapper/service/helper lanes stay distinct
- release posture stays tied to checked-in evidence
- support claims become auditable repo state instead of memory or optimism
