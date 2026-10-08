# rev0049 — publishdryrun-witnesscompact-scopejournal

rev0049 treats public bridge publication as unsafe even after rev0048's bridge shadow, local audit, and redress-GC lanes pass. It folds the publish dry-run branchlet and the public outbox/audit-gap branchlet into one current public-edge path.

The new risk-first guess is:

> A public side effect is not safe because it was shadowed, audited, journaled, compacted, or queued alone; all public-edge evidence must survive compaction and bind to exact scope/request/state before any live write.

Current active surfaces:

- `publishdryrun.py` binds shadow, audit, egress, profile, service, scope, request, payload, action, sequence, previous digest, and diversity before a future public write.
- `witnesscompact.py` compacts audit/witness/redress evidence while preserving hard negatives, refutes, forks, and active redress pressure.
- `scopejournal.py` writes accepted publish/witness observations into a signed previous-linked restart lane.
- `publicoutbox.py` stages exact-scope idempotent public side effects without performing them.
- `auditgap.py` plans local repair or withdrawal when public/audit evidence shows stale state, payload mismatch, missing outbox staging, or hard-negative pressure.
- `auditcompact.py` compacts raw audit receipts while preserving refute and same-family fork evidence so compaction cannot become moderation amnesia.
- `publishdryrunfold.py` and `outboxfold.py` keep both rev0049 branchlets visible and retain rev0048 shadow/audit/redress predecessor history.

Nonclaim: this is not a live publisher, not a SAM transport, not a production DHT, not a global governance system, and not a live public bridge implementation.
