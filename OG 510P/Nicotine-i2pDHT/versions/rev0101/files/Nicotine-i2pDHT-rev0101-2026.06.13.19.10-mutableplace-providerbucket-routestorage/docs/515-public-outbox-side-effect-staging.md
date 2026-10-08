# Public outbox side-effect staging

The public outbox is a no-network staging lane. It exists because future live publication will need crash/restart memory, idempotency, and exact boundary binding before a public bridge update can be sent.

A `PublicOutboxEntry` binds:

```text
action
profile_id
service_name
scope_digest
request_digest
payload_digest
bridge_shadow_digest
audit_quorum_digest
redress_gc_digest
outbox_effect_digest
idempotency_key
sequence
previous_entry_digest
family_id / path_family
signature
```

The lane rejects:

- component digest drift
- scope/request/payload drift
- action drift
- same-sequence forks
- idempotency-key conflicts
- missing family/path diversity
- uncarried watch debt
- hard-negative redress pressure hidden behind a convenient queue attempt

This is not exactly-once networking. It is the place where future network side effects must become idempotent and auditable before they are allowed to become real.
