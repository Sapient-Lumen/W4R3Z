# AnonSync rev0897 audit

## Heart of the mission

AnonSync is an authority-preserving convergence system. Exact authorized
history, exact durable cutpoints, and live owned capabilities decide identity,
content availability, attempt, retry, receipt, and visible effect. Paths,
handles, clocks, status summaries, and process exit codes are evidence only when
they remain subordinate to those owners.

## Product correction

The product could report durable outbox-clock quarantine but could not invoke
the owner's exact recovery primitive. `rev0897` adds a clock-only writer
transaction and exposes `clock-observe` plus generation-fenced `clock-recover`.
The probe shares the same publication state machine and staged re-attestation as
lease work while spending no claim or dispatch authority.

## Severe database-boundary correction

The audit found that every product database open inherited
`SQLITE_OPEN_CREATE`. A typo in status, send, or recovery could manufacture
empty state. A pre-existing zero-byte file could still masquerade as genesis,
and unconditional `PRAGMA journal_mode=WAL` could rewrite an unrelated database
before its role was proved. Failed or read-only SQLite handles also crossed too
early into the strict connection owner, converting an ordinary targeting error
into the owner's process-integrity fail-stop path.

Every call site now declares `ExistingOnly` or `CreateIfMissing`. Existing-only
commands require nonempty persistent schema and an already-WAL profile without
rewriting it. Creation-capable commands may enable WAL only for schema-empty
bootstrap and cannot rewrite a nonempty wrong-role store. A separate RAII
candidate owns the raw `sqlite3*` until open success, non-nullness, and main-
database writability are proved. `serve-one` now proves TLS, listener, and
anchored membership prerequisites before it may create receiver/effect stores.

## Proof

The real process proof covers missing paths, a zero-byte placeholder, an
unrelated DELETE-mode SQLite database, a creation-capable wrong-role target,
receiver preflight ordering, the full quarantine/recovery lifecycle, mutual TLS,
filesystem publication, receipt, and sender settlement. The SQLite owner test
passes 244 checks. The focused source audits pass 15/15 and 28/28 checks, and the
complete GCC 14 Debug registry passes 215/215 after final dependency closure.

## Waste and remaining work

The full build still required resumed invocations despite a narrow product
slice. Hundreds of fragmented targets and several large translation units remain
a material cloudtainer tax. The next authority correction should be an explicit
store-set `init` command and deployment manifest, followed by a bounded durable
supervisor that consumes status, retry, and explicit clock-recovery policy.
Causal directories/tombstones/renames, reachability/GC, chunking/resume, indexed
scale, at-rest encryption, and a real anonymity/privacy threat model remain
unclaimed.
