# Summary delivery witness

`summarydeliverywitness.py` separates delivery observations from drain readiness.

Observation kinds include:

```text
ack_delivered
useful_refusal
missing_ack
nack
payload_mismatch
redaction_ok
contradiction_memory
```

This distinction matters. A missing ACK is watch pressure. A useful refusal is backoff pressure. A NACK is negative evidence. A payload mismatch is quarantine pressure. None of those states may be collapsed into a single boolean called delivery.

The lane remains no-network and local. It provides typed evidence for a future summary settlement boundary without pretending to be a production ACK protocol.
