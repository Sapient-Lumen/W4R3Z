# Service ticket exact-scope grants

`serviceticket.py` treats service grants as a distinct signed boundary after
service catalog acceptance and load-sheath scheduling.

A service ticket binds:

```text
issuer node/key
sequence and validity window
catalog digest
catalog report digest
load-sheath report digest
service class
caller node id
demand digest
scope digest
object digest
request digest
request-capsule digest
granted units/streams/raw-key budget
previous ticket digest
signature
```

The risky guesses tested here:

- a signed ticket is useless if its catalog/load report changed;
- a ticket for an unscheduled demand should hold, not silently become work;
- a ticket must not grant more work or metadata than the caller requested;
- replay, rollback, same-sequence fork, expired/future windows, bad signatures,
  and exact-scope drift are protocol boundaries.

The ticket is not payment, not trust, and not a global admission token. It is a
local side-effect precondition.
