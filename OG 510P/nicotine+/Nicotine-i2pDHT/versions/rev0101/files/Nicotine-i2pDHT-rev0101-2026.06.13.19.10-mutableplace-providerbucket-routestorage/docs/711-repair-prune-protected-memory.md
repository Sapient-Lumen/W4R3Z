# Repair prune protected memory

`repairprune.py` gates soft pruning after repair settlement and closure archive.

Allowed:

```text
soft_repair_trace_prune
```

Forbidden:

```text
drop_remote_witness
drop_cooldown
drop_contradiction
drop_settlement
drop_hard_negative
```

The important design decision is that pruning is a side effect. It may reduce soft repair trace weight only when protected evidence remains archived: settlement, contradiction, remote-witness, and cooldown facts must survive.

repair prune needle.
