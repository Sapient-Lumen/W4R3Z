# BOOTSTRAPROSE

> **ANONSYNC EXISTS TO REPLACE RESILIO SYNC. PERIOD.**

AnonSync is a practical C++ folder-synchronization product for a person's own
machines and chosen peers. It must run continuously, survive ordinary failure,
and make useful real folders converge over direct networking, Tor, and I2P.

The product test is concrete:

> A person can uninstall Resilio Sync from a named real workflow, leave
> AnonSync running instead, and trust it with that workflow's files, routes,
> outages, restarts, recovery, performance, and daily operation.

Everything else is subordinate. Crash consistency, authenticated peers,
bounded work, durable databases, exact paths, tests, audits, and historical
records matter only when they protect or accelerate that replacement product.
They are not a second mission. The size of an old subsystem or proof family
never grants it product priority.

Here “Resilio Sync” means the personal device/folder product, not Resilio Active
Everywhere. Wire compatibility is not currently required. Only a direct human
correction may change this mission.


## Wake here

```text
MISSION
    Replace Resilio Sync with one usable C++ folder-sync application.

ROUTES
    Direct TCP, Tor, and I2P are first-class. A route locked to Tor or I2P
    fails closed; router trouble never silently becomes clearnet traffic.

CURRENT SHAPE
    Linux/headless pre-alpha. Two retained C++ peer services can synchronize
    nested regular-file create, edit, delete, and same-path recreation in both
    directions. They watch, periodically repair missed events, reconnect,
    selectively retain metadata without bytes, transfer large files through
    bounded crash-safe ranges with content-defined same-path and current-visible
    cross-file chunk reuse, expose an owner-only local status/drain/recheck/
    quarantine/release/causal-version inspection/restore socket, and install as
    a systemd user service.
CURRENT REVISION MOVE
    Rev1020 bounds rev1019's regular-file rename planner for large media trees
    and million-path namespaces. Ordinary one-file planning is now
    path/content-indexed and history-cold: exact catalog and replica path
    cutpoints combine with named-index content lookups that return at most two
    rows. Exact schema-v6/v8 migrations rebuild the projections under writer
    transactions; normalized rows are re-bound to immutable authority.

    Catalog commits now stream canonical rows with O(1) row memory rather than
    retaining whole-catalog vectors. They still pay O(N) SQLite I/O for the
    global digest. An actual causal rename publication retains one O(N-visible)
    streamed integrity fence over current visible state, but never decodes the
    complete retained operation history. This is a scale correction, not a
    dense million-file throughput measurement, and it does not change the wire
    protocol or rev1019 causal identity shape.
FIRST SUPPORTED WORKFLOW
    Linux/headless synchronization of large media trees measured in terabytes.
    Delta transfer and selective synchronization are mandatory. Rev0994 provides
    bounded content-defined predecessor reuse after shifted insertions and
    deletions; rev0992's constant-size manifest continuation survives inside the
    generation-7 grouped-window path; rev0987 provides bounded metadata-only
    selection, safe rooted dematerialization, and later ordinary acquisition.
    Credentials and private keys remain operator-owned and outside AnonSync
    backup authority. Retention is best effort; uncertain continuity fails
    conservatively and resets any deletion-age confidence.

ANDROID DIRECTION
    Android compatibility is desirable but not claimed. A Termux or app-private
    Linux experiment may exercise the portable C++ core, but Android scoped
    storage and foreground-service lifecycle rules do not provide the same
    rooted POSIX namespace or always-running daemon contract. A supported app
    needs explicit storage, lifecycle, notification, battery, and permission
    adapters. Do not bend the Linux authority model into false Android claims.

NOT A RESILIO REPLACEMENT YET
    Selective sync has no placeholders, polished user interface, or automatic
    private-payload eviction. The real sparse >4 TiB gate does not qualify
    dense media I/O, page cache, delta-transfer throughput, filesystem pressure,
    allocator fragmentation, cgroup pressure, or million-file trees. Sampled
    PSS can miss between-point transients; Linux peak RSS is a process-lifetime
    high-water signal, not attribution.

    The durable replica and file-effect owners remain O(history) reference
    owners and still perform one complete reconstruction at cold owner open.
    Ordinary one-file rename planning is indexed, but catalog publication still
    streams O(N) rows and actual identity publication streams O(N-visible)
    current paths. One active transfer
    may retain one 327,680-byte O(chunk count) sequence until terminal proof,
    and a cold 4 TiB source still costs 131,072 local 32 MiB hash pulses.
    Directory/subtree moves, complete directories and empty directories,
    portable metadata, ordinary conflict handling, best-effort retention
    collection, quota/ENOSPC recovery, live public Tor/I2P qualification,
    many-share ownership, Android, and polished setup remain incomplete.
NEXT PRODUCT EDGE
    Continue product semantics with complete directory and empty-directory
    operations, then understandable conflict copies/status/resolution and
    controlled ENOSPC. Measure rename planning and dense delta throughput at
    million-file and multi-terabyte scale rather than extrapolating this slice.
    Grow dense multi-terabyte, million-file, delta-throughput, restart, and
    high-latency route tests alongside those semantics. Android remains a worthy
    target, but requires explicit scoped-storage, lifecycle, notification,
    battery, and permission adapters; do not claim that the Linux daemon model
    already transfers unchanged.
RUN LOOP
    `/run` means: read this page, obey the newest human correction, open only
    the hidden material needed, make one useful bounded C++ product move,
    audit/refactor one concrete risk or drag, keep this page truthful, run the
    touched/product/release gates, and return one next-revision ZIP link.
```



REV1020 RELEASE CUTPOINT
    AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite.zip
    variscite
    Exact rev1020 source passed a fresh GCC 14.2 Debug graph (573/573 configured build edges), all 312/312 registered tests, and an independent 56/56 product replay. Focused GCC suites passed network model 104/104 with 41 generated operations, SQLite owner 433/433, folder owner 562/562, and sync-once 114/114. Source audits passed bounded rename 23/23, identity-preserving rename 31/31, selective sync 52/52, targeted local publication 30/30, SQLite owner 43/43, and structural authority 705/705. The exact Clang 17 ASan/UBSan product graph completed 284/284 edges and reached a no-work state; all 56/56 product tests passed with leak detection and halt-on-error. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev1019 parent SHA-256 matched 6598db7b72152953b02539f16338dbf04bea358b0318d26b5723bb641140829c and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 17/17 changed files. The active implementation projection contains 650 files / 29,625,955 bytes with SHA-256 3874720c5071b841920e6a3c3dadc71f8554c519a792b0eed89bebb78f4af833. Final wrapper-directory verification passed 32/32 checks, ZIP verification and CRC passed 41/41 checks, and clean extraction matched every path, byte, type, and mode.
    Rev1020 bounds ordinary one-file rename planning with startup-attested
    content indexes and path-local cutpoints, converts catalog publication from
    whole vectors to O(1)-row-memory streams, preserves one explicit
    O(N-visible) rename integrity fence, and keeps the scale and product
    nonclaims honest.


REV1019 RELEASE CUTPOINT
    AnonSync-rev1019-2026.08.07.06.02-causalrename-projectionreproof-singlepayload-bixbite.zip
    bixbite
    Exact rev1019 source passed a fresh GCC 14.2 Debug graph (573/573 configured build edges), all 311/311 registered tests, and an independent 56/56 product replay. Focused GCC proofs passed 104 network-model checks plus 41 generated operations, 416 SQLite-owner checks, 562 folder-owner checks, and 114 sync-once checks. The focused identity-preserving-rename source audit passed 31/31 checks and the structural authority audit passed 698/698 checks. An exact Clang 17 ASan/UBSan product graph reached a no-work state against the 284-edge configured product shape, and all 56/56 product tests passed with leak detection and halt-on-error. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev1018 parent SHA-256 matched 02fc26329d2274e6dbf440f3e9d4319a8af08efaa00bdfce8f61c8a59eddf90b; its stale rev1017 release metadata and generated Python cache are explicitly not borrowed as publication authority. The binary-aware source patch reconstructed all 19/19 changed active files. The final active implementation projection contains 649 files / 29,541,244 bytes with SHA-256 ef1df087c17ef62ee25466caeea2e4f105c8716aab3299553b391cc9bcefabf7. Final wrapper-directory verification, ZIP verification and CRC, canonical path/no-symlink policy, and clean-extraction path/byte/type/mode comparison all passed.
    Rev1019 publishes one conservative regular-file causal identity continuation
    with atomic per-database pairs, exact rooted ambiguity fences, complete
    visible-projection reproof, single-payload reuse, restart inference, and
    honestly regenerated release metadata.


REV1018 RELEASE CUTPOINT
    AnonSync-rev1018-2026.08.07.02.31-historycold-sparsefourterabyte-memoryproof-danburite.zip
    danburite
    Exact rev1018 source passed a fresh GCC 14.2 Debug graph (578/578 configured build edges), all 310/310 registered tests, and an independent 56/56 product replay. Focused GCC proofs passed 22 history-cold source-frame/startup checks, 26 real sparse multi-terabyte process checks, 90/90 folder-observer checks, 6/6 observer-race checks, and 557 folder-owner checks. Source audits passed 19/19 history-cold startup checks, 18/18 sparse multi-terabyte checks, and 690/690 structural authority checks. A fresh Clang 17 ASan/UBSan product graph completed 286/286 edges and all 56/56 product tests passed with leak detection and halt-on-error. The exact rev1017 parent SHA-256 matched and passed 41/41 wrapper-aware package checks. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The obsolete predictable-path validator, its kill guard, interrupted caches, and divergent branches are excluded.
    Rev1018 composes peer services from bounded identity cutpoints, preserves
    complete cold owner authority, and proves two real selective-sync services
    over exactly 4,399,120,252,928 sparse logical bytes with 4,096-name batch,
    zero selected payload work, sampled PSS, and Linux lifetime peak RSS gates.

REV1017 RELEASE CUTPOINT
    AnonSync-rev1017-2026.08.07.00.36-resourcewatch-peakenvelope-restartfence-oligoclase.zip
    oligoclase
    Exact rev1017 source passed a fresh GCC 14.2 Debug graph (573/573 configured build edges), independent 55/55 product tests, and 250/250 documentation-independent non-product tests; the two final documentation-sensitive audits then passed for complete 307/307 registry accounting. Focused GCC proofs passed 45 Linux process-resource checks and 246 real-process resource-series checks. Source audits passed 27/27 focused resource-boundary checks and 675/675 structural-authority checks. A fresh Clang 17 ASan/UBSan product graph completed 284/284 edges and all 55/55 product tests passed with leak detection and halt-on-error. The exact rev1016 parent passed 41/41 wrapper-aware package checks. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. Transient remount losses, predictable-path validators, divergent startup prototypes, interrupted runs, and their build products are excluded.
    Rev1017 adds a bounded fixed-schedule Linux process-resource series with
    O(processes + samples) retained state, sampled peak envelopes, and exact
    PID/start-tick continuity across rounds. It remains diagnostic-only.

REV1016 RELEASE CUTPOINT
    AnonSync-rev1016-2026.08.06.22.55-processresources-pssaggregate-deadlinefence-clinohumite.zip
    clinohumite
    Exact rev1016 source passed a fresh GCC 14.2 Debug graph (573/573 configured build edges), a no-work bundled-SQLite re-attestation, independent 55/55 product tests, and 252/252 non-product tests for all 307/307 registered tests. Focused GCC proofs passed 45 Linux process-resource, 165 local private-socket, and 42 real-process aggregate checks. Source audits passed 22/22 focused resource-boundary checks and 667/667 structural-authority checks. A fresh Clang 17 ASan/UBSan product graph completed 284/284 edges and all 55/55 product tests passed with leak detection and halt-on-error. The exact rev1015 parent passed 41/41 wrapper-aware package checks. Aggregate terminal-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. Predictable-path validators, the post-freeze divergent source delta, interrupted runs, and their build products are excluded.
    Rev1016 adds one explicit owner-only Linux process-resource snapshot and a
    bounded multi-socket aggregate with one total deadline. Ordinary status
    remains procfs-cold; the result is diagnostic evidence, not sync authority.

REV1015 RELEASE CUTPOINT
    AnonSync-rev1015-2026.08.06.20.55-activefixeddigest-terminalrelease-multishare-kornerupine.zip
    kornerupine
    Exact rev1015 source passed a fresh GCC 14.2 Debug graph (567/567 configured build edges), a no-work bundled-SQLite re-attestation, independent 53/53 product tests, and final 251/251 non-product accounting for all 304/304 registered tests. Focused GCC proofs passed 86 resumable-SHA-256, 737 payload-store, 30 source-manifest-checkpoint, 35 compact-manifest, 16 source-frame-memory, and 215 reconciliation-service checks. Source audits passed 19/19 active-source-memory, 22/22 terminal-cache, 22/22 checkpoint-memory, and 659/659 structural-authority checks. A fresh Clang 17 ASan/UBSan product graph completed 278/278 edges and all 53/53 product tests passed with leak detection and halt-on-error. The exact rev1014 parent passed 41/41 wrapper-aware package checks. Aggregate terminal-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic.
    Rev1015 stores every active source chunk as one 40-byte fixed record,
    removes the transient digest-string terminal path, publishes checkpoints
    in place, and releases the completed compact manifest after the terminal
    frame and exact checkpoint reproof. The synthetic 64-source frontier uses
    20 MiB through 64 record-vector allocations instead of the prior 52.5 MiB
    requested shape. One 327,680-byte active sequence and whole-process
    multi-share measurement remain.


REV1014 RELEASE CUTPOINT
    AnonSync-rev1014-2026.08.06.18.37-borrowedmanifest-directframe-singleallocation-wulfenite.zip
    wulfenite
    Exact rev1014 source passed a fresh GCC 14.2 Debug graph (567/567 configured build edges), a no-work bundled-SQLite re-attestation, independent 53/53 product accounting, and final 249/249 non-product accounting for all 302/302 registered tests. Focused GCC proofs passed 35 compact-manifest, 5,004 protocol, 25 memory-shape, 10 source-frame-memory, 30 checkpoint-codec, and 45 content-defined-chunker checks. A fresh Clang 17 ASan/UBSan product graph completed 278/278 edges; all 53/53 product tests and focused 35 compact, 5,004 protocol, and 10 source-frame checks passed with leak detection and halt-on-error. Source audits passed 32/32 borrowed-manifest, 30/30 fixed-binary, 29/29 compact-cache, 34/34 inherited direct-source, and 646/646 structural-authority checks. The exact rev1013 parent passed 41/41 wrapper-aware package checks. Aggregate terminal-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. Final staged-directory verification passed 32/32 checks; ZIP verification and CRC passed 41/41 checks; clean extraction matched every path, byte, type, and POSIX mode.
    Rev1014 lends the one retained fixed-width compact source manifest directly
    to canonical generation-9 frame assembly. Maximum direct publication owns
    one large final-frame allocation rather than that frame plus a 327,680-byte
    manifest copy; borrowed and owning frames are exact byte equals. One
    327,680-byte retained O(chunk count) sequence and whole-process multi-share
    measurement remain.


REV1013 RELEASE CUTPOINT
    AnonSync-rev1013-2026.08.06.16.45-fixedbinarymanifest-sharedcodec-singleallocation-scheelite.zip
    scheelite
    Exact rev1013 source passed a fresh GCC 14.2 Debug graph (567/567 configured build
    edges across bounded resumptions), a no-work bundled-SQLite re-attestation, all
    301/301 registered tests, and independent 53/53 product accounting. Focused GCC
    proofs passed 22 compact-manifest, 30 checkpoint-codec, 45 chunker, 43 restart,
    5,004 protocol, 25 memory-shape, 10 source-frame-memory, 20 terminal-state, 737
    payload-store, 397 SQLite-owner, 536 folder-owner, 114 sync-once, 2,047 TLS, and
    211 reconciliation-service checks. A fresh Clang 17 ASan/UBSan product graph
    completed 278/278 edges; all 53/53 product tests and the additional 737-check
    payload-store proof passed with leak detection and halt-on-error. Source audits
    passed 30/30 fixed-binary, 29/29 compact-cache, 22/22 checkpoint-memory, 27/27
    manifest-reference, and 635/635 structural-authority checks; the exact rev1012
    parent passed 41/41 wrapper-aware package checks. Aggregate terminal-log
    inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer,
    runtime-error, or LeakSanitizer diagnostic. Divergent controllers, overwritten
    authorities, discarded caches, interrupted runs, and the stale lexical oracle are
    excluded.
    Rev1013 replaces heap-backed SHA-256 text in the generation-9 source
    manifest object with one shared fixed 32-byte value also used by the compact
    cache and durable checkpoint. Maximum 8,192-chunk receive, cache, copy, and
    publication shapes each require one 327,680-byte vector allocation instead
    of 8,193 allocations / 860,160 requested bytes. Network and checkpoint
    bytes remain exact. Whole-process multi-terabyte measurement remains
    required.


REV1012 RELEASE CUTPOINT
    AnonSync-rev1012-2026.08.06.14.42-compactmanifest-cumulativeindex-wirematerialization-dumortierite.zip
    dumortierite
    Exact rev1012 source passed a fresh GCC 14.2 Debug graph (567/567 configured build
    edges) and no-work bundled-SQLite re-attestation; all 300/300 registered tests and an
    independent 53/53 product replay passed. Focused GCC proofs passed 20 compact-manifest,
    30 checkpoint-codec, 45 content-defined-chunker, 43 true-process restart, 5,001
    reconciliation-protocol, 25 memory-shape, 20 terminal-state, 737 payload-store, 397
    SQLite-owner, 536 folder-owner, 114 sync-once, 2,047 TLS, and 211 reconciliation-service
    checks. A fresh Clang 17 ASan/UBSan product graph completed 278/278 edges and all 53/53
    product tests passed serially with leak detection and halt-on-error. Source audits
    passed 29/29 compact-cache, 36/36 retained-checkpoint, and 625/625 structural-authority
    checks; the exact rev1011 parent passed 41/41 wrapper-aware package checks. Aggregate
    terminal-log inspection found no compiler, linker, AddressSanitizer,
    UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. Superseded pre-
    hotfix builds, the interrupted early registry, and pre-correction lexical-audit failures
    are excluded.
    Rev1012 replaces the retained string-backed source manifest plus separate
    chunk-offset vector with one 40-byte cumulative-end/fixed-digest record per
    chunk. Maximum retained allocator requests fall from 8,194 / 925,704 bytes
    to one / 327,680 bytes while generation-9 wire publication remains exact and
    intentionally transient. Numeric cumulative lookup is allocation-cold.
    Whole-process multi-terabyte measurement remains required.


REV1011 RELEASE CUTPOINT
    AnonSync-rev1011-2026.08.06.10.19-fixedwidthdigest-singleallocation-wirecompat-axinite.zip
    axinite
    Fresh GCC 14.2 Debug graph 563/563; GCC registry 298/298; GCC product 52/52; focused 30 checkpoint-codec, 45 chunker, 43 true-process restart, 5,001 protocol, 25 memory-shape, 20 terminal-state, 737 payload-store, 397 SQLite-owner, 536 folder-owner, 114 sync-once, 2,047 TLS, and 211 reconciliation-service checks; fresh Clang 17 ASan/UBSan product graph 274/274 and product 52/52 with leak detection and halt-on-error; dedicated heap-compaction audit 22/22, retained rev1010 checkpoint audit 36/36, structural authority audit 617/617, and exact rev1010 parent verification 41/41. Incremental, remount-lost, stale-validator, and transient aggregate TLS-EOF attempts are excluded.
    Rev1011 replaces each heap-backed checkpoint chunk digest with one fixed
    32-byte array while preserving the exact rev1010 v2 wire image and all
    rooted restart authority. It removes 8,192 digest allocations from maximum-
    shape construction and leaves one contiguous 327,680-byte vector allocation
    for maximum-shape copy. The ordinary protocol manifest and offset index
    remain O(chunk count); whole-process multi-terabyte measurement is still
    required.


