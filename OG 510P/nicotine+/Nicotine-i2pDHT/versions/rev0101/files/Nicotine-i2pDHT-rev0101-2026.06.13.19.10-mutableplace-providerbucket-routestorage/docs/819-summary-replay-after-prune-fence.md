# Summary replay after prune fence

`summaryreplay.py` turns rev0077's ACK ledger, delivery archive, and prune fence into restart-replay evidence.

The replay markers carry:

```text
ack ledger digest
delivery archive digest
summary prune fence digest
accepted ACK/archive/prune marker digests
restart generation
previous restart generation
redaction memory
contradiction memory
family and path-family hints
```

Replay accepts only when the restart generation advances, the component digests bind to one exact boundary, sequence/previous links are intact, and redaction/contradiction memory survives.

This is still not remote truth. It is local restart evidence.
