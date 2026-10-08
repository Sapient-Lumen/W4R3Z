# Durable source-manifest restart checkpoint audit — rev1010

## Product reason

AnonSync must synchronize multi-terabyte Linux media trees with bounded memory,
selective synchronization, and delta transfer. Rev1008 made source-side
content-defined manifest construction independent of an attached peer after the
first exact causal operation was discovered, but every process restart discarded
all unfinished source hashing. A cold 4 TiB payload therefore still had to repeat
as many as 131,072 bounded 32 MiB pulses after every restart.

Rev1010 retains one conservative restart checkpoint for the one source manifest
already selected by the existing reconciliation owner. It does not add a global
chunk database, scan the media tree at startup, or make cached state source-byte,
causal, payload, or transfer authority.

## Retained authority chain

The checkpoint lives inside the exact private payload-store root and is named by
one reserved internal basename. Its checksum-framed v2 body binds:

- the payload-store identity digest and exact identity-inode POSIX observation;
- one monotonic checkpoint generation;
- the exact causal file operation ID and canonical path;
- the immutable payload SHA-256, extent, and exact payload-inode observation;
- the content-defined chunking parameters;
- the arbitrary-byte source frontier;
- completed chunk extents and SHA-256 digests;
- provider-independent resumable whole-file and current-chunk SHA-256 states;
- the rolling chunker's gear hash, pending extent, completed count, and terminal
  flag; and
- for a complete record, the canonical reconciliation manifest digest.

The format is bounded by 8,192 chunk records and less than 384 KiB at the
shipping frontier. It is O(chunk count), not constant-size. Invalid magic,
checksum, field lengths, path bytes, digest spelling, metadata, extent sums,
hash continuation, chunker state, chunk count, or disposition fails closed as
unusable acceleration.

The payload-store loader and publisher both re-enter the retained rooted
no-follow authority, establish the current store identity, acquire the existing
store lease, duplicate the reviewed shared open-description bridge, open and
re-prove the exact reserved record, and verify the root and lease again before
returning. Publication uses the existing atomic create/replace owner and then
reopens and parses the named record. The record is excluded from payload and
transient inventory.

## Restart use is not transfer authority

A fresh reconciliation owner does not trust the record directly. Explicit
source-work discovery:

1. loads at most the one bounded checkpoint;
2. performs a targeted SQLite lookup of the exact stored operation ID and
   canonical path rather than loading global history;
3. requires the current retained operation, content digest, extent, and path to
   match;
4. targeted-opens the digest-named immutable payload through the ordinary
   payload-store access owner;
5. re-proves the exact payload inode observation and chunking parameters; and
6. only then restores the in-memory chunker/hash frontier or completed manifest.

Stale operation state, missing bytes, changed inode metadata, malformed records,
or unsupported state discards acceleration and leaves ordinary exact hashing
available. The filesystem-cold status accessor remains effect-free. The shipping
single-owner scheduler invokes one explicit discovery effect before deciding
whether source-local work is pending, so restart recovery does not require a new
peer request.

A complete checkpoint is still only acceleration. Every payload range served to
a peer is independently opened and re-proved through the existing targeted
source path, and the receiver still requires authenticated range digests and the
whole target SHA-256 before publication.

Completion and checkpoint publication have separate failure domains. Hashing may
finish while the optional atomic checkpoint write encounters typed lease
contention or a local publication error. The bounded complete record remains
process-local, and peer-free owner discovery retries it before deciding whether
more source work exists. Another authenticated request is not required merely to
make already-completed work restart-durable.

## Bounded durability cost

The 32 MiB fairness pulse remains unchanged. Publishing an atomic record after
every pulse would impose 131,072 file-sync, rename, and directory-sync sequences
for a 4 TiB source. Rev1010 therefore uses a coarser durability cadence:

- the first nonterminal pulse publishes immediately;
- later active records publish only after another 1 GiB of exact source progress;
- completion always publishes; and
- a pending publication remains bounded and is retried by later owner turns.