REV1010 RELEASE CUTPOINT
    AnonSync-rev1010-2026.08.06.08.49-pulsecheckpoint-execrestart-retryfence-eucryptite.zip
    eucryptite
    Fresh GCC 14.2 Debug graph 563/563; GCC registry 297/297; GCC product 52/52; focused 20 checkpoint-codec, 45 chunker, 43 true-process restart, 5,001 protocol, 25 memory-shape, 20 terminal-state, 737 payload-store, 397 SQLite-owner, 536 folder-owner, 114 sync-once, 2,047 TLS, and 211 reconciliation-service checks; fresh Clang 17 ASan/UBSan product graph 274/274 and product 52/52 with leak detection and halt-on-error; dedicated checkpoint audit 36/36, structural authority audit 610/610, exact rev1008 parent verification 41/41. Interrupted runs killed by a stale-validator guard are excluded.
    Rev1010 retains one checksum-framed, store-identity- and exact-inode-bound
    source-manifest checkpoint. A true three-process self-exec proof resumes an
    arbitrary interior frontier without a peer and then reuses the completed
    manifest with zero source hashing. A deterministic final-write fault proves
    peer-free discovery seals the retained completion without another request.
    Active publication is coalesced to one GiB after the first pulse;
    completion is always sealed. The exact available
    parent is rev1008 because the user-visible rev1009 handoff was unmaterialized
    in this cloudtainer. The record remains acceleration only, bounded O(8,192
    chunks), and does not claim solved 4 TiB total hashing or completed-manifest
    RSS.


REV1008 RELEASE CUTPOINT
    AnonSync-rev1008-2026.08.06.02.39-sourcelocalscheduler-turnfairness-peerindependent-tsavorite.zip
    tsavorite
    Fresh GCC 14.2 Debug graph 557/557; GCC registry 294/294; GCC product 50/50; focused 5,001 protocol, 25 memory-shape, 211 reconciliation-service, 2,047 TLS, 114 sync-once, 737 payload-store, 536 folder-owner, 397 SQLite-owner, and 20 terminal-state checks, plus the shipping source-scheduler process oracle; fresh Clang 17 ASan/UBSan product graph 268/268 and product 50/50 with leak detection and halt-on-error; focused source-local scheduler audit 35/35 and structural authority audit 602/602.
    Rev1008 lets one authenticated request discover an exact source manifest
    obligation and lets the retained single owner finish it through bounded
    peer-independent 32 MiB pulses. Source and receiver-local hash work share one
    ordinary-turn fairness gate and alternate when both are pending. The work is
    process-local, restart-cold, and still O(chunk count) after completion; it
    does not claim solved multi-terabyte RSS or a durable/global chunk index.


REV1007 RELEASE CUTPOINT
    AnonSync-rev1007-2026.08.06.00.57-sourcemanifest-turncollapse-sessionresume-vivianite.zip
    vivianite
    Fresh GCC 14.2 Debug graph 557/557; GCC registry 292/292; GCC product 49/49; focused 5,001 protocol, 25 memory-shape, 207 reconciliation-service, 2,047 TLS, 114 sync-once, 737 payload-store, 536 folder-owner, 397 SQLite-owner, and 20 terminal-state checks; fresh Clang 17 ASan/UBSan product graph 268/268 and product 49/49 with leak detection and halt-on-error; focused source audit 26/26 and structural authority audit 592/592.
    Rev1007 advances reconciliation to generation 9. Rev1007 bounds source-side
    content-defined manifest work to one exact 32 MiB request pulse, retains one
    process-local projection across fresh authenticated
    sessions, advances wire and digest domains to generation 9, and exposes a
    typed payload-cold SourcePayloadPreparing cutpoint. Consecutive preparation
    turns remain on the same authenticated stream while its bounded round-trip
    budget remains. The work is not restart-durable and does not eliminate the
    131,072-pulse cost of a 4 TiB source; a bounded source-local scheduler remains
    the next measured scale edge.


REV1006 RELEASE CUTPOINT
    AnonSync-rev1006-2026.08.05.22.03-receiverlocalscheduler-restartdiscovery-ownerfairness-malachite.zip
    malachite
    Exact rev1006 source passed a fresh GCC 14.2 Debug complete graph with 557/557 configured build edges and exact-source no-work re-attestation; all 291/291 registered tests and the independent 49/49 product set passed. Focused GCC proofs passed 20 terminal-state-codec, 737 payload-store, 397 SQLite-owner, 536 folder-owner, 110 sync-once, 196 reconciliation-service, and 2,044 TLS-transport checks; the shipping peer-independent scheduler process regression passed with no source peer. Source audits passed 33/33 receiver-local terminal-scheduler and 584/584 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 268/268 configured edges; all 49/49 product tests passed with leak detection and halt-on-error, and focused sanitizer payload-store proof passed all 737 checks. No compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic remained in passing evidence. The exact rev1005 parent SHA-256 matched b94e3c496bbec3c230c8d3af3081f53d0f519e9945943022df80ecc3f5e3199d and passed 41/41 wrapper-aware package checks. The final active implementation projection contains 622 files / 28,656,401 bytes with SHA-256 808d8740871083908600d243359c97e0253b456afef4ba65c5f4e88bb39e2b1f. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excludes the pre-correction sanitizer fixture-link failure, interrupted wrapper commands, the duplicate Ninja that briefly entered the same cache and was terminated, the remount-vanished unsealed worktree, and all obsolete validator branches and builds.
    Rev1006 discovers complete staged-prefix terminal obligations through an
    ordinary complete payload-store scan, advances one exact 32 MiB pulse in
    the retained single owner thread, and forces an ordinary service turn
    between pulses. A source peer is no longer required after target bytes are
    durable. Restart reconstructs work from the existing journal; final
    publication still requires the complete payload-store scan.


REV1005 RELEASE CUTPOINT
    AnonSync-rev1005-2026.08.05.19.37-targetedterminal-localpulse-exactcursor-goshenite.zip
    goshenite
    Exact rev1005 source passed a fresh GCC 14.2 Debug complete graph with 555/555 configured build edges and exact-source no-work re-attestation; all 289/289 registered tests were accounted for across bounded immutable invocations, and the complete 48/48 product set was accounted for through aggregate and isolated heavy-test runs. Focused GCC proofs passed 20 terminal-state-codec, 706 payload-store, 4,999 reconciliation-protocol, 196 reconciliation-service, 536 folder-owner, 397 SQLite-owner, and 2,044 TLS-transport checks. Source audits passed 24/24 targeted-terminal/local-pulse, 38/38 terminal-continuation, 27/27 response-memory-shape, 34/34 direct-source-frame, 21/21 bounded-history-access, and 575/575 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 266/266 configured edges with no-work re-attestation; all 48/48 product tests were accounted for with leak detection and halt-on-error, including serial isolation of the two memory-heavy suites and the remaining lifecycle process tests. Focused sanitizer proofs passed 706 payload-store, 196 reconciliation-service, and 536 folder-owner checks; payload-store and folder-owner peak RSS were 729,432 KiB and 1,707,948 KiB. No compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic remained in passing evidence. The exact rev1004 parent SHA-256 matched 26c3fa06faeac08f6086d7154a76f05d536443067a941d7adf37579ca0f796d1 and passed 41/41 wrapper-aware package checks. The final active implementation projection contains 619 files / 28,550,115 bytes with SHA-256 5be67041b1b0254d8524a9ce05b0262a524f235d764601008398b9b95b69d778. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excludes interrupted aggregate CTest wrappers, one concurrent sanitizer lifecycle fixture whose precondition was invalidated by test concurrency but which passed serially on the same binaries, remount-vanished unsealed worktrees, and obsolete validator branches and builds.
    Rev1005 exact-opens the terminal journal, complete staged inode, and possible
    digest name for intermediate verification without payload-root enumeration.
    One authenticated apply advances at most 32 fixed steps (1 GiB shipping
    frontier), and a deferred-terminal range path prevents multi-file pages from
    crossing that budget. Final publication still requires the complete store
    scan and exact no-replace rename.


REV1004 RELEASE CUTPOINT
    AnonSync-rev1004-2026.08.05.16.01-terminalcontinuation-zerobytepulse-inodejournal-cordierite.zip
    cordierite
    Exact rev1004 source passed a fresh GCC 14.2 Debug complete graph with 555/555 configured build edges, followed by exact-source CMake regeneration and bundled-SQLite no-work re-attestation; all 288/288 registered tests and an independent isolated 48/48 product replay passed. Focused GCC proofs passed 20 terminal-state-codec, 696 payload-store, 4,999 reconciliation-protocol, 194 reconciliation-service, 536 folder-owner, 397 SQLite-owner, and 2,044 TLS-transport checks. Source audits passed 38/38 bounded terminal-verification-continuation checks and 567/567 structural authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph compiled its 266-edge configured dependency set across bounded resumptions; the first final link exposed that the new codec test was present in the sanitizer compile inventory but absent from the final-link inventory, the target graph was corrected, 28 exact-source relink edges and a no-work re-attestation passed, and all 48/48 registered product commands passed serially with leak detection and halt-on-error. Focused sanitizer proofs passed the same 20 terminal-state-codec, 696 payload-store, 4,999 protocol, 194 reconciliation-service, and 536 folder-owner checks; payload-store, reconciliation-service, and folder-owner peak RSS was 648,772 KiB, 780,832 KiB, and 1,694,640 KiB. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev1003 parent SHA-256 matched 58be646d3714895037e2dd1f928aa81e2fd200614eb9dfa75a5fdde16a424b53 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 36/36 changed wrapper files, all 35/35 changed project files, all 32/32 changed active files, and the complete 618-file active projection byte-for-byte and mode-for-mode. The final active implementation projection contains 618 files / 28,499,104 bytes with SHA-256 7b4499a95932e5d3ec3452c9982c3dc8f3f2a3e15b79962f90b953144ac709e9. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excludes both remount-vanished unsealed worktrees and their builds, obsolete pre-generation-8 evidence, the first aggregate sanitizer run invalidated by concurrent memory-heavy tests, the CTest wrapper invocation that stalled despite a passing direct proof, and the pre-correction sanitizer final-link failure.
    Rev1004 bounds receiver terminal SHA-256 to 32 MiB per owner call with a
    checksum-framed, store-identity- and staged-inode-bound two-slot journal.
    Reconciliation generation 8 preserves the exact operation obligation after
    all payload bytes arrive: terminal turns are payload-cold, keep the prior
    cursor, and admit metadata only after final local publication. Missing,
    malformed, foreign, or stale journals restart boundedly at offset zero and
    never cause a complete legacy reread or data truncation. Per-step peer-turn
    and namespace-observation amplification, source-side whole-manifest work,
    target-scale measurements, durable indexing, rename/move, directory
    semantics, and selective placeholders/eviction remain open.

REV1003 RELEASE CUTPOINT
    AnonSync-rev1003-2026.08.05.12.35-boundedpredecessor-partialindex-terminalfence-phenakite.zip
    phenakite
    Exact rev1003 source passed a fresh GCC 14.2 Debug graph: 262/262 product-dependency edges plus 290/290 remaining all-target edges (552/552 total), followed by bundled-SQLite re-attestation; all 286/286 registered tests and an independent 47/47 product replay passed. Focused GCC proofs passed 677 payload-store, 189 reconciliation-service, 536 folder-owner, 397 SQLite-owner, and 2,044 TLS-transport checks. Source audits passed 22/22 bounded predecessor projection, 32/32 bounded cross-file projection, 31/31 bounded local reuse, 31/31 content-defined delta, 27/27 multi-range window, 27/27 manifest reference, 21/21 bounded-history access, and 548/548 structural authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 262/262 edges and all 47/47 product tests passed with leak detection and halt-on-error; focused sanitizer proofs passed 677 payload-store, 189 reconciliation-service, and 536 folder-owner checks, with peak RSS 519,504 KiB, 791,616 KiB, and 1,704,200 KiB respectively. Aggregate final-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev1002 parent SHA-256 matched e547cbe11ae3bae98f15946a38f30dd64881510987edac35a6c490a64220bf03 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 14/14 changed wrapper paths, all 13/13 changed project paths, all 10/10 changed active paths, and the complete 614-file active projection byte-for-byte and mode-for-mode. The final active implementation projection contains 614 files / 28,363,976 bytes with SHA-256 16eeae537cb0683f6a51aa044b9c9aea9a44f93ced30530664b5de55cb580aa8. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excluded the remount-vanished initial worktree and build, the rejected raw pathname-carried SHA-state prototype, the stale non-authoritative /home/oai/share validator and its build tree, the initial unbuilt focused-sanitizer target invocation, and the superseded rev0999 lexical oracle failure before its exact cutpoint-owned lifetime check was corrected.
    Rev1003 bounds same-path predecessor content-defined projection to one
    32 MiB step per apply, reuses completed chunks before whole-source
    completion, centralizes same-path and cross-file incremental indexing, and
    clears enclosing indices when lower projection state fails. It explicitly
    leaves terminal whole-target verification exact and unbounded, excludes a
    rejected raw pathname-carried SHA-state shortcut, and remains process-local,
    not restart-durable, and not a durable or global chunk index.


REV1002 RELEASE CUTPOINT
    AnonSync-rev1002-2026.08.05.11.19-localcopyfrontier-interiorresume-wireoverlap-sinhalite.zip
    sinhalite
    Exact rev1002 source passed a fresh GCC 14.2 Debug graph (551/551 configured build edges) and a no-work bundled-SQLite re-attestation; all 285/285 registered tests were accounted for, including both final documentation-sensitive audits, and an independent 47/47 product replay passed. Focused GCC proofs passed 677 payload-store, 185 reconciliation-service, 536 folder-owner, 397 SQLite-owner, and 2,044 TLS-transport checks. Source audits passed 31/31 bounded local reuse, 32/32 bounded resumable cross-file projection, 31/31 content-defined delta, 27/27 multi-range window, 27/27 manifest reference, and 538/538 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product dependency graph completed 262/262 edges and reached a no-work re-attestation; all 47/47 product tests were accounted for with leak detection and halt-on-error. Focused sanitizer proofs passed 677 payload-store, 185 reconciliation-service, and 536 folder-owner checks; the folder-owner proof completed in 30.21 seconds at 1,694,316 KiB peak RSS, the reconciliation-service proof in 21.07 seconds at 778,188 KiB, and the payload-store proof in 9.47 seconds at 519,228 KiB. Aggregate final-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev1001 parent SHA-256 matched f5f7313ecd228074cd040cf432305626aa2654e4d936c125ec4daa26098b2de4 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 17/17 changed wrapper paths, all 16/16 changed project paths, all 13/13 changed active paths, and the complete 613-file active projection byte-for-byte and mode-for-mode. The final active implementation projection contains 613 files / 28,332,387 bytes with SHA-256 adcc77e2efda814bfb8d69cfd03ee289ba7077085cd3fa6a6c44e45d90cd4374. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excluded remount-vanished scratch worktrees, the divergent unsealed local-copy prototype, an interrupted aggregate sanitizer shard, the pre-build missing-target invocation, superseded lexical-audit failures, and generated Python bytecode removed before projection sealing.


REV1001 RELEASE CUTPOINT
    AnonSync-rev1001-2026.08.05.08.49-boundedprojection-lateavailability-singleindex-chrysoprase.zip
    chrysoprase
    Exact rev1001 source passed a fresh GCC 14.2 Debug graph (551/551 configured build edges) and a no-work bundled-SQLite re-attestation; all 284/284 registered tests were accounted for, including both final documentation-sensitive audits, and an independent 47/47 product replay passed. Focused GCC proofs passed 677 payload-store, 158 reconciliation-service, 536 folder-owner, 397 SQLite-owner, and 2,044 TLS-transport checks. Source audits passed 32/32 bounded resumable projection, 22/22 inherited cross-file discovery, 31/31 content-defined delta, 27/27 manifest reference, and 521/521 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product dependency graph completed 262/262 edges and reached a no-work re-attestation; all 47/47 product tests were accounted for with leak detection and halt-on-error. Focused sanitizer proofs passed 677 payload-store, 158 reconciliation-service, and 536 folder-owner checks; the folder-owner proof completed in 32.10 seconds at 1,684,368 KiB peak RSS. Aggregate final-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev1000 parent SHA-256 matched c68736ec03cd91298180b689a5c85228cdced06679e3b1fc836949017fd6d8c3 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 21/21 changed wrapper paths, all 20/20 changed project paths, all 17/17 changed active paths, and the complete 612-file active projection byte-for-byte and mode-for-mode. The final active implementation projection contains 612 files / 28,276,868 bytes with SHA-256 9e3197543e4f453cd5bd17897304ab44c3733e08e510a496b391d56383ee3b9e. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excluded remount-vanished worktrees and caches, the divergent availability-only release branch, interrupted aggregate CTest wrappers, superseded lexical-audit failures, and generated Python bytecode removed before projection sealing.


REV1000 RELEASE CUTPOINT
    AnonSync-rev1000-2026.08.05.06.02-crossfilechunks-visiblepage-singlehash-hackmanite.zip
    hackmanite
    Exact rev1000 source passed a fresh GCC 14.2 Debug graph (551/551 configured build edges) and a no-work bundled-SQLite re-attestation; all 283/283 registered tests were accounted for, including the two final documentation-sensitive source audits, and an independent 47/47 product replay passed. Focused GCC proofs passed 397 SQLite-owner, 144 reconciliation-service, 536 folder-owner, and 2,044 TLS-transport checks. Source audits passed 22/22 cross-file discovery, 31/31 content-defined delta, 27/27 manifest-reference, and 511/511 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product dependency graph completed 262/262 edges and reached a no-work re-attestation; all 47/47 product tests passed with leak detection and halt-on-error. Focused sanitizer proofs passed 397 SQLite-owner, 144 reconciliation-service, and 536 folder-owner checks; the folder-owner proof completed in 29.87 seconds at 1,690,840 KiB peak RSS, the reconciliation-service proof in 30.17 seconds at 774,444 KiB, and the SQLite-owner proof in 11.38 seconds at 777,440 KiB. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0999 parent SHA-256 matched 7b897c44e66870dd55e5df707d5d5e5180f60edbbe2baf4af431b861490cd3e0 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 20/20 changed wrapper paths, all 19/19 changed project paths, all 16/16 changed active paths, and the complete 611-file active projection byte-for-byte and mode-for-mode. The final active implementation projection contains 611 files / 28,197,616 bytes with SHA-256 9653cca2703de4448b510a49c8321d95c72354716de08152bedaec8185197c05. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excluded remount-vanished worktrees and caches, timestamp-only CMake regeneration attempts, interrupted aggregate real-process harnesses, a divergent indexed cross-file prototype and its validators, unrelated build lanes, and a redundant terminated sanitizer rerun.


