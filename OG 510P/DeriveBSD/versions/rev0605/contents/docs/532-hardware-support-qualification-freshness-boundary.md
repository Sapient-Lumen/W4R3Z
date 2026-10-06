# Hardware support qualification freshness boundary

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, operability  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt

`docs/531-hardware-support-qualification-profile-boundary.md` fixed that support receipts must point at a typed qualification standard.
This doc makes the next small hard decision:
**the qualification standard must also define freshness, and receipts must record a concrete `fresh_until`, so support claims stop counting as fresh in a typed way rather than through “recently tested” folklore.**

See also:
- ADR: `adrs/ADR-0122-hardware-support-qualification-freshness-boundary.md`
- support-catalog boundary: `docs/528-hardware-support-matrix-and-bundled-admission-boundary.md`
- promotion semantics: `docs/529-hardware-support-promotion-and-qualification-boundary.md`
- qualification receipt boundary: `docs/530-hardware-support-qualification-receipt-boundary.md`
- qualification profile boundary: `docs/531-hardware-support-qualification-profile-boundary.md`
- hardware qualification profile shape: `spec/hw.support.qualification.profile.schema.json`
- hardware qualification receipt shape: `spec/hw.support.qualification.receipt.schema.json`
- hardware compatibility report shape: `spec/hw.compat.report.schema.json`

## Why this needs a hard decision

The archive can now answer two important questions:

- which support catalog entry matched,
- and which typed standard + receipt backed that support claim.

But there was still no typed answer for a third question:

- **is that qualification still fresh enough to count?**

Without that answer, support claims quietly drift:

- a workstation support claim that passed on an earlier kernel/firmware stack keeps sounding current,
- a factory support bundle carries an impressive receipt that may already be stale for the shipped release train,
- fleet rollout gates treat ancient validation as equivalent to fresh cohort evidence,
- and “recently verified recovery path” remains a prose argument instead of a contract.

That is too much ambiguity for A/B/D and too much hidden risk for C when it opts into typed support posture.

## Accepted boundary

Across all profiles:

- `hw.support.qualification.profile` now carries `freshness`, and `hw.support.qualification.profile.freshness` is the typed freshness policy,
- `hw.support.qualification.receipt.freshness.fresh_until` is the concrete freshness bound for one qualification receipt,
- `hw.support.qualification.receipt.freshness.reverify_on` carries the invalidating change classes copied from the profile,
- and `hw.compat.report` may emit `qualification-stale` when a matched support claim no longer counts as fresh. `qualification-superseded` and `qualification-revoked` remain separate publication-state findings rather than synonyms for staleness.

The point is narrow:
**support qualification is no longer just standard-bound and receipt-bound; it is also freshness-bound.**

## Minimal v0 contract worth implementing

### `hw.support.qualification.profile.freshness`

The profile now carries a tiny freshness policy:

- `max_age_days_by_stage` sets the maximum age for `lab-validated`, `canary-observed`, `release-qualified`, and `field-sustained` claims,
- `reverify_on` lists the change classes that invalidate freshness early (`kernel-or-kmod-change`, `firmware-change`, `boot-manifest-change`, `role-regression`, `qualification-profile-change`, `recovery-lane-change`).

This keeps the freshness rule attached to the same typed standard that defined the checks.

### `hw.support.qualification.receipt.freshness`

The receipt now records the concrete outcome of that policy:

- `fresh_until`
- `reverify_on`

That is enough for offline bundles and preflight reports to answer “does this still count as fresh?” without inventing a live certification portal.

### `hw.compat.report`

Preflight/reporting now has an explicit stale-support finding:

- `qualification-stale`
- `qualification-superseded` and `qualification-revoked` remain distinct findings for support proofs whose publication state changed even if age was not the problem

That finding is for freshness drift in the support-qualification lane.
It is intentionally separate from `support-matrix-miss`, `trusted-ui-floor-risk`, or `recovery-path-missing`.
Those findings answer different questions.

## Product-shape fit

### A) Secure fleet host

- rollout gates can treat stale qualification evidence as a real cohort risk rather than silently inheriting old support claims
- kernel/kmod/firmware movement can require requalification without inventing per-host spreadsheets

### B) Secure workstation

- trusted-display / trusted-input support can stop sounding current once `fresh_until` has elapsed
- consent surfaces can explain `qualification-stale` instead of pretending that old qualification evidence is as good as fresh validation
- “recently verified recovery path” pressure now has a typed home instead of a vague checklist note

### C) General-purpose OS

- local override remains viable
- when C opts into typed support posture, stale support evidence is visible rather than ambient

### D) Appliance factory / regulatory

- shipped bundles can carry a digest-bound freshness answer offline
- support claims stay auditable across long-lived release trains without depending on vendor ticket portals

## What this does **not** decide yet

This doc does **not** freeze:

- the full automation/notification workflow after repeated field regressions (the receipt-status semantics themselves now live in `adrs/ADR-0123-hardware-support-qualification-status-boundary.md`),
- the exact trusted-UI wording for stale support claims,
- the complete replay/scheduler automation for qualification reruns,
- or any live online certification service.

The decision is smaller:
**typed support claims now have a typed answer for freshness.**

## Why this is the right small hard decision

This is not a giant recertification subsystem.
It is a coherence move:

- the matrix stays the compact published catalog,
- the profile stays the typed qualification standard,
- the receipt stays the typed proof object,
- and freshness is now part of the same portable evidence lane instead of a side conversation.

That is enough to make future implementation work more honest without forcing the archive to solve the entire lab-automation story up front.

Last updated: 2026-03-17r262
