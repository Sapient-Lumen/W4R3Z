# Simulator status — rev0026

The simulator is now a working automated beta with multiple guardrails:

```text
public DecisionFrame interface
split agent/transition RNG
mulligan agency
promotion gate
statistical gate
replay traces
C++ trace checker
C++ shadow rollout checker
```

The biggest simulator-facing change in rev0026 is RNG separation for public games.  This is a correctness/fairness improvement, not a rules change.

The C++ shadow rollout path is a cutover rehearsal.  It shows that current public-game traffic can be mirrored by the C++ transition microkernel in bulk.  Python still remains authoritative for observations, legal-frame construction, mulligans, and RNG transcripts.

Current trust level:

```text
automated play: yes
promotion-gated smoke comparisons: yes, with caveats
strategic claims: only after larger nontruncated samples
full C++ authority: not yet
```
