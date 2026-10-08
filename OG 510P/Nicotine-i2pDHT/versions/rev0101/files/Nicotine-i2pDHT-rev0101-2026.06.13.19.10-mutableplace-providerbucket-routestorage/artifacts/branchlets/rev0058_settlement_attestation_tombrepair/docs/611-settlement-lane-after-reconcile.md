# Settlement lane after reconcile

`settlementlane.py` turns rev0057's reconcile decision into signed, previous-linked local memory.

The lane distinguishes:

```text
commit_settled
abort_settled
retry_held
dead_letter_held
quarantined
```

The important rule is that retry is not terminal cleanup. If an effect reconcile report accepts retry, the settlement entry must carry `dead_letter_required = true`. Dropping dead-letter memory during retry is treated as a local corruption / laundering attempt.

Settlement entries bind:

```text
action
profile/service
scope/request/payload/idempotency
effect reconcile digest
dead-letter digest
retry-quorum digest
attestation-pack digest
sequence / previous digest
family / path family
```

This is intentionally local. It is restart memory and side-effect discipline, not network consensus.
