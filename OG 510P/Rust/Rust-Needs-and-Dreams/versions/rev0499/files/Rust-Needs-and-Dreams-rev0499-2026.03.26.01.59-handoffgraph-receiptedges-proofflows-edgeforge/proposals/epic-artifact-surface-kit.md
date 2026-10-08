## Execution addendum (rev0443)
Read this proposal with `design/cargo-artifact-contract-execution-blueprint-2026Q1.md`.

Interpretation rule:
- the epic is now better understood as a **final-output / sidecar / downstream-handoff execution blueprint** rather than only a promoted seam;
- and future rollout language should stay anchored to selected-subject truth, artifact identity, origin/staging truth, sidecar truth, and consumer handoffs.

## Refresh note (rev0398)
This proposal is now promoted as the archive's clearest next **build-system/plumbing-shaping** move beneath Cargo's current plumbing and external-tool surfaces.
It should be read alongside `design/cargo-artifact-contract-2026Q1.md`.

Interpretation rule:
- the worthy contribution is still a thin reusable artifact boundary;
- it is **not** a new build system, release orchestrator, or path-scraping convenience wrapper.

# Epic proposal: Artifact Surface Kit (`cargo artifacts`, `artifact-pack/v0`)

## One-line thesis
Build a thin Cargo companion layer for **final-output truth** that links **selected build subject**, **final artifact identity**, **origin/location facts**, **artifact-linked sidecars**, and **bounded downstream handoffs** into one portable review boundary without pretending build caches, release bundles, install receipts, and SBOM exports are all the same thing.

## Why this is now worth doing
Rust now has enough real upstream motion around final outputs that the missing contribution looks like a **reviewable artifact boundary above the ingredients** rather than one more ingredient:
- Cargo now publicly distinguishes final outputs from intermediate build state;
- `artifact-dir` exists because exact final filenames are otherwise awkward and JSON-heavy to recover;
- build-dir layout changes are actively forcing tools to confront which path assumptions were public versus accidental;
- Cargo is explicitly exploring structured custom-final-artifact uplift instead of direct build-script writes;
- SBOM precursor files now attach to executable/linkable outputs;
- `cargo-dist` already proves downstream appetite for machine-readable artifact/release manifests.

What is still missing is the **kit-level boundary that says one selected build subject produced these final outputs, with these origin and path facts, these sidecars, and these bounded downstream handoffs**.

## Working name
- CLI: `cargo artifacts`
- primary artifact: `artifact-pack/v0`

## Scope
### This epic should own
- selected build-subject identity
- final Cargo-facing output identity
- origin class (Cargo-native / rustdoc / package / Cargo-mediated uplift)
- produced-path versus copied/uplifted-path truth
- artifact-linked sidecars and attachment pointers
- diffable final-output review points across builds/releases
- bounded handoffs to Release/Inventory/Repro/Support/Productization consumers

### This epic should not own
- intermediate cache topology or lock analysis
- build-script authoring or sandbox policy
- release orchestration / hosted artifact pages / installers
- install-channel selection or receipts
- one universal SBOM/export format
- a fake “artifact completeness” score

## Candidate artifact family
### `artifact-brief/v0`
Why this build subject exists, what classes of final output were observed, and where uncertainty remains.

### `artifact-subject/v0`
The exact workspace/package/command/target/profile/toolchain/features selection and output-exposure posture.

### `artifact-entry/v0`
One final output with identity, origin class, path facts, freshness, and sidecar links.

### `artifact-manifest/v0`
The machine-readable collection of final outputs, layout facts, omissions, and collision notes.

### `artifact-report/v0`
Reviewable findings covering selection drift, path drift, origin drift, sidecar drift, and unstable/lossy inference.

### `artifact-pack/v0`
The portable bundle linking the manifest, report, raw Cargo evidence, optional sidecars, and bounded handoff notes.

### `artifact-diff/v0`
What changed between two review points, with separate sections for:
- selected-subject drift
- output-class drift
- origin/path drift
- sidecar drift
- handoff drift

### `artifact-handoff/v0`
Lossy summaries for Release Truth, Inventory, Repro, Support, Host Package, Native Edge, Firmware, Client App, and assistant/editor consumers.

## Recommended rollout
1. Cargo-native binary/library lane
2. doc + package lane
3. build-script uplift lane
4. SBOM-sidecar lane
5. release/repro/support handoff lane
6. productization/import lanes

This should be driven by [`design/artifact-surface-kit.md`](../design/artifact-surface-kit.md), with Tooling Contract and Release Truth importing the result rather than replacing it.

## What makes this epic “epic” rather than incremental
An incremental tool would improve one lane:
- better target-dir scraping,
- better JSON parsing helpers,
- better artifact-dir wrappers,
- or better release-manifest generation.

An epic contribution here instead gives Rust one **portable final-artifact contract** above those lanes.
That is strategically different because it can:
- let Cargo-native outputs, docs/packages, and custom uplift share one artifact subject boundary;
- give Release/Inventory/Repro/Support/Productization tools a reusable handoff instead of bespoke scanners;
- keep selected-subject truth, final-output truth, sidecar truth, release truth, and install truth distinct but linked;
- and absorb future Cargo output features without forcing every downstream layer to reinvent the artifact model.

## Design principles
- **Selected subject truth is not output-path truth.**
- **Origin class is not consumer meaning.**
- **Sidecars attach; they do not replace the artifact.**
- **Release/install stories remain downstream.**
- **Lossiness and instability are explicit.**
- **The kit remains thin.**

## Success conditions
This epic is succeeding when Rust teams can say:
- “this is the exact build subject we selected,”
- “these are the final outputs Cargo exposed for that subject,”
- “here is which output was native, doc/package, or uplifted,”
- “here is where each output was produced and/or copied,”
- “here are the sidecars that actually attach,”
- and “here is what downstream release/repro/support/productization consumers may safely conclude,”

without reconstructing the story from target-dir archaeology, raw JSON streams, CI glue, and release-tool manifests.

## Read this with
- `gaps/final-artifact-surface-identity-selection-outputs-and-handoffs.md`
- `design/artifact-surface-kit.md`
- `design/build-cache-kit.md`
- `design/build-extension-kit.md`
- `design/tooling-contract-stack.md`
- `design/release-truth-stack.md`
- `design/distribution-contract-stack.md`
- `design/inventory-evidence-stack.md`
