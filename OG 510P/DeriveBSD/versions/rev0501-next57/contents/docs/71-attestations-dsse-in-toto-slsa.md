# Attestation formats: DSSE + in-toto statements + SLSA predicates

DeriveBSD wants attestations that are:
- portable
- verifiable offline
- composable across ecosystems

The current best practice “stack” is:
- **in-toto Statement** (payload)
- **DSSE Envelope** (signature wrapper)
- optional bundling (e.g., sigstore bundle) + transparency log inclusion proofs

## DSSE / Envelope
The in-toto attestation repository defines the DSSE envelope schema (“Envelope layer specification”).
Sigstore bundle format requires a DSSE envelope whose payloadType is `application/vnd.in-toto+json` and typically contains a single signature.

The in-toto Attestation Framework describes these objects as authenticated metadata intended for **policy engines**. They become meaningful only when a verifier or policy engine inspects them.

## SLSA attestation model
SLSA documents an attestation model that recommends:
- DSSE envelope
- in-toto statement
- predicates such as provenance or SPDX

SLSA is equally explicit that attestations do not do anything unless somebody performs **verification**. Its Verification Summary Attestation (VSA) is a verifier's judgment about evaluation against policy, not a replacement for a product's own release authority.

## DeriveBSD posture

- Use DSSE-wrapped in-toto statements for:
  - build provenance
  - reproducibility test results
  - vulnerability gate results (optional)
  - runtime launch decisions (policy digests)

- Store attestations as first-class objects in the store (content-addressed), but do not bake them into store-path identity unless policy says so.
- Keep attestation existence separate from verifier judgment and separate again from final release authority.

- Optional: use **in-toto layouts** to express and verify required workflows (who can do which steps, and how they chain), emitting a Derive receipt for explainability.
  See `docs/202-in-toto-layouts-and-step-policy.md`.

References:
- in-toto specs, DSSE envelope spec, sigstore bundle format, SLSA model in `docs/32-curated-references.md`.

Last updated: 2026-03-07r218
