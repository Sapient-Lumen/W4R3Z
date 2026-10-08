# Verifier diversity & independent implementations

**Track:** A (Deployable core)


## Why this exists
In E2E systems, **verification** is part of the security boundary.
If all verifiers share a bug (or a backdoor), universal verifiability collapses (“verifier monoculture”).

This document specifies a multi-implementation verification ecosystem that is harder to subvert.

## 1) Requirements (normative)

1. The election MUST ship at least **two independent verifier implementations**, ideally in different languages and maintained by different organizations.
2. The election MUST publish **test vectors** (Merkle proof vectors, proof transcripts, sample tallies) that all verifiers MUST pass.
3. The federation MUST publish a `VerifierReport` per implementation:
   - build hash
   - dependency lock hashes
   - suite ids supported
   - conformance results

4. For each evidence packet / audit bundle the federation publishes, it SHOULD solicit and publish
   at least two independent packet verification reports (one per verifier):
   - kind: `hfv.verifier.packet_verification_report`
   - schema: `schemas/PacketVerificationReport.json`

## 2) Conformance harness
The spec pack includes a starter set of vectors.
Additions SHOULD include:
- fork/equivocation detection vectors
- replay and reordering tests
- revoting edge cases (if enabled)
- malformed ZK proofs

## 3) Operational posture
- Verifiers SHOULD be reproducibly built.
- Verifiers SHOULD be downloadable via a secure update framework (see 17-supply-chain-and-build-integrity.md).
- At least one verifier SHOULD run fully offline from an audit bundle.

## 4) Public verification events
For high-stakes elections, consider a “verification day”:
- publish the final audit bundle
- encourage independent groups to verify live
- publish signed third-party verification statements