REV0999 RELEASE CUTPOINT
    AnonSync-rev0999-2026.08.05.02.52-primarykeypage-identitycutpoint-historycold-taaffeite.zip
    taaffeite
    Exact rev0999 source passed a fresh GCC 14.2 Debug graph (551/551 configured build edges)
    and a no-work bundled-SQLite re-attestation; all 282/282 registered tests were accounted
    for, including the two final documentation-sensitive source audits, and an independent 47/47
    product replay passed. Focused GCC proofs passed 380 SQLite-owner, 122 reconciliation-
    service, and 536 folder-owner checks. Source audits passed 21/21 bounded-history-access,
    34/34 direct-source-frame, 27/27 response-memory-shape, 30/30 targeted-path-cutpoint, and
    503/503 structural-authority checks. A fresh Clang 17 Debug
    AddressSanitizer/UndefinedBehaviorSanitizer product dependency graph completed 262/262 edges
    across bounded resumptions and reached a no-work re-attestation; all 47/47 product tests
    passed with leak detection and halt-on-error. Focused sanitizer proofs passed 380 SQLite-
    owner, 122 reconciliation-service, and 536 folder-owner checks; the folder-owner proof
    completed in 28.75 seconds at 1,689,024 KiB peak RSS, while the complete product lane peaked
    at 1,692,312 KiB. Aggregate retained-log inspection found no compiler, linker,
    AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic.
    The exact rev0998 parent SHA-256 matched
    dbc9b4f7fb972abd2ecfa10cabebeed6b5bba7c8c277d511bf2834d87bfd702f and passed 41/41 wrapper-
    aware package checks. The binary-aware source patch reconstructed all 17/17 changed wrapper
    paths, all 16/16 changed project paths, all 13/13 changed active paths, and the complete
    610-file active projection byte-for-byte and mode-for-mode. The final active implementation
    projection contains 610 files / 28,125,448 bytes with SHA-256
    5110b2cce7e9f19917c9bf10a958fb22c4a42eee1affdadb64b5c88128153d68. Validation excluded
    divergent unsealed rev0999 prototypes, an orphaned exclusion guard that named the live
    authority, unrelated compiler/test lanes, vanished remount-era worktrees and build caches,
    interrupted build chunks, and every result not re-proved from the reconstructed exact
    source. Final directory, ZIP, CRC, path-policy, no-symlink, and clean-extraction equality
    checks remain mandatory publication gates.


REV0998 RELEASE CUTPOINT
    AnonSync-rev0998-2026.08.05.01.10-directsourceframe-zerostaging-fourterabyteproof-ulexite.zip
    ulexite
    Exact rev0998 source passed a fresh GCC 14.2 Debug graph (551/551 configured build edges) and a no-work bundled-SQLite re-attestation; all 281/281 registered tests and an independent 47/47 product replay were accounted for from the exact source. Focused GCC proofs passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 652 payload-store, 39 content-defined-chunker, 98 network-model plus 41 generated-operation, 361 SQLite-owner, 536 folder-owner, 110 sync-once, 4,989 reconciliation-protocol, 6 response-frame-memory, 25 borrowed-memory-shape, 10 direct-source-frame, 117 reconciliation-service, 2,044 TLS-transport, and 162 local-control checks. Source audits passed 34/34 direct-source-frame, 19/19 response-frame-memory, 27/27 response-memory-shape, 33/33 targeted-source-access, and 496/496 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product dependency graph completed 262/262 edges; all 47/47 product tests passed with leak detection and halt-on-error. Focused sanitizer proofs passed 652 payload-store, 4,989 reconciliation-protocol, 10 direct-source-frame, 117 reconciliation-service, 2,044 TLS-transport, and 536 folder-owner checks; the folder-owner proof completed in 29.39 seconds at 1,692,128 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0997 parent SHA-256 matched 64125a2e82f1e9bb789c14abc2f94f5dbf55c667e6f61b92406b5fbd4389e6de and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 25/25 changed project paths, all 22/22 changed active paths, the one changed wrapper restart page, and the complete 609-file active projection byte-for-byte and mode-for-mode. The final active implementation projection contains 609 files / 28,088,843 bytes with SHA-256 35acfcd7ff22a865d1321a5272b96af33dd6d138a21641178386a4ab746fbe41. Validation excluded two divergent unsealed rev0998 branches, pathname-based cleanup actors, vanished worktrees, interrupted aggregate CTest wrappers, and every result not bound to the final exact source. Final directory, ZIP, CRC, path-policy, no-symlink, and clean-extraction equality checks remain mandatory publication gates.


REV0997 RELEASE CUTPOINT
    AnonSync-rev0997-2026.08.04.22.41-singleframe-ownedtls-borrowedstaging-diaspore.zip
    diaspore
    Exact rev0997 source passed a fresh 549-edge GCC 14.2 Debug graph and a no-work bundled-SQLite re-attestation; all 279/279 registered tests passed, and an independent 46/46 product replay passed. Focused GCC proofs passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 650 payload-store, 39 content-defined-chunker, 98 network-model plus 41 generated-operation, 361 SQLite-owner, 536 folder-owner, 110 sync-once, 4,967 reconciliation-protocol, 6 source-frame-memory, 25 borrowed-memory-shape, 117 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 19/19 direct-response-frame, 27/27 borrowed-response-memory, and 482/482 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 260/260 edges; all 46/46 product tests passed with leak detection and halt-on-error, and focused sanitizer proofs passed 650 payload-store, 4,967 reconciliation-protocol, 6 source-frame-memory, 25 borrowed-memory-shape, 117 reconciliation-service, and 2,044 TLS-transport checks. The sanitized 536-check folder-owner proof completed in 28.20 seconds at 1,688,636 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0996 parent SHA-256 matched f57105c8156a138decc394c4c25092b87d5df83f919b03c401e18a3fec75a007 and passed 41/41 wrapper-aware package checks. Its inherited stale visible goshenite/20.48 labels were corrected to the actual sealed petalite/20.52 identity already bound by lineage and release gate. The active implementation projection contains 607 files / 27,989,270 bytes with SHA-256 00840cfa9a06971c6d5e69784303b524a8158275624a7abe78b17b38027c8f5b. Final directory, ZIP, CRC, path-policy, no-symlink, and clean-extraction equality checks remain mandatory publication gates.


REV0996 RELEASE CUTPOINT
    AnonSync-rev0996-2026.08.04.20.52-multirangewindow-turncollapse-memoryfrontier-petalite.zip
    petalite
    Exact rev0996 source passed a fresh 545-edge GCC 14.2 Debug graph and a no-work bundled-SQLite re-attestation; all 275/275 registered tests were accounted for across bounded terminal shards, and an independent 44/44 product replay passed. Focused GCC proofs passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 650 payload-store, 39 content-defined-chunker, 98 network-model plus 41 generated-operation, 361 SQLite-owner, 536 folder-owner, 110 sync-once, 4,960 reconciliation-protocol, 117 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 31/31 content-defined-delta, 18/18 source-chunk-index, 27/27 manifest-reference, 33/33 targeted-source-access, 52/52 selective-sync, 27/27 multi-range-window, and 472/472 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 256/256 edges; all 44/44 product tests passed with leak detection and halt-on-error, and focused sanitizer proofs passed 650 payload-store, 39 content-defined-chunker, 4,960 reconciliation-protocol, 117 reconciliation-service, and 2,044 TLS-transport checks. The sanitized 536-check folder-owner proof completed in 31.26 seconds at 1,694,252 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0995 parent SHA-256 matched 1129c9f66ba195ceda3f18b274ae58a997820ce332b44c39f9cfdf0fa033efc2 and passed 41/41 wrapper-aware package checks. The active implementation projection contains 603 files / 27,896,855 bytes with SHA-256 a42f7210b2c2109e990fef097fc26e87497cffe3770b4a1fe4b1de20f6432052. Final directory, ZIP, CRC, path-policy, no-symlink, and clean-extraction equality checks remain mandatory publication gates.

REV0995 RELEASE CUTPOINT
    AnonSync-rev0995-2026.08.04.19.00-sourceindex-millionrange-framingfrontier-indicolite.zip
    indicolite
    Exact rev0995 source passed a fresh 545-edge GCC 14.2 Debug graph and a no-work bundled-SQLite re-attestation; all 274/274 registered tests were accounted for across bounded terminal shards and an independent 44/44 product replay passed. Focused GCC proofs passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 650 payload-store, 39 content-defined-chunker, 98 network-model plus 41 generated-operation, 361 SQLite-owner, 536 folder-owner, 110 sync-once, 4,956 reconciliation-protocol, 115 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 18/18 source-chunk-index, 31/31 content-defined-delta, 27/27 manifest-reference, 33/33 targeted-source-access, 52/52 selective-sync, and 463/463 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 256/256 edges; all 44/44 product tests passed with leak detection and halt-on-error, and focused sanitizer proofs passed 650 payload-store, 39 content-defined-chunker, 4,956 reconciliation-protocol, 115 reconciliation-service, and 2,044 TLS-transport checks. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0994 parent SHA-256 matched cce60aea2ce146228f5163720b74b1ec666b3e56e204c5f155108d22f91ecd9a and passed 41/41 wrapper-aware package checks. The active implementation projection contains 602 files / 27,851,618 bytes with SHA-256 98fd496d786433027529c2628adc2a0f1e12c029300cb1084bd55804c965d7c1. Final directory, ZIP, CRC, path-policy, no-symlink, and clean-extraction equality checks remain mandatory publication gates.

REV0994 RELEASE CUTPOINT
    AnonSync-rev0994-2026.08.04.17.13-contentdefined-shiftedreuse-boundedmanifest-kyanite.zip
    kyanite
    Exact rev0994 source completed a fresh 540-edge GCC 14.2 Debug graph and a no-work bundled-SQLite re-attestation; all 273/273 registered tests and all 44/44 product tests were accounted for across bounded terminal shards. Focused GCC proofs passed 39 content-defined-chunker, 650 payload-store, 4,955 reconciliation-protocol, 113 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 31/31 content-defined-delta, 27/27 manifest-reference, 33/33 targeted-source-access, 52/52 selective-sync, and 458/458 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 256/256 edges; all 44/44 product tests and the same five focused suites passed with leak detection and halt-on-error. The sanitizer folder-owner proof passed 536 checks with 1,686,160 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0993 parent SHA-256 matched a9ac6bd2a95c56061d4ea836725d3e5691f117e2887d415b4bb82c9964540504 and passed 41/41 checks under its sealed wrapper-aware verifier. The binary-aware source patch reconstructed all 29/29 changed project paths, all 26/26 changed active paths, and the complete 601-file active projection byte-for-byte and mode-for-mode. The active projection contains 601 files / 27,831,652 bytes with SHA-256 ec5931b9b28566148ffd8d053d22d88a07549ac39b52d1e22dffb66db21e07e7. Final directory, ZIP, CRC, path-policy, no-symlink, and clean-extraction equality checks remain mandatory publication gates.


REV0993 RELEASE CUTPOINT
    AnonSync-rev0993-2026.08.04.15.02-requestscopedsource-liveavailability-retentionunroot-prehnite.zip
    prehnite
    Exact rev0993 source reached a no-work GCC 14.2 Debug complete graph across four bounded resumptions with no retained compiler or linker diagnostic; all 272/272 registered tests and all 43/43 independently replayed product tests were accounted for. Focused GCC proofs passed 644 payload-store, 119 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 42/42 fixed-block-delta, 52/52 selective-sync, 31/31 manifest-reference, 33/33 targeted-source-access, and 453/453 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 252/252 edges and all 43/43 product tests passed with leak detection and halt-on-error; focused sanitizer proofs passed the same 644, 119, and 2,044 checks, including the 536-check folder-owner proof in the product lane. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0992 parent SHA-256 matched 2e0c19129634200ea2c1e2575e3cdcb286b46257bea2f47993558ebfdcbbca93 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 14/14 changed active files and the complete 598-file projection byte-for-byte and by mode. The final active implementation projection contains 598 files / 27,812,299 bytes with SHA-256 3416936101fdc9cc2ae244bedaa39546575e9a3a52ae5c7c017fcc3d5f6af9ba. The final wrapper directory and ZIP passed release-package verification, CRC integrity, canonical-path and no-symlink checks, and clean-extraction path/byte/type/mode equality.

REV0992 RELEASE CUTPOINT
    AnonSync-rev0992-2026.08.04.13.20-manifestreference-indexcache-restartbootstrap-sodalite.zip
    sodalite
    Exact rev0992 source passed the GCC 14.2 Debug 340-edge rebuild to a no-work bundled-SQLite re-attestation, all 271/271 registered tests, and an independent 43/43 product replay. Focused GCC proofs passed 4,891 reconciliation-protocol, 109 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 42/42 fixed-block-delta, 52/52 selective-sync, 31/31 manifest-reference, and 448/448 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 252/252 edges; all 43/43 product tests passed with leak detection and halt-on-error. Focused sanitizer proofs passed 98 network-model checks plus 41 generated operations, 26 selective-policy, 4,891 protocol, 361 SQLite-owner, 238 prepared-publication, 536 folder-owner, 109 service, and 2,044 TLS checks; the folder-owner proof peaked at 1,689,104 KiB RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0991 parent SHA-256 matched ac2c873d6828d1421a7c0e637ba7efa49dce62f59e7f7dbcf8e9c40d1398016c and passed 41/41 wrapper-aware package checks. The final active implementation projection contains 597 files / 27,777,046 bytes with SHA-256 25a5beffcc7792c5a6a96e42e85803597a67f56d7eb6b67f0a617ad3397a565d.

REV0991 RELEASE CUTPOINT
    AnonSync-rev0991-2026.08.04.11.50-countedwitness-targetedpublication-quarantinefence-spessartine.zip
    spessartine
    Exact rev0991 source passed the GCC 14.2 Debug complete graph across its 470-edge exact-change dependency state, followed by a no-work bundled-SQLite re-attestation, all 270/270 registered tests, and an independent 43/43 product replay. Focused GCC proofs passed 1,291 hash-graph, 238 prepared-publication, 361 SQLite-owner, and 536 folder-owner checks. Source audits passed 43/43 SQLite-owner, 30/30 targeted local-publication, and 442/442 structural authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 252/252 edges; all 43/43 product tests passed with leak detection and halt-on-error. Direct sanitizer proofs passed the same 1,291, 238, 361, and 536 checks; the folder-owner proof peaked at 1,688,812 KiB RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0989 parent SHA-256 matched 9af82eab8ce067088e65bf1ca165eb099967b72e18fde3660767454374a9387e and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 14/14 changed active files and the complete 596-file projection byte-for-byte and by mode. The final active implementation projection contains 596 files / 27,719,683 bytes with SHA-256 25888965fb9c560846cb528617655c38586f80dd9e27f2c3538baecb83f696b3. The final wrapper directory and ZIP passed release-package verification, CRC integrity, canonical-path and no-symlink checks, and clean-extraction path/byte/type/mode equality.

REV0989 RELEASE CUTPOINT
    AnonSync-rev0989-2026.08.04.07.53-targetedreplica-historybounded-pathreproof-larimar.zip
    larimar
    Exact rev0989 source passed the GCC 14.2 Debug complete graph in its 540-edge configured dependency state, followed by a no-work bundled-SQLite re-attestation, all 269/269 registered tests, and an independent 43/43 product replay. Focused GCC proofs passed 356 SQLite-owner checks and 536 folder-owner checks. Source audits passed 52/52 selective-sync checks, 24/24 targeted catalog-cutpoint checks, 30/30 targeted replica path-cutpoint checks, and 433/433 structural authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 251/251 edges; all 43/43 product tests passed with leak detection and halt-on-error, including direct 356-check SQLite-owner and 536-check folder-owner proofs. The sanitized folder-owner proof peaked at 1,664,276 KiB RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0988 parent SHA-256 matched 067de76a76061db941ebccde03821c84134428152784954a51feba153505d23d and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 13/13 changed active files and the complete 593-file projection byte-for-byte and by mode. The final active implementation projection contains 593 files / 27,588,416 bytes with SHA-256 195b1897e39b44b6f32d2838ee6eff35dc65849de7a3e2e70c6bb0882d43ea4a. The final wrapper directory and ZIP passed release-package verification, CRC integrity, canonical-path and no-symlink checks, and clean-extraction path/byte/type/mode equality.

REV0988 RELEASE CUTPOINT
    AnonSync-rev0988-2026.08.04.06.00-targetedcatalog-pathcutpoint-projectionfence-celestite.zip
    celestite
    Exact rev0988 source passed the complete GCC 14.2 Debug graph in its 540-edge configured dependency state, including 261 exact-change rebuild edges and a no-work source re-attestation; 266/266 documentation-independent tests plus the finalized targeted-cutpoint and structural audits for complete 268/268 registered accounting; and 43/43 product tests in bounded exact-source invocations. Focused proof passed 532 folder-owner checks. Source audits passed 52/52 selective-sync, 24/24 targeted catalog-cutpoint, and 425/425 structural authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 251/251 edges; all 43/43 product tests passed with leak detection and halt-on-error, including the direct 532-check folder-owner proof at 1,668,096 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0987 parent SHA-256 matched 33680473e933ecf4e588eb24d8d90cf080002c256a2b4ed6408253424ded6d96 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 9/9 changed active files and the complete 592-file projection byte-for-byte and by mode. The final active implementation projection contains 592 files / 27,537,575 bytes with SHA-256 d9d3383d821bb05d6c41b9610ec3cbe0bfaceec60ec0c968d4ea9fa430c759f9. The final wrapper directory and ZIP passed release-package verification, CRC integrity, canonical-path and no-symlink checks, and clean-extraction path/byte/type/mode equality.

REV0987 RELEASE CUTPOINT
    AnonSync-rev0987-2026.08.04.03.36-selectivepolicy-rooteddematerialization-expansionfence-dioptase.zip
    dioptase
    Exact rev0987 source passed a fresh GCC 14.2 Debug complete graph (540/540 configured build edges), 265/265 documentation-independent tests plus the finalized selective-sync and structural audits for complete 267/267 registered-test accounting, and an independent 43/43 GCC product replay. Focused GCC proofs passed 26 selective-policy, 18/18 conditional-unlink-authority, 644 payload-store, 4,861 reconciliation-protocol, 106 reconciliation-service, 518 folder-owner, 2,043 TLS-transport, and 110 sync-once checks. Source audits passed 52/52 selective-sync, 43/43 atomic-publication, 42/42 fixed-block-delta, and 420/420 structural payload-store authority checks. A fresh Clang 17 Debug product graph completed 251/251 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 43/43 product tests passed in bounded exact-source invocations with leak detection and halt-on-error. Focused sanitizer proofs passed the same 26, 18, 644, 4,861, 106, 518, 2,043, and 110 checks; the folder-owner proof peaked at 1,649,884 KiB RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0986 parent SHA-256 matched 00eca1b35b4072365aac651717506a4d02f6ea9593124151c18af99de0d8c3c3 and passed 41/41 wrapper-aware package checks. The binary-aware patch reconstructed all 31/31 changed active files and the complete 591-file projection byte-for-byte and by mode. The final active implementation projection contains 591 files / 27,507,720 bytes with SHA-256 307fe1ce3827c871ffe3dfdc3f9c4ac477fbad1b205dfb6ef986ac3fccd2f59f. The final wrapper directory and ZIP remain publication-gated on the exact manifest, package verification, CRC integrity, canonical paths, absence of symlinks, and clean-extraction path/byte/type/mode equality.

