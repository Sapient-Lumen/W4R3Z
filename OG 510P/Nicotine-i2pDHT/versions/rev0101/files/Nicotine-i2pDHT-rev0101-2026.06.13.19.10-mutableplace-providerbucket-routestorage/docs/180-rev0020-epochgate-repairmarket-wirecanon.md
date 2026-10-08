# rev0020 — `epochgate-repairmarket-wirecanon`

This revision keeps the cube in risk-first DHT design.  It does not add live I2P/SAM transport and does not claim a production DHT.

The revision attacks three hard boundaries:

1. **Epoch-gated mutable heads**: mutable control-plane heads now need local monotonic history, previous-digest linkage, time-window checks, and path/source diversity before acceptance.
2. **Repair market without money or authority**: garden nodes can advertise bounded repair capacity, but selection rejects bad signatures, one-family abundance, tombstone gaps, and unbounded useful-refusal loops.
3. **Canonical wire envelopes**: future network messages now have deterministic signed frame fixtures for payload digests, TTLs, request ids, flags, and transcript digests.

The audit/refactor lane adds `surfacefold.py`, which folds current-revision docs, public-surface pointers, active surface-ledger entries, and stale artifact stems into one pass/fail report.

Core sentence:

```text
Mutability, repair capacity, and wire framing are safety boundaries, not plumbing details.
```
