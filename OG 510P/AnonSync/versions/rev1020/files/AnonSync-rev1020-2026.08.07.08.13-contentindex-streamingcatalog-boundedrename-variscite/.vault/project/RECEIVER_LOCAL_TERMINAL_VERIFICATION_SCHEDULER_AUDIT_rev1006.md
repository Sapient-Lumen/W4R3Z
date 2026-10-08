# Receiver-local terminal-verification scheduler audit — rev1006

## Product reason

Rev1005 removed repeated payload-root enumeration from intermediate whole-target
SHA-256 and allowed one authenticated reconciliation apply to advance as much as
1 GiB of receiver-local terminal work. A larger completed staged file still
needed another authenticated peer turn for each later pulse. That coupling was
especially poor for the first supported workflow: Linux/headless selective
synchronization of multi-terabyte media trees over routes that may be slow,
intermittent, or intentionally offline after the bytes have arrived.

Rev1006 moves the already-durable terminal-verification obligation into the
retained receiver service's single owner loop. It does not add another content
authority, another worker thread, or another publication engine.

## Durable discovery, process-local scheduling

The durable facts remain the rev1004 two-slot terminal SHA-256 journal and the
canonical complete staged-prefix inode. A complete writable payload-store scan
now projects every exact usable pair into one compact process-local work cache.
Each item contains only the content digest, total extent, and verified offset.
The cache is bounded by the existing transient-entry frontier and retains no
payload bytes or SHA-256 checkpoint bytes beyond what already exists in the
journal.

A fresh owner begins with the observation marked unknown. Targeted staging or
terminal work cannot manufacture a claim that the complete payload namespace
has been observed. The first ordinary complete store scan discovers pending
work. After restart, another ordinary complete scan reconstructs the cache from
the durable prefix and journal; no scheduler-specific database or mutable queue
is introduced.

The discovery scan also treats a complete staged prefix without a usable exact
journal as pending from offset zero. Malformed, stale, foreign, or torn state
never becomes acceleration authority. The ordinary terminal verifier retains
its existing fail-closed journal handling.

## One exact bounded local pulse

`continue_one_pending_terminal_verification_or_throw()` selects one obligation
by the smallest verified offset, with digest order as the deterministic tie
break. It then enters the existing exact targeted terminal-verification path
under the store-global exclusive lease.

One call reads at most the shipping 32 MiB terminal frontier with the existing
fixed 64 KiB buffer. Intermediate work reopens only the exact store identity,
journal, complete staged prefix, and possible final digest name. It does not
enumerate unrelated payload entries. Final completion still enters the ordinary
complete payload-store scan before no-replace digest publication.

The process cache is advisory scheduling state. Every filesystem effect is
re-proved by the existing rooted descriptor and lease boundaries. If another
owner has already published the payload, a stale cache entry is reconciled and
removed. That reconciliation reports zero hashed bytes when no terminal SHA
step occurred; it cannot mislabel process-local offset movement as byte work.

The adjacent audit found another cross-owner edge: a stale complete projection
can temporarily overcount work after another process publishes one prefix and a
new prefix replaces it. A valid durable staging effect must not fail afterward
merely because the advisory vector cannot add another entry. Post-effect cache
maintenance is therefore no-throw: any standard allocation or canonicalization
failure clears the vector and marks observation unknown. The next ordinary
complete scan rebuilds it. A focused regression fills the stale projection,
commits replacement prefixes through the same owner, and proves both the
non-failing durable call and conservative rebuild.

## Service-loop fairness and availability

The peer service executes at most one local terminal pulse before forcing at
least one ordinary owner-loop turn. That intervening turn observes stop and
owner-control actions, ingress state, watcher work, repair scheduling, lease
retry cutpoints, and authenticated networking before another local pulse is
eligible.

This is deliberately not an independent background thread. The scheduler is a
receiver-local lane inside the existing single owner thread and shares its
failure, lease-deferral, integrity, readiness, and shutdown state machine.
The authenticated listener and owner-only control socket remain available while
local terminal work progresses.

