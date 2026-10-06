# Keyless signing + publisher identity receipts (Sigstore-shaped)

Most ecosystems fail at “everyone signs everything” because key management is hard.
A greenfield OS can preserve strong *release authority* (threshold keys, publish receipts, explicit roles) **and** make publisher identity easier to explain by supporting a **keyless, identity-bound evidence lane**.

Sigstore is the best-known example of this pattern:
- a client creates an ephemeral keypair
- Fulcio issues a **short-lived cert** binding that key to an **OIDC identity**
- the signing event is recorded in a **transparency log** (Rekor)

DeriveBSD accepts that shape, but fixes one hard boundary for v0:
**identity evidence is useful; identity evidence is not publish authority.**

## Goals

- Make “who published this artifact?” easy to answer without long-lived signing keys.
- Treat identity claims as **digest-bound evidence objects** that can be mirrored and verified offline.
- Keep identity evidence composable with release authority, transparency, witnesses, and support bundles.

## Non-goals

- Replacing DeriveBSD’s **release authority** model.
- Letting “signed by CI” become a silent substitute for threshold publish approval.
- Assuming public-internet verification at consume time.

## The evidence object

The canonical object is `publisher.identity.receipt`.

It:
- binds a **subject digest** (artifact or bundle) to an **issuer + subject identity**
- records the method (`sigstore-keyless`, `x509`, `ssh`, `gpg`, `custom`)
- carries `authority_semantics = identity-evidence-only`
- may point at mirrored offline verification material

Schema: `spec/publisher.identity.receipt.schema.json`  
Example: `spec/examples/publisher.identity.receipt.json`

## The hard boundary

### Identity evidence is supplemental, not authoritative

DeriveBSD’s publish authority remains:
- `release.authority.policy`
- `release.publish.receipt`

A `publisher.identity.receipt` may help explain:
- which workflow/service account signed the bytes
- which issuer vouched for that identity
- which transparency coordinates were observed

It does **not** satisfy release-authority thresholds by itself.

### Prefer stable automation identities over fragile human semantics

OIDC claims are policy-dependent.
For automation, human email strings are usually the weakest principal.
Prefer identities like:
- repo/workflow subjects
- service accounts
- workload identities

`publisher.identity.receipt` therefore treats identity as structured evidence, not as a magical trust token.

## Bundle-first for `sigstore-keyless`

For `method = sigstore-keyless`, DeriveBSD is bundle-first.
A portable `publisher.identity.receipt` must point at:

- `sigstore_bundle_digest`
- `verification_roots_digest`

That gives offline verifiers the two things they actually need:
- the mirrored verification bundle
- the pinned trust roots that govern verification

This keeps A/D viable in disconnected or tightly controlled environments and stops B/C from normalizing invisible live-service dependencies.

See: `docs/333-sigstore-bundles-and-offline-verification.md`.

## How it composes with DeriveBSD authority

### `release.authority.policy` may constrain identity evidence

The release-authority lane may optionally declare `identity_evidence` rules such as:
- ignored / optional / required
- allowed methods
- allowed issuers
- required bundle/offline-verifiable material

That is a *supplemental review constraint*, not a replacement for threshold publish authority.

### `release.publish.receipt` should explain whether identity evidence mattered

A publish receipt may carry an `identity_evidence` summary so a reviewer can answer:
- was identity evidence required?
- was it accepted or rejected?
- which `publisher.identity.receipt` digests were consulted?

That turns “why did we trust this?” into a one-receipt question instead of a CI folklore question.

## Practical wins

### 1) Safer dev and third-party lanes

Keyless identity receipts let policy say:
- “accept this workflow identity for dev/test channels”
- “never let identity evidence alone publish to prod”

### 2) Better explainability

Repo/workflow/service-account identities are more legible in review than raw key IDs.
They fit naturally into `derive explain`, support bundles, and supply-chain queries.

### 3) Offline verification that still feels modern

DeriveBSD already has:
- air-gap mirror kits (`docs/273-airgap-mirror-kits-and-sneakernet-updates.md`)
- witness checkpoint receipts (`docs/282-witness-cosigning-checkpoints-and-witness-networks.md`)

Bundle-first publisher identity receipts compose with those lanes instead of bypassing them.

## Risks / sharp edges

- **OIDC semantics are policy-dependent**: issuer + subject + workflow/service identity matter more than human-friendly labels.
- **Availability**: public-good Sigstore workflows often assume the internet.
  - Mitigation: require mirrored bundles + pinned verification roots for portable verification.
- **Over-trust**: teams may still read “signed” as “ship it”.
  - Mitigation: keep `authority_semantics = identity-evidence-only` and keep publish authority threshold-bound.

## Related docs

- `docs/333-sigstore-bundles-and-offline-verification.md`
- `docs/260-release-authority-policy-and-key-management.md`
- `docs/487-keyless-identity-evidence-and-offline-verification-boundary.md`
- `spec/publisher.identity.receipt.schema.json`
- `spec/release.authority.policy.schema.json`
- `spec/release.publish.receipt.schema.json`

Last updated: 2026-03-07r216