REV0986 RELEASE CUTPOINT
    AnonSync-rev0986-2026.08.03.20.41-fixedblockdelta-multiterabyte-memoryfrontier-azurite.zip
    azurite
    Exact rev0986 source passed a fresh GCC 14.2 Debug complete graph (536/536 configured build edges), 264/264 documentation-independent tests plus the finalized fixed-block delta audit for complete 265/265 registered-test accounting, and an independent 42/42 GCC product replay. Focused GCC proofs passed 30 deployment-manifest, 4,638 reconciliation-protocol, 644 payload-store, 99 reconciliation-service, 2,043 TLS-transport, 470 folder-owner, and 110 sync-once checks. Source audits passed 42/42 fixed-block delta and multi-terabyte capacity checks, 41/41 database-replacement checks, and 412/412 structural payload-store authority checks. A fresh Clang 17 Debug product dependency graph completed 247/247 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 42/42 product tests passed in bounded exact-source invocations with leak detection and halt-on-error. Focused sanitizer proofs passed the same 4,638 protocol, 644 payload-store, 99 reconciliation-service, 2,043 TLS, and 470 folder-owner checks; the folder-owner proof peaked at 1,485,264 KiB RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0985 parent SHA-256 matched a87f6fcd1f7ea371e0974c4b89ca097def56e07301bc3ffeb9cbe19bdf496c4c and passed 41/41 wrapper-aware package checks. The binary-aware patch reconstructed all 23/23 changed active files and the complete 587-file projection byte-for-byte and by mode. The final active implementation projection contains 587 files / 27,271,627 bytes with SHA-256 7c706289c0b0e26d28a42d9b6c486a148044ab92c13a6cb0757696f038fbe1e2. The final wrapper directory and ZIP remain publication-gated on the exact manifest, package verification, CRC integrity, canonical paths, absence of symlinks, and clean-extraction path/byte/type/mode equality.

REV0985 RELEASE CUTPOINT
    AnonSync-rev0985-2026.08.03.18.23-roleboundbackup-detachedprofile-sharerecoverymap-orthoclase.zip
    orthoclase
    Exact rev0985 source passed the fresh GCC 14.2 Debug complete graph (536/536 configured build edges), all 264/264 registered tests in indexed final-source accounting, and an independent 42/42 product replay. Focused GCC proofs passed 108 file-effect SQLite-owner checks, 470 folder-owner checks, the existing 598-check database backup/recovery/replacement process oracle, and the new 699-check five-role backup oracle. Source audits passed 28/28 original backup checks, 31/31 role-bound backup checks, 39/39 TLS-membership profile checks, and 412/412 structural authority checks. A fresh Clang 17 Debug product dependency graph completed 247/247 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 42/42 product tests passed with leak detection and halt-on-error, including the direct 470-check folder-owner proof at 1,479,148 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0984 parent SHA-256 matched 0dcadb3e3bd4aa620e80e39ba009b9bdbbf89686b638c61c2e1fc4db961cd664 and passed 41/41 wrapper-aware package checks. The final active implementation projection contains 585 files / 27,187,739 bytes with SHA-256 ec2072db6a95736b907e8363844ac46cad7550c78433af2f9f0d359c4a9fdeb6. The binary-aware source patch and complete active projection
    are release-gated on exact reconstruction by bytes and mode. The final
    wrapper directory and ZIP remain publication-gated on the exact manifest,
    package verification, CRC integrity, canonical paths, absence of symlinks,
    and clean-extraction path/byte/type/mode equality.

REV0984 RELEASE CUTPOINT
    AnonSync-rev0984-2026.08.03.12.22-receiptresume-pathreproof-successorfence-grandidierite.zip
    grandidierite
    Exact rev0984 active source passed a fresh GCC 14.2 Debug graph (536/536 configured build edges), all 262/262 registered tests in an indexed final-source replay (261/261 immutable-preseal tests plus the final documentation-sensitive structural audit), and an independent 41/41 product replay. Focused GCC proofs passed 334 SQLite-owner checks, 38 deployment-binding checks, 102 snapshot-seal checks, 53 SQLite live-backup/replacement checks, 470 folder-owner checks, and the shipping database backup, recovery, replacement, and restart oracle passed 598 checks. Source audits passed 24/24 bounded-reader checks, 41/41 database-replacement checks, and 404/404 structural authority checks. A fresh Clang 17 Debug product dependency graph completed 247/247 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 41/41 product tests passed with leak detection and halt-on-error, including the direct 470-check folder-owner proof at 1,481,008 KiB peak RSS, and focused sanitized proofs passed the same 334, 38, 102, and 53 checks. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0983 parent SHA-256 matched 64ef96593d809861275fe7b9ec5fbf67554a25c23b6e543de70cfe9fd59519b6 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 12/12 changed active files and the complete 583-file projection byte-for-byte and by mode. The final active implementation projection contains 583 files / 27,098,385 bytes with SHA-256 48c4b04bb58f482b3dc8dc853ba951d78941ccbea552ddbb3e442a0b2ede2419. Validation excluded overlapping Ninja invocations, vanished build trees, divergent source authorities, interrupted nonterminal runs, and every result not bound to the frozen exact C++ source or the final prose-and-audit seal. The final wrapper directory and ZIP remain publication-gated on the exact manifest, package verification, CRC integrity, canonical paths, absence of symlinks, and clean-extraction path/byte/type/mode equality.

REV0983 RELEASE CUTPOINT
    AnonSync-rev0983-2026.08.03.06.40-logicalreplace-familyfence-rollbackproof-andalusite.zip
    andalusite
    Exact rev0983 active source passed the fresh GCC 14.2 Debug graph (535/535 configured build edges), all 262/262 registered tests in an indexed final-source replay, and an independent 41/41 product replay. Focused GCC proofs passed 334 SQLite-owner checks, 38 deployment-binding checks, 102 snapshot-seal checks, 53 SQLite live-backup/replacement checks, and the 381-check real database backup, recovery, and replacement process oracle. Source audits passed 28/28 database-backup checks, 28/28 database-replacement checks, 26/26 SQLite live-backup checks, and 402/402 structural authority checks. The fresh Clang 17 Debug product dependency graph completed 246/246 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 41/41 product tests passed in bounded exact-source shards with leak detection and halt-on-error, and focused sanitized proofs passed the same 334, 38, 102, and 53 checks. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0982 parent SHA-256 matched 41ce680f8a8b2cfc0cbf53e9be7379bab5460424da1fb0b20a721445222e48b2 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 15/15 changed active files and the complete 581-file projection byte-for-byte and by mode. The final active implementation projection contains 581 files / 27,002,934 bytes with SHA-256 819d8a6650843ecb0e3fe795e37eb69bc23449e308111f5c0f604954bdb62d3b. Validation excluded the divergent integrated branch, orphaned validators, vanished build trees, interrupted nonterminal runs, and every result not bound to the reconstructed exact source. The final wrapper directory and ZIP remain publication-gated on the release manifest, package verification, CRC integrity, canonical paths, absence of symlinks, and clean-extraction path/byte/type/mode equality.

REV0982 RELEASE CUTPOINT
    AnonSync-rev0982-2026.08.02.23.59-backupartifact-detachedverify-recoverybridge-scapolite.zip
    scapolite
    Exact rev0982 active source passed a fresh GCC 14.2 Debug graph (534/534 configured build edges), all 261/261 registered tests after final release-prose sealing, and an independent 41/41 product replay. Focused proofs passed 334 SQLite-owner checks, 38 deployment-binding checks, and the 265-check database backup/recovery process oracle. Source audits passed 27/27 deployment-binding checks, 100/100 transaction-stack authority checks, 27/27 backup checks, and 393/393 final structural authority checks. A fresh Clang 17 Debug product dependency graph completed 245/245 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 41/41 product tests were accounted for in bounded fresh invocations with leak detection and halt-on-error, and focused sanitized proofs passed the same 334 and 38 checks. Aggregate authoritative-log inspection retained no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0981 parent SHA-256 matched 1f27e580cae7e25d5b0f55df14688ff975e4e3b88f103a96e36f47421716b934 and passed 41/41 wrapper-aware package checks. The binary-aware patch reconstructed all 17 changed active files and the complete 577-file projection byte-for-byte and by mode. The final active implementation projection contains 577 files / 26,906,635 bytes with SHA-256 3e15ca2ba0f24c68b808290b11d64e0cd8b3d5b05c99eca5a7be358a988faaf4. Validation excluded the raw-savepoint prototype, source-divergent workers, vanished build trees, stale caches, and interrupted runs without terminal evidence. The final wrapper directory and ZIP are publication-gated on package verification, CRC integrity, canonical paths, absence of symlinks, and clean-extraction path/byte/type/mode equality.

REV0981 RELEASE CUTPOINT
    AnonSync-rev0981-2026.08.02.22.54-forensicpreflight-commitresult-singletonorder-euclase.zip
    euclase
    Exact rev0981 active source passed a fresh GCC 14.2 Debug graph (532/532 configured build edges), all 260/260 registered tests after final release-prose sealing, and an independent 41/41 product replay. The 105-check real-process recovery oracle proved descriptor-rooted read-only inspection, byte-for-byte SQLite-family preservation for malformed and stale expectations, exact one-step advancement, consumed-token rejection before writable open, narrow authority, and deployment-singleton ordering. The database-open policy audit passed 48/48 checks and the structural authority audit passed 385/385 checks. A fresh Clang 17 Debug product dependency graph completed 243/243 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 41/41 product tests passed serially with leak detection and halt-on-error. Aggregate authoritative-log inspection retained no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0980 parent SHA-256 matched 0fc470ab43ce97374e1a562f9c2c275b18bbc6f4e3f8c27127711ed7b18ca40d and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 14/14 changed active files and the complete 574-file projection byte-for-byte and by mode. The final active implementation projection contains 574 files / 26,812,446 bytes with SHA-256 d399a8ad3f077bf3467752e4355933be71117cdfff0f4cd789cd0cfd445f1b16. Validation was rerun from the reconstructed exact source after the cloudtainer removed prior unsealed worktrees; all vanished, interrupted, stale-cache, and source-divergent results were excluded. The final wrapper directory and ZIP are publication-gated on 41/41 package checks, CRC integrity, canonical paths, absence of symlinks, and clean-extraction path/byte/type/mode equality.

REV0980 RELEASE CUTPOINT
    AnonSync-rev0980-2026.08.02.19.56-databaseincarnation-recoveryepoch-retentionwitness-cassiterite.zip
    cassiterite
    Exact rev0980 C++ source passed a clean GCC 14.2 Debug graph (532/532 configured build edges), all 259/259 registered tests in an uninterrupted serial replay in 123.72 seconds, and an independent 40/40 GCC product replay in 67.12 seconds. The finalized source audits passed 43/43 SQLite-owner checks and 372/372 structural authority checks. Focused exact-source suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 30 retention-mark, 640 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 334 SQLite-owner, 470 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 158 local-control, 87/87 observer, and 6/6 observer-race checks. A clean Clang 17 Debug product dependency graph completed 243/243 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 40/40 product tests passed serially in 122.76 seconds with leak detection and halt-on-error. Focused sanitizer proof passed the 640-check payload-store suite in 16.57 seconds at 514,388 KiB peak RSS, the 470-check folder-owner suite in 21.90 seconds at 1,467,012 KiB peak RSS, and the 158-check local-control suite in 1.12 seconds at 106,900 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0979 parent SHA-256 matched 5fc1ee63e991a261b9473f7a80887eb2b010e5d6167dc09405dba20fb779f58f and passed 41/41 wrapper-aware package checks. Validation excluded the divergent local-control prototype, vanished or interrupted build caches, source-divergent workers, the superseded v6-only SQLite audit oracle, duplicate validators, and every result not bound to the reconstructed schema-v7 source. The binary-aware source patch reconstructed all 16/16 changed active files and the complete 573-file projection byte-for-byte and by mode. The final active implementation projection contains 573 files / 26,745,576 bytes with SHA-256 c3b2f86e2a279e4114a546260c4010af75030ae5cf03657beb5371f55405248f.

REV0979 RELEASE CUTPOINT
    AnonSync-rev0979-2026.08.02.17.02-durablemark-sourcegeneration-exceptionprovenance-jeremejevite.zip
    jeremejevite
    Exact rev0979 C++ source passed a clean GCC 14.2 Debug graph (532/532 configured build edges), 258/258 preseal registered runtime tests, and an independent 40/40 GCC product replay in 114.17 seconds. The finalized registered structural authority audit passed 362/362 checks, accounting for all 259/259 registered tests across the unchanged C++ bytes and final release prose. Focused exact-source suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 30 retention-mark, 640 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 463 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 158 local-control, 87/87 observer, and 6/6 observer-race checks. A clean Clang 17 Debug product dependency graph completed 243/243 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 40/40 product tests passed serially in 155.48 seconds with leak detection and halt-on-error. Focused sanitizer proof passed the 640-check payload-store suite in 11.33 seconds at 514,824 KiB peak RSS, the 463-check folder-owner suite in 37.23 seconds at 1,467,772 KiB peak RSS, and the 158-check local-control suite in 0.68 seconds at 113,860 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0978 parent SHA-256 matched 5d8c9bc1470f3c7bcd38ed039dc69d766bc1ff9fdddba1ee4ef9de49a045d734 and passed 41/41 wrapper-aware package checks. Validation excluded source-divergent retention prototypes, shared-cache and in-tree build contamination, self-restarting mutable-source launchers, interrupted rev0979-named sanitizer processes, and every result not bound to the byte-reconciled clean source. The binary-aware source patch reconstructed all 13/13 changed active files and the complete 573-file projection byte-for-byte and by mode. The final active implementation projection contains 573 files / 26,681,569 bytes with SHA-256 7ef1c72b253f25a8e8fb1154aafbc4ce0220891b4de7eebef6ce139eb76e7f7b.

REV0978 RELEASE CUTPOINT
    AnonSync-rev0978-2026.08.02.13.43-processscope-writerfence-candidateprobe-serendibite.zip
    serendibite
    Exact rev0978 source passed a fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests in bounded final-source shards, and an independent 39/39 product replay in 86.36 seconds. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 630 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 450 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 158 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 349/349 checks. An isolated Clang 17 Debug product dependency graph completed 239/239 edges with AddressSanitizer and UndefinedBehaviorSanitizer. All 39/39 product tests passed in bounded lanes with leak detection and halt-on-error: the allocation-heavy 450-check folder-owner test passed separately in 30.71 seconds at 1,454,776 KiB peak RSS, and the remaining 38/38 product tests passed in 114.43 seconds. Focused sanitizer proof also passed the 630-check payload-store suite in 9.06 seconds at 503,672 KiB peak RSS and the 158-check local-control suite in 0.74 seconds at 112,900 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0977 parent SHA-256 matched acf4f08be987f2fb5d44b2ff1a0e4b34a460248ac29f72ff0f3498f7d7f0e73f and passed 41/41 checks under the rev0978 wrapper-aware verifier. The binary-aware source patch reconstructed all 16/16 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,575,951 bytes with SHA-256 f47ed3037fb6a2e553a2b278e7dd591f3b97afd4d62e44e8d0fb0dcb69962c89. Validation excluded superseded monolithic sanitizer invocations, interrupted full-registry wrappers, competing orphan release launchers, stale or source-divergent runs, and a transient Python bytecode cache removed before projection sealing.

REV0977 RELEASE CUTPOINT
    AnonSync-rev0977-2026.08.02.11.43-livecapabilities-inodelease-readerfence-painite.zip
    painite
    Exact rev0977 source passed a fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests in a final serial replay (129.22 seconds), and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 613 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 448 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 155 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 339/339 checks. An isolated Clang 17 Debug product dependency graph completed 239/239 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 39/39 product tests passed serially in 144.09 seconds with leak detection and halt-on-error. Focused sanitizer proof passed the 613-check payload-store suite in 13.33 seconds at 484,272 KiB peak RSS, the 448-check folder-owner suite in 39.78 seconds at 1,453,628 KiB peak RSS, and the 155-check local-control suite in 1.44 seconds at 105,116 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0976 parent SHA-256 matched 44d90e8b74fffe16239ea0e6b1516a215950d7bc1d558344e7c64b5189a7f566 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 18/18 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,498,367 bytes with SHA-256 d4ad87ef909365a2af2515451da83248a94680bce23f0056dfff0f3c8db0b8b6. Validation excluded overlapping or stale shared-tree launchers, interrupted wrappers, divergent unsealed branches, and every result not bound to the exact final active projection.

REV0976 RELEASE CUTPOINT
    AnonSync-rev0976-2026.08.02.09.24-transientroots-inodewitness-reservedfrontier-tanzanite.zip
    tanzanite
    Exact rev0976 source passed a fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 601 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 443 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 155 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 320/320 checks. A fresh Clang 17 Debug product dependency graph completed 239/239 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 601-check payload-store suite in 9.26 seconds at 471,604 KiB peak RSS, the 443-check folder-owner suite in 21.26 seconds at 1,435,944 KiB peak RSS, and the 155-check local-control suite in 0.60 seconds at 99,144 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0975 parent SHA-256 matched f702193a48c41b500ded456a901532f18113d183170a86fed4203dcbc0606269 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 16/16 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,404,832 bytes with SHA-256 1e93e8685e695b93153a8a2a4ff05991c67ca5587a11b95f02cf5c95c931a17b. Validation excluded the partially generated unsealed evidence directory, every divergent cache tree, and every interrupted or superseded run.

REV0975 RELEASE CUTPOINT
    AnonSync-rev0975-2026.08.02.07.33-linearprojection-candidatewitness-cutpointmark-vesuvianite.zip
    vesuvianite
    Exact rev0975 source passed a fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 441 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 155 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 312/312 checks. A fresh Clang 17 Debug product dependency graph completed 239/239 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 441-check folder-owner suite in 22.74 seconds at 1,418,744 KiB peak RSS and the 155-check local-control suite in 0.63 seconds at 99,008 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0974 parent SHA-256 matched 82d713da7546d14e3875e4b5beea1fb6ecb3fe4d4031e07c01ec7a10d39165f7 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 11/11 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,357,846 bytes with SHA-256 f2df82e79b066db5af8cef5545d4135e6714bbdf7cd05b1d72d6b8c069e12826. Validation excluded the contaminated unsealed payload-usage prototype, its abandoned worktree, and every result produced from it.

REV0974 RELEASE CUTPOINT
    AnonSync-rev0974-2026.08.02.05.24-retentionplan-rootreasons-digestcursor-zircon.zip
    zircon
    Exact rev0974 source passed the fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 441 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 155 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 305/305 checks. A clean Clang 17 Debug product dependency graph completed 239/239 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 39/39 product tests passed across bounded serial shards with leak detection and halt-on-error. One superseded combined sanitizer shard let the unchanged service lifecycle oracle reach its 30-second runtime cap after four of five cycles; the isolated authoritative rerun passed in 12.79 seconds with no sanitizer diagnostic. Focused sanitizer proof passed the 320-check SQLite-owner suite in 3.33 seconds at 556,136 KiB peak RSS, the 441-check folder-owner suite in 21.71 seconds at 1,412,208 KiB peak RSS, and the 155-check local-control suite in 0.63 seconds at 98,620 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0973 parent SHA-256 matched 62d265f026db82c946fe86df8700c6019826afc86604242716e9af564b84f7cd and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 18/18 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,336,658 bytes with SHA-256 1eb35263f32e14bb15be047a6bcadc88eb7aaac6bd5bcb9fd0898bf593b3377b. Validation excluded the rejected duplicate age-based planner prototype and every interrupted or timing-only non-authoritative run.

