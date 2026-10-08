# Outbox drain / commit receipts

`outboxdrain.py` is a no-network boundary between a staged public outbox entry and any future public write. It models two phases:

```text
prepare -> local drain intent exists, but no commit
commit  -> local commit receipt exists, still no network claim
```

A drain receipt binds:

```text
profile/service
scope/request/payload
accepted public outbox report
accepted outbox entry digest
publish dry-run report
SAM trace report
scope journal report
idempotency key
drain effect digest
sequence and previous receipt
family/path-family hints
signature
```

Risk tests added in rev0050 cover component watch debt, replay, sequence rollback, previous-link mismatch, same-sequence fork, action drift, payload drift, digest drift, phase regression, and idempotency conflicts.

A commit receipt is still local evidence. It does not prove the write happened on a network.
