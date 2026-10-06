# ADR-0077: Keyless identity evidence and offline-verification boundary

Date: 2026-03-07
Status: Accepted

## Context

DeriveBSD already had a promising keyless-signing lane:

- `publisher.identity.receipt` for digest-bound identity evidence,
- `sigstore.bundle` for mirrored verification material,
- and `release.authority.policy` / `release.publish.receipt` for the real publication authority path.

But the boundary was still too soft in three ways:

- operators could still read “keyless signed” as implicit publish authority,
- the release-authority lane had no typed place to say whether identity evidence was ignored / optional / required,
- and the keyless examples still allowed a portability gap where a receipt might exist without the mirrored bundle and trust roots needed for offline verification.

That is exactly the kind of drift DeriveBSD is supposed to resist.
If identity evidence quietly becomes release authority, or if air-gapped A/D shapes inherit a public-internet assumption through Sigstore-shaped tooling, the archive stops being coherent across product shapes.

## Decision

DeriveBSD will treat keyless publisher identity as a **supplemental evidence lane**, never as silent release authority.

The accepted v0 boundary is:

1. `publisher.identity.receipt` is **identity evidence only**.
   It may explain *who signed a subject digest*, but it does not satisfy `release.authority.policy` thresholds by itself.

2. `release.authority.policy` remains the authoritative publish/halt/rotate surface.
   It may optionally declare an `identity_evidence` section that says whether publisher identity evidence is ignored, optional, or required for a namespace/channel.

3. `release.publish.receipt` may carry an `identity_evidence` summary that records whether identity evidence was accepted, rejected, unused, or not required, plus the referenced `publisher.identity.receipt` digests.

4. For `method = sigstore-keyless`, DeriveBSD is **bundle-first**:
   a portable `publisher.identity.receipt` must point at both:
   - `sigstore_bundle_digest`
   - `verification_roots_digest`

   That keeps offline verification material mirrorable instead of assuming live Fulcio/Rekor/TUF lookups.

5. `verification_roots_digest` points at the governing trust-root material for verification (for example a pinned `pki-trust-bundle` or equivalent trust-root artifact).

6. Identity evidence is policy-shaped, not authority-shaped:
   - prefer stable workload/service identities over fragile human-email semantics for automation,
   - allow issuer restrictions,
   - and keep production promotion in the threshold publish lane.

## Consequences

### Positive

- “signed by CI” no longer risks being interpreted as “authorized to publish”.
- A/D can verify mirrored keyless evidence without inheriting public-internet assumptions.
- B/C can still use keyless evidence for dev channels, portable bundles, and accountability.
- Release receipts become more explainable: they can show whether identity evidence was part of the decision.

### Negative / trade-offs

- The release-authority schema grows one more optional section.
- Portable keyless evidence now requires carrying one more digest join (`verification_roots_digest`).
- Some ecosystems that treat online Sigstore verification as enough will look more convenient than DeriveBSD’s offline-first posture.

## Non-goals

This ADR does **not** decide:

- the exact matcher language for identity templates,
- the final issuer-allowlist UX,
- whether public-good Sigstore, private Sigstore, or non-Sigstore keyless systems are preferred,
- or witness-network quorum for all identity-evidence transports.

Those remain follow-on policy and implementation work.

## Why this shape

This is a narrow coherence move:

- keep publish authority in the threshold lane,
- keep identity evidence cheap and useful,
- require portable verification material for the keyless adapter lane,
- and make the release receipt say what happened.

That is enough to stop “identity evidence” from quietly turning into “ship it”.