After one successful active publication, an ordinary crash loses less than one
1 GiB interval instead of the entire source projection. A typed atomic
publication failure cannot make already re-proved payload bytes unavailable;
the record remains optional acceleration. Identity, codec, rooted-reproof, and
logic failures remain terminal rather than being reclassified as harmless
cache misses.

The total first-pass disk work is not reduced: a 4 TiB source still requires
131,072 32 MiB hash pulses. The completed manifest and offset index remain
O(chunk count) process memory. Rev1010 addresses restart replay and checkpoint
write amplification only.

## Runtime proof

The self-exec regression uses three fresh process images over one durable
payload store:

1. the first process discovers an exact 10 MiB source and publishes an active
   checkpoint at a 1 MiB interior frontier;
2. the second process explicitly discovers that checkpoint without a peer,
   resumes only the remaining 9 MiB, and publishes the complete manifest; and
3. the third process serves the same operation from the complete checkpoint
   without source hashing or a content-defined source scan.

The regression also covers checksum and grammar failures, stale operation/path,
changed same-byte inode, conservative lower-frontier replacement, optional
publication retry, bounded record extent, inventory exclusion, and completion
generation. A deterministic `RLIMIT_FSIZE` fault rejects the final write, proves
the prior active record is unchanged, then requires peer-free discovery to seal
the retained completion and a fresh service to reuse it with zero hashing.
Focused codec, chunker, payload-store, and reconciliation tests bind the same
path.

## Adjacent refactor/audit correction

The payload-store accumulator comment still claimed restart checkpoints existed
only at complete chunk boundaries; rev1010 now records the true arbitrary-byte
frontier. A test name also overstated the record as constant-size. The retained
claim is the exact one: the record is payload-extent independent but bounded
O(8,192 chunks).

The structural descriptor-bridge inventory was updated to include the two new
checkpoint load/publication paths rather than allowing a second root-descriptor
duplication mechanism.

## Explicit nonclaims

Rev1010 does not provide:

- a global, multi-file, or multi-share chunk index;
- automatic startup scanning of the payload namespace or synchronized tree;
- constant-memory completed manifests;
- durability for every 32 MiB pulse;
- zero replay after power loss or storage that lies about synchronization;
- transfer authority from the checkpoint alone;
- rename/move identity, complete directory semantics, conflict UX, selective
  placeholders, quota/ENOSPC policy, Android support, or retention collection;
- hostile same-UID protection; or
- live public Tor/I2P privacy and performance qualification.

The next measured edge is sparse multi-terabyte RSS, allocator fragmentation,
page-cache pressure, checkpoint write amplification, restart replay, and final
manifest/index memory. If the completed O(chunk count) representation dominates,
the next change should page or persist that exact manifest rather than create an
unmeasured global index.

## Validation and release identity

Exact final source passed a fresh GCC 14.2 Debug graph (563/563 build edges), the complete 297/297 registry, and an independent 52/52 product replay. Focused GCC proofs passed 20 checkpoint-codec, 45 content-defined-chunker, 43 true-process restart, 5,001 reconciliation-protocol, 25 response-memory, 20 terminal-state, 737 payload-store, 397 SQLite-owner, 536 folder-owner, 114 sync-once, 2,047 TLS-transport, and 211 reconciliation-service checks. A fresh Clang 17 ASan/UBSan product graph completed 274/274 edges; the exact source rebuilt and reached a no-work state, and all 52/52 product tests passed with leak detection and halt-on-error. No compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic remained. The dedicated checkpoint audit passed 36/36 and the structural authority audit passed 610/610. The exact rev1008 parent SHA-256 matched and its wrapper-aware package verifier passed 41/41. A stale-validator guard that had been pointed at the authoritative build paths was disabled; every interrupted result it caused is excluded from this release evidence.

Archive: `AnonSync-rev1010-2026.08.06.08.49-pulsecheckpoint-execrestart-retryfence-eucryptite.zip`

Codename: `eucryptite`
