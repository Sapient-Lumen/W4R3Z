# Rev1004 bounded terminal payload-verification continuation audit

## Product question

Rev1003 bounded same-path predecessor projection, but a completed staged target
was still SHA-256 verified in one owner call. Fixed memory did not make that
turn acceptable for a file measured in terabytes: it retained the exclusive
payload-store lease through an unbounded read and exposed restart amplification,
long scheduler stalls, and uncontrolled page-cache pressure.

Rev1004 preserves exact whole-target SHA-256 while limiting one terminal owner
call to **32 MiB** with a fixed 64 KiB read buffer. The continuation survives
restart and is carried by reconciliation protocol generation 8 until the exact
staged inode is published. It does not use raw hash state in a mutable pathname
as publication authority.

## Retained design

### Complete data first, computation progress second

The basename of `.anonsync-payload-prefix-v1-...` remains the durable received-
data cutpoint. Ordinary ranges retain the existing order: authenticate the
range digest, write the exact range, `fsync(2)` the staged file, atomically move
the basename to the new committed prefix, refresh the permitted rename ctime
transition, and re-prove the exact pathname and inode.

Terminal SHA-256 state is not created until that basename names a complete file
whose physical size equals the exact target size. Rev1004 deliberately does not
feed the network buffer into whole-file SHA-256 and does not add a second
per-range readback. Terminal verification reads the exact complete staged inode
once in sequential bounded steps.

### Fixed, identity- and inode-bound two-slot journal

Each staged content digest may have one canonical private journal named
`.anonsync-payload-prefix-verification-v1-<sha256>`. The journal consists of
exactly two fixed-width slots. Each checksum-framed slot binds:

- the payload-store identity digest and exact private single-link identity-file
  metadata;
- a nonzero monotonic generation;
- the target content SHA-256 and exact total extent;
- the exact private single-link metadata of the complete staged-prefix inode;
- a nonterminal verified offset; and
- a canonical provider-independent `ResumableSha256Checkpoint` whose byte count
  equals that offset.

Every valid slot in a reused journal must match the current store, target, and
total extent. The latest valid generation is selected; conflicting equal
generations fail closed. A torn newest slot can leave the prior valid slot.
Unused hash-buffer bytes are canonical zeroes through the shared resumable
SHA-256 codec.

The journal is bounded computation evidence only. It is excluded from payload,
semantic transient, retention, and reclaim roots. Its exact byte extent and
entry count are still bounded, its basename is recognized by all payload-root
observers, fresh product-store bootstrap rejects preexisting journal influence,
and successful or reconciled publication removes the matching journal.

### One bounded terminal step

The terminal owner opens the exact complete prefix through the descriptor-rooted
store authority and holds the exact exclusive store lease. A usable journal is
accepted only when its staged-prefix metadata equals that opened inode. Missing,
malformed, foreign, or stale state is replaced by generation 1 at the initial
SHA-256 checkpoint; no complete legacy-prefix rebuild occurs.

The owner reads at most
`kSyncReplicaFilePayloadStoreMaximumTerminalVerificationBytesPerStep` (32 MiB)
from the current verified offset using `pread(2)` and a fixed 64 KiB buffer. It
re-proves the descriptor metadata, exact staged pathname, store identity, and
lease before progress can publish.

For a nonterminal step, the alternate journal slot is written and synchronized,
then independently reopened and parsed. A crash during that write falls back to
the older valid slot, so at most one 32 MiB computation step is repeated. The
complete staged data is never shortened because computation metadata is absent
or damaged.

For the final step, no terminal state is serialized. The current
`ResumableSha256` instance produces the exact whole-file digest in process. A
mismatch unlinks the exact invalid staged inode and journal and publishes
nothing. A match still does not publish immediately: the owner performs the
ordinary complete final namespace scan, re-proves the exact journal and staged
inode observations, checks capacity and durable-name absence, then no-replace
renames that exact opened inode under the trusted digest and synchronizes the
directory.

### Explicit generation-8 obligation

Generation 7 could not represent “all bytes received, local whole-file proof
unfinished.” An early rev1004 integration therefore advanced the source cursor
at the final range while the receiver returned local `Progress`. That made the
remaining proof obligation disappear across the protocol boundary.

Generation 8 permits one canonical payload continuation at the exact total
extent. The final payload response keeps the prior operation cursor, carries the
same exact file operation, and sets `next_offset_bytes == total_size_bytes`.
Subsequent requests cannot carry a cached delta-manifest digest. Their responses
repeat one exact operation, preserve the prior cursor and continuation, set
`has_more`, and contain no payload ranges or metadata-only admission. The source
therefore performs zero payload opens, range copies, source windows, or payload
bytes during terminal verification turns.

The receiver calls the separate terminal-continuation API, accepts zero network
bytes, and admits the operation only after local publication. A source-changed
cutpoint or operation mismatch remains fail closed. Generation 8 is a protocol
generation change; mixed generation-7/generation-8 operation is not claimed.

## Crash and failure transitions

1. **No journal or unusable journal:** preserve the complete staged prefix,
   install an initial bound slot, read at most 32 MiB, and return progress.
2. **One valid slot:** resume its exact offset and hash state.
3. **Torn newest slot:** fall back to the older checksum-valid slot, repeating
   at most one 32 MiB computation step.
4. **Foreign or stale binding:** treat the journal as disposable, restart from
   offset zero, and never bridge the foreign state into the current inode.
