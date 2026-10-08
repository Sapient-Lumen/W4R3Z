# closure seal after audit

The closure seal is a compact, previous-linked local marker after closure audit. It is intentionally not finality consensus and not a publication token.

It binds:

```text
action
profile/service
scope/request/payload/idempotency
closure audit digest
archive journal digest
prune replay digest
accepted audit marker
contradiction-carried bit
export-boundary bit
family/path family
```

The seal lane rejects component boundary drift, component digest drift, sequence replay/fork/rollback, previous-link mismatch, contradiction drops, low diversity, and hard-negative pressure.

The purpose is to prevent the phrase "closure audited" from becoming a license to forget the trace that made the closure meaningful.
