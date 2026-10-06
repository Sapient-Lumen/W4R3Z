# Keyless identity evidence and offline-verification boundary

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, operability  
**Patterns:** Plan→Apply→Receipt, Registry→Diff→Gate  

DeriveBSD already had a Sigstore-shaped lane for answering “who signed this digest?”
The missing piece was a crisp authority boundary.

This doc fixes that boundary for v0.

## Accepted boundary

DeriveBSD keeps **release authority** and **publisher identity evidence** separate.

The authoritative publish lane remains:

- `release.authority.policy`
- `release.publish.receipt`

The supplemental identity-evidence lane is:

- `publisher.identity.receipt`
- `sigstore.bundle`

That means:

- `publisher.identity.receipt` is never enough to publish by itself
- identity evidence may be ignored, optional, or required by `release.authority.policy`
- `release.publish.receipt` should say whether identity evidence was accepted, rejected, unused, or not required

## `publisher.identity.receipt` is evidence-only

The schema now carries `authority_semantics = identity-evidence-only`.
That is not decorative text; it is the archive’s answer to a recurring supply-chain failure mode:

> “It was signed by CI, so we shipped it.”

DeriveBSD should instead say:

- threshold / role-separated publication still comes from `release.authority.policy`
- identity evidence may help explain *who produced the bytes*
- but identity evidence does not replace threshold publish authority

## Bundle-first for `sigstore-keyless`

For `method = sigstore-keyless`, portable verification requires more than an identity string.
A portable receipt must point at:

- `sigstore_bundle_digest`
- `verification_roots_digest`

`sigstore_bundle_digest` carries the mirrored signature/transparency bundle.
`verification_roots_digest` points at the pinned trust-root material used to verify that bundle.

This keeps A/D viable offline and stops B/C from normalizing invisible live-service dependencies.

## Release authority may ask for identity evidence, but only as a supplement

`release.authority.policy` may now declare `identity_evidence` to say:

- whether publisher identity evidence is ignored / optional / required
- which issuers / methods are allowed
- whether bundle-first offline-verifiable material is required

That section constrains publication review.
It does **not** replace role thresholds or publish signatures.

## Release receipts should explain the decision

When identity evidence is consulted, `release.publish.receipt` should carry an `identity_evidence` summary that records:

- the decision (`accepted`, `rejected`, `not-used`, `not-required`)
- the referenced `publisher.identity.receipt` digests

This makes “why was this publish allowed?” answerable from one receipt chain.

## Product-shape fit (A–D without forks)

- **A / fleet host:** keyless identity evidence is useful for dev/test and provenance review, but production promotion should stay threshold-bound and offline-verifiable where required.
- **B / workstation:** keyless evidence is useful for portable app bundles and user-facing explainability; bundle-first keeps verification dependable when disconnected.
- **C / general OS:** the lane stays optional and adapter-friendly, but authority still lives in explicit trust/publish policy rather than ad-hoc CI identity.
- **D / appliance factory / regulatory:** production promotion should assume offline or pinned-root verification material; public-internet availability is not the security boundary.

## Why this is the right narrow decision

This does not try to solve the entire keyless ecosystem.
It does the archive job:

- identity evidence stays useful,
- publish authority stays explicit,
- offline verification stops being an afterthought,
- and the release receipt becomes the explainable join point.

## Related docs

- `adrs/ADR-0077-keyless-identity-evidence-and-offline-verification-boundary.md`
- `docs/290-keyless-signing-and-publisher-identity-receipts.md`
- `docs/333-sigstore-bundles-and-offline-verification.md`
- `docs/260-release-authority-policy-and-key-management.md`
- `spec/publisher.identity.receipt.schema.json`
- `spec/sigstore.bundle.schema.json`
- `spec/release.authority.policy.schema.json`
- `spec/release.publish.receipt.schema.json`
- `spec/examples/publisher.identity.receipt.json`
- `spec/examples/release.authority.policy.json`
- `spec/examples/release.publish.receipt.json`

Last updated: 2026-03-07r216
