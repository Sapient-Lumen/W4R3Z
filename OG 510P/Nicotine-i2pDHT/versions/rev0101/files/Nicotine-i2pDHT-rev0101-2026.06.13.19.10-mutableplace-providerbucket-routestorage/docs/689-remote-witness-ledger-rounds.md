# Remote witness ledger rounds

`remotewitnessledger.py` turns rev0064 remote witness evidence into repeated-round local memory.

A single delivery-repair mesh report can say a duplicate delivery is benign or conflicting under remote witnesses. rev0065 asks the harder question: what happens when those observations repeat, replay, drift, or drop contradiction memory?

The lane records signed-ish toy `RemoteWitnessRound` markers with:

```text
kind
sequence
previous_digest
action/profile/service/scope/request/payload/idempotency boundary
delivery_repair_mesh_digest
idempotency_mesh_digest
retry_publish_digest
egress_journal_digest
witness digests
family/path family labels
contradiction_carried
```

The ledger accepts:

```text
benign duplicate round
remote conflict round
```

It holds:

```text
no remote rounds
absent/mixed rounds
low family diversity
low path diversity
```

It quarantines:

```text
component not accepted
boundary drift
digest drift
replay
sequence rollback
same-sequence fork
previous-link mismatch
conflict evidence that drops contradiction memory
hard-negative pressure
```

The design guess is that remote witness data should be useful, but not authoritative. It is local evidence that can guide repair, cooldown, and future publication staging.

remote witness ledger needle.
