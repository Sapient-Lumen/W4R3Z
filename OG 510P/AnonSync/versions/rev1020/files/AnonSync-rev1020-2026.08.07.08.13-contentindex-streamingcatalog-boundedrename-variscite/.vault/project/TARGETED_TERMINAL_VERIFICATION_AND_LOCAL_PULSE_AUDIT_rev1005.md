# Targeted terminal verification and receiver-local pulse audit — rev1005

## Product reason

Rev1004 made receiver terminal whole-target SHA-256 restart-safe and bounded to
32 MiB per payload-store call, but every incomplete step still required a new
peer turn and a complete payload-store namespace observation. That shape was
safe but wasteful for the first supported workflow: Linux/headless selective
synchronization of multi-terabyte media trees over routes that may have high
latency.

Rev1005 keeps the exact rev1004 durable journal and publication authority while
removing both avoidable multipliers from the ordinary intermediate path.

## Exact targeted observation

An intermediate terminal step now runs beneath the existing store-global
exclusive mutation lease and independently reopens the retained payload root.
It opens only three exact names:

- the checksum-framed terminal-verification journal;
- the canonical complete staged-prefix basename; and
- the final digest name, if it already exists.

The observer validates private regular-file shape, exact extent, exact pathname
binding, root identity before and after observation, retained/root authority,
and the lease cutpoint. It performs no directory enumeration and gains no
namespace-health, capacity, cleanup, or publication authority.

That restriction is deliberate. A terminal completion still enters the
existing complete `scan_store_under_lease_or_throw()` preflight before the
no-replace digest publication. An unexpected unrelated basename can therefore
coexist with intermediate computation progress but blocks final publication.
Rev1005 reduces repeated work without weakening the final namespace boundary.

## Receiver-local pulse

One authenticated reconciliation apply may now execute up to 32 fixed 32 MiB
terminal-verification steps after all source bytes are durable. The shipping
frontier therefore advances at most 1 GiB of receiver-local SHA-256 per apply
with the same fixed 64 KiB streaming buffer. These steps carry no source bytes,
do not reopen source payload authority, and retain the exact operation cursor
until local publication.

The result exposes exact counts for total terminal steps, receiver-local
continuation steps, and per-apply budget exhaustion. TLS and both shipping CLI
JSON surfaces retain those counters.

## Mechanical budget enforcement

The adjacent audit found a real overclaim in the first integration. A page can
finish several ranged files, and the ordinary range-staging API was allowed to
start one terminal hash step for each file even after the service pulse had
spent its configured budget.

Rev1005 adds a narrow deferred-terminal range entry point. It commits and
re-proves the exact authenticated range under the existing writer-fenced prefix
owner, but if the byte prefix becomes complete it returns exact progress at the
total-size cutpoint without creating or advancing SHA state. Later receiver-
local continuation must verify and publish that exact staged inode. The service
selects this entry point after its terminal-step frontier is exhausted and
rejects any accounting path that crosses the configured maximum.

This is not a second staging or publication engine. The ordinary API, durable
journal, exact final digest, complete final scan, and no-replace publication
remain authoritative.

## Runtime proof

The focused payload-store regression inserts an unexpected unrelated root entry
between intermediate and final verification. The exact targeted step advances
the journal without enumerating that entry; final publication then fails at the
mandatory complete scan. Removing the unexpected entry permits exact digest
publication. A second regression proves deferred terminal verification commits
all bytes, performs zero hash steps, publishes nothing, and is later completed
through the ordinary exact continuation.

The service regression uses a payload larger than two 32 MiB steps and a
one-step configured pulse. The first payload-cold apply advances exactly one
step, publishes no operation, and reports one exhaustion. The next apply hashes
the exact tail and admits the operation. Constructor tests reject zero and
above-shipping frontiers.

The two-process TLS regression now completes a 64 MiB-plus-tail payload in the
second authenticated response with three local terminal steps. A final 560-byte
payload-cold response confirms the exact operation cursor without retransmitted
ranges or source payload access.

## Product boundary and remaining scale work

Rev1005 does not remove all peer-turn coupling. A file larger than the shipping
1 GiB pulse still yields an exact payload-cold continuation; a 4 TiB file can
therefore require up to 4,096 verification applies after its bytes arrive.
First journal admission and final digest publication still require complete
payload-store observations. Source-side target-manifest construction can still
read a complete source in one owner call.

The next scale step should measure sparse synthetic multi-terabyte trees and
files, including RSS, page-cache pressure, directory work, restart behavior,
disk amplification, and high-latency routes. If 1 GiB pulses remain material,
terminal verification should become a bounded background receiver-local
scheduler whose durable obligation no longer depends on peer traffic. That
scheduler must preserve exact inode/journal authority and the complete final
scan rather than inventing a second content authority.

Rev1005 does not add a durable/global chunk index, identity-preserving
rename/move, complete directory semantics, Android support, selective
placeholders or automatic eviction, ENOSPC qualification, or public Tor/I2P
performance proof.

## Release cutpoint

Validation: `Exact rev1005 source passed a fresh GCC 14.2 Debug complete graph with 555/555 configured build edges and exact-source no-work re-attestation; all 289/289 registered tests were accounted for across bounded immutable invocations, and the complete 48/48 product set was accounted for through aggregate and isolated heavy-test runs. Focused GCC proofs passed 20 terminal-state-codec, 706 payload-store, 4,999 reconciliation-protocol, 196 reconciliation-service, 536 folder-owner, 397 SQLite-owner, and 2,044 TLS-transport checks. Source audits passed 24/24 targeted-terminal/local-pulse, 38/38 terminal-continuation, 27/27 response-memory-shape, 34/34 direct-source-frame, 21/21 bounded-history-access, and 575/575 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 266/266 configured edges with no-work re-attestation; all 48/48 product tests were accounted for with leak detection and halt-on-error, including serial isolation of the two memory-heavy suites and the remaining lifecycle process tests. Focused sanitizer proofs passed 706 payload-store, 196 reconciliation-service, and 536 folder-owner checks; payload-store and folder-owner peak RSS were 729,432 KiB and 1,707,948 KiB. No compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic remained in passing evidence. The exact rev1004 parent SHA-256 matched 26c3fa06faeac08f6086d7154a76f05d536443067a941d7adf37579ca0f796d1 and passed 41/41 wrapper-aware package checks. The final active implementation projection contains 619 files / 28,550,115 bytes with SHA-256 5be67041b1b0254d8524a9ce05b0262a524f235d764601008398b9b95b69d778. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excludes interrupted aggregate CTest wrappers, one concurrent sanitizer lifecycle fixture whose precondition was invalidated by test concurrency but which passed serially on the same binaries, remount-vanished unsealed worktrees, and obsolete validator branches and builds.`

Archive: `AnonSync-rev1005-2026.08.05.19.37-targetedterminal-localpulse-exactcursor-goshenite.zip`

Codename: `goshenite`
