# AnonSync rev0840 next work

## P0 — classify and seal every machine serializer

Use `inventory/LOCALE_SENSITIVE_SERIALIZATION.json` as a starting point, not as an
automatic verdict. For each `std::ostringstream` site, decide whether it emits diagnostics
or protocol/persistence bytes. Machine serializers should have one invariant owner,
classic or otherwise explicit locale, deterministic number rules, byte budgets, and a
test that perturbs the global locale. Prioritize:

1. signed effect-transition intent construction in `sqlite_replay_ledger.cpp`;
2. replay-ledger JSON lines and journals in `replay_ledger.cpp`;
3. operator/status JSON in `sync_operator_cli.cpp`;
4. validation reports in `reporting.cpp`; and
5. remaining JSON/signing streams in `runner.cpp` and `json_codec_crypto.cpp`.

Do not silently call current hand-written JSON “canonical.” Either define a local exact
format contract or adopt/test an appropriate canonicalization scheme.

## P0 — make heartbeat oversize failure operationally observable

The current fail-closed ceiling prevents self-unreadable publication. Add explicit
per-field byte limits at the producer boundary, especially for `reason` and paths. Return
a typed oversize cause, preserve the last valid heartbeat when appropriate, and publish a
separate bounded failure receipt or operator event. Test crash/restart behavior at
65,535, 65,536, and 65,537 bytes and with multi-byte UTF-8 near the boundary.

## P1 — reduce the adapter's dependency on the broad core model

The codec is now small, but the adapter still includes `anonsync_core.hpp` and preprocesses
40,884 lines. Move the daemon heartbeat option/result subset into a dedicated domain
header or introduce a narrow view produced by the daemon owner. Preserve the one-way
boundary and the audit that every serialized field maps exactly once.

## P1 — authenticate lifecycle evidence without confusing it with authority

Define who may write and verify a heartbeat, how keys bind to device/service generations,
how replay and rollback are detected, and how revocation works. Authentication should
reduce forgery and denial-of-service risk but must not replace durable checkpoint owner
generation or exact local process observation.

## P1 — executable convergence algebra

Classify durable operations as commutative/order-sensitive, idempotent/single-use,
monotone/retracting, causally dependent/independent, and coordination-free/coordinated.
Build a small deterministic reference model that generates duplicate, reordered,
partitioned, retried, concurrent update/delete, restart, and key/schema-epoch traces.
Differentially compare production C++ transitions against that model.

## P1 — crash-cut protocol oracle

Enumerate write, sync, truncate, WAL/journal, rename, directory-sync, sidecar, receipt,
and external publication cuts. Evaluate SQLite, manifests, receipts, checkpoints,
staging files, and externally visible effects as one recovery protocol rather than only
checking database structural validity.

## P2 — hostile input isolation and privacy mission

Move hostile SQLite/document interpretation into disposable workers with descriptor,
CPU, memory, wall-clock, syscall, and namespace restrictions. Separately define payload
confidentiality, metadata leakage, enrollment, key epochs, rotation, revocation,
recovery, forward secrecy, post-compromise recovery, backup, and erasure. Authentication
alone is not anonymity.
