# 353. Special-case voter-facing surface triplet propagation and doc-only drift firewall

**Track:** Shared

This document is a compact companion to `docs/330-*`, `docs/349-*`, `docs/350-*`, `docs/351-*`, and `docs/352-*` for the highest-risk voter-facing special-case cluster: the `special_case_high_risk` rows in `artifacts/tables/voter-facing-public-answer-surfaces.csv` (currently `317–328` and `335–343`).

It exists to answer one bounded maintainer question:

**“Even when a high-risk voter-facing edge-case control exists in the numbered doc, has it also been propagated into the payload template and operator checklist so release wiring cannot preserve the essay while dropping the operational skeleton?”**

## Why this exists (bounded)

The archive already does two important things for the voter-facing family:

1. requires every surface to exist as a doc/template/checklist triplet via `docs/330-*`, and
2. requires the `special_case_high_risk` subfamily to carry concrete operational fields and routing rules via `docs/349-*`, `docs/350-*`, `docs/351-*`, and `docs/352-*`.

That still leaves one quiet maintenance seam.

A high-risk doc can say all the right things about direct help routes, responsible office identity, secure-channel use, minimum disclosure, and operability-now checks while the linked payload template or checklist silently drifts backward. That is a real failure mode because the numbered doc is not the only release artifact maintainers touch. In practice, operators often start from the checklist, builders start from the template, and reviewers spot-check the numbered doc later. If the doc carries the rule but the template/checklist pair no longer carries the same bounded control fields, the archive can pass a superficial prose review while shipping a weaker operational surface than the maintainer intended.

For this specific subfamily, that is not just style drift. These are the edge-case voter surfaces most likely to fail under deadline pressure, jurisdiction confusion, disclosure mistakes, or last-mile office-routing ambiguity. The release gate should therefore reject **doc-only control drift** for the latest high-risk floors instead of merely hoping the triplet stays synchronized.

## What this adds (and what it does not)

This document adds a compact **triplet-propagation / doc-only-drift firewall** for `special_case_high_risk` surfaces.

It does **not** replace:
- the family triplet/orphan control in `docs/330-*`,
- the direct-help-route and contactability floor in `docs/349-*`,
- the responsible-office specificity floor in `docs/350-*`,
- the official secure-channel and minimum-disclosure floor in `docs/351-*`, or
- the operability-now and deadline-imminence floor in `docs/352-*`.

It only adds one more bounded rule: **for the highest-risk special-case surfaces, the template and checklist must carry the same compact operational backstop that the numbered doc now requires.**

## Propagation floor

For each row tagged `special_case_high_risk` in `artifacts/tables/voter-facing-public-answer-surfaces.csv`, the release gate should require all of the following:

1. the linked payload template carries the direct-help-route fields required by `docs/349-*` — `authoritative_help_uri` and/or `authoritative_help_phone`,
2. the linked payload template carries the responsible-office fields required by `docs/350-*` — `authoritative_office_name` plus `authoritative_office_scope`,
3. the linked payload template carries the secure-channel / minimum-disclosure fields required by `docs/351-*` — `official_secure_channel_note` plus `minimum_necessary_disclosure_note`,
4. the linked payload template carries the operability-now fields required by `docs/352-*` — `operability_now_note` plus `deadline_imminence_note`, and
5. the linked operator checklist carries a compact dedicated backstop section that reminds the maintainer to preserve all four field groups above and to keep `305` as the ordinary-help / confirmation lane and `307` as the rights/safety escalation lane.

The point is not to turn every checklist into a duplicate of the numbered doc.
The point is to keep the triplet **operationally coherent** so a future edit cannot preserve the prose while dropping the fields that make the public surface usable.

## What this is meant to catch

This check is intentionally narrow. It is meant to catch bounded but meaningful failures such as:

- a high-risk numbered doc that was tightened to require a real help path while the linked template still lacks `authoritative_help_uri` and `authoritative_help_phone`,
- a doc that names the responsible office role while the template/checklist pair still treats help as undifferentiated,
- a secure-channel / oversharing warning added to prose but not reflected in the template/checklist that operators actually use,
- an operability-now rule added to prose while the checklist no longer reminds maintainers to confirm live availability near a cutoff,
- or a future promotion where the triplet exists formally under `docs/330-*` but the latest high-risk control fields were never propagated into the linked artifacts.

## Mechanical check

The release gate should reject the archive if any current `special_case_high_risk` row points to a template or checklist that fails this propagation floor.

The checker for this is:

- `scripts/check_voter_facing_special_case_triplet_propagation.py`

and it should run as part of:

- `scripts/release_gate.py`

## Why this stays narrow

This does **not** require a new nationwide voter product, a new schema family, or another long doctrinal control stack.
It only requires the existing `special_case_high_risk` triplets to keep the latest bounded control fields synchronized across:

- the numbered doc,
- the payload template, and
- the operator checklist.

That is a release-discipline improvement, not a new voter-policy theory.

## Cross-references

- `docs/330-voter-facing-public-answer-surface-triplet-coherence-and-orphan-control.md`
- `docs/349-special-case-voter-facing-surface-direct-help-route-and-contactability-floor.md`
- `docs/350-special-case-voter-facing-surface-responsible-office-specificity-and-jurisdiction-match-floor.md`
- `docs/351-special-case-voter-facing-surface-official-secure-channel-and-minimum-disclosure-floor.md`
- `docs/352-special-case-voter-facing-surface-operability-now-and-deadline-imminence-floor.md`
- `scripts/check_voter_facing_special_case_triplet_propagation.py`
For the canonical ordered current control-stack map that keeps newer tail controls discoverable from anywhere in this maintainer subfamily, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`. For the companion checklist-workflow rule that keeps the earlier non-overlap / lane-change / no-portability controls visible in the linked high-risk checklist instead of only in the numbered doc, see `docs/357-special-case-voter-facing-surface-boundary-portability-checklist-backstop.md`.
