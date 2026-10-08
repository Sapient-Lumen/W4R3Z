# 94 — Independent Verifier Diversity

**Track:** A (Deployable core)


## Requirement
For any E2E-verifiable deployment, require:
- **at least two** independent verifier implementations,
- and a public process to reproduce verifier builds and compare outputs.

## Why
A single verifier bug, library vulnerability, or supply-chain compromise can invalidate “universal verifiability” socially, even if the cryptography is correct.

## Implementation guidance
- Provide a reference verifier (open source).
- Provide an independently developed verifier (different language/runtime).
- Publish shared test vectors and expected outputs.
- Require signed `VerifierAttestation` for each verifier build used for public claims.

## Suggested minimum verifiers
- ElectionGuard reference verifier implementation(s).
- An independently developed verifier (e.g., academic/NGO).

## Publication
Include verifier binaries (or reproducible build instructions) inside ObserverKit bundles, or publish them with content hashes pinned in the EPB.