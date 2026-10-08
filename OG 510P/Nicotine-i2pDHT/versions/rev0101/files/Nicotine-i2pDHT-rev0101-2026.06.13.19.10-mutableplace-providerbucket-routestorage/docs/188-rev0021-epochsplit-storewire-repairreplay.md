# rev0021 — `epochsplit-storewire-repairreplay`

This revision keeps the cube in risk-first DHT design.  It still does not add live I2P/SAM transport and still does not claim a production DHT.

The revision attacks three hard boundaries that become dangerous only after several rounds:

1. **Epoch split-view pressure**: repeated mutable-head observations now detect same-sequence forks, previous-link splits, local-memory stale replay, and weak path/source diversity before an epoch can be treated as stable enough.
2. **STORE/custody wire transcripts**: exact-digest STORE requests, STORE receipts, custody challenges, and custody proofs now ride canonical frame fixtures as a role-complete transcript.
3. **Repair-market replay pressure**: garden repair offers are evaluated across windows so replayed capacity, sequence rollback, useful-refusal pacing, and family monoculture become visible.

The audit/refactor lane makes `surfacefold.py` revision-aware instead of hard-coding the previous revision, and extends the active surface ledger to rev0021.

Core sentence:

```text
Repeated plausibility is a separate attack surface.
```
