# Wake from amnesia rev0076

Start here:

1. Read `docs/798-rev0076-summarydrain-deliverywitness-settlementfence.md`.
2. Run `tests/test_rev0076_summarydrain_deliverywitness_settlementfence.py`.
3. Inspect `src/i2p_dht_lab/summarydrain.py`, then `summarydeliverywitness.py`, then `settlementfence.py`.
4. Use `src/i2p_dht_lab/summarydeliveryfold.py` to confirm the current path.

The current boundary chain now ends:

```text
summary outbox -> redaction archive -> publish fence -> summary send canary -> redaction GC join -> outbox settlement -> summary drain -> delivery witness -> settlement fence
```
