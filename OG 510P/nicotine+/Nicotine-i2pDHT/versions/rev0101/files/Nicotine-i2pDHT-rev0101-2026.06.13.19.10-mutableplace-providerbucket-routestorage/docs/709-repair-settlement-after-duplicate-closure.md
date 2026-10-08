# Repair settlement after duplicate closure

A duplicate closure is a useful observation, not final settlement. rev0067 adds `repairsettlement.py` so a closed duplicate conflict must still carry:

```text
repair publish digest
repair ACK digest
duplicate closure digest
remote witness digest
conflict cooldown digest
contradiction memory
sequence/previous links
family/path diversity
```

The lane intentionally rejects or holds:

```text
component not accepted
boundary drift
digest drift
replay
sequence rollback
same-sequence fork
previous-link mismatch
contradiction dropped
hard-negative pressure
low family/path diversity
```

The design guess is that repair settlement is a restart-sensitive local fact. It is not a global claim that the DHT is clean.
