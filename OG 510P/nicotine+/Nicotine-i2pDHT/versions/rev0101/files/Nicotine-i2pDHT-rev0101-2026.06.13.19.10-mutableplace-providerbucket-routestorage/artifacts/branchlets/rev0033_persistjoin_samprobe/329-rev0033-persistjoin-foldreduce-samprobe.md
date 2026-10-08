# rev0033 — persistjoin / foldreduce / samprobe

rev0033 continues the risk-first DHT cube by moving from locally valid component reports to restart-safe and probe-safe joined boundaries.

The core sentence for this revision is:

```text
A restart boundary and a router probe are side-effect boundaries, not plumbing.
```

## Risk-first surfaces

- `persistjoin.py` joins persisted reload state, journal replay, checkpoint assessment, scope-ledger state, and store-debt state before sticky local memory can advance after restart.
- `samprobe.py` builds and classifies a no-network SAM probe transcript for a future local streaming-first harness. Router-unavailable is a safe explicit outcome; external SAM endpoints, datagram-primary dependency, transient destinations, option drift, and reply-shape errors are not.
- `foldreduce.py` is the audit/refactor lane. It makes rev0033 current surfaces visible while reducing fold sprawl to a current fold with predecessor fold regressions.

## Nonclaims

This still does not implement live I2P/SAM transport, a production DHT, a production database, or a production SAM client. The probe transcript is intentionally no-network. The persistence join is a local safety model, not consensus.
