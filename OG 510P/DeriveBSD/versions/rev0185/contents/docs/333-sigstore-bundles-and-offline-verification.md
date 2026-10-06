# Sigstore bundles + offline verification (bundle-first keyless signing)

Keyless signing is compelling because it removes long-lived private keys from the developer/CI loop.
But many “keyless” systems quietly assume the public internet at verify time.

Greenfield advantage for DeriveBSD: **treat verification material as an artifact**.
If a signature depends on a transparency log and a CA, then the *bundle that proves those facts* should be
mirrorable, digest-addressed, and attachable to support/airgap kits.

This doc tightens the “publisher identity” lane from `docs/290-keyless-signing-and-publisher-identity-receipts.md` by:
- standardizing on a **bundle-first** approach for offline/airgapped verification
- pinning the minimum verification inputs we expect to store and mirror


## 1) What a Sigstore bundle buys you

Sigstore’s “bundle” format packages the verification material needed to verify a signature/attestation without
re-querying online services.

At a high level:
- the signature payload is a **DSSE envelope** containing an **in-toto statement**
- the signer uses an ephemeral key that is bound to an OIDC identity via a short-lived Fulcio certificate
- the signing event is recorded in the Rekor transparency log

The Sigstore bundle format explicitly constrains the DSSE envelope (payloadType is `application/vnd.in-toto+json` and
only one signature). Reference: https://docs.sigstore.dev/about/bundle/

Cosign overview (keyless): https://docs.sigstore.dev/cosign/signing/overview/


## 2) Trust roots are still required (and must be mirrorable)

A bundle is not magic: verifiers still need trusted roots for:
- Fulcio (certificate chain)
- Rekor (log public keys)
- CT log keys (where applicable)

Sigstore distributes these through a TUF repository in common workflows (Cosign uses a Sigstore TUF repo for keys and
trusted-root material). References:
- Cosign installation / TUF notes: https://docs.sigstore.dev/cosign/system_config/installation/
- Cosign repo note on airgapped verification and trusted root retrieval: https://github.com/sigstore/cosign

DeriveBSD design consequence:
- treat “trusted roots for verification” as **versioned trust-bundle artifacts** (already aligned with
  `spec/pki.trust.bundle.schema.json` and `docs/304-trust-bundles-and-ca-injection-as-artifacts.md`)
- allow policy to require “bundle verification must use roots pinned in this bundle digest”


## 3) DeriveBSD interop shape

### A) Store the Sigstore bundle as a first-class artifact

Introduce a tiny wrapper artifact that stores the Sigstore bundle JSON (as-is) so it becomes:
- content-addressed
- mirrorable
- attestable

Schema: `spec/sigstore.bundle.schema.json`
Example: `spec/examples/sigstore.bundle.json`

### B) Point publisher identity receipts at the bundle digest

`publisher.identity.receipt` already records identity + transparency coordinates.
Add an optional `sigstore_bundle_digest` so an offline verifier can fetch the bundle from a mirror.

Schema: `spec/publisher.identity.receipt.schema.json` (v0.1)


## 4) Policy notes (avoid common keyless footguns)

Keyless signatures shift the hard problem from “who has the private key” to “what identity claims do we accept”.

Bake in:
- **issuer allowlists** (OIDC issuer is part of the security boundary)
- **identity templates** (repo/workflow/service-account claims are often more stable than email)
- **transparency requirements** (policy can require rekor inclusion coordinates or proof material)

See Sigstore’s end-user bundle verification guidance for the “Instance / Identity provider / Identities” framing:
https://blog.sigstore.dev/cosign-verify-end-user/


## 5) Recommendation: bundle-first by default for portable artifacts

- For portable service bundles and airgap kits, prefer attaching:
  - the signature/attestation itself (DSSE envelope)
  - the Sigstore bundle (verification material)
  - the pinned trusted-root/trust-bundle digest

This keeps verification deterministic and reduces “verification worked yesterday but not today” incidents.

See: `docs/273-airgap-mirror-kits-and-sneakernet-updates.md`, `docs/253-bundle-plans-and-deterministic-exports.md`.

Last updated: 2026-02-26r92
