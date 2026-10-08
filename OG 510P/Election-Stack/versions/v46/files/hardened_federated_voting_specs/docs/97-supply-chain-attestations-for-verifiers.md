# 97 — Supply-Chain Attestations for Verifier Tools

**Track:** A+C (Core + North Star)


## Goal
Observers must be able to answer:
- “Is this verifier binary the one that was audited/reviewed?”
- “Did it come from the expected source and build process?”

## Minimum requirements
- Publish reproducible build instructions for each verifier.
- Publish a signed provenance statement for each release:
  - source repo + commit
  - build system identity
  - dependencies (SBOM where feasible)
  - output artifact hashes

## Recommended (SLSA / in-toto patterns)
- Treat verifier releases like critical infrastructure:
  - hardened CI builds
  - provenance attestations
  - threshold signing or keyless signing + transparency
- Require at least two independent verifiers (see `94-independent-verifier-diversity.md`).

## Where attestations are stored
- In the same Evidence Portal used for election bundles.
- Optionally in an external transparency log for independent auditing.