# Keyless signing + publisher identity receipts (Sigstore-shaped)

Most ecosystems fail at “everyone signs everything” because key management is hard.
A greenfield OS can preserve strong *release authority* (threshold keys, TUF-like metadata) **and** also make casual publishing safer by supporting a **keyless, identity-bound signing lane**.

Sigstore is the best-known example of this pattern:
- a client creates an ephemeral keypair
- Fulcio issues a **short-lived cert** binding that key to an **OIDC identity**
- the signing event is recorded in a **transparency log** (Rekor)

Sigstore’s docs describe keyless signing and the role of Fulcio/Rekor.

References:
- Cosign signing overview: https://docs.sigstore.dev/cosign/signing/overview/
- Cosign quickstart: https://docs.sigstore.dev/quickstart/quickstart-cosign/


## Goals

- Make “who published this artifact?” easy to answer without long-lived keys.
- Treat identity claims as **evidence objects** that can be stored, mirrored, and verified offline.
- Integrate with existing DeriveBSD lanes:
  - transparency logs + witness checkpoints
  - trust policies
  - multiparty approvals

## Non-goals

- Replacing DeriveBSD’s **release authority** model.
  - Channel metadata + publish receipts remain the real authority surface.
  - Keyless signing is an *auxiliary identity lane*.

## The evidence object

Introduce `publisher.identity.receipt`:

- binds a **subject digest** (artifact or bundle) to an **issuer+subject identity**
- records the method (`sigstore-keyless`)
- includes transparency log coordinates (and optionally an inclusion proof bundle)

Schema (v0.1): `spec/publisher.identity.receipt.schema.json`

Example: `spec/examples/publisher.identity.receipt.json`

## What this enables (practical wins)

### 1) Safer third-party caches and PR artifacts

You may accept unsigned artifacts from untrusted sources today because the alternative is friction.
Keyless identity receipts let policy say:
- “accept artifacts from *this* CI workflow identity for dev channels”
- “never accept for prod channels”

### 2) Human-legible accountability

Unlike raw key IDs, OIDC identities (repo/workflow/service-account) can be meaningful in reviews.
This helps in `derive explain` and in “why did we trust this?” workflows.

### 3) Air-gapped verification that still feels modern

DeriveBSD already has:
- air-gap mirror kits (`docs/273-airgap-mirror-kits-and-sneakernet-updates.md`)
- witness checkpoint receipts (`docs/282-witness-cosigning-checkpoints-and-witness-networks.md`)

A `publisher.identity.receipt` can carry enough material (or pointers to a mirrored bundle) so verification does not require a live callout.

## How it composes with DeriveBSD’s authority model

### Trust policy integration

Trust policy can optionally map identity receipts into allow/deny decisions:
- allow identities only for certain channels/namespaces
- require multiparty approvals for “promotion” even if identity is present

See: `docs/46-cache-trust-model.md`, `spec/trust.policy.schema.json`.

### Not a replacement for release authority

Release publish remains:
- threshold keys
- policy-defined publish rules
- receipts bound to a release capsule

See: `docs/260-release-authority-policy-and-key-management.md`, `spec/release.publish.receipt.schema.json`.

### Transparency and split-view defense

If the identity lane depends on a transparency log, we should treat log checkpoints as verifiable inputs.
DeriveBSD already has:
- optional transparency proofs
- witness checkpoint cosigning

See: `docs/131-sigsum-lightweight-transparency.md`, `docs/282-witness-cosigning-checkpoints-and-witness-networks.md`.

## Risks / sharp edges

- **OIDC semantics are policy-dependent**: “email” is not a stable principal; prefer workflow/service-account claims.
- **Availability**: keyless signing systems often assume the public internet.
  - Mitigation: treat identity receipts as optional; mirror bundles for offline verification.
- **Over-trust**: developers may assume “signed == safe”.
  - Mitigation: keep separation: identity evidence ≠ promotion authority.

## Open questions

See also: `docs/333-sigstore-bundles-and-offline-verification.md`.

- What is the minimal “offline verifiable bundle” format we want to standardize on?
- Should identity receipts be eligible for witness checkpointing (so offline fleets can verify against a known checkpoint set)?
- How should we bind identity receipts into provenance attestations (in-toto predicate field vs sidecar evidence graph node)?

Last updated: 2026-02-26r92
