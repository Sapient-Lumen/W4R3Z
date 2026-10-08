# Wake from amnesia — rev0050

Start here if memory is gone:

- The cube is designing a generic mutable DHT over I2P, still no live SAM/I2P transport.
- Garden nodes give capacity, not truth.
- Public bridge publication is the current risk lane, but still only shadow/no-network.
- rev0049 staged public side effects with dry-run, public outbox, audit gaps, witness/audit compaction, and scope journals.
- rev0050 adds the commit barrier and outbox drain lane.

Key invariant:

> A staged public side effect is not safe to commit or drain until dry-run, outbox, audit-gap, egress, and restart memory bind to the same idempotency/effect boundary.

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_rev0050_commitbarrier_outboxdrain_fold.py
```

Then run the evidence scripts before packaging.
