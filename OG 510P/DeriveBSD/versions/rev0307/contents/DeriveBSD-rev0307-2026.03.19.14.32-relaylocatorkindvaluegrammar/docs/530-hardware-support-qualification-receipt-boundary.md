# Hardware support qualification receipt boundary

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, operability  
**Patterns:** Plan→Apply→Receipt, Registry→Diff→Gate

`docs/529-hardware-support-promotion-and-qualification-boundary.md` fixed what positive support labels must say.
This doc makes the next small hard decision:
**support promotion must stay reviewable by pointing at a typed receipt object, not by assuming the matrix row and some external ticket together tell the story.**

See also:
- ADR: `adrs/ADR-0120-hardware-support-qualification-receipt-boundary.md`
- support catalog boundary: `docs/528-hardware-support-matrix-and-bundled-admission-boundary.md`
- promotion summary boundary: `docs/529-hardware-support-promotion-and-qualification-boundary.md`
- qualification-profile boundary: `docs/531-hardware-support-qualification-profile-boundary.md`
- qualification freshness boundary: `docs/532-hardware-support-qualification-freshness-boundary.md`
- qualification status boundary: `docs/533-hardware-support-qualification-status-boundary.md`
- conditions / limitations boundary: `docs/534-hardware-support-conditions-and-known-limitations-boundary.md`
- hardware compatibility preflight: `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`
- workstation viability: `docs/410-desktop-viability-checklist.md`
- support catalog shape: `spec/hw.support.matrix.schema.json`
- qualification receipt shape: `spec/hw.support.qualification.receipt.schema.json`
- compatibility report shape: `spec/hw.compat.report.schema.json`

## Why this needs a hard decision

The matrix now has a `qualification` summary, which is good.
But summary-only support promotion still leaves a familiar escape hatch:

- the matrix says a class is `conditional` or `supported`,
- the real evidence is “in the lab system somewhere,”
- and operators or support bundles can no longer explain that claim offline.

That is too much hidden state for DeriveBSD.
A digest-bound catalog row should not force readers back into ticket portals or release notes to understand why a support claim is legitimate.

The right small move is not to build a giant hardware-certification bureaucracy.
It is to add one typed evidence object that the matrix summary can point at.

## Accepted boundary

Across all profiles:

- `hw.support.matrix` remains the catalog artifact,
- `entries[].qualification` remains the compact promotion summary,
- `qualification.receipt_digest` now points at `hw.support.qualification.receipt`,
- that receipt now also carries `qualification.profile_digest`, pointing at `hw.support.qualification.profile`,
- and `hw.compat.report.support_matrix` may surface `matched_qualification_receipt_digests` for target-specific gating/explanation.

The important split is deliberate:

- **matrix summary** = the review/discovery/catalog surface
- **qualification receipt** = the bundleable evidence object behind that summary
- **runtime policy** = still lives elsewhere

This keeps the archive coherent without turning support catalogs into a control plane.

## Minimal v0 contract worth implementing

### `qualification.receipt_digest`

Every positive `hw.support.matrix` entry now carries `qualification.receipt_digest`.
That digest points at the typed receipt that backs the summary.

The summary stays in the matrix because readers need a compact review surface.
The receipt exists because the summary should not be forced to smuggle every evidentiary detail inline.

### `hw.support.qualification.receipt`

The new receipt is intentionally narrow.
It records:

- the target artifact lineage (`release.capsule`, `host.generation`, `reset.authorization`, or `base.set`),
- the support claim (`entry_id`, profiles, roles, support level),
- the same typed qualification summary (`stage`, `verified_roles`, `evidence_floor`, `regression_policy`, `target_binding`, `last_verified_at`, `qualification.profile_digest`),
- `support_claim.condition_ids` for non-fully-supported claims so the receipt snapshots the same published `conditions[]` caveats/prerequisites the matrix entry declared,
- concrete freshness state (`fresh_until`, `reverify_on`) derived from the qualification profile instead of vague “recently tested” prose,
- supporting evidence digests,
- `check_results[]` keyed to the qualification-profile `check_id`s,
- and the publication decision, now with operational `decision.status`, `status_effective_at`, typed `reason_code`, and `replacement_receipt_digest` when a receipt is superseded.

