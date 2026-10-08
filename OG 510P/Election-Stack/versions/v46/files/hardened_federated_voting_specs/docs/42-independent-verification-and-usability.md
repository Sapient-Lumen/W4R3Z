# 42 — Independent verification and verifier usability

**Track:** A (Deployable core)


E2E systems only achieve their goals if **independent auditors can actually verify** outcomes with reasonable effort and without trusting the vendor.

This document defines verifier diversity requirements and usability guardrails.

## Threats

- Verifier monoculture: a single verifier implementation has a bug, and everyone repeats it.
- “Verifier theater”: verification exists but is too hard for real observers.
- Proof complexity DoS: verifiers are overwhelmed by expensive proofs.

## Normative requirements

### Verifier diversity
- At least **two independent verifier implementations** MUST exist and be usable by third parties.
- Implementations MUST be built from separate codebases or teams to reduce correlated failures.
- Each verifier MUST emit a signed `VerifierReport` covering:
  - software identity (hashes, version)
  - supported crypto suites
  - conformance results on published test vectors
  - verification outcome for the election

### Test vectors
- The project MUST publish test vectors for:
  - inclusion/consistency proofs
  - ZK proof verification
  - tally proof verification
  - evidence bundle manifests

### Cost controls
- Proof systems MUST have predictable verification cost.
- The PBB MUST support pagination and streaming verification so observers can verify incrementally.

## Usability requirements (minimum)
- “Does my receipt appear?” must be a 30-second task.
- If verification fails, the UI must say **FAILED**, not “inconclusive.”
- The system must support offline verification from downloaded evidence bundles.

## Evidence artifacts
- `schemas/VerifierReport.json`
- `artifacts/checklists/verifier-diversity-checklist.md`