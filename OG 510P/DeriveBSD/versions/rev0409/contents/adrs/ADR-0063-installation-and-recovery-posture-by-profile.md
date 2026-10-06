# ADR-0063: Installation-and-recovery posture by profile

- **Status:** Accepted
- **Date:** 2026-03-06

## Context

DeriveBSD already has the raw pieces for a first-class install/recovery story:
`docs/309-installation-and-recovery-as-derived-operations.md` makes install a normal Plan→Apply→Receipt workflow,
`docs/310-disk-layout-plans-and-receipts.md` makes partitioning/pool mutation typed and receipted,
`docs/360-derived-recovery-images-and-minimal-userspace.md` keeps recovery userspace derived instead of folkloric,
and `docs/250-breakglass-and-recovery-workflows.md` keeps emergency authority explicit.

What the archive still lacked was the **product-shape default** for installation and recovery.
Without that, four incompatible postures quietly blur together:

- **A** may talk about idempotent fleet reprovisioning while still allowing “picked the wrong disk” or ad-hoc destructive edits in the normal path.
- **B** may claim a human-safe workstation while quietly normalizing scary destructive reinstall flows, weak disk confirmation, or non-encrypted defaults.
- **C** may lose general-purpose viability by pretending only one opinionated installer is acceptable, or by hiding destructive repartitioning inside “easy mode”.
- **D** may claim factory/regulatory rigor while still making recovery depend on live reachability or unreviewed on-bench wipe scripts.

We do **not** need to choose one partitioning frontend, one ncurses/TUI flow, one live image layout, or one factory station workflow here.
We do need a stable, checkable answer to:

- when target-device identity is mandatory,
- when additive create/grow semantics are the default,
- where destructive disk mutation requires explicit breakglass or stronger confirmation,
- where encrypted-root posture is the baseline,
- and where a verified recovery path must remain present without live-network assumptions.

## Decision

We define installation/recovery as a **profile-shaped default** and keep it threaded through `spec/examples/product.profiles.json` under the stable `installation_recovery` knob.

Cross-profile guardrail:
- install/recovery media remain derived, signed, and policy-bound artifacts rather than mutable rescue folklore,
- target-device selection must be explainable and reviewable rather than “best guess” disk picking,
- additive create/grow semantics are the normal path and destructive shrink/reformat/erase operations require stronger intent,
- encrypted-root posture is a product decision, not an installer convenience toggle,
- and recovery availability is a first-class claim: weaker compatibility lanes in C must not silently redefine stricter A/B/D expectations.

### A) `fleet_host`

Default posture: `target-bound-additive-breakglass`

- Fleet reprovisioning should be idempotent, bundle-driven, and safe to retry.
- Target-device identity (WWN/serial/path class) is required by default so remote install/recovery does not become “hope we picked da1 correctly”.
- The ordinary path is additive create/grow; destructive disk mutation belongs to breakglass/maintenance policy, not routine automation.
- Verified recovery/install media must remain available via on-disk recovery slot, virtual media, or similarly policy-controlled carrier.

### B) `workstation`

Default posture: `guided-consent-encrypted-default`

- The workstation baseline is a trusted-UI-guided install/recovery flow with explicit disk identity confirmation before destructive edits.
- Encrypted-root posture is the default for ordinary private user state; recovery must not force hidden convenience keys into live images.
- A local verified recovery path should remain available so the person holding the device can repair or reinstall without improvising unsafe tooling.
- Silent destructive reprovisioning is out of bounds for the ordinary B story.

### C) `general_os`

Default posture: `guided-choice-explicit-destructive`

- General-purpose viability means the archive can keep both opinionated Derive-guided install paths and bounded compatibility/classic installer adapters.
- Encryption remains preferred, but explicit compatibility fallback is allowed instead of forcing a fork or pretending every install target wants the same tradeoff on day one.
- Destructive repartition/reformat paths must stay explicit and reviewable; convenience must not hide the danger.
- Adapter lanes remain killable and must not silently redefine A/B/D defaults.

### D) `appliance_factory`

Default posture: `target-bound-offline-resettable`

- Factory/regulatory installs are target-bound by device identity and staged through approved offline media, mirror kits, or station-local bundles.
- Additive replay is the normal production posture; destructive reprovisioning belongs to signed reset bundles/markers and retained approval, not bench folklore.
- Verified recovery media must remain available without assuming live upstream reachability.
- Factory reset is a policy-governed product capability, not a hidden shell script.

## Consequences

DeriveBSD now has a stable answer for install/recovery authority by product shape:

- **A** is safe-to-retry and target-bound by default.
- **B** is trusted-UI-guided and encrypted by default.
- **C** keeps choice explicit without hiding destructive operations.
- **D** is target-bound, offline-capable, and reset-governed by default.

This narrows future work without overcommitting on implementation:

- disk-layout plan schema evolution stays open,
- exact recovery-media packaging stays open,
- exact trusted-UI wording and user education on B stay open,
- exact factory reset marker/bundle mechanics stay open,
- and remote virtual-media / BMC adapters remain adapter-shaped implementation choices.

## Alternatives considered

### One universal strict posture for all A–D

Rejected.
It would either make C less viable than promised, or water down A/B/D so much that the default becomes meaningless.

### Leave install/recovery posture as implementation detail

Rejected.
That allows the highest-risk disk-mutation decisions to drift through tooling convenience, which directly contradicts the archive’s evidence and product-shape discipline.

### Decide only encrypted-root defaults and leave disk mutation vague

Rejected.
That would still leave the main destructive-authority question unanswered: how DeriveBSD avoids “installer folklore” and wrong-disk incidents across A–D.
