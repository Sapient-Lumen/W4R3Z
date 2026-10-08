# Conflict cooldown duplicate pressure

`conflictcooldown.py` keeps repeated duplicate-conflict observations from laundering themselves into repeated repair or retry publication.

It consumes:

```text
remote_witness_ledger_report
repair_outbox_report
ConflictCooldownObservation entries
```

Observation kinds:

```text
remote_conflict
benign_witness
repair_staged
useful_refusal
```

The cooldown lane can:

```text
activate conflict cooldown
release after benign diverse evidence
hold while repair outbox is pending
hold while observations are pending
quarantine replay/fork/drift/hard-negative pressure
```

The goal is not to punish a peer or create reputation. It is purely local flow control: repeated conflict evidence should make the node more careful, not more spammy.
