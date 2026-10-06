# Hardware support qualification profile boundary

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, operability  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt

`docs/530-hardware-support-qualification-receipt-boundary.md` fixed that support claims must point at a typed evidence receipt.
This doc makes the next small hard decision:
**support qualification receipts must themselves point at a typed qualification standard, `hw.support.qualification.profile`, so “qualified” means the same check set across release trains and support bundles.**

See also:
- ADR: `adrs/ADR-0121-hardware-support-qualification-profile-boundary.md`
- support-catalog boundary: `docs/528-hardware-support-matrix-and-bundled-admission-boundary.md`
- promotion semantics: `docs/529-hardware-support-promotion-and-qualification-boundary.md`
- qualification receipt boundary: `docs/530-hardware-support-qualification-receipt-boundary.md`
- qualification freshness boundary: `docs/532-hardware-support-qualification-freshness-boundary.md`
- workstation viability constraint list: `docs/410-desktop-viability-checklist.md`
- hardware qualification profile shape: `spec/hw.support.qualification.profile.schema.json`
- hardware qualification receipt shape: `spec/hw.support.qualification.receipt.schema.json`

## Why this needs a hard decision

A support matrix plus a promotion ladder plus a receipt still leaves one last ambiguity: what exact qualification floor did the receipt satisfy?

Without a typed answer, `release-qualified` drifts back toward folklore:

- one lab means “booted once and Wi-Fi came up,”
- another means “switch, rollback, suspend, and secure-attention all passed,”
- workstation trusted-UI claims quietly depend on tribal knowledge,
- and factory/offline support bundles can carry the proof object without carrying the standard that made the proof meaningful.

That is too much ambiguity for A/B/D, and it is exactly how certification prose turns back into ticket systems.

## Accepted boundary

Across all profiles:

- `hw.support.qualification.profile` is the typed qualification standard / playlist / test-plan artifact,
- that profile target now carries `release_train` so the standard itself stays train-scoped instead of sounding timeless,
- `hw.support.matrix.entries[].qualification` must now carry `profile_digest` as well as `receipt_digest`,
- `hw.support.qualification.receipt` must carry the same `qualification.profile_digest`, publish `qualification.target_binding` (`target_binding`), and list `check_results[]` keyed by profile `check_id`,
- and the profile remains evidence-policy only rather than a runtime authority or a giant certification portal.

The point is narrow:
**support promotion must now point at both the standard and the proof.**

## Minimal v0 contract worth implementing

### `hw.support.qualification.profile`

The new profile artifact stays intentionally small:

- one release/generation/reset bundle lineage at a time,
- explicit scope by product `profiles`, support `support_levels`, and claimed `roles`,
- stable `required_checks[]` with `check_id`, `purpose`, accepted evidence kinds, and blocking posture,
- typed `freshness` with `max_age_days_by_stage` plus `reverify_on`,
- one acceptance rule: all applicable blocking checks pass.

It is not trying to encode the entire lab runner, vendor workflow, or certification bureaucracy.
It only makes the qualification floor digest-bound and explainable.

### Receipt linkage

`hw.support.qualification.receipt` now names:

- `qualification.profile_digest`,
- `check_results[]` with the `check_id`s actually satisfied,
- `fresh_until` plus `reverify_on`,
- and the supporting evidence digests used for each check.

That means a workstation trusted-UI claim can now say both:

- *which profile defined the required checks*, and
- *which evidence objects satisfied those checks on this release train*.

## Product-shape fit

### A) Secure fleet host

- qualification profiles keep cohort maturity comparable across release trains
- support claims can be audited without rediscovering what each release team counted as “qualified”

### B) Secure workstation

- the trusted UI floor is now defined by a digest-bound qualification profile instead of ticket comments
- `trusted-ui-basic`, `boot`, `generation-switch`, and `rollback-or-recovery` can be named as standard checks instead of hand-waved prose

### C) General-purpose OS

- local override remains viable
- the profile only matters when C opts into typed support-catalog posture

### D) Appliance factory / regulatory

- offline bundles can carry the support matrix, the receipt, and the qualification profile together
- auditors no longer need a live portal to understand what “supported hardware” meant for a shipped artifact

## What this does **not** decide yet

This doc does **not** freeze:

- the final global namespace of every possible hardware qualification check,
- the concrete lab runner or certification service implementation,
- the eventual diff/review surface for qualification-profile changes,
- or the full automation/notification workflow when field regressions appear after publication; `adrs/ADR-0123-hardware-support-qualification-status-boundary.md` now fixes the receipt-status semantics themselves.

The decision is smaller: the qualification lane now has a typed standard/proof split, and that standard now also owns the freshness policy that keeps `qualification-stale` out of prose-land. Receipt lifecycle now lives separately in `adrs/ADR-0123-hardware-support-qualification-status-boundary.md`, keeping `qualification-superseded` and `qualification-revoked` distinct from age-based drift.

## Why this is the right small hard decision

This is not a giant certification subsystem.
It is a coherence move:

- the support matrix stays the small published catalog,
- the receipt stays the concrete proof object,
- and the new profile is the typed standard that makes the proof interpretable.

That is enough to keep future implementation work honest without locking the archive into a huge lab bureaucracy.

Last updated: 2026-03-17r264
