# AnonSync rev1008 revision notes

Rev1008 lets a retained linked-peer daemon finish one already-discovered source
content-defined manifest through bounded peer-independent owner turns.

## Added

- Exact source-manifest projection status and one-step continuation API on the
  reconciliation service and inbound peer owner.
- A typed `SourceManifestProjectionAdvanced` peer-service step.
- One shared source/receiver local-payload scheduler with alternating priority
  and one mandatory ordinary owner turn after every hash pulse.
- Canonical live and terminal `anonsync.peer-service.status.v26` projection,
  counters, and last-step evidence.
- A focused C++ regression proving fresh-session discovery, local completion,
  and completed-cache reuse.
- A real shipping-process regression proving one peer discovery, exactly two
  local production-frontier pulses, same-PID readiness, fresh-request reuse,
  owner drain, and terminal-status preservation.
- A focused lexical audit for the source-local scheduler and shared owner
  fairness boundary.

## Refactored

- Network-request and source-local projection now share one exact helper for
  projection restart, bounded hashing, canonical manifest construction, digest,
  and chunk-offset indexing.
- Receiver terminal verification now participates in the same local-work gate
  instead of retaining a separate fairness flag.
- Historical rev1006 and rev1007 audits now follow the shared implementation
  boundary rather than obsolete inline spellings.

## Correctness boundary

First discovery remains authenticated. Every local pulse exact-opens and
re-proves the retained operation's immutable payload. Missing bytes clear the
process-local projection. Completion is acceleration only: it does not mutate
replica, catalog, payload namespace, or request cursor authority.

## Remaining scale cost

A cold 4 TiB source still costs 131,072 32 MiB pulses and restart repeats
unfinished work. Completed manifest and offset-index memory remains O(chunk
count). Rev1008 deliberately postpones durable or paged source indexing until
sparse multi-terabyte measurement identifies whether restart I/O or completed
RSS is the dominant constraint.

## Validation

Fresh GCC 14.2 Debug graph 557/557; GCC registry 294/294; GCC product 50/50; focused 5,001 protocol, 25 memory-shape, 211 reconciliation-service, 2,047 TLS, 114 sync-once, 737 payload-store, 536 folder-owner, 397 SQLite-owner, and 20 terminal-state checks, plus the shipping source-scheduler process oracle; fresh Clang 17 ASan/UBSan product graph 268/268 and product 50/50 with leak detection and halt-on-error; focused source-local scheduler audit 35/35 and structural authority audit 602/602.

Archive: `AnonSync-rev1008-2026.08.06.02.39-sourcelocalscheduler-turnfairness-peerindependent-tsavorite.zip`

Codename: `tsavorite`
