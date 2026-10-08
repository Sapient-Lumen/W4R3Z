# Workbench review gate audit rev0275

Rev0275 focuses on the next risky seam after the rev0274 workbench-seed source-clock gate. The cube could produce a valid `NOT_ACCEPTED` seed and then fall back into an unstructured manual workbench note. That was a completion risk because the next operator could accidentally treat the seed, a copied note, or a weak local review as evidence acceptance.

## Concrete change

Rev0275 adds a bounded local workbench-review record between `workbench-seed.json` and the first-packet decision board:

- `tools/record_ft0181_workbench_review.py` records `workbench-review.json` and `WORKBENCH-REVIEW-SUMMARY.md` in `scratch/` or external local paths only.
- `tools/check_owner_workbench_review.py` validates the new path.
- `tools/ft0181_field_guards.py` now has `owner_workbench_review_integrity_error(...)` so the router and contact-status recorder share the same review boundary.
- `tools/decide_ft0181_field_next_action.py` now routes a valid seed to `make owner-workbench-review ...` instead of a prose-only manual review instruction.
- `tools/record_ft0181_owner_contact_status.py` can source a bounded `REASK_AWAITING_REPLY` clock from a valid `REASK-OWNER` workbench review.

## What the gate blocks

The new gate blocks:

1. edited workbench seeds that claim `ACCEPTED` or closure;
2. reviews that copy owner answers, contact details, raw CSV rows, or proceed-staged row text;
3. proceed decisions with `UNVERIFIED-OWNER-REPLY` source class;
4. proceed decisions with fewer than two reviewer roles;
5. proceed decisions with pending re-ask fields;
6. proceed decisions while raw learner data, protected facts, security payloads, or public claim upgrades are flagged;
7. release-controlled output paths for review records; and
8. local workbench reviews that try to become evidence, custody, closure, or public-summary support.

## What remains manual

The archive still cannot know whether the owner really sent a valid packet. A human must still review the local staged note and decide field survival. Rev0275 makes that step structured and auditable without pretending that local bookkeeping proves real-world delivery, source truth, learning benefit, safety, access, workload, compliance, scale, or effectiveness.

## Next true external move

The real forward move is unchanged: send or adapt the bounded owner request, record only the local send/status clocks, intake a real returned CSV through the source-clock gate, create a seed, then record a bounded workbench review. Only after that should the first-packet decision board be opened.
