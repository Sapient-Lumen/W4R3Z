# Assurance plan (how we earn trust)

**Track:** A (Deployable core)


This system is only as trustworthy as the evidence it produces and the discipline with which it is built and operated.

## 1) Formal specification (machine-checkable)
Model critical invariants (e.g., in TLA+/PlusCal or similar):
- append-only log + consistency,
- “only last ballot counts” (if revoting),
- tally correctness (“tallied as recorded”),
- safety under partitions (no conflicting finalization without witness quorum).

## 2) Independent implementations (key paranoia lever)
Require at least:
- 2 independent verifier implementations for log proofs,
- 2 independent verifier implementations for ballot proof/tally proof verification,
- differential testing across implementations with shared test vectors.

## 3) Public test vectors and continuous monitoring
- Publish deterministic test vectors for:
  - Merkle inclusion/consistency proofs,
  - ballot well-formedness proofs,
  - threshold decryption proofs.
- Run independent monitors that:
  - mirror the PBB,
  - verify every published STH,
  - publish signed alerts on any inconsistency.

## 4) Secure development and supply chain evidence
Adopt:
- NIST SSDF (SP 800-218): https://csrc.nist.gov/pubs/sp/800/218/final
- C-SCRM guidance (SP 800-161r1): https://csrc.nist.gov/pubs/sp/800/161/r1/final
- in-toto pipeline integrity: https://www.usenix.org/system/files/sec19-torres-arias.pdf
- TUF-secured updates: https://theupdateframework.github.io/specification/latest/

## 5) Third-party review and red teaming
- multiple cryptography reviews focused on ZK and threshold protocols,
- multiple systems reviews focused on ops and abuse cases,
- bug bounty program,
- pre-election red team exercises (servers, client distribution, witness gossip, key ceremonies).

## 6) Certification alignment
For U.S. contexts, map artifacts to:
- EAC E2E Protocol Evaluation Process: https://www.eac.gov/voting-equipment/end-end-e2e-protocol-evaluation-process
- VVSG 2.0 Test Assertions (current): https://www.eac.gov/sites/default/files/2026-01/VVSG_2.0_Test_Assertions_v1.4.pdf

## 7) “Assume breach” drills (mandatory)
Run recurring exercises:
- key compromise simulation,
- witness partition simulation,
- DDoS simulation and safe failure,
- insider misuse scenario,
- emergency pivot to paper/in-person workflow.
