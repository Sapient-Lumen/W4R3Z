# Bounded source-manifest projection, same-stream turn collapse, and session resume audit — rev1007

## Product reason

AnonSync must delta-synchronize multi-terabyte Linux media trees without either
holding whole files in memory or letting one authenticated request monopolize an
owner for the time needed to read an entire source payload. Rev0994–rev1003
made chunk manifests and receiver-side reuse bounded, but the source still
constructed its complete content-defined manifest inside one request. A 4 TiB
source could therefore keep one request in source disk work for hours before a
single range became transferable.

Rev1007 converts that source-side manifest construction into one exact **32 MiB
per authenticated request** projection step. It also keeps consecutive
preparation turns on the **same authenticated TLS stream** while the existing
round-trip budget remains. This is a liveness and handshake-cost boundary, not a
claim that multi-terabyte source preparation is now fast.

## Retained authority model

The retained `SyncReplicaReconciliationService` owns at most one incomplete
`SourceContentDefinedProjection` and one completed source-manifest cache. The
projection binds:

- the exact SHA-256 content name;
- the exact total extent;
- the selected content-defined chunking parameters;
- the exact POSIX regular-file metadata observed by the rooted payload owner;
- the resumable SHA-256/chunker state and bounded completed-chunk frontier.

The projection belongs to the process-lifetime reconciliation service, not to a
TLS serve-session object. A later authenticated session can therefore resume
work already paid by the same retained owner. Every step still creates a fresh
targeted payload access, exact-opens the digest-named payload, re-proves digest,
extent, and inode metadata, advances at most the configured byte frontier, and
releases the descriptor before a response reaches TLS backpressure.

A service restart loses this acceleration and starts the projection again. The
projection is deliberately **process-local**: it is not durable payload
identity, protocol authority, or a restart-stable global chunk index.

## Generation-9 blocked response

Reconciliation advances to generation 9. Request and response structural and
semantic digest domains all advance with the wire version. A mixed
generation-8/generation-9 exchange therefore fails before application rather
than interpreting the new disposition under an older digest domain.

When the bounded source step is incomplete, the responder emits
`SourcePayloadPreparing`. The response:

- identifies the exact blocked operation;
- keeps `has_more=true`;
- does not include that operation in the transferable prefix;
- carries no payload continuation and no source range bytes;
- may carry only an earlier canonical evidence prefix;
- releases the exact source descriptor before network I/O.

The receiver maps this to typed bounded progress rather than to missing-payload
failure. `sync once`, TLS client/server ownership, session supervision, and both
shipping CLI switch surfaces preserve the state.

## Same authenticated-stream turn collapse

The first end-to-end replay exposed a serious integration defect in the initial
rev1007 shape: every preparing response immediately discarded the authenticated
channel. A one-shot source process then lost its process-local projection, so a
payload larger than one pulse could restart forever.

The retained TLS loop now treats preparation as an intermediate application
turn whenever another configured round trip remains:

- the server writes the bounded preparing frame and waits for the next request
  on the same authenticated stream;
- the client retains its exact page cursor and any durable payload continuation;
- an initial-page retry does not invent source-digest continuation authority;
- a resumed-payload retry keeps its already-authorized source digest and exact
  durable offset even though the preparing response itself carries no payload
  continuation;
- the final allowed turn still returns the typed
  `SourcePayloadPreparing` disposition if preparation remains incomplete.

The default 64-turn TLS ceiling can therefore perform at most **2 GiB** of
source-manifest hashing in one authenticated stream. The hard 4,096-turn ceiling
can perform at most **128 GiB**. A persistent peer-service owner can retain the
projection across later connections; the one-shot `serve-one` process remains a
diagnostic path and is restart-cold when its stream budget is insufficient.

Requester JSON now reports `source_payload_preparing_responses`, so a terminal
wire range cannot hide the source-hashing turns that preceded it.

## Adjacent accounting and audit refactor

The first TLS integration regression exposed duplicate accounting. The serve
session incremented `source_payload_preparing_responses`, and the TLS response
observer then copied that cumulative count and incremented the same result once
more. Rev1007 keeps the direct service-session counter for focused ownership
proofs, while the TLS result counts each emitted response only in its canonical
response observer.

An inherited rev0995 source-index audit also still required a session-owned
cache reset. That spelling was stale after the cache moved to the exact retained
service owner. The corrected audit now binds the actual safety property: digest,
extent, chunking, or inode drift clears the completed cache and starts one
cohesive exact-identity projection. Unrelated source-operation progress need not
discard valid content-based acceleration.

## Runtime proof

The focused service regression uses a 3 MiB-plus-173-byte source and a 1 MiB
frontier. It destroys the serve-session after every request while retaining the
service owner. Exactly three source-preparing responses each perform one pulse;
a fourth fresh session completes the canonical manifest and hashes only the
173-byte tail. No ranged payload bytes are framed during preparation.

The TLS regression uses a 512 KiB frontier and a source of two frontiers plus 17
bytes. One authenticated stream spends two turns on exact preparation, then the
third turn completes the manifest and transfers the first bounded 8-byte range
window. Both endpoints report three turns, two preparing responses, one
manifest/index publication, and one ranged window.

The shipping process regression uses a 64 MiB-plus-4,096-byte source with the
production 32 MiB frontier. Each one-shot session performs two preparing turns
and one wire-progress turn under `max_round_trips=3`; the first session durably
stages 64 MiB and the second stages the tail and publishes the operation. This
proves the command-line integration no longer restarts before any range can be
sent.

Protocol regressions bind canonical generation-9 bytes and reject malformed
blocked identities, included blocked operations, cursor advancement, and
payload-continuation authority. Existing insertion-shift and cross-file delta
suites explicitly account for the preparation turn before their first wire
range.

## Scale boundary and next edge

Memory remains bounded by one source projection, one completed manifest, the
existing 8,192-chunk frontier, fixed hash/chunker buffers, and the ordinary
bounded response page. Rev1007 does not retain source payload bytes or a map of
per-peer projections.

The time and turn cost remains severe. A 4 TiB source requires **131,072** 32 MiB
pulses if no cache already exists. Same-stream collapse removes a TLS handshake
per pulse but does not remove the disk reads or owner turns. A persistent
service needs multiple bounded sessions for sources above the stream ceiling,
and process restart repeats unfinished source work.

The next source-scale move should therefore be a bounded **source-local
scheduler** or a crash-safe durable source/chunk index that advances between
ordinary owner turns without requiring an authenticated retry for every pulse.
It must retain exact rooted reproof, fair scheduling across competing payloads,
strict memory ceilings, conservative restart behavior, and the existing
payload-before-operation rule. Measurement on sparse multi-terabyte files
should decide whether that scheduler or durable index is justified before more
protocol complexity is added.

Rev1007 does not add identity-preserving rename/move, full directory semantics,
Android support, selective placeholders or eviction, ENOSPC qualification,
garbage collection, or live public Tor/I2P performance proof.

## Release cutpoint

Validation: `Fresh GCC 14.2 Debug graph 557/557; GCC registry 292/292; GCC product 49/49; focused 5,001 protocol, 25 memory-shape, 207 reconciliation-service, 2,047 TLS, 114 sync-once, 737 payload-store, 536 folder-owner, 397 SQLite-owner, and 20 terminal-state checks; fresh Clang 17 ASan/UBSan product graph 268/268 and product 49/49 with leak detection and halt-on-error; focused source audit 26/26 and structural authority audit 592/592.`

Archive: `AnonSync-rev1007-2026.08.06.00.57-sourcemanifest-turncollapse-sessionresume-vivianite.zip`

Codename: `vivianite`
