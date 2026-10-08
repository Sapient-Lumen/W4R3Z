# Scope journal restart boundary

`scopejournal.py` makes local memory a first-class boundary after restart.

The journal stores signed, previous-linked observations for one profile/service/scope/request boundary. It can carry publish dry-run reports, witness-compaction reports, audit-quorum facts, hard negatives, and redress memory.

The hard guess is that restart state is not a cache. It is a replayable protocol surface that must reject rollback, same-sequence fork, previous-link mismatch, component digest drift, and cross-scope/request drift.
