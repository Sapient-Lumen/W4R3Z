# Scope ledger joined advance

`scopeledger.py` binds scope-fence reports, repeated-round probe ledgers, and proof-obligation reports into signed local observations.

The risky bug class is accepting sticky state because each component looked valid in isolation. The joined ledger requires exact:

```text
scope id
object digest
request id
purpose
source/path diversity
monotonic actor sequence
non-replay
no hidden open obligations, unless explicitly accepted as proof debt
```

A valid joined observation is still not global truth. It is restart-sensitive local memory that says a sticky bootstrap or repair step is locally justified.
