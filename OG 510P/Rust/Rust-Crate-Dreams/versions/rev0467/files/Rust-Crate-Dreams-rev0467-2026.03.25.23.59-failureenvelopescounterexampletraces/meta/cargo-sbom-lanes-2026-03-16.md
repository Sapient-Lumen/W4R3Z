# Cargo SBOM lane boundaries — 2026-03-16

This note keeps the archive from collapsing several related supply-chain ideas into one fake “SBOM crate”.

## Main judgment

Rust’s 2026 goals make **Cargo SBOM support** feel newly real.
But the worthy crates here still split into distinct layers:

1. **Cargo-native SBOM precursor capture and normalization**
2. **general sidecar attachment / schema-drift contracts**
3. **publish identity / trusted-publishing / post-publish receipts**
4. **public/private dependency or SemVer release-surface truth**
5. **higher-level provenance / policy / attestation / distribution systems**

Those layers can compose.
They should not be flattened.

## The layers

### 1. P-0125 Cargo SBOM Precursor Workbench Kit

This is the lane for:

- precursor capture locks,
- precursor ingest reports,
- normalized build-graph transforms,
- transform loss / exactness receipts,
- precursor diffs,
- and VEX starter stubs that stay visibly downstream of precursor facts.

This crate answers:

- which precursor files were captured,
- how they were matched to built artifacts,
- which build facts came directly from Cargo,
- and how those facts changed between two builds.

It is the best current candidate for the **boring workflow crate above Cargo’s SBOM precursor feature**.

### 2. P-0479 Cargo Artifact Sidecar Contract Kit

This is the lane for:

- general sidecar attachment rules,
- schema/version labels for sidecars,
- package/release shipping decisions,
- and diffable sidecar presence across builds.

It is broader than SBOM.
It should not own SBOM-specific normalization, VEX starter semantics, or precursor-to-format loss reporting.

### 3. Publish-surface identity crates

This includes proposals like trusted-publishing rehearsal and post-publish receipt joins.

Those crates answer:

- who published,
- under which CI identity,
- what registry receipts exist after publish,
- and whether release identity lines up with expectations.

They are not the same as precursor capture.
A build can have perfect SBOM precursor evidence and still lack trustworthy publish identity receipts, or vice versa.

### 4. Release-surface / public-API crates

This includes public/private dependency boundaries and SemVer witness artifacts.

Those crates answer:

- which dependencies are public API surface,
- whether a release broke SemVer expectations,
- and which release-review bundles are justified.

SBOM inputs can support these workflows, but they do not replace them.

### 5. Policy / provenance / attestation / distribution crates

This includes:

- cargo-policy style gates,
- provenance/attestation suites,
- OCI artifact distribution bundles,
- and signed release-evidence pipelines.

These layers may import precursor or transform outputs, but they should remain explicitly above them.

## Anti-patterns to avoid

### Anti-pattern 1: “SBOM support” means one giant crate

Cargo precursor capture, CycloneDX/SPDX emission, VEX, policy gates, publish identity, provenance attestations, and OCI distribution are **not one crate**.

### Anti-pattern 2: treating sidecar discovery as equivalent to normalized SBOM truth

A sidecar file existing next to an artifact does not by itself say:

- how it was discovered,
- which fields were exact,
- what was normalized away,
- or whether artifact association was ambiguous.

That is why P-0125 and P-0479 should stay separate.

### Anti-pattern 3: pretending format emission is lossless

CycloneDX, SPDX, VEX, and organization-specific policy views should all preserve a visible loss surface.
If a pass cannot say what was exact versus normalized, it is not done.

### Anti-pattern 4: collapsing publish receipts into SBOM capture

Trusted publishing, crates.io post-publish receipts, and registry-side facts are about **release identity and registry truth**, not about what Cargo knew during compilation.

## What future passes should do

When touching SBOM proposals, state explicitly:

1. whether the crate owns **Cargo precursor capture**, **general sidecar attachment**, **publish identity**, **public-API/release truth**, or **policy / provenance / distribution**,
2. which facts are exact Cargo-native inputs versus later normalization,
3. which artifacts another tool author could actually implement against,
4. and where ambiguous artifact matching or format loss forces manual review.

That honesty is part of the product.
