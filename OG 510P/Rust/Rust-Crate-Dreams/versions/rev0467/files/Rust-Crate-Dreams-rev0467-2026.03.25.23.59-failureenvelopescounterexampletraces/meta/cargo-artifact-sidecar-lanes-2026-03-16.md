# Cargo artifact sidecar lane boundaries — 2026-03-16

This note keeps the archive from flattening several nearby artifact-adjacent ideas into one fake “artifact metadata crate”.

## Main judgment

Cargo now has enough substrate that **artifact sidecars** deserve their own lane.
But the worthy crates here still split into distinct layers:

1. **general artifact handoff / produced-output manifests**
2. **artifact↔sidecar association and shipping policy**
3. **SBOM precursor capture and transform-loss honesty**
4. **publish identity / post-publish receipts**
5. **debuggability support promises and debugger-side consumption**

Those layers compose.
They should not be collapsed.

## The layers

### 1. P-0471 Cargo Artifact Handoff Kit

This is the lane for:

- what primary artifacts a build produced,
- copied-output manifests,
- native/build-script output summaries,
- and downstream CI / package-manager handoff bundles.

It answers:

- what outputs exist,
- which package/target/profile produced them,
- and what another build system or packager should import.

It does **not** need to own the full contract for sidecar schema drift or ship/local/manual-review policy.

### 2. P-0479 Cargo Artifact Sidecar Contract Kit

This is the lane for:

- which companion files belong to which promoted artifact,
- whether that association was exact or conservative,
- which sidecars should ship with the artifact,
- and which schema/version/stability lane each sidecar belongs to.

This crate answers:

- “does this sidecar travel with the artifact?”,
- “how do we know that?”,
- and “what changed in the sidecar surface between two builds?”

It is the best current candidate for the **boring shared layer above raw artifact output and below broader release/provenance systems**.

### 3. P-0125 Cargo SBOM Precursor Workbench Kit

This is the lane for:

- Cargo-native SBOM precursor capture,
- precursor→artifact matching,
- normalized build-graph transforms,
- and transform-loss / exactness receipts for downstream SBOM formats.

It is more specific than P-0479.
A sidecar contract crate may import SBOM precursor sidecars, but it should not absorb SBOM-specific normalization or VEX starter semantics.

### 4. Publish-surface identity crates

This includes trusted-publishing rehearsal and post-publish receipt joins.

Those crates answer:

- who published,
- under which CI identity,
- what registry/index confirmations exist,
- and how local package facts joined with registry facts.

They are not the same as artifact-sidecar contracts.
An artifact can have perfect sidecar receipts and still lack trustworthy publish identity, or vice versa.

### 5. Debug / support-surface crates

This includes docs.rs parity, debuggability support contracts, symbol-sidecar expectations, and toolchain support promises.

Those crates answer:

- whether a project promises split DWARF, PDBs, Natvis, pretty-printers, docs.rs targets, or manual-linker support,
- and whether the local or hosted environment meets those promises.

Some of those facts may show up as sidecars.
That does **not** mean P-0479 should become the debugger-support truth crate.

## Anti-patterns to avoid

### Anti-pattern 1: “artifact metadata” means one giant crate

Produced-output manifests, sidecar association, SBOM precursor capture, publish receipts, and debug-support contracts are **not one crate**.

### Anti-pattern 2: file adjacency equals ship policy

A file sitting next to an artifact does not, by itself, mean:

- it belongs to that artifact,
- it should ship,
- or its schema/stability is appropriate for automation.

That is why P-0479 needs explicit association and attachment receipts.

### Anti-pattern 3: SBOM sidecars stand in for all sidecars

SBOM precursor files are the strongest current example, but a general sidecar-contract crate must still preserve:

- non-SBOM sidecar kinds,
- ship/local/manual-review policy,
- association provenance,
- and schema drift unrelated to SBOM transforms.

### Anti-pattern 4: handoff truth and sidecar truth are the same thing

Knowing that Cargo produced `artifact X` is not the same as proving that `artifact X` owns `sidecar Y` and that `sidecar Y` should ship.

## What future passes should do

When touching artifact-adjacent proposals, state explicitly:

1. whether the crate owns **artifact handoff**, **sidecar contracts**, **SBOM precursor capture**, **publish identity**, or **debug/support promises**,
2. which facts come from stable Cargo messages versus unstable copied-output structure or scanning,
3. which artifact in the bundle carries shipping policy,
4. and where ambiguous association or missing sidecars still force manual review.

That honesty is part of the product.
