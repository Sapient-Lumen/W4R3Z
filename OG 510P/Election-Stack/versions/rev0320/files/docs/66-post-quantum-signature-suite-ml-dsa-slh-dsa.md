# Post-quantum signature suite (ML-DSA / SLH-DSA) and hybrid transition

**Track:** A (Deployable core)


Election evidence must remain verifiable for long periods. This document updates the PQC plan
to include finalized NIST post-quantum signature standards.

## Standards

- **FIPS 204 (ML-DSA)** — module-lattice based signatures
- **FIPS 205 (SLH-DSA)** — stateless hash-based signatures (SPHINCS+ family)

## Hybrid signatures (recommended transition profile)

During migration windows, evidence objects (STHs, checkpoints, EPBs, notarizations, packages) SHOULD
use **hybrid signatures**:

- classical signature (e.g., Ed25519 / P-256) AND
- ML-DSA signature (FIPS 204) AND/OR SLH-DSA signature (FIPS 205)

Rationale:
- early PQC deployments benefit from defense-in-depth
- hash-based SLH-DSA provides algorithmic diversity against lattice surprises

## Operational notes

- PQC signatures are larger; plan bandwidth and storage for receipts and evidence bundles
- Verifier diversity is critical: at least two independent verifiers must implement the same suite set

## References

- NIST CSRC: FIPS 204 final
- NIST CSRC: FIPS 205 final
- NIST news: finalization announcement