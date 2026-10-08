# Audit-gap repair planning

Audit receipts are not truth. They are local evidence. rev0049 adds `auditgap.py` so gaps do not silently collapse into either publication or forgetting.

The planner takes local signals such as:

```text
publication_observed
stale_public_record
payload_mismatch
redress_gap
shadow_accepted
outbox_staged
```

It can decide:

```text
accept_no_gap
accept_repair_plan
accept_withdraw_plan
hold_outbox_not_staged
hold_low_signal_diversity
quarantine_* drift/conflict/hard-negative cases
```

The important behavior is that negative audit-gap evidence needs diversity and exact-scope binding, and repair is blocked when live hard-negative pressure says the safer action is quarantine or withdrawal.