REV0973 RELEASE CUTPOINT
    AnonSync-rev0973-2026.08.02.03.59-retentionpins-migrationproof-actionlane-kunzite.zip
    kunzite
    Exact rev0973 source passed the fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 433 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 140 local-control, 87/87 observer, and 6/6 observer-race checks. The upgraded SQLite-owner source audit passed 43/43 checks, and the complete structural authority audit passed 292/292 checks. A clean Clang 17 Debug product dependency graph completed 239/239 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 320-check SQLite-owner suite in 2.89 seconds at 556,172 KiB peak RSS, the 433-check folder-owner suite in 26.11 seconds at 1,432,996 KiB peak RSS, and the 140-check local-control suite in 0.56 seconds at 94,148 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0972 parent SHA-256 matched 5d8c791ded176f4b76e685103bf75b7697d5e466f5f8236ef7bf822f03523ded and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 21/21 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,229,745 bytes with SHA-256 576051d058ff39a23b32d3aef2487e296a18a398a67e4e28bc5a331e4e8b043e. The registry-driven audit correction also added direct exact v5-to-v6 migration, restart, and malformed-cutpoint rollback proof.

REV0972 RELEASE CUTPOINT
    AnonSync-rev0972-2026.08.02.01.45-retainedreachability-canonicalfrontier-schemaseal-demantoid.zip
    demantoid
    Exact rev0972 source passed the fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 296 SQLite-owner, 421 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 132 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 279/279 checks. A clean Clang 17 Debug product dependency graph completed 239/239 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 421-check folder-owner suite in 33.17 seconds at 1,376,128 KiB peak RSS and the 132-check local-control suite in 0.57 seconds at 91,608 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0971 parent SHA-256 matched 7212288343824982bfc5c505cf32c39c9ec920d84850103daeafdbd8187f8c33 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 14/14 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,108,596 bytes with SHA-256 e226a95f2c0bf343ad4ff41353415686ea78bde24bcf3ea12c615eaac745d912. Validation also removed multiple orphaned divergent rev0972 build and prototype trees so only the sealed reachability/frontier source and its isolated build directories contributed release authority.

REV0971 RELEASE CUTPOINT
    AnonSync-rev0971-2026.08.02.00.10-bytefrontier-canonicalstream-singlecopy-charoite.zip
    charoite
    Exact rev0971 source passed the clean GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 296 SQLite-owner, 406 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 132 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 267/267 checks. A clean-root Clang 17 Debug product dependency graph completed 239/239 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 406-check folder-owner suite in 18.93 seconds at 1,371,184 KiB peak RSS and the 132-check local-control suite in 0.57 seconds. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0970 parent SHA-256 matched 57cb832afa5b63c3b7ab63028873855ec18c6e2ec90059c7ac7b64200ba2e7d7 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 13/13 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,058,026 bytes with SHA-256 11b2a46a3fc169546819c71172347dc64bb6f05bbca16d58ff5a790d21e239a8.

