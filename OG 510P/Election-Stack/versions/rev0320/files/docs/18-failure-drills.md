# Failure modes & drills (publish before the election)

**Track:** A (Deployable core)


You need pre-committed procedures for predictable disasters.

## Required drill scenarios (minimum set)
1) Sequencer equivocation detected (fork proof published)  
2) Witness quorum unavailable (partial outage / targeted DDoS)  
3) Region-wide network partition (routing incident)  
4) Credential compromise event (mass revocation attempt)  
5) Client compromise report (malware campaign)  
6) Key ceremony anomaly (trustee failure / suspected insider compromise)  
7) Tally proof failure (ZK verification fails)  
8) Mismatch between crypto record and paper audit (paper mode)

## Human-layer drills (minimum)
In addition to technical failure drills, run **at least three** drills that stress the human process under overload:
- conflicting reports across media + social (what do you publish, when, and with what epistemic tags?),
- forged “official” statement circulating (time-to-refute target),
- selective delivery / geoblock (different audiences see different bytes; drill `selective_delivery_split_view`),
- political pressure to publish unverified claims (practice uncertainty-safe updates; drill `political_pressure_unverified_claims`).
- political pressure to **prematurely expand scope** (e.g., remote ballot return) without satisfying promotion guardrails (drill `premature_promotion_remote_return`).

Canonical scenario registry: `artifacts/registries/drill-scenarios.csv`.

## Pre-commitment requirements
Before polls open, publish:
- pause/extend/fallback decision rules,
- who can trigger each rule and under what evidence,
- how evidence is published (signed statements, logs),
- how voters are informed (multi-channel).

## Safe defaults (recommended)
- If FINAL checkpoints cannot be produced reliably, remote ballots become **provisional**.
- If equivocation is detected, freeze to the last agreed checkpoint and switch to paper/in-person.
- If tally proofs fail, do not certify electronically; escalate to paper audit.
