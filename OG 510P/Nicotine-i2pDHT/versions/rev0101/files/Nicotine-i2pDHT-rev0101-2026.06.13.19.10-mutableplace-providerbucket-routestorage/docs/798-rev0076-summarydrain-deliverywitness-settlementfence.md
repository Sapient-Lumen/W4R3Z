# rev0076 — summarydrain-deliverywitness-settlementfence

rev0076 moves one seam after `summarysendcanary-redactiongc-outboxsettlement`.

```text
summary send canary
+ outbox settlement
+ redaction GC
    ≠ summary drain
    ≠ delivery evidence
    ≠ settlement fence
```

The new current path is deliberately no-network. It does not send to SAM, I2P, a DHT peer, or a public bridge. It records local evidence that a future redacted-summary write could be drained, watched for delivery, and fenced for settlement without dropping contradiction or redaction memory.

Strong sentence:

```text
A summary-send canary is not delivery; drain, witness, and settlement fence must each preserve redaction and contradiction memory at the exact boundary.
```

New active surfaces:

```text
src/i2p_dht_lab/summarydrain.py
src/i2p_dht_lab/summarydeliverywitness.py
src/i2p_dht_lab/settlementfence.py
src/i2p_dht_lab/summarydeliveryfold.py
tests/test_rev0076_summarydrain_deliverywitness_settlementfence.py
```

The design pressure stays local and typed: missing ACK is not failure, useful refusal is not success, and a delivery-looking ACK is not settlement until the fence agrees.