The service may continue a completed staged file without a running source peer.
A real process regression creates a 64 MiB-plus-tail deferred prefix, starts one
configured receiver service and no peer process, and requires exactly three
local pulses: two progress steps and one completion/publication step. The same
PID remains ready and owner-controllable throughout.

## Status contract and adjacent hardening

Live and terminal status advance to `anonsync.peer-service.status.v25` and expose:

- whether the complete terminal-work observation is known;
- the pending count and aggregate verified and total bytes;
- the exact next digest, extent, and verified offset;
- scheduler steps, progress steps, completions, insertions, stale-cache
  reconciliations, hashed bytes, and ordinary-turn yields; and
- the exact last local terminal step when it was the most recent service action.

The renderer now rejects internally inconsistent scheduler projections rather
than serializing plausible but impossible JSON. Unknown observations cannot
carry work, empty/nonempty state must agree with the next item, pending offsets
must remain below exact extents, and aggregate verified bytes cannot exceed
aggregate total bytes.

### Sanitizer target-inventory correction

The adjacent build audit found that the new terminal-verification fixture had
joined the product graph but not the inherited graph's two explicit sanitizer
inventories. Its static dependencies were therefore instrumented while its own
final link omitted the ASan/UBSan runtime, producing undefined sanitizer symbols
in a clean Clang build. The fixture is now named in both the compile and final-
link inventories, and the focused source audit parses those two scopes
independently so a future product fixture cannot repeat the same integration
drift. The failed pre-correction link is retained only as negative evidence.

## Scale boundary

Rev1006 removes authenticated peer-turn coupling after all bytes are durable.
It does not make terminal verification instantaneous. A 4 TiB file still
requires 131,072 bounded 32 MiB local pulses, interleaved with ordinary service
turns. The device must remain running long enough to perform that disk work;
restart resumes from the durable journal after a complete store observation.

First journal admission and final digest publication still require complete
payload-store scans. Source-side target-manifest construction can still read a
complete source in one owner call. Cross-file chunk discovery remains
process-local rather than a restart-durable global index. Rev1006 does not add
identity-preserving rename/move, complete directory semantics, Android support,
selective placeholders or automatic eviction, ENOSPC qualification, or public
Tor/I2P performance proof.

The next scale decision should be measurement-driven: sparse multi-terabyte
files and trees, restart latency, page-cache pressure, terminal-pulse throughput,
source manifest construction, and chunk-index rebuild cost. A bounded durable
source/chunk index is a likely next scale move if those measurements show that
source reconstruction dominates; otherwise priority should return to rename and
move identity, directory semantics, and selective-sync user surfaces.

## Release cutpoint

Validation: Exact rev1006 source passed a fresh GCC 14.2 Debug complete graph with 557/557 configured build edges and exact-source no-work re-attestation; all 291/291 registered tests and the independent 49/49 product set passed. Focused GCC proofs passed 20 terminal-state-codec, 737 payload-store, 397 SQLite-owner, 536 folder-owner, 110 sync-once, 196 reconciliation-service, and 2,044 TLS-transport checks; the shipping peer-independent scheduler process regression passed with no source peer. Source audits passed 33/33 receiver-local terminal-scheduler and 584/584 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 268/268 configured edges; all 49/49 product tests passed with leak detection and halt-on-error, and focused sanitizer payload-store proof passed all 737 checks. No compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic remained in passing evidence. The exact rev1005 parent SHA-256 matched b94e3c496bbec3c230c8d3af3081f53d0f519e9945943022df80ecc3f5e3199d and passed 41/41 wrapper-aware package checks. The final active implementation projection contains 622 files / 28,656,401 bytes with SHA-256 808d8740871083908600d243359c97e0253b456afef4ba65c5f4e88bb39e2b1f. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excludes the pre-correction sanitizer fixture-link failure, interrupted wrapper commands, the duplicate Ninja that briefly entered the same cache and was terminated, the remount-vanished unsealed worktree, and all obsolete validator branches and builds.

Archive: `AnonSync-rev1006-2026.08.05.22.03-receiverlocalscheduler-restartdiscovery-ownerfairness-malachite.zip`

Codename: `malachite`