REV0970 RELEASE CUTPOINT
    AnonSync-rev0970-2026.08.01.21.06-metadatamode-payloadcold-cutpointscope-fluorite.zip
    fluorite
    Exact rev0970 source passed the complete GCC 14.2 Debug graph (527/527 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 296 SQLite-owner, 406 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 123 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 260/260 checks. A clean-root Clang 17 Debug product dependency graph completed 238/238 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 406-check folder-owner suite in 18.02 seconds at 1,370,916 KiB peak RSS and the 123-check local-control suite. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0969 parent SHA-256 matched f06573e09238174517eb8cef22fd5df19276665665edcba71cb151527daa1d6b and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 14/14 changed active files and the complete 568-file projection byte-for-byte and by mode. The final active implementation projection contains 568 files / 26,027,982 bytes with SHA-256 4c1be1a1ff28901e0a9d769316dc258a7eceb2ce99794b332c07bf638e380fb8.

REV0969 RELEASE CUTPOINT
    AnonSync-rev0969-2026.08.01.20.11-exactcurrent-stalefence-oraclehygiene-jadeite.zip
    jadeite
    Exact rev0969 source passed the complete GCC 14.2 Debug graph (527/527 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 296 SQLite-owner, 397 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 119 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 247/247 checks. A clean-root Clang 17 Debug product dependency graph completed 238/238 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 397-check folder-owner suite in 22.24 seconds at 1,348,040 KiB peak RSS and the 119-check local-control suite. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0968 parent SHA-256 matched 3edbc700faa3f736321ae8f41aade11e2198985f3a1a0552b1a237e72d9d916f and passed 41/41 wrapper-aware package checks. The final active implementation projection contains 568 files / 25,986,608 bytes with SHA-256 0d8b28b316b616dcd091fe374eff3468b36dfacc52749a39f7e14cb0c9851174.

REV0968 RELEASE CUTPOINT
    AnonSync-rev0968-2026.08.01.18.25-sourcecutpoint-causalbracket-transientoracle-beryl.zip
    beryl
    Exact rev0968 source passed the complete GCC 14.2 Debug graph (527/527 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 296 SQLite-owner, 393 folder-owner, 7 folder-process, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 115 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 237/237 checks. A clean-root Clang 17 Debug product dependency graph completed 238/238 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error, including the focused 393-check folder-owner suite in 28.51 seconds at 1,342,052 KiB peak RSS and the 115-check local-control suite. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic.

REV0967 RELEASE CUTPOINT
    AnonSync-rev0967-2026.08.01.16.39-pagedversions-groupedprojection-cursorproof-alexandrite.zip
    alexandrite
    Exact rev0967 source passed the complete GCC 14.2 Debug graph (527/527 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 296 SQLite-owner, 386 folder-owner, 7 folder-process, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 113 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 227/227 checks. A fresh Clang 17 Debug product dependency graph completed 238/238 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error, including the 386-check folder-owner suite in 18.72 seconds at 1,347,424 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic.

REV0966 RELEASE CUTPOINT
    AnonSync-rev0966-2026.08.01.14.33-causalversions-rootedrestore-boundedinventory-morganite.zip
    morganite
    Exact rev0966 source passed the complete GCC 14.2 Debug graph (527/527 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 92 network-model plus 41 generated-operation, 296 SQLite-owner, 379 folder-owner, 7 folder-process, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 107 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 219/219 checks. A fresh Clang 17 Debug product dependency graph completed 238/238 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error, including the 379-check folder-owner suite in 18.10 seconds at 1,338,192 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic.


## `/run`

The recurring instruction is:

```text
Good. Thank you. Continue. Please `/run`: BOOTSTRAPROSE.md as you see fit.
```

Interpret that as permission to continue useful product work, not to manufacture
ceremony. A good run does at least one of these:

- adds a user- or operator-visible Resilio-replacement capability;
- completes a vertical slice through the retained C++ service;
- removes a correctness, security, performance, or lifecycle defect;
- consolidates duplicate product ownership;
- falsifies an inflated claim and records the real boundary;
- strengthens an executable test for the first uninstall target;
- surfaces an owner decision while continuing reversible work.

Do not create another visible document family. Do not fork another daemon or
sync engine. Do not expose an internal scheduler knob merely because it exists.
Do not grow a taxonomy when a direct C++ state, test, or operator message will
do. Old cube material is donor code, history, warnings, tests, and ideas. It is
hidden, not dead, and it is never mission authority.

Use this archive family:

```text
Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip
```

For this project use `AnonSync-...`. A completed turn returns only one link, and
the link text is the complete filename.


## Product acceptance target

AnonSync replaces Resilio only when the owner's normal workflow works without
special pleading. At minimum:

1. A person can create or join a share without hand-building databases.
2. Peers retain stable identities and explicit authorization.
3. Either peer may dial or accept; those are session roles, not device classes.
4. Local changes are noticed promptly and full scans repair missed events.
5. Create, edit, rename, delete, recreation, conflict, restart, and outage have
   understandable outcomes.
6. Large files resume, and changed large files avoid needless retransmission
   when the named workflow requires it.
7. Direct, Tor, and I2P use the same sync semantics with no hidden fallback.
8. Start, stop, status, diagnostics, upgrade, recovery, and removal are usable.
9. Storage, CPU, memory, bandwidth, partials, and retained history stay bounded.
10. Supported filesystems preserve the promised names, bytes, metadata,
    conflict behavior, and failure behavior.

Internal proofs count only when they protect or accelerate one of these product
obligations.


## Shipping C++ spine

The intended product spine is the newer replica path:

```text
anonsync_sync
    identity-create / share-create / share-join / run / status / stop /
    recheck / quarantine / quarantine-release / versions / restore
        ↓
retained linked-peer service
        ↓
folder watch + complete-scan repair
        ↓
SQLite operation/catalog owners + private payload store
        ↓
share-global reconciliation over authenticated TLS
        ↓
direct connector | Tor SOCKS connector | I2P SAM connector
        ↓
fenced filesystem publication beneath the configured root
```

`anonsync_replica` and `anonsync_folder` remain low-level, diagnostic, and test
surfaces. They must not become competing daemons. The older `sync_domain` body
is donor/oracle material until a useful part is migrated or retired; it cannot
define another mission.

One service configuration currently binds one local share, one peer, TLS
material, durable stores, a local root, outbound route, inbound publication
mode, budgets, and an owner-only status socket. A broad Resilio replacement
needs one device owner supervising many shares and peers. That consolidation is
not finished.


## Product state

### What works now

**Continuous symmetric two-peer operation**

- Two retained processes can publish and receive in both directions.
- Folder events wake the service; periodic complete scans repair missed wakes.
- Restart, peer outage, reconnect, and bounded catch-up are exercised.
- Nested parent directories are created beneath the retained root without
  escaping through symlinks.
- One process may be dialer or listener on different turns; peers are not fixed
  source/receiver classes.

**Direct, Tor, and I2P composition**

- Direct TCP, Tor SOCKS, and I2P SAM outbound routes use one service owner.
- Native I2P ingress owns SAM session creation and stream acceptance.
- Router outage degrades readiness and reconnects without changing route class.
- An I2P/Tor-locked service does not accept a hidden direct fallback.
- Live public-overlay scale and privacy qualification are still missing.

**Setup, trust, and lifecycle**

- Owner-only identity, first-share, signed pairing-card, pinned join, and linked
  service configuration paths exist.
- Pair cards bind the full fingerprint rather than trusting a friendly label.
- Existing populated folders can be adopted through explicit semantics rather
  than timestamp winner selection.
- A systemd user-service template, native readiness notification, graceful
  stopping, staged install, and residue checks exist.
- The local Unix status/control socket is owner-only: status is read-only,
  while drain, current-byte payload recheck, and exact corrupt-payload
  quarantine are explicit local operations.

**Regular files, deletion, and resurrection**

- Regular-file creates and edits publish exact content-addressed payloads.
- A complete successful scan may publish a causal tombstone for a missing file.
- Failed or bounded scans cannot infer deletion.
- A remote tombstone removes only the exact superseded cataloged file.
- A racing replacement or edit survives stale deletion work.
- Restart-stable absence and same-path recreation are covered by real peer
  processes.
- Internal publication residues are reserved and never become user files.

**Streaming and restartable transfer**

- Local admission and final materialization stream through descriptors rather
  than retaining a complete file in a C++ string.
- The ordinary share default is 64 MiB per file; committed manifests may select
  up to 4 GiB. That is an admission ceiling, not a scale qualification.
- Wire reconciliation uses bounded pages and 4 MiB ranges with durable prefix
  continuation and exact final size/digest proof.
- A 64 MiB plus 4 KiB file crossed the old allocation boundary at roughly
  14 MiB peak process RSS in the focused proof.
- Fixed-block and predecessor-reuse correctness slices exist, but production
  changed-block behavior is not yet a promise. One-byte edits may still move a
  complete file through sequential ranges.


### What does not work well enough yet

The first credible uninstall is blocked by some combination of:

- no named target workflow with real path count, bytes, largest file, churn,
  route, and acceptable catch-up time;
- complete private payload-namespace traversal at each cold snapshot or new
  mutation segment;
- fair scan segments still restart at the root and re-enumerate/`lstat` their
  skipped prefix, so semantic liveness is not yet huge-tree efficiency;
- the independent namespace-work ceiling still counts directories, symbolic
  links, special files, and internal artifacts, although only regular files
  spend the 100,000-file durable capacity;
- the resumable scan now retains at most one 4,096-name selected batch across
  the traversal, but descriptors and pending component/path records remain
  depth-indexed, while parent rescans and every skipped path prefix still repeat
  enumeration and metadata classification;
- a durable exact-observation checkpoint, byte-bounded rotating scrub, and
  owner-triggered whole-payload-store current-byte recheck now exist, but there
  is no live progress/coverage-age SLO, quarantine/restore workflow, or broader
  payload/catalog/remote-work change-sequence index;
- no payload, partial, tombstone, or superseded-version reachability/GC owner;
- incomplete identity-preserving rename, empty-directory, and metadata rules;
- conflicts and deleted versions are not ordinary-user recovery UX;
- no qualified multi-gigabyte interruption, ENOSPC/quota, and restart matrix;
- no long soak or large-tree qualification;
- no public Tor/I2P throughput, outage, DNS/address-leak, or traffic-shape study;
- one service per linked share/peer rather than one device daemon managing many;
- no macOS, Windows, mobile, NAS, tray, or graphical product surface.

Passing the existing proof corpus does not fill any item on this list.



## Rev0955: bounded rotating scrub and revocable snapshot authority

Rev0954 made exact unchanged metadata restart-reusable but deliberately did not
claim that unchanged metadata could reveal latent byte corruption. Rev0955 adds
one optional rotating complete-byte scrub after an ordinary authoritative
snapshot has released its shared lease. Each eligible attempt is bounded by both
bytes and distinct payloads; production defaults are 4 MiB and four entries.
A checksum-framed store-identity-bound journal retains a fair cyclic cursor and,
when a payload spans attempts, a canonical resumable SHA-256 checkpoint. The
continuation is scheduling evidence only: it is not a simultaneous byte image,
and a mismatch is re-proved by the complete leased scanner before it becomes
current corruption authority.

The SHA-256 continuation implementation is provider-independent, rejects
noncanonical or overflowing checkpoints, covers padding boundaries and the NIST
vectors, and is compared with OpenSSL as an independent oracle. The scrub record
uses the same centralized eleven-field POSIX regular-file snapshot codec as the
restart verification index, eliminating a second binary metadata grammar from
the payload-store owner. Torn tails reuse only their valid prefix; malformed,
overgrown, stale, or identity-rebound state is discarded and rebuilt under the
normal rooted authority.

A severe first-implementation liveness defect was corrected before sealing. In a
one-payload namespace, starting the next cycle retained that payload as both the
completed cursor and active target, so canonical validation rejected every new
checkpoint and each fresh owner could reread the same prefix forever. Cycle
entry now clears the old cursor before selecting the first target, and restart
regressions prove bounded progress, exact completion, wrap, and next-cycle work.

The durable failure journal is best effort, not sole authority. Rev0955 therefore
retains expected and observed digests in the shared owner-local verification
cache after a mismatch. An exception-safety audit replaced the first
heap-owning string representation with two fixed inline 64-character arrays and
a compile-time nonthrowing retention path. A deeper pass moved that retention
inside the scrubber's fixed-width digest comparison, before durable-state string
assignment, failure-record serialization, or typed exception construction;
integrity-epoch advancement can no longer outrun publication of the exact
blocking observation under memory pressure. Complete snapshots and mutation
preflights must hash the
faulted digest, pass-scoped targeted access rejects it, and restart-checkpoint
publication is suppressed until a final leased complete scan proves current
good bytes or absence. The oldest unresolved target is preserved when another
mismatch is encountered, so repairing a later observation cannot silently
restore the first payload's warm metadata authority.

Each newly retained mismatch also advances a non-wrapping integrity epoch. Every
writable snapshot captures that epoch when issued; its centralized state gate
rejects all later metadata and rooted methods when an active fault exists or the
epoch changed. Repair can issue replacement authority but cannot resurrect a
snapshot that was live when contradictory bytes were observed. A descriptor
already moved out before the alarm remains an explicit non-revocable boundary,
and independent processes retain independent caches.

The epoch exposed an adjacent concurrency defect during audit. Snapshot metadata
getters previously needed no cache access, but now read an intentionally
mutex-free owner-local epoch. The centralized snapshot gate and pass-scoped
targeted-access gate now perform the rooted authority's cheap process/thread
ownership proof before touching that state. Foreign-thread use is rejected
without adding a mutex or filesystem reproof to ordinary getters.

A separate lifecycle audit corrected readiness authority. The authenticated peer
listener can become visible before the local owner-only status socket is fully
published; provisioning had treated listener readiness as permission to issue a
drain. Its first repair then carried a startup socket observation across a
bounded convergence wait inside a nearly equal service lifetime. The process
harness now proves both startup endpoints, retains a bounded 60-second service
horizon, and re-proves the exact live non-symlink mode-0600 source control socket
immediately after convergence at the drain cutpoint. Listener availability and
control-plane availability are no longer conflated, and readiness observations
are not treated as durable authority.

This is still not retention, quarantine, restore, garbage collection, a
coverage-age service-level objective, hostile same-UID writer defense, a
point-in-time whole-store byte snapshot, changed-block transfer, or the named
Resilio uninstall workload. The complete scanner remains the descriptor-rooted
rebuild oracle, and ordinary snapshots remain O(total indexed namespace) in
metadata work.

## Rev0954: durable payload verification checkpoint and scrub boundary

Every fresh process previously re-opened and SHA-256-hashed every retained
payload byte during its first complete private-store snapshot. Near the 64 GiB
indexed-byte default, an ordinary restart could therefore cause tens of
gigabytes of read I/O even when the immutable payload set had not changed.
Rev0954 adds one narrow fixed-width verification checkpoint named
`.anonsync-payload-verification-index-v1`.

The checkpoint binds the exact store-identity digest and marker metadata, total
indexed bytes, and a sorted record for each digest-named payload. Each record
contains the canonical device, inode, mode, link count, owner, group, size,
mtime, and ctime observation, including nanoseconds. The complete scanner still
opens the retained root, holds the normal shared identity-marker lease,
enumerates every namespace object, rooted-opens and stats each payload, enforces
entry and byte capacity, and re-proves marker/root/directory/pathname authority.
Only an exact unchanged checkpoint observation may avoid reading payload bytes.
Missing, stale, malformed, over-capacity, identity-mismatched, or changed records
are fully streamed through SHA-256. `ReadOnlyInspect` deliberately ignores both
process and durable acceleration and hashes every payload on every forensic run.

The v1 parser is a separate linked leaf. It proves exact fixed-width length
before reserve, overflow-safe entry and byte ceilings, supported generation,
sorted unique lowercase digests, private metadata geometry, aggregate bytes, and
a final SHA-256 checksum over all preceding bytes. The checksum detects torn or
accidentally corrupted records; it is not a MAC and does not turn same-UID or
privileged interference into a hostile-host security claim.

Checkpoint publication is best-effort and non-authoritative. A shared complete
scan returns its proved snapshot before trying a fresh fail-fast exclusive lease
and another complete metadata reproof. Mutation batches and successful receiver
publication may record an exact post-publication set while already holding the
writer authority. Temp residues are recognized and repaired under the existing
staging owner. Exact transient capacity includes checkpoint geometry, and clean
same-process cache misses repair the durable checkpoint for the next process.
Cheap thread/owner gates now precede every mutex-free cache or scheduler read.

A namespace audit found that the first integration taught the full scanner about
the new reserved file but left the staged-prefix range observer rejecting it as
unexpected. Both descriptor-rooted loops now recognize and finally re-prove the
same checkpoint entry without making range work read unrelated payload bytes.
Shipping diagnostics partition process-local reuse from durable restart reuse.

Reconstruction over the exact sealed rev0953 source exposed an older branch that
had silently dropped the terminal equality check between a pass's published
remote fairness cursor and the final durable `sync-once` cursor. Rev0954 restores
the parent predicate, contract, structural guard, and compiled scheduling-only
movement regression. A source-fresh build also exposed a mutation-batch
constructor mismatch hidden by stale Ninja objects, and Clang ASan/UBSan exposed
the new instrumented leaf test missing from the explicit sanitizer final-link
inventory. The final graph and audit bind both compile and link closure.

The release audit rejected a late one-payload-per-pass scrub experiment. One
entry is not a meaningful I/O bound when a payload may be multi-gigabyte, and a
process-local cursor can repeat the same prefix after every restart. Rev0954
ships no such knob or integrity claim. This checkpoint is restart acceleration,
not permanent corruption detection. A future scrub must combine byte and entry
budgets, a durable continuation/epoch, and explicit quarantine or failure
semantics.

The exact source completed a fresh 515-step GCC 14.2 graph. All 255 registered
tests passed across deterministic 60/60, 60/60, 60/60, 60/60, and 15/15 shards;
the product lane passed 36/36 in 51.88 seconds. Focused checks passed 92 network-
model plus 41 generated operations, 30 POSIX resolution, 21 verification-index,
213 payload-store, 296 SQLite-owner, 347 folder-owner, and 110 sync-once
assertions; the structural audit passed 87/87. A fresh 226-step Clang 17
ASan/UBSan product graph started from an empty directory, was externally
interrupted after step 190, and resumed in that same untouched directory to
completion. All 36 sanitizer product tests passed serially with leak detection
in 132.44 seconds, and the same focused suites passed without a diagnostic.

History remains append-only. This revision does not add retention, restore,
reachability pins, quarantine, garbage collection, block-level changed-file
reuse, complete change-sequence indexing, rename and metadata UX, selective
sync, one-device many-share ownership, cross-platform qualification, or the
first named Resilio uninstall workload.

## Rev0953: targeted payload access and terminal cross-owner settlement

Rev0952 bounded descriptor-rooted remote inspection but remote-only file work
still forced a complete private payload snapshot. One desired digest could
therefore enumerate every retained payload and hash every restart-cold or changed
object. Rev0953 replaces that path with one pass-scoped exact-name capability.
Identity reconciliation and root setup happen once; every probe and selection
still obtains a fresh fail-fast shared lease, requires the exact identity-marker
observation, re-proves rooted mount/name authority, and opens only the admitted
lowercase SHA-256 basename.

Missing payloads remain unresolved scheduling work and do not block a ready
suffix. A selected descriptor stays open through the existing atomic publisher,
which streams and hashes the bytes before visible filesystem or catalog state
advances. Targeted access is explicitly not complete namespace health or capacity
authority. An invalid unrelated entry may coexist with a valid selected digest;
targeted apply can consume the digest, while a complete snapshot must still
reject the namespace. Same-size selected corruption fails at publication with no
visible/catalog effect.

The initial exact-name implementation repeated identity reconciliation and root
selection for every operation. The final move-only pass capability amortizes that
work without retaining a store lease across planning or destination I/O. Required
and optional POSIX regular-file component opens now share one implementation;
only `ENOENT` becomes optional absence. Symlinks, non-regular objects, unsafe
components, mount crossings, permission failures, and inode races remain errors.
Pass and process telemetry distinguish targeted access births, probes,
selections, and selected operation bytes from complete snapshots and deferrals.

A separate settlement audit found that a completed sweep needed a real final
replica observation. Rev0953 acquires a complete visible-projection guard under
replica `BEGIN IMMEDIATE`, then—while that writer guard remains live—uses a short
catalog `BEGIN IMMEDIATE` transaction to compare the exact catalog, authenticated
local-scan journal, and prior remote-work head before scheduling progress is
published. Any movement reports `authority_cutpoint_changed` and withholds
settlement. Ordinary and speculative-idle completion use the same helper.

The final audit closed a scheduling-only classification gap. Another process can
move the durable remote fairness cursor after the pass returns without changing
catalog content or the replica-visible digest. The centralized `sync-once`
settlement predicate now requires that final cursor to equal the cursor published
by the pass, as well as requiring exact terminal catalog/visible digests, complete
local and remote sweeps, no deferred/unresolved work, end-of-projection, and
inactive continuation journals.

The exact active source passed a fresh 511-step GCC 14.2 graph, one uninterrupted
254/254 registry run, and the 35/35 product lane. Focused checks passed 92
network-model plus 41 generated operations, 30 POSIX resolution, 164 payload-
store, 296 SQLite-owner, 347 folder-owner, and 110 sync-once assertions; the
structural audit passed 75/75. A fresh 222-step Clang 17 ASan/UBSan product graph,
all 35 product tests with leak detection, and the same focused suites passed with
no sanitizer diagnostic.

This removes one pathological complete scan and strengthens exact completion; it
is not an incremental index or cross-database/filesystem transaction. Remote
projection restoration remains complete, large remote sets still perform one
exact-name lookup per candidate, local/snapshot payload work remains restart-cold,
history is append-only, changed files transfer whole payloads, and rotating scrub,
retention/restore/garbage collection, multi-process fault qualification, and the
first named uninstall workload remain open.

## Rev0952: bounded remote inspection sweep and grouped visible projection

Rev0951's cyclic cursor prevented an eligible suffix from being monopolized by
a changing prefix, but the post-scan owner still rooted-opened every admitted
remote pathname in one pass. The operation frontier bounded effects only. A
large no-op or deferred projection could therefore consume an unbounded rooted
inspection turn and repeat without a durable proof that one stable projection
had been covered.

Rev0952 adds an independent 4,096-path default inspection frontier and catalog
schema v5. Its remote-work singleton now carries a sweep basis digest, start
cursor, acknowledged path count, and cumulative unresolved flag alongside the
last acknowledged fairness cursor. The basis binds the exact catalog digest and
replica visible-state digest. On the same basis, origin plus count must imply the
persisted cursor exactly; inconsistent durable state is rejected. A changed
basis starts a clean sweep at the retained fairness cursor.

Complete remote projection restoration and hard path/evidence/size admission
still precede all rooted effects. The bounded walk then visits only the remaining
cyclic suffix. Safe no-ops, conflicts, missing payloads, and unadjudicated local
absence are explicitly acknowledged for coverage, while unresolved state remains
sticky for that sweep. Selected applies publish before cursor/sweep progress; any
selected effect invalidates an incomplete pre-effect sweep. A clean complete
sweep is discarded and may support settlement only in the reporting pass.

The one-shot cutpoint and process/status JSON include the sweep state. The final
settlement classifier now requires a complete local scan epoch, a complete remote
inspection sweep, no unresolved sweep result, no deferred payload/apply/absence
work, and `end_of_projection`. The speculative idle path cannot bypass an active
partial sweep and runs only when the whole remote projection fits the inspection
budget.

The audit/refactor for this revision removed another scale trap. Bulk visible
projection previously gathered distinct paths, then rescanned all active
operations once per path through `visible_path()`. It now groups borrowed,
model-owned operations once by borrowed canonical path and shares one path-view
materializer with the single-path API. This removes repeated active-set scans and
path copies while preserving canonical order, maximal-operation conflict
semantics, primary selection, and preserved-file identities.

### Honest rev0952 boundary

The sweep bounds rooted inspection, not complete projection reconstruction or
hard admission. `visible_paths()` still allocates one candidate vector per path,
and maximality remains pairwise among operations sharing that path. The sweep
basis is catalog plus remote visible state, not a point-in-time filesystem
snapshot. A mutation behind either the local scan or remote inspection cursor is
ordinary next-epoch work. Cross-owner catalog, replica, payload, scan, cursor,
and filesystem cutpoints remain sequential. Root-prefix replay, whole-directory
name sorting, restart-cold payload inventory, append-only history, rename and
metadata semantics, recovery UX, many-share ownership, and target-workload
qualification remain open.

Exact-source GCC evidence covers all 254 registered tests as 253 aggregate
passes plus isolated inherited test 60 with 611/611 internal checks. The 35/35
product lane passed. Focused counts are 92 network-model, 321 folder-owner, 99
sync-once, and 164 payload-store checks; the structural audit is 74/74. Clang 17
ASan/UBSan rebuilt the 20 affected product steps and all 35 product tests passed
in isolated leak-detecting invocations without a sanitizer diagnostic.

## Rev0951: cyclic remote fairness and scan-independent predecessor reproof

Rev0950 made a stable remote prefix progressive, but a frequently changing early
path could still spend every bounded turn. Rev0951 persists the last selected
canonical path in exact catalog schema v4 and routes every remote file/tombstone
effect through one cyclic planner. Complete hard projection admission remains
non-cyclic and precedes effects. The planner starts strictly after the cursor,
wraps once, applies one count/byte-bounded segment, and publishes scheduling
progress only after selected rooted owners complete.

The first implementation still tied present-file eligibility to the current
local scan segment. That was safe but could strand a valid remote successor after
a completed scan epoch reset its journal and a restart began again at the root.
The final design does not use scan-journal rows as remote authority. A durable
catalog predecessor may nominate work after a fresh rooted descriptor observation
reproduces its source-snapshot digest. The exact apply owner then reopens and
fully hashes the file, reloads its predecessor, and re-proves causal supersession
immediately before effect. Metadata is a scheduling filter; a local edit or race
fails closed.

Remote file application also shares one frozen verified payload inventory per
pass instead of taking a complete payload-store snapshot for each file. If local
publication added bytes, the inventory is refreshed once. An authenticated file
operation whose payload has not arrived is deferred and does not block a ready
cyclic suffix. The snapshot cannot authorize bytes: the selected digest-named
payload and rooted publication are still exactly re-proved.

Diagnostics expose payload snapshot count/entries, missing-payload remainder,
catalog-predecessor metadata reproofs, and cursor movement. `sync-once` remains
unsettled while payload candidates are missing. The idle proof now reloads the
authenticated scan journal in addition to every other mutable cutpoint.

### Honest rev0951 boundary

The cursor and catalog predecessor rule remove two starvation windows; they do
not create an incremental index. Each pass still rebuilds the visible remote
projection, resumed local scans replay rooted prefixes and fully sort each
immediate directory, cold payload observations traverse the complete append-only
store, and cross-owner reads are not atomic. A same-metadata race is detected by
the final hash but may require another pass. Payloads arriving after the frozen
inventory may wait one pass. Retention/restore/GC, changed-block production
transfer, rename/directory metadata, selective sync, many-share ownership,
cross-platform behavior, and target-workload qualification remain open.

The exact final source passed the complete GCC 14.2 graph, all 254 GCC tests,
the 35/35 product lane, 292 focused folder-owner checks, 95 sync-once checks, the
70/70 structural audit, the fresh 222-step Clang 17 ASan/UBSan product graph, and
all 35 sanitizer product tests with leak detection and no diagnostic.

## Rev0950: bounded remote effect prefixes and settlement authority

The remote post-scan planner previously required all missing files to fit one
aggregate byte budget before applying any of them. A stable sorted set larger
than that budget failed at the same preflight forever. At the other extreme,
zero-byte files and tombstones could consume effect work proportional to the
full remote-path ceiling because bytes did not bound them.

Rev0950 continues to inspect the complete visible projection for hard path,
depth, per-file, operation-shape, and projection limits. It then chooses one
stable prefix under the remaining aggregate bytes and a fixed 4,096 remote
file/tombstone apply-call frontier. The first non-fitting candidate and all later
eligible candidates are deferred. Applied prefix values become exact no-ops on
the next pass, so a stable suffix advances without introducing a second remote
cursor. Candidate storage is reserved only to the remaining effect allowance.

A bounded prefix is useful progress, not settlement. The final folder pass must
complete its authenticated local scan epoch, leave no deferred remote or absence
work, and reach `end_of_projection` before `sync-once` reports settled. The
process cutpoint now includes the durable scan epoch, resume path, seen counts,
and chain digest, because a cursor/journal transition can survive a crash even
when catalog and replica content do not change.

A real two-peer proof drives three 42-byte files through a 42-byte pass frontier:
one file, then the remaining files while scan continuation remains, then a
scan-only settlement turn. A duplicate turn is still a no-op. Focused tests bind
byte and zero-byte/tombstone count progress, complete invalid-suffix preflight,
limit composition, and scan cutpoint behavior.

### Honest rev0950 boundary

Every remote pass still examines the complete visible projection, and there is
no persisted remote apply cursor or queue. Stable-prefix no-op behavior supplies
progress; sustained mutation of an early path can delay a suffix. Local scan
segments still replay their root prefix, immediate directories are still fully
buffered and sorted, watcher events remain acceleration only, history remains
append-only, and changed files remain whole-payload identities. The next scale
owner should be one crash-consistent metadata/subtree and remote-work index with
monotonic sequence, bounded queues, and rooted rebuild/scrub authority.

The exact source passed the complete GCC 14.2 graph, all 254 GCC tests, the
35/35 product lane, 260 focused folder-owner checks, 94 sync-once checks, the
65/65 structural audit, the complete 222-step Clang 17 ASan/UBSan product graph,
and 35/35 sanitizer product tests in seven completed serial shards with leak
detection and no diagnostic.

## Rev0948: count-bounded scan segments and lower idle path memory

Rev0947 made every admissible suffix path eventually reachable, but the local
segment stopped only at a file-byte frontier. Zero-byte or tiny-file trees could
therefore deliver every path admitted by the 100,000-entry hard ceiling, retain
all those acknowledgement strings, and publish them in one immediate scan-
progress transaction.

Rev0948 adds an independent delivered-regular-file frontier. Production uses an
internal default of 4,096 paths. Cursor-skipped paths still spend the whole-walk
entry budget but do not consume productive count or byte allowance. When the
count is full, the next eligible path is left for the following segment before
its visitor runs. A successful visitor remains the only operation that advances
the in-memory cursor.

The count stop is not a shortcut around namespace authority. It propagates
through the existing descriptor-rooted unwind, reopens every visited directory
by name, compares directory identity, and verifies the retained root before the
segment result returns. The folder owner stages a path only after its idempotent
effect commits, then publishes the bounded path set and progress head once. A
crash before that publication safely replays effects; a directory substitution
at the frontier throws before any cursor can be accepted.

A compiled restart proof converges five zero-byte files in `2 + 2 + 1` segments.
The first segment traces exactly two journal INSERTs and one progress UPDATE.
Reconstructing the owner between segments proves that continuation is durable.
The old observer overload remains compatible and byte-only; the shipping owner
explicitly selects the new scheduling contract. A zero count fails before any
catalog mutation.

The idle fast path previously allocated and sorted two additional whole-tree
path vectors solely to prove set equality. Rev0948 instead requires each
observed path to map to one unique catalog `File`, completes the traversal, and
compares observed-file and catalog-file cardinality. Tombstone paths remain
explicitly inspected. This removes duplicate O(files) path storage and sorting
without granting the fast path any new mutation authority.

### Honest rev0948 boundary

The 4,096 default bounds delivered callbacks, the in-memory seen-path batch, and
one journal publication. Rev0964 additionally bounded each selected immediate-
directory component batch to 4,096, and rev0965 prevents those selected-name
batches from multiplying across recursive depth. It still does not bound every
scan cost: descriptors and pending component/path records remain depth-indexed,
later batches and released-parent continuation rescan directories, each resumed
segment re-enumerates and `lstat`s the root prefix, the non-resumable observer
retains a complete immediate-directory vector, the whole-walk entry ceiling
includes ignored objects, and path-local durable attestation can remain
expensive. The epoch is
still an asynchronous sweep rather than snapshot isolation. No latency,
process-wide constant-memory, writer-horizon, or huge-tree performance claim is
made from the default alone.

The exact source passed all configured GCC 14.2 Debug targets, 254/254 registered GCC tests, the 35/35 GCC product lane, 64/64 observer checks, 232 folder-owner checks, the 55/55 structural audit, the complete Clang 17 ASan/UBSan product target, and 35/35 sanitizer product tests in five fresh bounded CTest shards with leak detection and no diagnostic. SQLite's current WAL
implementation supports large transactions; the new bound is application
backpressure and scheduling, not a workaround for an obsolete SQLite limit.

## Rev0947: durable fair scan epochs and absence fences

### Prefix starvation corrected

The local repair owner previously began every pass at the retained root. It
visited directory entries in deterministic component-wise order and charged all
classified regular-file bytes against one aggregate frontier. A stable prefix
large enough to consume that frontier could be replayed forever. Suffix files
would never receive path effects, and deletion authority would never become
available because no pass completed.

The descriptor-rooted observer now has a resumable counterpart. It classifies
but does not redeliver paths at or before a persisted cursor, stops cleanly
before the next over-budget eligible file, and returns only after all opened
directory identities and the retained root have been re-proved. At least one
eligible file must fit an empty segment. The cursor follows the actual recursive
walk order; a flat path comparison is wrong for cases such as `a/two.bin`
preceding sibling `a.txt`.

### Durable epoch and exact deletion authority

Catalog schema v3 owns one scan-progress row and an ordered seen-path table. The
head records epoch, cursor, seen count, cumulative path bytes, and a
domain-separated SHA-256 chain tail. Each path joins the segment journal only
after its idempotent path effect commits. Exact v1 and v2 catalog cutpoints
migrate transactionally; near-match schemas still fail closed.

A complete traversal is necessary but not sufficient for deletion. Before
absence inference the owner reloads every seen row, checks ordinal and traversal
order, recomputes every chain link, and binds count, path bytes, cursor, and tail.
A cataloged path omitted from the journal is then observed again: physical
absence may become a tombstone, while physical presence behind the cursor
restarts the epoch.

The scan is an asynchronous sweep, not a point-in-time snapshot. Changes to an
already-seen path are handled by a later epoch. A new uncataloged path behind the
cursor is likewise found later; because it has no predecessor, that delay cannot
create false deletion authority.

### Audit race corrected

The first epoch implementation still had one severe restoration race. A file
visited in an early segment could be deleted before the suffix completed. It
remained in the journal, so completion did not infer absence; generic remote
planning could then restore the exact old catalog predecessor immediately.

Rev0947 now defers that exact predecessor whenever the local path is absent and
the absence has not been independently adjudicated. A genuinely distinct remote
successor still follows the existing conflict/apply policy. Remote tombstones
also do not generically erase a present local regular file outside current-epoch
authority. The next complete epoch either sees recreation or publishes deletion.

### Journal refactor

The discarded prototype opened one immediate SQLite transaction per visited
file. The retained implementation commits path effects independently, stages the
segment's paths in memory, and publishes the complete segment with one prepared
INSERT loop and one compare-and-swap progress-head update. If journal publication
fails, synchronized path effects replay safely; the durable cursor never outruns
the traversal's final rooted identity reproof.

Rev0948 adds an explicit delivered-path frontier at this same reproof
boundary. It therefore bounds the staged journal rows without publishing a
cursor before directory/root identity has been checked.

### Honest rev0947 boundary

Fairness removes permanent suffix starvation and repeated payload/path effects.
It does not avoid metadata work on the skipped prefix: each resumed segment still
enumerates and `lstat`s from the root. The namespace-entry ceiling also counts
directories and ignored objects, not just cataloged regular files. Startup binds
the progress head and edge geometry; the complete middle hash chain is checked
before deletion authority, not rehashed on every process start.

The exact source passed the complete 254-test GCC registry, 49 observer checks,
225 folder-owner checks, the real process continuation/restart proof, the
51-check source audit, and 35/35 Clang ASan/UBSan product tests with leak
detection. These are cloudtainer proofs, not qualification for an unnamed huge
Resilio tree.


## Rev0946: truthful durable capacity and the next scale frontier

### Capacity drift corrected

The shipping folder catalog and convergence pass default to 100,000 current
paths, but the production payload-store helper changed only its byte ceilings
and inherited the generic 4,096-entry default. Because the payload namespace is
append-only and has no collector, a tree accepted by the folder contract could
become unable to publish its 4,097th distinct digest. Service configuration also
accepted path ceilings that the independently constructed durable owners could
not retain.

Production payload composition now explicitly owns 100,000 entries. The
content-inventory hard ceiling is aligned, default folder/catalog/pass values
are compile-time checked, each pass validates its local and remote path limits
against the actual catalog and payload-store capacities before mutation, and the
real linked-service `check-config` path rejects values above production
capacity. Focused runtime tests prove invalid composition leaves the catalog
unchanged.

Raising the capacity ceiling must not become routine allocation waste. Payload
namespace scans therefore reserve at most 4,096 index entries initially and grow
only as payloads are observed.

### What this does not solve

The payload store remains append-only. A full 100,000-file tree with distinct
current content has no guaranteed room for even one superseding digest. Rev0946
removes the hidden 4,096-entry contradiction; it does not provide retention,
recovery history, or garbage collection.

A deeper scan audit found a release-blocking fairness defect. Directory names
are visited in deterministic bytewise depth-first order; every regular file is
charged against one aggregate pass budget before its callback; and every pass
starts at the root. If a stable prefix fills the budget, later paths may never
be visited. Since deletion authority requires completion of the whole walk,
absence repair can also stall indefinitely. The durable correction needs a scan
epoch plus continuation cursor and may infer deletion only after the cursor
wraps. Merely increasing the default budget would hide the semantics problem.

### Mission and research conclusion

External comparison reinforces the product order. Mature synchronizers retain
incremental indexes, combine watchers with full-scan repair, transfer verified
blocks rather than whole changed files, preserve conflicts, and offer bounded
version recovery. Resilio's own ordinary product surface also includes
selective sync, permissions, encrypted storage roles, Archive restore, and
cross-platform lifecycle. AnonSync's rooted filesystem and fail-closed overlay
work are strong foundations, but they are not substitutes for those daily-use
features.

The exact findings, code seams, repository metrics, and recommended sequence are
in `REVISION_EVIDENCE/rev0946/AUDIT.md` and `RESEARCH.md`.


## Rev0945: lineage repair, warm batches, and shorter exclusion

### Why this revision had to start with an audit

Two unfinished directories both claimed to be the rev0945 continuation, and old
build directories were named as if they belonged to one source while
`CMAKE_HOME_DIRECTORY` pointed at another. Prior status text accidentally mixed
features and test claims from both branches. Directory names were not evidence.

The branches were reconciled by file-level source diff against the retained
rev0944 baseline. The rejected branch spread payload-batch tuning through CLI,
linked-service configuration, provisioning, and setup. That would have made an
internal scheduling choice part of the product contract before target-scale
measurement. The retained branch instead keeps those limits inside the folder
owner and preserves the stronger performance/correctness work:

- exact verified-index promotion when a successful mutation batch is released;
- a move-only batch that safely owns what it needs even if its creator store
  handle is destroyed first;
- retained payload-cutpoint reuse so unchanged and content-addressed duplicate
  paths do not enter mutation authority;
- exact work accounting and bounded internal batch segmentation;
- focused tests and source audit bound to the same source tree.

Every build used for this revision is checked by its configured source path, not
by its directory name.

The same audit then caught a smaller but important truth failure inside the
canonical branch: this bootstrap and the draft audit said likely same-size
catalog no-ops released an unrelated mutation batch before hashing, while the
C++ owner had not yet implemented that transition. The release was stopped,
the owner and runtime expectations were corrected together, and the complete
exact-source gates were rerun. Prose is not evidence that code exists.


### Warm verified-index publication

A mutation batch begins with one complete leased scan of the private payload
namespace. Successful durable create-new puts update that exact in-memory index.
On non-poisoned teardown, the batch re-proves its retained root and lease, then
publishes the complete index into a shared process-local verification cache.

The cache is acceleration only:

- publication failure cannot change a durable put result;
- a cold process still hashes complete payload bytes;
- any identity-marker or payload metadata change falls back to complete hashing;
- forensic read-only and exceptional-recovery scans do not borrow warm proof;
- the batch may outlive its creator because the cache owner is shared rather
  than referenced by a raw pointer;
- the old cache vector is reclaimed only after the exclusive file lock is
  released, so metadata destruction does not extend the lock window.

The immediate retained snapshot after a successful batch can therefore reuse
all just-admitted payload verification instead of rereading every byte once more.


### Exact payload cutpoint and mutation isolation

A fallback folder pass may contain one changed path and thousands of unchanged
ones. Rev0944's broad batch would present each source to the mutation owner even
when the content already existed. Rev0945 keeps one exact append-only payload
snapshot from the idle attempt, or obtains one best-effort snapshot before the
fallback when the catalog is nonempty.

For each observed local file:

```text
exact digest already exists at the retained payload cutpoint
    → release any mutation batch
    → reopen and re-prove that retained payload
    → commit catalog/operation work without a put

exact digest is genuinely missing
    → obtain or reuse one bounded mutation batch
    → stream the retained source descriptor into create-new durable storage
    → update the exact live batch index
```

A new pathname reusing existing bytes can publish without opening an exclusive
payload-store batch. A one-file edit in a large tree performs one put rather than
presenting every no-op source to the batch.

The audit found another avoidable horizon: after a changed path, a live batch
could remain exclusive while the following unchanged file was opened and fully
hashed just to discover a no-op. The folder owner now uses the cataloged kind and
classified extent as a scheduling hint. A likely same-size catalog no-op releases
the unrelated batch before preparation. A same-size edit simply reacquires after
its exact content proof. New paths, tombstone resurrection, and size-changing
edits may still amortize a bounded segment.

This hint authorizes no sync result. Exact content, durable catalog state, and
fresh commit checks remain authoritative.


### Internal segmentation, not a new configuration bureaucracy

One mutation batch is segmented internally at these current implementation
frontiers:

```text
maximum puts in one segment       256
maximum measured exact work       256 MiB
```

Measured work includes bytes prepared while the exclusive batch was live and
bytes presented to put operations. A cold namespace scan is known only after the
lease is acquired, so one scan plus one selected file may exceed the scheduling
frontier; no additional file is then admitted. One file larger than the frontier
is allowed alone because the deployment's per-file and whole-pass ceilings—not
this scheduler—decide admissibility.

These values are intentionally absent from the CLI, pairing card, linked-service
configuration, share setup, and provisioning formats. They are implementation
tuning, may change, and must be measured on the first uninstall workload before
becoming operator policy.

Folder and service JSON expose diagnostic totals for batch count, full scans,
puts, source bytes, exact work, peak puts/work, inserted payloads, and duplicates.
Those counters describe cost; they do not enter synchronization state.


### Honest rev0945 boundary

Rev0945 reduces repeated byte hashing and unnecessarily broad exclusive lease
ownership. It does **not** make the payload store incremental.

- Every new segment still walks, opens, and stats the complete private payload
  namespace before its first put.
- The warm verification cache is process-local and restart-cold.
- New local content is still read once to obtain a stable observation/digest and
  again for durable insertion.
- A hostile lock-ignoring process is outside the cooperative lease contract.
- There is no independent wall-clock lease deadline.
- Changed-file transfer, reachability, reclamation, and rotating bit-rot scrub
  remain missing.

The correct next scaling move is a crash-consistent exact metadata index plus a
bounded rotating complete-byte scrub, retaining the current complete scanner as
the cold oracle. The wrong next move is another parallel store, daemon, policy
plane, or user-facing tuning format.


## What the old cube contributed

The hidden history is large because many failure boundaries were explored. Keep
the useful product parts without letting their vocabulary become the mission:

- exact retained filesystem roots and descriptor-relative publication;
- crash-safe SQLite owners and restart classification;
- authenticated TLS peer identity and session bounds;
- Tor SOCKS and I2P SAM route owners;
- symmetric service turns and outage/rejoin behavior;
- share-global reconciliation instead of destination-queue dependence;
- signed pairing cards and exact fingerprint pinning;
- atomic delete displacement and conflict-preserving tombstones;
- prefix/range resume and payload-first metadata admission;
- source/build/package provenance checks that have caught real mistakes.

Keep the older whole-payload, complete scanner, and simple transfer paths as
oracles where useful. Do not ship two product spines merely to preserve history.


## How far from replacing Resilio Sync

Do not invent a percentage. Use product gates.

### Gate A — authenticated exact-file courier

**Reached for bounded regular files.** Exact content crosses authenticated
sessions and is published beneath a retained root over direct, Tor, or I2P route
adapters.

### Gate B — continuous symmetric two-Linux-peer bridge

**Substantially implemented, lightly qualified.** Retained services converge
create/edit/delete/recreate flows, restart, reconnect, wake repair,
status/drain/recheck,
signed-card setup, and interrupted range transfer. Qualification is still mostly
two peers, loopback, small trees, scripted routers, and short runs.

### Gate C — honest technical alpha

**Not reached.** The product needs target-scale payload indexing and scrubbing,
qualified large files and huge trees, bounded retention, useful conflict/delete
recovery, rename/directory semantics, identity lifecycle, live overlays, and
measured service stability.

### Gate D — first Resilio uninstall

**Not reached and not fully defined until the owner names the workflow.** The
likely boundary is:

```text
complete pairing/start experience
    + adequate initial and incremental transfer performance
    + required rename/directory/metadata semantics
    + understandable conflict/delete/history recovery
    + live required routes
    + target-host install/lifecycle proof
    + measured performance on the actual folder
```

A direct two-Linux-peer bridge is much closer than a broad replacement. It must
not be mislabeled as the uninstall target until the named workflow can move.

### Gate E — broad Resilio-class replacement

**Farther away.** Multi-share device ownership, discovery, selective sync,
encrypted helpers, cross-platform fidelity, polished UX, and sustained field use
belong here.

AnonSync has crossed from disconnected architecture into a real product spine.
The remaining distance is normal sync-product breadth, scale, recovery UX, route
qualification, and packaging—not another abstract proof system.


## Next C++ sequence

### 1. Name and measure the first uninstall workflow

Run the owner's real or representative folder through:

- cold initial sync;
- many-small-files publication and apply;
- one large-file interruption and resume;
- edit-in-place of large files;
- rename and delete/recreate churn;
- router outage/rejoin;
- daemon restart and host reboot;
- disk, memory, CPU, descriptors, bandwidth, and private-store growth.

Record operating systems, filesystem, path count, total bytes, largest file,
change shape, route, and acceptable catch-up time. These measurements decide
whether reusable blocks, rename/directories, many-share ownership, or recovery
UX is actually next.


### 2. Replace repeated root-prefix and payload metadata scans with exact durable indexes

The rooted local scanner and private payload scanner remain rebuild oracles. Add
crash-consistent metadata that tracks both namespace/subtree progress and exact
payload basename, size, inode/metadata identity, reachability class, and
verification/scrub state. Requirements:

```text
filesystem or payload publication and index update have recoverable ordering
    → restart can classify every interrupted frontier
    → resumed local repair avoids reclassifying the complete sorted prefix
    → mutation lookup is logarithmic or better
    → payload snapshots do not open every old payload
    → bounded rotating scrubs eventually read every retained byte
    → any drift falls back to a complete rooted scanner
```

Keep regular-file catalog capacity distinct from the all-entry traversal budget.
Do not turn cached metadata into authority to accept wrong bytes, and do not
remove the cold complete-store proof. Measure lock duration, WAL growth, prefix
amplification, and scanner rebuild on the first uninstall tree before adding
another scheduler surface.


### 3. Qualify large files and changed-file reuse

Prove the owner's required maximum, not an invented round number. Exercise
multi-gigabyte files, several interruption offsets, ENOSPC/quota, short writes,
final-byte corruption, daemon/host restart, sparse inputs, and bounded RSS.
Keep the 4 MiB range ceiling independent from whole-file size.

Only then promote reusable changed blocks into the shipping promise:

```text
verified source snapshot
    → bounded block/chunk manifest
    → receiver inventory of reusable verified content
    → bounded missing-content requests
    → durable reconstruction
    → complete size + digest proof
    → existing atomic publication
```

Fixed blocks are a useful oracle but reuse poorly after front insertion. Preserve
a seam for content-defined chunking if the measured workload needs it.


### 4. Rename, directories, metadata, and incompatible names

Define whether rename is an identity move or a conflict-safe delete/create pair.
Synchronize empty directories. Choose the first metadata subset explicitly; do
not accidentally promise every host permission bit. Report illegal or colliding
platform names instead of silently skipping or mangling them.


### 5. Recovery and bounded retention

Choose the delete/conflict restore contract. Add reachability, version windows,
partial-transfer expiry, payload/block reclamation, quotas, and interrupted-GC
recovery. Cleanup must never guess that a pathname still names the object it
examined.


### 6. Live Tor/I2P and product ownership

Exercise real Tor and I2P routers, restart them during transfers, verify
fail-closed behavior, measure reconnection and throughput, and inspect DNS,
address, identity, and traffic-shape leakage. Close the approval/activation flow,
then move from one-service-per-link toward one device owner for many shares and
peers.


## Odd product bets worth preserving

These are subordinate to ordinary sync, but they could make AnonSync a better
replacement rather than a smaller clone.

1. **Route parity with fail-closed overlays.** Direct, Tor, and I2P carry the
   same sync semantics; an overlay-locked link never silently becomes direct.
2. **Native I2P participation.** A peer can own an I2P SAM destination and
   inbound stream path rather than using I2P only as a generic SOCKS proxy.
3. **Symmetric peers.** Dialer/listener and source/requester are temporary
   session roles, not permanent device classes.
4. **No mandatory hosted account or central cloud.** Optional discovery or
   helpers must not become ownership of the user's share.
5. **Share-global catch-up.** A fresh peer reconstructs share state rather than
   depending on a stale destination queue.
6. **No silent timestamp conflict winner.** Concurrent candidates remain
   recoverable until an explicit or clearly declared rule resolves them.
7. **Conflict-preserving deletion.** Absence is a causal value; a racing edit is
   not erased by a stale pathname decision.
8. **Safe populated-folder adoption.** Existing differing trees become explicit
   adoption/conflict work, never timestamp-driven replacement.
9. **Managed incompatible paths.** A name illegal on one platform is reported
   and blocked there instead of silently skipped or mangled.
10. **Revocable pairing rather than immortal bearer secrets.** Invitations may
    become one-time, expiring, replaceable, and explicitly approved without a
    hosted control plane.
11. **Optional route/persona separation.** Unrelated peers need not learn that
    several direct/onion/I2P endpoints belong to one device.
12. **Encrypted untrusted helpers.** A later seed/relay may retain ciphertext
    without plaintext access.
13. **Selective disconnected materialization.** A peer may join a share but
    materialize selected paths without rewriting share history.
14. **Repairable bounded history.** Conflicts, old versions, tombstones, and
    interrupted transfers remain inspectable under an explicit retention limit.
15. **Clean removal.** AnonSync should uninstall without account dependency or
    hidden daemon residue, while leaving data/history choices explicit.

The first nine shape the near product. The later bets must not postpone scale,
rename, recovery, live overlays, packaging, or ordinary usability.


## Testing facility

### Is it fast enough?

**Yes for focused C++ work and the replacement-product lane. No for rebuilding
and running the entire inherited historical graph after every edit.**

Current source-bound observations for rev0948:

```text
GCC 14.2 Debug:
  all configured targets built from the exact source
  254/254 registered tests, 34.05 seconds real
  35/35 product tests, 16.83 seconds real
  observer 64/64; folder owner 232; structural audit 55/55

Clang 17 Debug with ASan/UBSan:
  product target completed from the exact source
  clean build reached 169/222 before the foreground ceiling
  retained build completed its 54-step resume
  35/35 product tests in five fresh bounded CTest shards
  89.72 cumulative real test seconds; leak detection; no diagnostic
```

The complete GCC graph and registry and the complete sanitizer product test
set passed on the exact final source. Long-lived serial sanitizer invocations in
this cloudtainer repeatedly stopped making progress only after earlier tests had
completed, while those same next tests passed in fresh invocations. A parallel
attempt also produced one load-sensitive replacement-SAM connection failure that
passed immediately in isolation. Final sanitizer evidence therefore comes only
from five fresh bounded serial shards covering product-label indices 1-19, 20,
21-28, 29, and 30-35. Every shard completed, every product test is represented
exactly once, and no result is borrowed from another source or build. Timings are
cloudtainer observations, not stable performance claims.

The facility's larger weakness is representativeness, not focused wall time:

- usually two peers, not a mesh;
- loopback or scripted routers, not public Tor/I2P;
- short runs, not days or weeks;
- small trees, not hundreds of thousands or millions of paths;
- largest focused streamed proof only 64 MiB plus 4 KiB;
- no macOS/Windows filesystem matrix;
- little disk-full, quota, suspend/resume, or power-loss injection;
- no measured comparison with the owner's actual Resilio workflow.

The rev0945 provenance rule remains binding: every publication claim verifies
`CMAKE_HOME_DIRECTORY` (or equivalent exact source identity) before using a
build result. Never aggregate results from divergent worktrees.

Rev0948 also reinforces that a foreground harness timeout is not automatically a
code timeout and is not permission to aggregate convenient partial green
output. Inspect process state, run the suspected test alone, and partition only
at explicit test boundaries. Final evidence must enumerate every shard and every
test exactly once. Raising a timeout remains no substitute for finding a
deadlock or pathological case.

### Test rules

- Build and run the touched owner/protocol/process proof first.
- Run the complete `product` label when a vertical slice is integrated.
- Use one canonical source tree and one isolated build directory per compiler.
- Verify the configured source path before trusting any build result.
- Never aggregate publication claims from divergent worktrees.
- Run the complete GCC graph and registry before packaging.
- Run the changed product path under Clang ASan+UBSan with leak detection.
- Treat readiness races and hangs as defects, not reasons to rerun until green.
- Regenerate the active source projection and exact manifest after all source,
  bootstrap, and evidence changes.
- Verify the wrapper directory and ZIP, test CRC, extract cleanly, and compare
  paths, bytes, types, and modes.

Do not answer suite cost by deleting useful product process tests or creating a
new audit universe. Keep one small touched-owner lane, one product lane, and one
complete release gate. Consolidate fixture and compile cost only when measured.


## Owner decisions still owed

Answer in ordinary language. Work continues with conservative reversible
defaults until an answer changes implementation priority.

### First uninstall target

- Which devices and operating systems?
- Which exact folder or kind of folder?
- Approximate path count, total bytes, largest file, and churn pattern?
- Direct, Tor, I2P, or mixed routes?
- Are both devices usually online together?
- Which Resilio features does this workflow actually use?

This answer defines the first credible uninstall gate and benchmark fixture.

### Filesystem and conflict promise

- Is changed-block reuse more urgent than rename for this workflow?
- Must empty directories synchronize?
- Which metadata matters: executable bit, mode, mtime, ownership, xattrs?
- Are symlinks rejected, copied as links, or followed?
- How should case/Unicode/incompatible-name collisions be presented?
- Should conflict candidates appear as files immediately or through managed
  history/export?

Default: regular files first, no silent metadata promise, preserve conflicting
candidates, and report unsupported paths.

### Deletion and history

- No trash, a bounded restore window, or approval before reclamation?
- How long should deleted and superseded bytes survive?
- Should delete/edit conflict materialize a conflict file automatically?
- May a quota evict old recoverable versions without interaction?

Default: retain recoverable bytes conservatively until a bounded policy is
chosen; never silently reclaim under an invented rule.

### Identity, routes, and “Anon”

- One device identity across shares, one identity per share, or optional
  personas?
- May one peer learn all routes for a device?
- Is transport through Tor/I2P enough, or must timing/address/identity linkage
  be reduced?
- Who owns and starts Tor/I2P: AnonSync, the operating system, or either mode?

Default: externally managed routers, explicit route per link, no fallback, and
no claim of traffic-analysis anonymity.

### Pairing and activation

- Is full fingerprint comparison mandatory every time?
- Should QR/short code be an authenticated convenience or the main ceremony?
- Should a successful pair automatically enable/start the user service?
- Is peer approval unilateral, mutual, or role-based?

Default: full pin, explicit mutual authorization, explicit final activation.

### Product surface

- Headless/CLI first, desktop tray first, or both?
- Is a systemd user service acceptable for the first uninstall target?
- Is one daemon managing many shares required immediately?
- Which status/error information must be visible without opening logs?

Default: Linux headless first, JSON status and clear terminal diagnostics, while
avoiding assumptions that block later desktop ownership.


## No-drift rules

Locked unless the owner directly changes them:

- Mission: replace Resilio Sync.
- Primary implementation: C++.
- Direct, Tor, and I2P are first-class route modes.
- Overlay-locked links fail closed.
- No silent timestamp-only conflict winner.
- One shipping product spine; no duplicate daemon.
- Internal scheduler choices are not automatically product configuration.
- `BOOTSTRAPROSE.md` is the sole visible root page.
- Hidden material remains recoverable donor/history/test material.
- Final response is one linked complete revision filename.

Reversible defaults:

- Linux/headless first.
- Externally managed Tor/I2P routers.
- Full pairing-card SHA-256 pin.
- Explicit service activation.
- Regular-file semantics before broad metadata.
- Streamed sequential range transfer remains the shipping baseline and oracle
  while reusable changed-block transfer is evaluated.
- Coordinated protocol breaks are acceptable during pre-alpha; compatibility
  becomes mandatory only when declared.

No future session should infer the mission from the largest source file, the
largest audit family, or the most recent internal abstraction. Read this page
first.


## Hidden layout

The release root intentionally looks like:

```text
BOOTSTRAPROSE.md          visible restart page
.h0p3/                    hidden revision/history material
.vault/project/           hidden complete source, tests, and tools
.vault/parent/            retained hidden parent source object
.vault/source-objects/    retained hidden donor archives
.vault/witnesses/         retained hidden mined donor material
.vault/README.md          hidden layout explanation
```

“Hidden” does not mean dead. It prevents a future session from confusing the
largest old subsystem with the product. Open hidden material only to implement,
test, audit, recover ideas, or answer an owner question.

Do not package build trees, VCS metadata, Python caches, binaries, sockets,
runtime databases, private test residues, or symlinks.


## Edition anchor

Revision: **rev0974**

Archive: `AnonSync-rev0974-2026.08.02.05.24-retentionplan-rootreasons-digestcursor-zircon.zip`

Codename: **zircon**

What changed:

- added one exact, deletion-free, digest-ordered physical payload-retention
  planner over current, superseded-active, inactive-evidence, and explicit-pin
  roots;
- bound continuation pages to the existing exact-v4 operation, evidence, pin,
  and payload cutpoint and rejected stale cursors rather than treating them as
  lexical insertion points;
- reused the mutex-linearized owner-only historical action lane and advanced
  live plus terminal status to `anonsync.peer-service.status.v19`;
- centralized the exact `(digest,size)` key, root masks, disposition mapping,
  reachability accounting, and canonical counted/emitted JSON stream; and
- corrected an unreachable 256 KiB presentation boundary to a proven 224 KiB
  frontier without granting quota, grace-period, quarantine, or unlink
  authority.

Validation:

```text
Exact rev0974 source passed the fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 441 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 155 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 305/305 checks. A clean Clang 17 Debug product dependency graph completed 239/239 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 39/39 product tests passed across bounded serial shards with leak detection and halt-on-error. One superseded combined sanitizer shard let the unchanged service lifecycle oracle reach its 30-second runtime cap after four of five cycles; the isolated authoritative rerun passed in 12.79 seconds with no sanitizer diagnostic. Focused sanitizer proof passed the 320-check SQLite-owner suite in 3.33 seconds at 556,136 KiB peak RSS, the 441-check folder-owner suite in 21.71 seconds at 1,412,208 KiB peak RSS, and the 155-check local-control suite in 0.63 seconds at 98,620 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0973 parent SHA-256 matched 62d265f026db82c946fe86df8700c6019826afc86604242716e9af564b84f7cd and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 18/18 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,336,658 bytes with SHA-256 1eb35263f32e14bb15be047a6bcadc88eb7aaac6bd5bcb9fd0898bf593b3377b. Validation excluded the rejected duplicate age-based planner prototype and every interrupted or timing-only non-authoritative run.
```

Release rule: this anchor is truthful only if the named archive passes the
internal active-source projection and exact manifest, wrapper directory and ZIP
verifiers, ZIP CRC and path/no-symlink policy, and a clean extraction preserves
all paths, bytes, entry types, and permission modes while the release root
exposes only `BOOTSTRAPROSE.md` plus the exact known hidden material.

## Rev0956: payload-integrity status and same-process recovery

Revision: **rev0956**

Archive: `AnonSync-rev0956-2026.07.31.12.22-integritystatus-degradedrecovery-ownerproof-peridot.zip`

Rev0956 keeps the linked-peer daemon alive when the payload store observes a
proven digest mismatch. The service moves to a fail-closed degraded state rather
than disappearing: readiness is false, synchronization authority is blocked, the
authenticated listener and owner-only status/control socket remain available,
and operator JSON reports the exact expected and observed SHA-256 values.
Recovery requires a complete current-byte payload-store reproof and ordinary
folder convergence before authority is restored. The recovered alarm remains as
bounded process-local history, not as payload authority.

The associated audit/refactor keeps rev0955's fixed-width allocation-independent
storage witness as the lower authority boundary, centralizes the v3 live and
terminal status renderer, separates ordinary TLS session I/O churn from
integrity alarms, and records the current waste: recovery may duplicate payload
namespace I/O until a future pass can safely thread the re-proved immutable
cutpoint into folder convergence.

## Rev0957: exact-owner reproof handoff and historical-cutpoint freshness

Revision: **rev0957**

Archive: `AnonSync-rev0957-2026.07.31.11.56-exacthandoff-cutpointfreshness-evidencepair-sapphire.zip`

Rev0957 removes an immediate duplicate complete payload-store observation from
integrity recovery without introducing a second synchronization algorithm. The
peer service moves the just-completed current-byte snapshot through the retained
folder process into the ordinary convergence body. Acceptance requires the exact
retained store owner: current thread and integrity epoch, rooted authority,
folder identity, attestation, limits, and the same process-local verification
cache. A foreign handle over the same durable store cannot lend authority.

The adjacent cutpoint audit found and corrected a one-pass false-absence defect.
A frozen append-only inventory is historical after any later mutation put—even
when the put reports `AlreadyPresent`. Remote planning now discards that
inventory and uses targeted exact-digest access, so a payload learned after the
snapshot cutpoint can be applied in the same pass without another complete root
scan. The hard regression freezes an empty handoff, appends a digest afterward,
forces local `AlreadyPresent`, and requires same-pass remote publication.

Operator evidence now attaches durable-witness publication only to the exact
expected/observed digest pair. Changed corrupt bytes start a new pair-scoped
publication result and increment a saturating observed-content transition count.
Native-I2P worker state is refreshed while faulted and at the recovery cutpoint
before readiness may return. Status advances to
`anonsync.peer-service.status.v4`.

Validation:

```text
GCC 14.2 Debug completed 527/527 edges from an empty build directory. The full
258/258 registry and an independent 39/39 product lane passed serially. Focused
suites passed 84 resumable-SHA, 16 scrub-state, 26 verification-index, 473
payload-store, 30 POSIX-resolution, 92 network-model plus 41 generated-operation,
296 SQLite-owner, 356 folder-owner, 110 sync-once, 2043 TLS, and 17 integrity-
evidence checks. The configured-service corruption/recovery process regression
passed. The structural audit passed 127/127.

Clang 17 ASan/UBSan completed the fresh 238/238 product dependency graph. All
39/39 product tests passed serially with leak detection under the disclosed
bounded-quarantine profile. No compiler, linker, sanitizer, runtime-error, or
leak diagnostic was retained.

The exact rev0956 parent SHA-256 matched and passed 41/41 wrapper-aware checks.
The recorded rev0957 patch reconstructed 20/20 changed active files exactly. The
active implementation projection binds 567 files / 25183267 bytes at SHA-256
1e20184b7974ab51607575c25f762ba411d90f850fceb41a2fe96356609a69f1.
```

Open boundaries remain explicit: the handoff is immediate and process-local,
changed paths can still require bounded mutation work, and no durable sequence
index, quarantine/restore/retention/garbage-collection policy, rename identity,
directory semantics, conflict UX, selective synchronization, many-share owner,
cross-platform qualification, named Resilio uninstall workload, or live Tor/I2P
leakage qualification is claimed.

## Rev0958: write-ahead scrub intent and restart authority fence

Revision: **rev0958**

Archive: `AnonSync-rev0958-2026.07.31.13.24-writeaheadintent-restartfence-exactwitness-rhodolite.zip`

Rev0958 closes a restart authority gap between durable verification-index reuse,
bounded rotating scrub, and cooperative lease deferral. Before a newly selected
payload is opened or read for scrub, the exact owner must commit and re-observe a
checksum-framed `Prepared` record binding the store identity, generation, digest,
canonical eleven-field POSIX observation, zero offset, and initial resumable
SHA-256 state. `Prepared` and `Progress` are crash witnesses, never content proof.
A fresh process observing either state must hash the active payload in its
ordinary complete scan before returning authority, even when the optional scrub
cannot acquire its exclusive lease.

The same process retains only a narrow acceleration exception: process-cache
reuse is permitted after its own exact commit/re-observation or a complete
current-byte scan while the exact active state and state-file observation remain
frozen. Durable-index reuse stays forbidden. Mismatch handling clears that
acceleration and installs the fixed-width fail-closed integrity witness before
terminal strings, best-effort evidence publication, or typed-error construction
can allocate.

The hard process regression constructs metadata-hidden corrupt bytes, a matching
stale durable verification entry, and a valid `Prepared` intent. A child holds a
shared store lease so the fresh owner's complete scan remains available while
optional scrub is mechanically blocked. The ordinary scanner still hashes the
payload and throws the exact integrity error; no durable failure publication is
falsely claimed.

Validation:

```text
GCC 14.2 Debug reached a complete no-work graph after the unchanged 527-edge
rev0957 target topology, with a final exact-source 15/15 rebuild. The complete
258/258 registry and an independent 39/39 product lane passed serially. Focused
suites passed 84 resumable-SHA, 19 scrub-state, 26 verification-index, 477
payload-store, 30 POSIX-resolution, 92 network-model plus 41 generated-operation,
296 SQLite-owner, 356 folder-owner, 110 sync-once, 2043 TLS, and 17 integrity-
evidence checks. The structural audit passed 135/135.

Clang 17 ASan/UBSan completed the fresh 238-edge product dependency graph. All
39/39 product tests passed serially with leak detection in 320.18 seconds. No
compiler, linker, sanitizer, runtime-error, or leak diagnostic was retained.

The exact rev0957 sapphire parent SHA-256 matched and passed 41/41 wrapper-aware
checks. The recorded rev0958 patch reconstructed 7/7 changed active files. The
active implementation projection binds 567 files / 25208824 bytes at SHA-256
d2efac72d8381cda1c910438915d4b86ef0231ae3410e7b33ef482ab4c2b533e.
```

The record format retains its fixed v1 width and prior encodings, but older
binaries do not understand `Prepared = 4`; downgrade safety is not claimed.
Power-loss qualification, hostile same-UID protection, quarantine/restore,
retention and garbage collection, rename/directory semantics, selective sync,
many-share supervision, cross-platform behavior, a measured first Resilio
uninstall workload, and live public Tor/I2P qualification remain open.

## Rev0959: reader fence, lease deferral, and versioned operator truth

Revision: **rev0959**

Archive: `AnonSync-rev0959-2026.07.31.19.02-readerfence-leasedeferral-statuscontract-blackopal.zip`

Rev0959 raises the minimum compatible writable payload-store reader at the
identity/lease inode itself. An exact v2/v3 legacy marker migrates only while the
same inode is exclusively locked and after a complete rooted current-byte scan
with every reuse shortcut disabled. The move is no-replace, file- and directory-
synchronized, pathname- and inode-reproved, and handed to ordinary snapshot
ownership without an immediate duplicate scan. Coexistence, unsupported v1,
corruption, lock contention, or post-cutpoint drift remain fail closed.

The same complete proof can settle damaged or superseded scrub intent without a
second payload read. One exact stale complete observation may be discarded before
any authority publishes and retried from a fresh rooted cursor; a second drift is
terminal. Typed cooperative lease contention now retains the same peer-service
PID, listener, owner-only control socket, ingress state, and integrity history,
while one bounded service-owned cutpoint schedules fresh re-observation. Unknown
network completion is reported as unknown rather than fabricated as a handoff.

The adjacent audit/refactor made Markdown prose checks whitespace-stable and
advanced the final JSON contract to `anonsync.peer-service.status.v6` after the
late lease-scheduling and ambiguous-network-outcome fields were added. This
prevents both line-wrapping from becoming false release authority and clients
from silently interpreting a widened object as the earlier rev0959 v5 shape.

Validation:

```text
GCC 14.2 Debug completed a fresh 527/527-edge graph. The complete 258/258
registry passed serially in 240.58 seconds; the independent 39/39 product
lane passed in 105.45 seconds. Focused suites passed 84 SHA,
19 scrub-state, 26 verification-index, 515 payload-store, 30/30
rooted-POSIX, 92 network-model plus 41 generated-operation, 296
SQLite-owner, 360 folder-owner, 110 sync-once, 2043 TLS, and
17 integrity-evidence checks. The structural audit passed 161/161.

Clang 17 ASan/UBSan completed a fresh 238/238-edge product graph. All 39/39
product tests passed serially with leak detection in 317.19 seconds and no
retained compiler, linker, sanitizer, runtime-error, or leak diagnostic.

The exact rev0958 parent SHA-256 matched and passed 41/41 wrapper-aware checks.
The recorded rev0959 patch reconstructed 15/15 changed active files. The active
projection binds 567 files / 25358294 bytes at SHA-256
007228fcaf45dfeee48840793391f5342b0625ff6971ad4d760cdc76fc1d4d48.
```

Open boundaries remain explicit: there is still no supported downgrade or
mixed-reader rolling-upgrade promise, universal power-loss qualification,
hostile same-UID defense, quarantine/restore/retention/garbage collection,
rename identity, directory semantics, conflict UX, selective sync, many-share
owner, cross-platform qualification, named measured Resilio uninstall workload,
or live public Tor/I2P leakage qualification.

## Rev0960: owner-triggered current-byte payload recheck

Revision: **rev0960**

Archive: `AnonSync-rev0960-2026.08.01.00.15-ownerrecheck-actionseal-exacthandoff-tourmaline.zip`

Rev0960 adds the owner command
`anonsync_sync recheck --socket ABSOLUTE_SOCKET` to the one retained linked-peer
service. The mode-0600 local socket accepts exactly `recheck\n`, binds the
response to the connected process PID, and advances a monotonic process-local
request generation. Requested, started, and completed generations remain
separate: acceptance is not byte proof, and a request is not durable across
process exit.

Drain and recheck now have one ordering model. One mutex protects both states,
one condition variable wakes the owner, one action snapshot is the sole owner
observation, and one shutdown seal binds every pre-seal accepted generation into
terminal accounting. Requests serialized after drain reject without advancing
the generation. Multiple requests may coalesce, while a request accepted after
an attempt starts remains pending and cannot defeat backoff established by that
attempt.

The proof path runs the complete rooted payload scanner with process-local and
durable verification reuse disabled. The returned snapshot requires zero reused
entries and bytes and exact hashed-entry and hashed-byte totals. That same
move-only snapshot enters ordinary folder convergence; no second complete
payload-root observation or mutation full scan is needed merely because the
operator requested proof. Lease contention retains the service and request.
Stable corruption retains exact expected/observed evidence and blocks readiness.
After external repair, forced bytes plus ordinary convergence restore authority
in the same PID and preserve immutable recovery history.

Status advances to `anonsync.peer-service.status.v7`. Live status and terminal
status use one canonical `payload_recheck` renderer and expose generation state,
bounded retry, hash work, snapshot handoff, duplicate-scan routes, coalescing,
and integrity recovery. The real-process oracle holds the exact writer lease,
queues two requests, proves coalescing and same-PID deferral, changes stable
corrupt bytes, repairs them, and requires completion with one handoff and no
duplicate complete scan.

Validation:

```text
GCC 14.2 Debug completed a fresh 527/527-edge graph and exact-source no-work
re-attestation. The complete 258/258 registry passed serially in 134.10 seconds;
the independent 39/39 product lane passed in 54.26 seconds. Focused suites
passed 84 resumable-SHA, 19 scrub-state, 26 verification-index, 519
payload-store, 30/30 rooted-POSIX, 92 network-model plus 41 generated-operation,
296 SQLite-owner, 360 folder-owner, 110 sync-once, 2043 TLS, 17 integrity-
evidence, and 69 local-status-socket checks. The structural audit passed
166/166.

Clang 17 ASan/UBSan completed a fresh 238/238-edge product dependency graph and
exact-source no-work re-attestation. All 39/39 product tests passed serially with
leak detection in 124.68 seconds. The core payload-store target was then built
and passed all 519 focused checks under the same sanitizer profile in 8.61
seconds. No retained compiler, linker, AddressSanitizer,
UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic remains.

The exact rev0959 parent SHA-256 matched and passed 41/41 wrapper-aware checks.
The recorded rev0960 patch reconstructed 16/16 changed active files exactly.
The active projection binds 567 files / 25420532 bytes at SHA-256
61fed36a59412827b9aec3e5d6604c37fecf5107de647cadef28422bf4086788.
```

This remains a payload-store operation. It does not claim filesystem-wide scrub,
durable requests, subpath selection, live byte progress, cancellation, hostile
same-UID defense, portable pathname-socket security, network-filesystem lock
equivalence, quarantine, restore, retention, reachability, garbage collection,
or completion of a named measured Resilio uninstall workflow.

