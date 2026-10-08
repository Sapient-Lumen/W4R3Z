# rev0050 — commitbarrier-outboxdrain-publicedgefold

rev0050 pushes the public-edge lane one boundary deeper. rev0049 staged public writes as dry-runs, outbox entries, audit-gap repair plans, witness/audit compaction, and scoped journals. This revision asks the harder question: when all those local surfaces pass, what prevents a future publisher from treating them as a live write permission too early?

The answer in this cube is a two-step no-network boundary:

1. `commitbarrier.py` creates a signed public commit candidate that joins dry-run, outbox, audit-gap, egress, and scope-journal reports at the exact profile/service/scope/request/subject/payload boundary.
2. `outboxdrain.py` creates a signed drain step that binds the accepted commit to the accepted outbox, egress report, and scope journal before a future network publisher may even consider draining the staged side effect.

Both surfaces remain local and shadow-only. They do not write to I2P, SAM, a DHT, a bridge record, or any public substrate.

Strong sentence:

> A staged public side effect is not safe to commit or drain until dry-run, outbox, audit-gap, egress, and restart memory bind to the same idempotency/effect boundary.

## New active surfaces

- `src/i2p_dht_lab/commitbarrier.py`
- `src/i2p_dht_lab/outboxdrain.py`
- `src/i2p_dht_lab/publicedgefold.py`
- `tests/test_rev0050_commitbarrier_outboxdrain_fold.py`

## Risk-first checks added

- component quarantine/hold propagation from dry-run, outbox, audit-gap, egress, and scope-journal reports
- commit candidate bad signature, replay, rollback, same-sequence fork, previous digest mismatch, scope drift, action drift, subject drift, payload drift, and component digest drift
- idempotency replay accepted only when the public effect digest is the same
- idempotency effect conflict quarantined
- outbox drain watch debt, component drift, sequence fork, replay, idempotency conflict, and low family/path diversity
- fold audit preserving rev0049 public outbox/audit-gap predecessor history

## Nonclaims

This is not a live publisher. It is not exactly-once network delivery. It is not a production DHT or bridge protocol. It is a local commit/drain algebra for the riskiest pre-publication side-effect seam.
