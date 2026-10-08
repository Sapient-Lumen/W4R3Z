# Work meter garden contribution pressure

Garden nodes give. The DHT should help them give predictably without turning receipts into money, status, or global reputation.

`workmeter.py` models local work events:

```text
served_head
served_witness
served_provider_proof
served_repair
served_seed_gate
refused_usefully
dropped_invalid
```

The work meter rewards fresh, diverse served work and tolerates useful refusal. It does not let refusal-only windows look healthy. It also quarantines replayed receipts, bad signatures, and one-family flood pressure.

The purpose is operator/local planning, not global scoring:

```text
healthy_contribution
watch_refusal_heavy
watch_under_diverse
quarantine_receipt_replay
quarantine_family_flood
quarantine_refusal_only
quarantine_invalid_event
drop_empty_window
```

Useful refusal remains a positive local evidence type, but not a proof of contribution by itself.
