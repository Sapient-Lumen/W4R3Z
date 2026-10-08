# Audit quorum transparency witness

`auditquorum.py` is a small local model of transparency-style witnessing for public bridge records.

It intentionally does **not** make a global transparency log.  Instead, it lets a node ask whether several independent witnesses observed the same publication boundary:

```text
profile
service
scope
request
publication digest
checkpoint sequence
checkpoint root
previous checkpoint digest
witness family/path
signature
```

The risky guess is that bridge records will eventually need public observability, but public observability can accidentally become a trusted oracle.  This surface keeps witness power small: witnesses produce signed observations, and local policy decides whether those observations are diverse and consistent enough to use.

The tests catch:

- bad signatures;
- expired/future checkpoints;
- replayed checkpoints;
- same-log same-sequence forks;
- sequence rollback;
- publication-boundary drift;
- low witness/path diversity;
- missing previous-link evidence after sequence one.

The design is inspired by transparency-log consistency thinking, but it remains only a local evidence surface.
