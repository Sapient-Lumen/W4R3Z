# Safe-start joined boundary

`safestart.py` joins three reports:

```text
NegotiationReport
MigrationReport
SamTraceReport
```

Each can be locally valid and still not authorize sticky state or future transport side effects by itself. Safe-start binds them to:

```text
session id
scope id
object digest
request id
purpose
```

Current tests cover:

- successful joined safe start;
- quarantined negotiation blocking start;
- quarantined migration blocking start;
- rejected SAM trace blocking start;
- soft-drop migration accepted only as explicit watch-listed start.

This is intentionally not a real session protocol. It is a seam where future live transport code should land only after the exact joined-boundary behavior is stable.
