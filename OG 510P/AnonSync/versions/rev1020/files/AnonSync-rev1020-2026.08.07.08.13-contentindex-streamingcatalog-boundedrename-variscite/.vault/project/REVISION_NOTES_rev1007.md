# Revision notes — rev1007

## Bounded source-side content-defined projection

Rev1007 removes the remaining whole-source manifest construction from one
reconciliation request. The shipping source owner now advances at most 32 MiB
of exact digest-named payload bytes per request and retains one bounded
process-local projection across fresh authenticated serve sessions.

Every later step reopens and re-proves the exact payload metadata. A different
digest, extent, chunking profile, or inode observation restarts the projection.
Completion enters the existing canonical content-defined manifest, digest, and
chunk-offset index; no second delta format or range planner was added.

## Generation 9 and same-stream progress

The protocol advances to generation 9 with distinct request/response structural
and semantic digest domains. An incomplete source projection returns the exact
`SourcePayloadPreparing` blocked operation with no payload bytes and no payload
continuation.

TLS now collapses consecutive preparation turns inside the existing authenticated
round-trip budget instead of discarding the channel after every pulse. The
requester preserves an already-authorized page cursor or payload offset, while
an initial unpinned page retry does not manufacture source-digest continuation
authority. If the final allowed turn is still incomplete, both sides retain the
typed source-preparing terminal state.

The default 64-turn stream can hash at most 2 GiB of source bytes; the 4,096-turn
hard ceiling can hash at most 128 GiB. Persistent peer-service ownership resumes
across later streams, while one-shot `serve-one` remains restart-cold if its
single stream cannot finish.

Shipping source and requester JSON report projection steps, projection
restarts, hashed bytes, and source-preparing response counts. A later wire range
therefore cannot hide the source work that preceded it.

## Adjacent audit corrections

The initial TLS path counted a preparing response once in the service session
and again in the TLS observer. The retained implementation leaves the direct
session counter intact but lets the TLS response observer be the only TLS-result
counter.

The historical source-index audit also assumed the cache still belonged to one
serve session. It now checks the real service-owned exact-identity fence: source
payload or inode drift clears the completed cache and starts one cohesive
projection, while unrelated operation-set progress need not throw away valid
content acceleration.

## Runtime and limits

A focused cross-session regression uses a 1 MiB frontier and proves three
preparing turns followed by an exact 173-byte final pulse in a fourth fresh
session. A TLS regression uses a 512 KiB frontier and proves two preparing turns
followed by one bounded range window on the same authenticated stream.

The shipping process oracle uses a 64 MiB-plus-4,096-byte payload and proves two
32 MiB preparation turns plus one wire-progress turn per one-shot TLS session.
The first session stages the 64 MiB prefix; the second stages the tail and
publishes the operation.

The projection is process-local and restart-cold. A 4 TiB payload still requires
131,072 32 MiB pulses. Same-stream collapse removes repeated handshakes within a
bounded stream but does not remove disk reads or owner turns. The next useful
scale step is a bounded source-local scheduler or a conservative durable
source/chunk index, driven by measured multi-terabyte behavior.

Rev1007 does not add rename/move identity, complete directories, Android,
selective placeholders or automatic eviction, ENOSPC qualification, retention
collection, or public Tor/I2P performance proof.

## Release cutpoint

Validation: `Fresh GCC 14.2 Debug graph 557/557; GCC registry 292/292; GCC product 49/49; focused 5,001 protocol, 25 memory-shape, 207 reconciliation-service, 2,047 TLS, 114 sync-once, 737 payload-store, 536 folder-owner, 397 SQLite-owner, and 20 terminal-state checks; fresh Clang 17 ASan/UBSan product graph 268/268 and product 49/49 with leak detection and halt-on-error; focused source audit 26/26 and structural authority audit 592/592.`

Archive: `AnonSync-rev1007-2026.08.06.00.57-sourcemanifest-turncollapse-sessionresume-vivianite.zip`

Codename: `vivianite`
