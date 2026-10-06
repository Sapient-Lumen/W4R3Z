# Hardware support matrix and bundled admission boundary

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, supply-chain, operability  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt

`docs/479-hardware-compatibility-posture-by-profile.md` fixed the product-default strength of compatibility gates.
This doc makes the next small hard decision:
**approved-hardware and support claims must travel as a typed, digest-bound catalog (`hw.support.matrix`), not as live discovery folklore, per-host allowlists, or release-note prose.**

See also:
- ADR: `adrs/ADR-0118-hardware-support-matrix-and-bundled-admission-boundary.md`
- hardware inventory lane: `docs/319-hardware-inventory-and-driver-binding-as-evidence.md`
- compatibility preflight lane: `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`
- product-default hardware posture: `docs/479-hardware-compatibility-posture-by-profile.md`
- workstation viability constraint list: `docs/410-desktop-viability-checklist.md`
- hardware support catalog shape: `spec/hw.support.matrix.schema.json`
- promotion semantics: `docs/529-hardware-support-promotion-and-qualification-boundary.md`, `docs/534-hardware-support-conditions-and-known-limitations-boundary.md`
- qualification receipts: `docs/530-hardware-support-qualification-receipt-boundary.md`
- qualification profile: `docs/531-hardware-support-qualification-profile-boundary.md`
- qualification freshness: `docs/532-hardware-support-qualification-freshness-boundary.md`
- qualification status: `docs/533-hardware-support-qualification-status-boundary.md`
- compatibility report shape: `spec/hw.compat.report.schema.json`

## Why this needs a hard decision

The archive already knew three things:

- A and D need something stronger than “best effort, maybe this NIC works.”
- B cannot stay viable if display/input/storage/recovery support is discovered only after reboot.
- C still needs room for explicit override and weird hardware without redefining stricter product shapes.

Without a narrow contract, that pressure spills into bad places:

- factory/regulatory support claims become PDFs and spreadsheets instead of typed release artifacts,
- workstation “supported hardware” becomes vague marketing instead of a trusted-UI-visible floor,
- fleets quietly grow per-host exception lists that are both privacy-toxic and impossible to review,
- and `hw.compat.report` ends up mixing live facts, policy, and support claims in opaque free text.

DeriveBSD needs one reviewable object for **support/admission claims**, while keeping runtime authority somewhere else.

## Accepted boundary

Across all profiles:

- `hw.inventory.receipt` remains the source of **observed hardware truth**,
- `hw.support.matrix` becomes the source of **declared support/admission claims**,
- `hw.compat.report` is where those two join a specific target generation/release/reset decision,
- and no matrix entry gets to directly load drivers, widen device authority, or mutate kernel posture.

This is the main cut.
The support matrix is a **catalog artifact**, not a control plane. A currently positive entry should point at an `accepted` qualification receipt, not at a superseded or revoked historical proof. That publication now also carries `release_train` at the target level and `qualification.target_binding` at the entry level so support proof cannot silently float onto the wrong target. When a report later matches the hardware class but not the proof scope, `hw.compat.report` should emit `qualification-target-mismatch` instead of pretending the old publication still counts.

## Minimal v0 artifact worth implementing

### `hw.support.matrix`

The new artifact is intentionally small:

- it targets one release/generation/reset/support bundle lineage at a time,
- it matches on **hardware-class summaries** rather than host identity,
- it states support level per matched class,
- it names the roles that matter (`boot-storage`, `primary-network`, `trusted-display`, `trusted-input`, etc.),
- and it records the minimum recovery expectation when warnings are acceptable.

The v0 shape is not trying to encode every lab note or certification workflow.
It is only trying to keep the support story typed enough that offline bundles, rollout gates, and trusted-UI explanations can all point at the same digest.

### `hw.compat.report` join state

When a support matrix is used, the report now has a typed `support_matrix` join object so reviewers can answer:

- which support catalog was consulted,
- whether the host matched any catalog entry,
- and which entry ids justified the final gate posture.

This keeps support/admission decisions out of free-text notes.

## What gets matched

The matching surface is deliberately **class-summary-first**:

- PCI vendor/device/subsystem ids
- USB VID/PID/class hints
- ACPI HIDs
- SMBIOS CHIDs / machine-class ids
- board product strings
- coarse CPU arch / virtualization posture

This mirrors real practice in modern hardware-targeting systems:
firmware/update stacks use stable machine IDs rather than serials, driver systems match explicit node properties rather than mystical probe vibes, and commercial certification catalogs publish support by tested product lines rather than by one machine's secret UUID.

That is the right lesson to steal.
DeriveBSD should keep the selector space **stable and privacy-bounded**, then bind actual target decisions through the report.

## Product-shape fit

### A) Secure fleet host

- support matrices are useful cohorting/support inputs, not replacements for fresh inventory
- missing matrix coverage can become a rollout warning or a stricter breakglass path depending on policy
- the important thing is that “supported hardware cohort” is typed and release-bound instead of living in spreadsheets

### B) Secure workstation

- support matrices are the place to declare the **trusted UI floor**: display, input, boot storage, and recovery expectations
- `hw.compat.report` may now emit `trusted-ui-floor-risk` or `recovery-path-missing` instead of burying that logic in generic warnings
- human consent stays meaningful because the support claim is digest-bound and reviewable before reboot

### C) General-purpose OS

- support matrices stay optional/advisory by default
- explicit local override remains viable for unusual hardware and lab workflows
- C keeps broad compatibility without weakening A/B/D’s stronger support claims

### D) Appliance factory / regulatory

- support matrices become part of the shipped support/admission contract
- release bundles, reset media, and factory kits can carry the exact hardware catalog they were validated against
- production support no longer depends on live reachability to a vendor portal

## What this does **not** decide yet

This doc does **not** freeze:

- the exact hardware-class canonicalization pipeline,
- the final diff/review surface for support-matrix changes,
- the exact vendor/lab workflow behind each matrix entry (promotion semantics are now fixed separately in `docs/529-hardware-support-promotion-and-qualification-boundary.md`),
- a universal version-range algebra beyond `release_train` plus `target_binding`,
- or every possible reason code inside `hw.compat.report`.

The point is smaller:
DeriveBSD now has one typed place to carry support/admission claims, and one typed place to join them with real inventory before a switch/install/recovery action.

## Why this is the right small hard decision

This is a leverage move, not a device-manager rewrite.
It keeps the hardware story coherent across all four product shapes:

- A can cohort and gate on supported classes,
- B can keep the trusted UI floor honest,
- C can stay permissive without becoming the default for everyone else,
- D can ship support claims offline and auditably.

That is enough to make future specs and implementation choices much less ambiguous without inventing a giant new subsystem.

Last updated: 2026-03-17r264