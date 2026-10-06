# SBOM formats: SPDX and CycloneDX (selection + mapping)

DeriveBSD SBOMs are optional outputs that can be policy-required for certain channels/targets.

## Candidates
- **SPDX**: long-standing standard, strong license compliance lineage; newer 3.x model expands beyond software.
- **CycloneDX**: BOM-first, strong supply-chain features; published as ECMA-424 and widely adopted; has first-class vulnerability/VEX shapes.

## DeriveBSD approach
- Treat SBOM as a signed attestation object:
  - DSSE envelope
  - in-toto statement
  - SBOM predicate payload (SPDX or CycloneDX)

## v1 recommendation
- Prefer emitting **one primary** format for operational simplicity:
  - default: `sbom.format = cyclonedx` (SBOM + vuln/VEX ecosystem)
  - optional: `sbom.format = spdx` (license/compliance-heavy workflows)
- Always support importing/attaching existing SBOMs by digest.

## VEX as a companion object

SBOM inventory alone becomes noisy once vulnerability data is in play.
DeriveBSD should standardize a companion, signable **VEX/VDR-style evidence object** that expresses exploitability context under a specific policy snapshot.

See: `docs/168-sboms-and-vex-as-evidence.md`.

## Minimal mapping requirements
- package/component identity (name, version, supplier)
- source provenance pointers (Lock inputs)
- dependency edges (closure)
- hashes for artifacts and relevant blobs

See RFC-0049. References in `docs/32-curated-references.md`.

Last updated: 2026-02-23