That is enough to keep support promotion bundleable and explainable without freezing a giant lab DSL. The receipt can now say both *what evidence existed* and *which typed qualification standard that evidence satisfied*, while also saying whether the proof is still the current published support evidence.

### `hw.compat.report` join surface

When a target-specific preflight used a support matrix, it may now surface:

- `support_matrix.matched_entry_ids`
- `matched_qualification_receipt_digests`

That means a workstation consent screen, a fleet rollout note, or a factory support bundle can point directly at the qualification receipt that backed the matched entry. The same join can now surface `matched_condition_ids` and `support-condition-triggered` when the published caveat behind a conditional claim is part of the outcome. It can also surface `matched_target_binding` and `qualification-target-mismatch` when the proof was published for another `release_train` or boot-manifest lineage. When that receipt's `fresh_until` has elapsed, `hw.compat.report` can now say `qualification-stale` instead of pretending the claim is still freshly revalidated. When the receipt is later replaced or withdrawn, the same join can now surface `qualification-superseded` or `qualification-revoked`.

## The hard decision for B and D

This is where the cut becomes useful instead of decorative.

### B) Secure workstation

A trusted-UI-visible warning should not stop at “this class is conditional.”
It should be able to say:

- which support-matrix entry matched,
- which qualification receipt backs that entry,
- and which floor (`trusted-ui-basic`, `rollback-or-recovery`, `network-basic`) was actually revalidated.

That gives the human a coherent explanation surface instead of a marketing adjective.

### D) Appliance factory / regulatory

A factory kit, reset bundle, or support package must often be reviewable offline.
If “approved hardware” only exists as a matrix row plus external ticket history, the support story falls apart under audit.

The receipt-bound contract makes the support claim portable.
The matrix says *what* is allowed; the receipt says *what evidence object backed that publication decision*.
A currently positive claim should therefore only point at an `accepted` receipt; if lifecycle state changes, the next published matrix/bundle should move to the replacement digest or downgrade/remove the claim.

## Product-shape fit

### A) Secure fleet host

- rollout cohorts can point at a qualification receipt instead of tribal memory
- support maturity is still class-summary-first and release-bound
- no per-host allowlist pressure is introduced

### B) Secure workstation

- trusted-UI support claims can be shown with a real evidence handle
- local recovery expectations are no longer implied by release-note tone
- operators can keep the human-visible warning small while the bundle stays precise

### C) General-purpose OS

- local override remains viable
- the support matrix and receipt stay advisory unless policy makes them gating
- unusual hardware still has room without weakening the other product shapes

### D) Appliance factory / regulatory

- support/admission bundles gain an offline evidence object for qualification
- published support claims become easier to audit and reproduce later
- support teams no longer need live reachability to explain why a class was allowed

## Why this is the right next revision

This compounds the last two hardware decisions without widening the scope.
The archive now knows:

- where hardware support claims live,
- how positive support labels are maturity-shaped,
- and what evidence object backs those labels.

That is enough to keep future workstation/fleet/factory implementation work honest while leaving plenty of room for later details.

## External practice that shaped this cut

- Android Compatibility program overview: https://source.android.com/docs/compatibility/overview
- Red Hat hardware certification policies (test plan + published supported-feature statuses): https://docs.redhat.com/en/documentation/red_hat_hardware_certification/2025/html/red_hat_hardware_certification_program_policy_guide/assembly_hardware-certification-policies_hw-pol-cert-process-overview
- Ubuntu Certified hardware catalog / lifecycle testing posture: https://ubuntu.com/certified
- Fuchsia driver binding (explicit property matching): https://fuchsia.dev/fuchsia-src/concepts/drivers/driver_binding

Last updated: 2026-03-17r264
