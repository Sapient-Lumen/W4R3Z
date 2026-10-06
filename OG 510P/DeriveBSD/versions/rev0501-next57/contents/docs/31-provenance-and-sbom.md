# Provenance attestations and SBOMs

DeriveBSD emits provenance by default and can optionally emit SBOMs.

## Provenance baseline
Every artifact records:
- Spec/Lock/Plan digests
- toolchain identity
- sandbox policy
- source hashes
- builder identity

Provenance is a signed attestation bound to the artifact digest.
It is valuable evidence, but not by itself a publish-authorization signal.

## Format recommendation
Use an in-toto Statement wrapped in a DSSE envelope.
Predicates:
- SLSA provenance predicate
- Derive Plan predicate (custom)
- SBOM predicate (SPDX or CycloneDX)
- optional verifier summaries such as SLSA Verification Summary Attestations when delegation is useful

## SBOM stance
SBOMs are optional outputs; policy can require them for certain targets or deployments.

See RFC-0014 and ADR-0004.

## Link pointers

- in-toto Statement v1: https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md
- DSSE envelope spec: https://github.com/in-toto/attestation/blob/main/spec/v1/envelope.md
- JCS (manifest digests): https://www.rfc-editor.org/rfc/rfc8785

## SBOM formats pointer

Canonical SBOM format notes live in `docs/75-sbom-formats-spdx-cyclonedx.md` (RFC-0049).

## Attestation formats pointer

Canonical envelope/predicate notes live in `docs/71-attestations-dsse-in-toto-slsa.md` (RFC-0046).

## Workflow policy pointer

Optional in-toto layout-based workflow policy notes live in `docs/202-in-toto-layouts-and-step-policy.md`.

Publication review should treat provenance / SBOM / VSA objects as evidence or verifier outputs, with any publish-time decision summarized separately in `release.publish.receipt`.

Last updated: 2026-03-07r218
