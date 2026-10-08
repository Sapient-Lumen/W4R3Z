# rev0078 — summaryreplay-ackclosure-exportfence

rev0078 follows the redacted-summary ACK path past rev0077's ACK ledger, delivery archive, and summary prune fence.

The new seam is restart and export readiness:

```text
summary ACK ledger
+ delivery archive
+ summary prune fence
    ≠ replay-safe after restart
    ≠ locally closed ACK path
    ≠ redacted export fence
```

New active surfaces:

```text
src/i2p_dht_lab/summaryreplay.py
src/i2p_dht_lab/ackclosure.py
src/i2p_dht_lab/summaryexportfence.py
src/i2p_dht_lab/summaryreplayfold.py
tests/test_rev0078_summaryreplay_ackclosure_exportfence.py
```

Strong sentence:

```text
Restart replay, ACK closure, and redacted export are separate local permissions; none may erase contradiction or redaction memory from the delivered-summary path.
```

The revision stays no-network and does not add live I2P/SAM transport. It keeps the design discipline that a locally plausible component report is not permission for the next boundary unless exact scope, request, payload, idempotency, component digests, diversity, and hard-negative memory agree.
