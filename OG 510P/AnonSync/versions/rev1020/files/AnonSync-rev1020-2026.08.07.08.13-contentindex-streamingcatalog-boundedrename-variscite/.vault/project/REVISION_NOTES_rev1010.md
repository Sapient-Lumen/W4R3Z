# Revision notes — rev1010

Rev1010 makes the one retained source-side content-defined manifest projection
restart-durable without creating a global chunk database or scanning the media
tree at service startup.

The payload store now owns one checksum-framed, identity-bound checkpoint. An
active record captures the exact arbitrary-byte frontier, completed chunk
records, resumable whole/current-chunk SHA-256 state, rolling chunker state,
causal operation/path, payload observation, and store identity. A complete
record carries the canonical manifest digest. The record is bounded to 8,192
chunks and less than 384 KiB, remains acceleration only, and is excluded from
payload inventory.

A fresh reconciliation owner explicitly discovers at most that one record,
re-proves the exact operation through targeted SQLite path access, targeted-opens
and re-proves the digest-named payload, and only then restores progress. The
shipping peer-service owner performs this discovery before selecting local
source work, so restart recovery no longer waits for another authenticated
request. Filesystem-cold status remains effect-free.

Checkpoint publication is deliberately coarser than the 32 MiB fairness pulse.
The first active pulse publishes immediately, later active records advance every
1 GiB, and completion always publishes. This bounds successful-checkpoint crash
replay to less than 1 GiB while avoiding one atomic fsync/rename/directory-fsync
sequence per 32 MiB pulse. The total hash cost of a cold 4 TiB source remains
131,072 pulses, and the completed manifest remains O(chunk count) memory.

If the final optional publication fails after hashing completes, the bounded
complete candidate remains retained. Peer-free owner discovery retries that
exact candidate before asking whether further source hashing is pending, so
another authenticated request is not required to make the completed manifest
restart-durable.

A true self-exec regression proves one process publishes a 1 MiB interior
checkpoint, a second process resumes only the remaining 9 MiB without a peer,
and a third process reuses the completed manifest with zero new source hashing.
A separate `RLIMIT_FSIZE` regression forces the final atomic write to fail,
proves the prior active record remains unchanged, then requires peer-free
completion publication and fresh-service zero-hash reuse. The focused codec,
chunker, payload-store, reconciliation, source-scheduler, and structural audits
bind the same boundary.

The user-visible rev1009 handoff was not materialized in this cloudtainer. The
exact sealed source parent for rev1010 is rev1008; rev1010 does not claim an
unavailable rev1009 source delta.

Validation: Exact final source passed a fresh GCC 14.2 Debug graph (563/563 build edges), the complete 297/297 registry, and an independent 52/52 product replay. Focused GCC proofs passed 20 checkpoint-codec, 45 content-defined-chunker, 43 true-process restart, 5,001 reconciliation-protocol, 25 response-memory, 20 terminal-state, 737 payload-store, 397 SQLite-owner, 536 folder-owner, 114 sync-once, 2,047 TLS-transport, and 211 reconciliation-service checks. A fresh Clang 17 ASan/UBSan product graph completed 274/274 edges; the exact source rebuilt and reached a no-work state, and all 52/52 product tests passed with leak detection and halt-on-error. No compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic remained. The dedicated checkpoint audit passed 36/36 and the structural authority audit passed 610/610. The exact rev1008 parent SHA-256 matched and its wrapper-aware package verifier passed 41/41. A stale-validator guard that had been pointed at the authoritative build paths was disabled; every interrupted result it caused is excluded from this release evidence.

Archive: `AnonSync-rev1010-2026.08.06.08.49-pulsecheckpoint-execrestart-retryfence-eucryptite.zip`

Codename: `eucryptite`
