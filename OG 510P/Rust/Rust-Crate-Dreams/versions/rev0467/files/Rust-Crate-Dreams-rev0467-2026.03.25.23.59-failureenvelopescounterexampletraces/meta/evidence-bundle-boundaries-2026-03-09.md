# Evidence bundle boundaries note — 2026-03-09

This pass exists to resist a quieter failure mode inside the archive:

> once a proposal says “bundle”, future revisions start silently mixing container rules, attestation syntax, signature material, and publication infrastructure into one pseudo-layer.

That is not a sharper proposal.
It is an amnesia trap.

## Main judgment

For **P-0256 Evidence Bundle Core Kit**, the missing crate should now be read as four distinct layers:

1. **core bundle substrate** — deterministic packing, manifest vocabulary, redaction receipts, explainable verification, semantic diffing,
2. **embedded attestation/signature lanes** — DSSE envelopes, COSE objects, Sigstore bundles, or similar imported materials,
3. **domain profile contract** — what a conformance, reproducibility, verification, or debugging profile requires above the core,
4. **optional publication/transparency lane** — OCI, SCITT, or other external distribution and trust infrastructure.

The sharper product is the small reusable layer at **(1)** plus clean contracts for **(2–4)**.

## Why this boundary matters now

The ecosystem now has better pieces than it did even a year ago:

- in-toto explicitly documents bundle/envelope/statement/predicate layering,
- Sigstore explicitly documents a bundle format for verification material and signed content,
- SCITT is clarifying publication and transparency architecture,
- and Rust already has crate substrate for ZIP packaging, COSE, Sigstore work, and JCS.

That means future revisions should stop acting as if Rust still mainly lacks raw primitives.
The sharper missing value is the boring receiver-facing **coordination artifact** above them.

## Practical rule for future passes

When a proposal wants to emit a portable bundle, it must say explicitly:

1. what the **core manifest/container** owns,
2. which **signature or attestation lanes** it embeds or references,
3. what the **domain profile** adds beyond the core,
4. and whether any **publication/transparency** system is required, optional, local, or entirely out of scope.

Do **not** let a proposal silently flatten:

- local shareable bundles,
- DSSE envelopes,
- Sigstore verification material,
- COSE signing lanes,
- profile-specific reports,
- and external SCITT/OCI publication

into one vague “signed bundle format”.

## Healthy vocabulary to preserve

- **bundle substrate** — stable pack/unpack/diff/redact/verify rules
- **profile contract** — domain-required reports and entry kinds
- **attestation lane** — imported signature/predicate material
- **publication lane** — external distribution / transparency / registry story
- **review pack** — human-facing rendering above imported evidence

## What a worthy P-0256 bundle is allowed to say

- “the bundle verified locally, but external trust-root or transparency checks were intentionally deferred to caller policy,”
- “this profile embeds a DSSE envelope and a Sigstore bundle, but the core crate is not re-specifying their semantics,”
- and “this export is shareable-redacted and intentionally unsigned because the workflow is a local support handoff, not a publishable attestation.”

That honesty is part of the product.

## Sources

- https://in-toto.io/docs/specs/
- https://github.com/in-toto/attestation/blob/main/spec/v1/envelope.md
- https://docs.sigstore.dev/about/bundle/
- https://datatracker.ietf.org/doc/draft-ietf-scitt-architecture/
- https://www.rfc-editor.org/rfc/rfc8785
- https://docs.rs/sigstore/latest/sigstore/
- https://docs.rs/coset/latest/coset/
- https://docs.rs/serde_jcs/latest/serde_jcs/
- https://docs.rs/zip/latest/zip/
