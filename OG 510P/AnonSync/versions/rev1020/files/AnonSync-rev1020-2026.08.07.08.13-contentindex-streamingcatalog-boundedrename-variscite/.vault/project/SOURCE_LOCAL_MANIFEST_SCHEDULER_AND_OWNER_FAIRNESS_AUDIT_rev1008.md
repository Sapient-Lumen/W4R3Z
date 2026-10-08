# Source-local manifest scheduler and owner fairness audit — rev1008

## Question

After an authenticated requester discovers that a large immutable source payload
needs a content-defined manifest, can the retained peer service finish that
bounded source work without keeping a requester connected, without creating a
second worker, and without starving ordinary service activity?

## Retained authority path

One authenticated reconciliation request remains the only discovery boundary.
It exact-opens the digest-named source payload and advances the existing
content-defined projection by at most 32 MiB. If the manifest is incomplete, the
response remains `SourcePayloadPreparing` and names the exact blocked operation.
The retained reconciliation service keeps only process-local projection state.

A later peer-service owner turn may call the same projection helper without a
peer. The source-local call:

1. requires the exact reconciliation owner identity;
2. begins targeted payload access through the existing payload-store owner;
3. exact-opens the retained causal operation's digest-named payload;
4. re-proves digest, extent, chunking parameters, and POSIX inode observation;
5. advances at most the same 32 MiB frontier; and
6. releases descriptor and targeted-access authority before returning.

A missing payload clears the stale projection and returns a typed
`PayloadUnavailable` step. Completion enters the existing canonical manifest,
manifest-digest, chunk-offset, and ranged-response path. It does not publish a
replica operation, mutate the folder catalog, write a payload object, or advance
a request cursor.

## One shared local-work gate

Receiver terminal verification and source-manifest preparation are two choices
inside the existing single-threaded peer-service owner. They do not own threads,
executors, timers, databases, or event loops. Before either path touches payload
authority, it publishes one ordinary-turn obligation. The next owner call is
reserved for control, ingress, network, watcher, or repair observation even if
none is ultimately ready. When both local lanes are pending, the preferred lane
alternates after each selected pulse.

The service exposes the exact source projection and counters in
`anonsync.peer-service.status.v26`, both live and terminal:

- scheduler steps;
- progress steps;
- completions;
- payload-unavailable outcomes;
- projection restarts;
- hashed bytes; and
- ordinary-turn yields.

Impossible status combinations fail during canonical rendering rather than
silently producing approximate JSON.

## Runtime evidence

The focused C++ regression uses a 3 MiB plus 173 byte source and a 1 MiB test
frontier. One authenticated request discovers the obligation and pays the first
pulse. Three peer-independent calls complete it. A fresh authenticated session
then reuses the completed manifest and index with zero new projection steps,
zero source bytes hashed, and no second manifest build.

The shipping process regression uses a 64 MiB plus 4,097 byte source and the
production 32 MiB frontier. One shipped requester discovers the obligation and
exits. The same daemon finishes the remaining 32 MiB plus 4,097 bytes in exactly
two local pulses, stays ready and owner-controllable, and lets a fresh requester
stage sixteen ranges without another preparing response. Live and terminal
status retain the same counters and settled projection.

## Scale and memory boundary

Rev1008 removes peer-turn coupling; it does not remove source disk work. A cold
4 TiB source still requires 131,072 32 MiB pulses. Unfinished projection state is
process-local, so restart repeats unfinished source hashing. After completion,
the content-defined manifest and offset index remain O(chunk count) memory. The
implementation therefore does not claim solved multi-terabyte RSS, allocator
fragmentation, page-cache pressure, or restart cost. Those need sparse synthetic
measurement before choosing a durable or paged index.

## Explicit nonclaims

Rev1008 does not add a durable source projection, global chunk index,
multi-source chunk database, rename/move identity, complete directory semantics,
placeholders, automatic selective-sync eviction, ENOSPC policy, Android support,
retention collection, or live public Tor/I2P qualification. Source spelling and
this document are not semantic proof; compiler, sanitizer, runtime,
reconstruction, and package evidence remain load-bearing.

## Release cutpoint

Fresh GCC 14.2 Debug graph 557/557; GCC registry 294/294; GCC product 50/50; focused 5,001 protocol, 25 memory-shape, 211 reconciliation-service, 2,047 TLS, 114 sync-once, 737 payload-store, 536 folder-owner, 397 SQLite-owner, and 20 terminal-state checks, plus the shipping source-scheduler process oracle; fresh Clang 17 ASan/UBSan product graph 268/268 and product 50/50 with leak detection and halt-on-error; focused source-local scheduler audit 35/35 and structural authority audit 602/602.

Archive: `AnonSync-rev1008-2026.08.06.02.39-sourcelocalscheduler-turnfairness-peerindependent-tsavorite.zip`

Codename: `tsavorite`
