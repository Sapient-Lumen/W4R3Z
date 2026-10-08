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