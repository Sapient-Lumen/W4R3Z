# rev0049 — outboxlane-auditgap-fold

rev0049 keeps public bridge publication in no-network design space and adds a durable local staging seam before any future SAM/I2P or DHT write exists.

The new risk-first claim:

```text
bridge shadow accepted
+ audit quorum accepted
+ redress GC accepted
  ≠ safe public network side effect
  ≠ safe repair plan
  ≠ safe restart replay
```

New active surfaces:

- `src/i2p_dht_lab/publicoutbox.py` — signed, exact-scope, idempotent public side-effect staging.
- `src/i2p_dht_lab/auditgap.py` — local audit-gap repair/withdraw planning without turning audits into truth.
- `src/i2p_dht_lab/outboxfold.py` — rev0049 audit/refactor fold that preserves rev0048 shadow-audit predecessor history.
- `tests/test_rev0049_publicoutbox_auditgap_fold.py` — regression pressure for replay, idempotency conflict, watch debt, hard negatives, and audit-gap repair.

The strongest sentence:

```text
A shadowed public side effect is still not a queued public side effect.
```
