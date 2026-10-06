# SBOMs and VEX as evidence objects (policy-bound, digest-addressed)

DeriveBSD already binds **bytes** (Lock → Plan → Artifact) into verifiable identities.
The missing step for day-0 “why/what/where-from” is to make **inventory + vulnerability context** first-class, signable outputs.

This document tightens how SBOMs (inventory) and VEX (exploitability context) plug into the Derive pipeline.

## Standards (don’t invent a format)

- **CycloneDX** is an international standard (ECMA-424) for bills of materials, with explicit supply-chain and vulnerability shapes.
- CycloneDX explicitly supports VEX-style exploitability communication.
- **SPDX 3.0.1** provides an SBOM model with a Security profile, including a vulnerability class.
- **OpenVEX** is a minimal VEX format (JSON-LD) designed to be embeddable and interoperable; it is explicitly designed to fit into attestation workflows.
- CISA’s “minimum requirements for VEX” captures the core semantics operators expect from VEX.

## DeriveBSD objects

### 1) `sbom.statement`

A signed evidence object whose predicate is an SBOM document.

- subject: `{ artifact_digest, plan_digest }`
- predicate: CycloneDX JSON (default) or SPDX JSON (optional)
- envelope: DSSE + in-toto Statement (existing DeriveBSD attestation lane)

If you want a small Derive-native wrapper (for indexing and cross-links), use `spec/sbom.statement.schema.json`.

### 2) `vex.statement`

A signed evidence object that expresses exploitability status *in context*.

- subject: `{ artifact_digest, plan_digest, sbom_digest }`
- predicate:
  - CycloneDX vulnerability/VEX shapes, or
  - OpenVEX documents
- binds to:
  - the vulnerability DB snapshot digest used by policy
  - the policy decision record digest

This avoids a common failure mode: treating “vulnerable component present” as equivalent to “exploitable here.”

If you want a small Derive-native wrapper (for indexing and cross-links), use `spec/vex.statement.schema.json`.

## v0 recommendation

- Default SBOM output: **CycloneDX JSON** (inventory + broad tooling; standardized).
- Optional SBOM output: SPDX (license/compliance-heavy workflows).
- Prefer VEX payloads that are widely understood:
  - CycloneDX VEX, or
  - OpenVEX for minimal/noise-reduction workflows.

## Identity + freshness

SBOMs should be **deterministic** from the closure proof and artifact digest.
VEX is intentionally **non-deterministic over time** (new vulns; new assessments), so:

- SBOM digest can be treated as a stable artifact companion.
- VEX statements must be timestamped, policy-bound, and treated as “current best assessment,” not as an immutable property of the artifact.

## Where this plugs in

- SBOM selection/mapping: `docs/75-sbom-formats-spdx-cyclonedx.md`
- Provenance lane: `docs/71-attestations-dsse-in-toto-slsa.md`
- Vulnerability snapshot + query receipts: `docs/60-vulnerability-intel-and-gates.md`
- Vulnerability-verification release boundary: `docs/491-vulnerability-verification-evidence-and-publish-gate-boundary.md`
- Policy decision records: `docs/93-policy-decision-records.md`
- Verification surfaces: `docs/92-verification-matrix.md`

## References

- CycloneDX standard (ECMA-424): https://ecma-international.org/publications-and-standards/standards/ecma-424/
- CycloneDX spec overview: https://cyclonedx.org/specification/overview/
- CycloneDX VEX capability: https://cyclonedx.org/capabilities/vex/
- SPDX 3.0.1 spec: https://spdx.github.io/spdx-spec/v3.0.1/
- OpenVEX spec: https://github.com/openvex/spec
- OpenVEX attesting notes (embedding in in-toto): https://github.com/openvex/spec/blob/main/ATTESTING.md
- CISA VEX minimum requirements (PDF): https://www.cisa.gov/sites/default/files/2023-04/minimum-requirements-for-vex-508c.pdf

Last updated: 2026-03-07r220