5. **Staged inode drift:** reject the checkpoint; the current complete inode
   must be re-observed and verification restarts boundedly.
6. **Uncommitted physical tail:** truncate only bytes beyond the basename-bound
   data cutpoint before terminal work.
7. **Final digest mismatch:** remove the exact invalid staged owner and its
   journal; no digest-named payload appears.
8. **Crash after payload rename but before journal cleanup:** the durable payload
   wins; the next exact reconciliation removes the obsolete transient state.

## Runtime evidence before final sealing

The clean focused codec regression passes **20 checks**. It proves exact slot and
journal widths, state round trip, nonterminal-only state, two-slot rotation,
torn-slot fallback, equal-generation conflict rejection, checksum and framing
rejection, canonical basename grammar, and the public 32 MiB frontier.

The clean focused payload-store regression passes **696 checks**. Its rev1004
matrix proves a 32 MiB-plus-tail target stops at the first checkpoint, survives
owner restart, completes only the remaining tail, keeps the journal outside
semantic transient accounting, replaces a malformed journal with one bounded
step, rejects the terminal sentinel on the range API, detects final staged-byte
mismatch, cleans invalid state, and enforces hidden-journal capacity.

The clean focused protocol and service regressions pass **4,999** and **194**
checks. They prove canonical generation-8 framing, exact total-offset handoff,
negative response shapes, a 48 MiB content-defined transfer whose local proof
spans two bounded steps, zero source payload work on the terminal page, final
payload publication, and causal operation admission only after that proof.

## Adjacent refactor and rejected work

The final source removes unused helpers from a rejected per-range SHA checkpoint
model. That model mixed received-data commit and whole-file computation state,
required complicated one-range catch-up, and still had an unbounded missing-
journal rebuild. A separate rejected prototype encoded raw resumable hash state
in a mutable pathname. Neither design remains in the release source.

The audit also rejected the cursor-advancing generation-7 integration and a
stale-object validation tree that did not rebuild the real service regression.
A fresh Clang build then exposed an executable present in the sanitizer compile
inventory but absent from the final-link inventory. The codec test now receives
both instrumentation and runtime linkage, and the focused audit parses that
link inventory explicitly. Final validation must use exact-source builds and
no-work re-attestation.

## Explicit nonclaims and next risk

The byte and memory bound does not by itself make terminal verification
multi-terabyte efficient. Every incomplete 32 MiB step currently causes a
payload-cold peer request/response and re-observes the staged-prefix namespace.
For a multi-terabyte target, high route latency and a large payload namespace can
therefore dominate work even though no source payload bytes are retransmitted.
The next product correction should retain the exact proof while decoupling local
terminal advancement from peer round trips and avoiding a whole payload-root
traversal on every nonterminal step. A targeted exact-inode continuation with a
complete final scan is one candidate, but it must preserve crash and namespace
failure semantics.

Source-side target-manifest construction can also still read a complete source
in one owner call. Process-local chunk projections are not a durable/global
index. Target-scale sparse multi-terabyte RSS, page-cache, restart,
disk-amplification, high-latency route, and controlled-ENOSPC measurements
remain incomplete. Rename/move identity, complete directories, selective
placeholders and automatic eviction, Android lifecycle/storage adapters, and
live public Tor/I2P qualification remain product work.

## Release cutpoint

Validation: `Exact rev1004 source passed a fresh GCC 14.2 Debug complete graph with 555/555 configured build edges, followed by exact-source CMake regeneration and bundled-SQLite no-work re-attestation; all 288/288 registered tests and an independent isolated 48/48 product replay passed. Focused GCC proofs passed 20 terminal-state-codec, 696 payload-store, 4,999 reconciliation-protocol, 194 reconciliation-service, 536 folder-owner, 397 SQLite-owner, and 2,044 TLS-transport checks. Source audits passed 38/38 bounded terminal-verification-continuation checks and 567/567 structural authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph compiled its 266-edge configured dependency set across bounded resumptions; the first final link exposed that the new codec test was present in the sanitizer compile inventory but absent from the final-link inventory, the target graph was corrected, 28 exact-source relink edges and a no-work re-attestation passed, and all 48/48 registered product commands passed serially with leak detection and halt-on-error. Focused sanitizer proofs passed the same 20 terminal-state-codec, 696 payload-store, 4,999 protocol, 194 reconciliation-service, and 536 folder-owner checks; payload-store, reconciliation-service, and folder-owner peak RSS was 648,772 KiB, 780,832 KiB, and 1,694,640 KiB. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev1003 parent SHA-256 matched 58be646d3714895037e2dd1f928aa81e2fd200614eb9dfa75a5fdde16a424b53 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 36/36 changed wrapper files, all 35/35 changed project files, all 32/32 changed active files, and the complete 618-file active projection byte-for-byte and mode-for-mode. The final active implementation projection contains 618 files / 28,499,104 bytes with SHA-256 7b4499a95932e5d3ec3452c9982c3dc8f3f2a3e15b79962f90b953144ac709e9. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excludes both remount-vanished unsealed worktrees and their builds, obsolete pre-generation-8 evidence, the first aggregate sanitizer run invalidated by concurrent memory-heavy tests, the CTest wrapper invocation that stalled despite a passing direct proof, and the pre-correction sanitizer final-link failure.`

Archive: `AnonSync-rev1004-2026.08.05.16.01-terminalcontinuation-zerobytepulse-inodejournal-cordierite.zip`

Codename: `cordierite`
