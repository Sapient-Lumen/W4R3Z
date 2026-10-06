# Hardware support qualification target-scope boundary

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, reproducibility  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt

`docs/534-hardware-support-conditions-and-known-limitations-boundary.md` fixed why a support claim may be less than fully supported.
This doc fixes the next small but expensive ambiguity:
**what target span a support proof is allowed to cover must be typed and reviewable, not inferred from notes or memory.**

See also:
- ADR: `adrs/ADR-0125-hardware-support-qualification-target-scope-boundary.md`
- support catalog boundary: `docs/528-hardware-support-matrix-and-bundled-admission-boundary.md`
- promotion semantics: `docs/529-hardware-support-promotion-and-qualification-boundary.md`
- qualification receipt boundary: `docs/530-hardware-support-qualification-receipt-boundary.md`
- qualification profile boundary: `docs/531-hardware-support-qualification-profile-boundary.md`
- qualification freshness boundary: `docs/532-hardware-support-qualification-freshness-boundary.md`
- qualification status boundary: `docs/533-hardware-support-qualification-status-boundary.md`
- support conditions boundary: `docs/534-hardware-support-conditions-and-known-limitations-boundary.md`
- hardware compatibility preflight: `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`
- workstation viability: `docs/410-desktop-viability-checklist.md`
- support catalog shape: `spec/hw.support.matrix.schema.json`
- qualification receipt shape: `spec/hw.support.qualification.receipt.schema.json`
- compatibility report shape: `spec/hw.compat.report.schema.json`

## Why this needs a hard decision

The archive can already answer several support questions with typed artifacts:

- which catalog entry matched,
- which standard and receipt back it,
- whether the proof is fresh enough to count,
- whether the proof is still the current published evidence,
- and which published caveats explain a non-fully-supported claim.

But it still could not answer one practical question cleanly:

- **how far does this proof actually apply?**

Without that boundary, a support claim qualified on one release train quietly drifts onto another:

- a workstation trusted-UI claim keeps sounding current after the boot-manifest lineage changed,
- a fleet rollout treats r261 qualification as if it were r262 qualification,
- and a factory bundle ships a receipt whose proof applies to an older target than the one actually being installed.

That is too mushy for a release-shaped archive.

## Accepted boundary

Across all profiles:

- support targets now carry `release_train` in `hw.support.matrix`, `hw.support.qualification.profile`, `hw.support.qualification.receipt`, and `hw.compat.report`,
- positive support claims now publish `qualification.target_binding`,
- `target_binding` is the tiny typed answer for how far a proof reaches (`exact-artifact-digest`, `same-release-train`, `same-release-train-and-boot-manifest`),
- `hw.compat.report` may now emit `qualification-target-mismatch`,
- and `hw.compat.report.support_matrix` may record `matched_target_binding` plus `target_scope_state`.

The point is narrow:
**the archive now has a typed answer for whether a matched support proof applies to this target at all.**

## Minimal v0 contract worth implementing

### `release_train`

Hardware-support publication/evidence/report targets now carry `release_train`.
That keeps support qualification tied to the same release-train language the rest of the archive already uses for base, updates, and rollout policy.

### `qualification.target_binding`

The target-scope vocabulary is intentionally tiny:

- `exact-artifact-digest` = only the exact published artifact target counts
- `same-release-train` = the proof may be reused within the same `release_train`
- `same-release-train-and-boot-manifest` = the proof only counts when both the `release_train` and boot-manifest lineage still match

For workstation trusted-UI floor claims, `same-release-train-and-boot-manifest` is the honest default more often than not.
That keeps B from pretending an older boot stack qualification still counts after a release hop or boot-path change.

### `hw.compat.report`

Preflight/reporting gets a direct target-scope answer:

- `qualification-target-mismatch` in `findings[]`
- `support_matrix.matched_target_binding`
- `support_matrix.target_scope_state`

This is intentionally distinct from `qualification-stale`, `qualification-superseded`, and `qualification-revoked`.
One answer says *the proof no longer applies to this target*; the others say *the proof aged out or stopped being current publication*. Those are not the same operational problem.

## Product-shape fit

### A) Secure fleet host

- cohorting can reject “qualified on the old train” without operator folklore
- rollout review stays honest when a release train advances faster than qualification replay

### B) Secure workstation

- trusted-UI consent can say when a matched machine class is only qualified for the old train / old boot-manifest lineage
- `qualification-target-mismatch` is a clearer reason to stop than a vague workstation warning blob

### C) General-purpose OS

- explicit local override still exists
- typed target scope keeps support messaging honest without forcing every install into a factory-style gate

### D) Appliance factory / regulatory

- support bundles can say whether the included proof really applies to the shipped target
- offline audit gets a direct answer instead of ticket comments about “same hardware class, probably okay”

## What this does **not** decide yet

This doc does **not** freeze:

- a general version-range DSL for every future support lane,
- automatic requalification scheduling,
- or a universal target-family taxonomy.

The decision is smaller:
**support proof now declares its target span, and preflight can say when that span does not cover the current target.**

## Why this is the right small hard decision

This is not a giant compatibility portal.
It is a coherence move:

- the matrix still says what is published,
- the receipt still says which evidence backed that publication,
- the profile still says which check standard mattered,
- freshness and status still answer whether the proof is current,
- conditions still answer why a claim is conditional,
- and `target_binding` now answers whether that proof even applies to this target.

That is enough to keep future implementation work honest without forcing DeriveBSD to solve general compatibility range algebra up front.

## External practice that shaped this cut

- Android publishes compatibility policy per release and expects CTS packages that match the device Android version.
- Ubuntu certification is tied to the life cycle of the Ubuntu release against which the system was certified.
- Red Hat hardware certification is specific to a major RHEL version and architecture.
- Windows HLK official playlists must match the kit/target release version.

Last updated: 2026-03-17r264
