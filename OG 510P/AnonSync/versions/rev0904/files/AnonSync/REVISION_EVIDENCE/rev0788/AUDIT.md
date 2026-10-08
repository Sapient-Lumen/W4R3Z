# rev0788 deep audit — SQLite connection publication and release truth

## Heart of the mission

AnonSync is not primarily a transport or file-copy program. It is an
evidence-authorized convergence engine. Every transition must be attributable
to exact, bounded evidence that survives the failure mode relevant to that
transition. Live connection capabilities prevent accidental use of the wrong
process/thread/connection generation; durable receipts and content-bound
records authorize restart convergence. Neither category substitutes for the
other.

## Findings and corrections

### 1. False release lineage

The previous turn named a rev0787 ZIP that does not exist in the cloudtainer.
The recovered tree contains an audit traceback caused by an unterminated regex
and an explicit `passed: false` result. Rev0788 therefore uses two lineage
anchors:

- **archived parent:** verified rev0786 ZIP, SHA-256 recorded in LINEAGE.json;
- **recovered candidate:** a source projection copied from the unfinished
  rev0787 tree and frozen as Git baseline commit
  `923d302edc572e0db04ba607b50bc40612d7c954`.

No release claim depends on an imaginary rev0787 archive.

### 2. Diagnostic evidence promoted to authority

Rev0787 used `SQLITE_FCNTL_VFSNAME` and accepted a textual component match.
SQLite states that file-control operations may do nothing and that VFSNAME is
for diagnostics. The implementation now compares the pointer returned by
`SQLITE_FCNTL_VFS_POINTER` to the exact `sqlite3_vfs*` selected before open.
This closes URI VFS override and same-name substitution across the open
boundary, subject to the process-level trust assumption that the VFS registry
is not maliciously mutated concurrently.

### 3. Hidden URI configuration channel

A `file:` URI can override the fourth `sqlite3_open_v2` VFS argument and the
cache flags, and can request `mode=memory`, `nolock=1`, or `immutable=1`. URI
parsing can be enabled globally. Checking only `SQLITE_OPEN_URI` is therefore
not a sealed policy. The new boundary rejects the scheme independently of the
flag and rejects alternate storage/cache/mutex flags.

### 4. Busy-handler lifetime laundering

SQLite has one busy-handler slot per connection and no getter. A destructor
that clears the slot cannot know whether the slot still contains the callback
it installed. The rev0787 scope could destroy another operation's handler. The
abstraction and callback-budget context were deleted. A future replacement must
be owned by the same connection-operation authority that serializes all handler
mutation, or must use an immutable connection-wide policy.

### 5. Build architecture as correctness debt

The extracted boundary is 267 lines and its focused adversarial test is 297
lines, but it links against a 24,530-line domain unit. Sanitized compilation of
that one unit could not complete inside repeated 30-minute foreground windows;
a persistent process was required. This is not merely inconvenience: slow
feedback suppresses sanitizer frequency, encourages partial validation, and
made earlier revisions vulnerable to publishing before final gates. Split by
invariant ownership, not by arbitrary helper count.

## What the new evidence does and does not prove

It proves, for the successful process-local connection generation:

- canonical requested access flags;
- no accepted URI/memory/shared-cache/NOMUTEX control plane;
- a concrete main-database filename from the VFS;
- realized read-only/read-write mode;
- presence of a connection mutex;
- exact top-level VFS object identity; and
- publication ordering after all checks.

It does **not** prove that storage media honors sync, that a custom trusted VFS
is honest, that the pathname and native descriptor cannot be raced after open,
or that a transaction is durably committed. Those need path-identity controls,
VFS fault injection, transaction evidence, and crash reconstruction.

## Quantified migration debt

The deterministic owner-generation inventory reports:

- 70 legacy raw transaction-control sites;
- 40 raw open sites outside the migrated domain;
- 17 raw prepare sites;
- four legacy `sqlite3_close_v2` sites;
- three raw-pointer compatibility declarations; and
- one generic owner-borrow mint.

The dominant source units remain:

- `src/sync_domain.cpp`: 24,530 lines;
- `src/sqlite_replay_ledger.cpp`: 4,466 lines;
- `src/sync_peer_ingress_lifecycle.cpp`: 3,833 lines.

The next refactor should extract an invariant-owned checkpoint repository and
connection factory from `sync_domain.cpp`, then migrate one complete transaction
family at a time so the static inventory monotonically decreases.
