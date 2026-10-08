# Assurance plan (how we earn trust)

**Track:** A (Deployable core)


This system is only as trustworthy as the evidence it produces and the discipline with which it is built and operated.

**Meta-assurance:** the archive/spec/tooling can be wrong. Track A deployments and reviews should plan for verifier disagreement and spec repair loops; see `docs/243-archive-self-threat-model-and-spec-correctness.md` and `artifacts/playbooks/spec-error-response-playbook.md`.


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
- NIST SSDF (SP 800-218) (`xref: nist_sp800_218_final_html`)
- Track SSDF revisions as they progress (e.g., SP 800-218r1 IPD) (`xref: nist_sp800_218_r1_ipd_html`)
- C-SCRM guidance (SP 800-161r1) (`xref: nist_sp800_161r1_final_html`)
- in-toto pipeline integrity (`xref: usenix_intoto_pipeline_integrity_pdf`)
- TUF-secured updates (`xref: tuf_spec_latest_html`)

## 5) Third-party review and red teaming
- multiple cryptography reviews focused on ZK and threshold protocols,
- multiple systems reviews focused on ops and abuse cases,
- bug bounty program,
- pre-election red team exercises (servers, client distribution, witness gossip, key ceremonies).

## 6) Certification alignment
For U.S. contexts, map artifacts to:
- EAC E2E Protocol Evaluation Process (`xref: eac_e2e_protocol_evaluation_process_page`)
- VVSG 2.0 Test Assertions (current) (`source: eac_vvsg2_test_assertions_v1_4_pdf`)

## 7) “Assume breach” drills (mandatory)
Run recurring exercises:
- key compromise simulation,
- witness partition simulation,
- DDoS simulation and safe failure,
- insider misuse scenario,
- emergency pivot to paper/in-person workflow.