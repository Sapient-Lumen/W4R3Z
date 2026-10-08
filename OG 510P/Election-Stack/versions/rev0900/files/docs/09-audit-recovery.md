# Audit & recovery

**Track:** A (Deployable core)

> **Read-first:** before treating anything here as deployment guidance, read `166-scope-and-claims-contract.md` and `167-non-claims-and-boundaries.md` (they are binding on interpretation).



## Software independence (non-negotiable)
A software fault or compromise MUST NOT be capable of producing an undetectable change in outcome.

This is why serious recommendations emphasize **human-readable paper ballots** and **risk-limiting audits (RLAs)**.  
source: nasem_securing_the_vote_highlights_pdf

---

## 1) Preferred posture for “real elections”: paper ballot of record + RLAs
### Paper ballot of record
- Voter-marked paper ballots are the gold standard audit trail.
- Voter-verifiable printouts are better than paperless, but come with caveats (voter attention, printer failure, etc.).

source: stark_gentle_introduction_rla_2012_pdf

### Risk-limiting audits
- RLAs provide statistical evidence that the reported outcome is correct, escalating sampling when discrepancies are found.
- If discrepancies exceed thresholds, audits escalate to larger samples or full hand counts.

---

## 2) How the PBB helps even with paper
Even if paper is the ballot of record, the PBB/federation can:
- detect **selective censorship** (who got “recorded” vs who didn’t),
- detect **split views** and tampering attempts via transparency log proofs,
- make election artifacts **publicly auditable** (encrypted ballots, proofs, logs),
- speed up incident detection and postmortems.

---

## 3) Degraded mode / emergency policy (must be pre-written)
If anomalies are detected:
- fail closed for remote return (stop accepting), or
- switch to “deliver/mark only, return via mail/in-person,” or
- extend voting windows and increase safe fallback capacity (subject to law/policy).

**Rule:** never let a degraded mode quietly change security properties; communicate clearly to voters.

---

## 4) Dispute resolution evidence (courts)
Maintain:
- final quorum-cosigned STH(s),
- archived log mirrors,
- cryptographic proofs and verifier outputs,
- chain-of-custody records for paper ballots and audit samples.
