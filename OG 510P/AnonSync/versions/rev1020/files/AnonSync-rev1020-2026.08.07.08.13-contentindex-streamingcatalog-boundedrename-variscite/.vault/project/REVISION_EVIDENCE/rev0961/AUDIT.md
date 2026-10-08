# Rev0961 implementation and adjacent audit

## Mission checkpoint

AnonSync remains one C++ product spine whose purpose is to replace Resilio Sync
for a real folder workflow. Direct TCP, Tor, and I2P remain routes into the same
authenticated synchronization semantics. Rev0961 adds an explicit recovery
operation to the retained daemon; it does not add another scanner, catalog,
service, transport protocol, or synchronization engine.

## Implemented exact quarantine slice

- The owner command `anonsync_sync quarantine --socket ABSOLUTE_SOCKET
  --expected SHA256 --observed SHA256` admits only the exact active process
  integrity pair.
- The owner rehashes current source bytes under the existing reader-fenced
  exclusive identity lease and returns typed stale, absent, repaired, changed,
  idempotent, entry-capacity, or byte-capacity results.
- A successful preservation synchronizes the exact source bytes, performs a
  rooted Linux no-replace same-inode rename, synchronizes the directory, and
  re-proves source absence and destination identity.
- Existing exact destinations are fully rehashed and synchronized before they
  can be treated as retained evidence.
- Canonical quarantine is excluded from payload inventory and targeted access,
  capped at sixteen entries, and bounded by the active indexed-byte budget.
- The integrity alarm remains active until authenticated ordinary convergence
  re-admits good bytes and completes the existing recovery cutpoints.
- Drain, recheck, and one exact quarantine pair share one mutex-linearized action
  snapshot, condition variable, generation model, and shutdown seal.
- Live and terminal output share status schema
  `anonsync.peer-service.status.v8` and canonical quarantine renderers.

## Adjacent audit/refactor corrections

The authority audit corrected several defects rather than only documenting the
feature. A pre-existing canonical destination is no longer trusted by name;
non-mutating outcomes no longer report a destination that was not retained;
fresh standalone bootstrap cannot adopt unexplained quarantine bytes; repeated
same-image corruption can remove only the duplicate authoritative source after
both copies are rehashed; and the implementation now records the unavoidable
post-mutation full scan instead of claiming rev0960's duplicate-scan-free
handoff across a namespace change.

The final review found two additional operational defects. First, a normal full
quarantine frontier raised `std::length_error` through the service owner and
could terminate the retained daemon. Exact entry and byte exhaustion now return
typed non-mutating terminal dispositions while structurally invalid over-budget
namespaces remain fail closed. Second, directory synchronization did not ensure
that dirty in-place corrupt bytes were durable under the new name. The exact
source is now synchronized before rename, and an existing retained destination
is synchronized after its complete-byte reproof.

## Validation

The exact active source completed a fresh GCC 14.2 Debug 527/527-edge graph,
exact-source no-work re-attestation, one uninterrupted 258/258 serial registry in
115.95 seconds, an independent 39/39 product lane in 60.36 seconds, and the
focused matrix including 551 payload-store and 83 local-control checks. The
structural authority audit passes 180/180 checks.

Clang 17 ASan/UBSan completed a fresh 238/238-edge product graph and no-work
re-attestation. All 39/39 product tests passed serially with leak detection in
123.14 seconds. The focused payload-store suite passed 551 checks in 8.93
seconds. No retained compiler, linker, AddressSanitizer,
UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic remains.

## Nonclaims

Rev0961 does not provide automatic quarantine, user-file versioning, restore,
retention age, reachability pins, quota eviction, crash-safe garbage collection,
durable local action requests, hostile same-UID protection, universal
power-loss qualification, portable local-control or network-filesystem lock
semantics, rename identity, directory/metadata parity, selective sync,
changed-block transfer, many-share supervision, live public Tor/I2P privacy
qualification, or completion of a named measured Resilio uninstall workflow.
