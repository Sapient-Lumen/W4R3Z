# Sigstore bundles + offline verification (bundle-first keyless signing)

Keyless signing is compelling because it removes long-lived private keys from the developer/CI loop.
But many “keyless” systems quietly assume the public internet at verify time.

Greenfield advantage for DeriveBSD: **treat verification material as an artifact**.
If a signature depends on a transparency log and a CA, then the *bundle that proves those facts* should be mirrorable, digest-addressed, and attachable to support and air-gap kits.

This doc tightens the publisher-identity lane from `docs/290-keyless-signing-and-publisher-identity-receipts.md` by standardizing on a **bundle-first** approach.

## 1) What a Sigstore bundle buys you

A Sigstore bundle packages the verification material needed to verify a signature or attestation without re-querying online services.

At a high level:
- the signature payload is a message signature or DSSE envelope
- an ephemeral signing key is bound to an identity via a short-lived Fulcio certificate
- the signing event is anchored in Rekor

DeriveBSD consequence:
- treat that bundle as a first-class mirrorable artifact
- do not hide it behind transient CI logs or live service lookups

Schema: `spec/sigstore.bundle.schema.json` (`sigstore.bundle`)  
Example: `spec/examples/sigstore.bundle.json`

## 2) Trust roots are still required

A bundle is not magic.
Verifiers still need the trust-root material that governs:
- Fulcio certificate validation
- Rekor log verification
- other trusted transparency / timestamp authorities where applicable

DeriveBSD therefore requires portable keyless identity receipts to point at both:
- `sigstore_bundle_digest`
- `verification_roots_digest`

`verification_roots_digest` points at pinned trust-root material such as a `pki-trust-bundle` or equivalent trusted-root artifact.

## 3) Why DeriveBSD insists on bundle-first

Bundle-first solves the archive problem, not just the CLI problem:

- **offline A/D viability** — disconnected or regulated lanes cannot assume live Fulcio/Rekor/TUF access
- **deterministic support** — support bundles can carry the exact material a verifier used
- **explainability** — reviews can point at digests instead of hand-waving about “whatever Cosign fetched today”
- **mirror hygiene** — air-gap kits and portable release bundles can carry complete verification inputs

## 4) Release authority still governs promotion

Bundle-first does **not** make keyless evidence authoritative.
The real publish lane is still:
- `release.authority.policy`
- `release.publish.receipt`

Keyless evidence is supplemental.
It may be ignored, optional, or required by release policy, but it does not replace threshold publish authority.

## 5) Recommended archive posture

### Portable artifacts

For portable service bundles, dev artifacts, and air-gap kits, prefer carrying:
- the signature or attestation payload
- the Sigstore bundle
- the pinned trust-root digest used for verification
- the resulting `publisher.identity.receipt`

### Review surfaces

When identity evidence affects publication, `release.publish.receipt` should say so explicitly through an `identity_evidence` summary.

### A–D fit

- **A:** prefer offline-verifiable supplemental identity evidence; production promotion remains threshold-bound.
- **B:** use keyless evidence for explainability and portable bundles, not ambient trust shortcuts.
- **C:** keep the lane optional and adapter-friendly, but preserve bundle-first portability.
- **D:** assume production verification may happen under pinned-root or offline conditions.

## Related docs

- `docs/290-keyless-signing-and-publisher-identity-receipts.md`
- `docs/260-release-authority-policy-and-key-management.md`
- `docs/487-keyless-identity-evidence-and-offline-verification-boundary.md`
- `spec/publisher.identity.receipt.schema.json`
- `spec/sigstore.bundle.schema.json`
- `spec/pki.trust.bundle.schema.json`

Last updated: 2026-03-07r216
