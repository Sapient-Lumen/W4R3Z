# Go / No-Go checklist (remote components)

This checklist is intentionally strict. If a box is unchecked, default to NO-GO.

## Governance
- [ ] Independent witness organizations confirmed and contracted.
- [ ] Incident response authority defined (who can pause remote return).
- [ ] Public disclosure policy and postmortem process agreed.

## Supply chain
- [ ] Reproducible builds for all critical components.
- [ ] Signed provenance for releases (SLSA-style).
- [ ] End-to-end pipeline integrity (in-toto) deployed.
- [ ] Secure update framework (TUF) deployed for clients and servers.

## Crypto / protocol
- [ ] Independent implementations of verifiers exist (>=2 teams/languages).
- [ ] Public test vectors cover inclusion/consistency proofs and ballot proof verification.
- [ ] Threshold cryptography ceremony completed with public report.

## Client risk mitigations
- [ ] Clear safe fallback exists (paper/in-person).
- [ ] “Recorded vs pending vs not recorded” UI is user-tested for comprehension.
- [ ] At least one anti-malware mitigation beyond “trust the browser” (e.g., cast-or-spoil, second-device verify, return codes, or supervised override).

## Observability
- [ ] Public mirrors can rebuild and verify the bulletin board from first principles.
- [ ] Monitors running continuously and publishing signed alerts.

## Resilience
- [ ] Multi-region entrypoints and mirrors tested under DDoS simulation.
- [ ] Partition behavior tested; system fails safe (no conflicting finalization).

## Legal / policy
- [ ] Receipt language reviewed to ensure it cannot be used as proof-of-vote.
- [ ] Privacy assessment completed (metadata, turnout surveillance, logging).
- [ ] Audit and recount procedures mapped to cryptographic artifacts.

