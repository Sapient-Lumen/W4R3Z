# ADR-0124: hardware support conditions and known limitations boundary

Date: 2026-03-17
Status: Accepted

## Context

`adrs/ADR-0118-hardware-support-matrix-and-bundled-admission-boundary.md` fixed where support claims live: `hw.support.matrix` is the digest-bound catalog artifact.
`adrs/ADR-0119-hardware-support-promotion-and-qualification-boundary.md` fixed that positive entries must carry a typed `qualification` summary.
`adrs/ADR-0120-hardware-support-qualification-receipt-boundary.md`, `adrs/ADR-0121-hardware-support-qualification-profile-boundary.md`, `adrs/ADR-0122-hardware-support-qualification-freshness-boundary.md`, and `adrs/ADR-0123-hardware-support-qualification-status-boundary.md` then made those claims proof-bound, standard-bound, freshness-bound, and status-bound.

That still left one expensive ambiguity: `support_level = conditional` was mostly prose. The archive could say *which* proof backed a claim, but not *which published limitation or prerequisite made the claim conditional in the first place*. That leaves workstations, fleets, and factory bundles to infer the real caveat from notes.

Real ecosystems tend not to treat compatibility as one timeless boolean. Android compatibility is per-release and per-device/SKU policy. Ubuntu’s certified hardware guidance explicitly distinguishes “listed and tested” from “try it and verify.” Red Hat certification is model-specific and test-plan-specific rather than a vague evergreen badge.

## Decision

Accept a typed boundary for support conditions / known limitations.

1. **Conditional publication must carry typed `conditions[]`.**
   `conditions[]` becomes the canonical place to publish the small machine-readable limitation/prerequisite set behind `conditional`, `canary-only`, and `maintenance-only` claims.

2. **Conditions are published catalog semantics, not a live rule engine.**
   Each condition carries a stable `condition_id`, typed `reason_code`, `affected_roles`, a human-readable `summary`, and a typed `required_posture`. The matrix stays a release snapshot rather than an online advisory service.

3. **Receipts snapshot the condition ids they back.**
   `support_claim.condition_ids` records the published condition ids for non-fully-supported claims so proof stays bound to the same caveats the matrix published.

4. **Preflight/reporting can point at triggered conditions directly.**
   `hw.compat.report.support_matrix.matched_condition_ids` plus the `support-condition-triggered` finding keep warning surfaces and support bundles tied to the exact published limitation rather than vague text.

## Consequences

Good:
- B/workstation can explain *why* a claim is conditional (for example, dock-display topology not qualified) instead of only saying “trusted UI risk.”
- D/appliance support bundles can carry a published prerequisite like verified local recovery without ticket folklore.
- A/fleet rollouts get condition ids that can inform cohorts and breakglass reviews without inventing a live certification portal.

Trade-offs:
- The support lane gains a small new vocabulary surface (`conditions[].reason_code`, `required_posture`, `support-condition-triggered`).
- The archive still does not define a universal topology matcher or automatic remediator.

## Follow-up

This ADR does **not** decide:
- the final global taxonomy of every possible condition reason code,
- the exact trusted-UI wording for every triggered condition,
- or a live service that pushes support advisories after publication.

It only fixes the missing boundary so non-fully-supported hardware claims stop collapsing back into prose.
