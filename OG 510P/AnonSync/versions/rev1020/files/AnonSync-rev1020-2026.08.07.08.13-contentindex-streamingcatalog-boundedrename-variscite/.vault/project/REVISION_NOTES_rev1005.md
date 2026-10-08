# Revision notes — rev1005

## Targeted intermediate terminal verification

Rev1005 retains the rev1004 32 MiB resumable SHA-256 journal but removes a
complete payload-store namespace traversal from each intermediate step. Under
the existing exclusive store lease, the receiver independently reopens the
payload root and exact-observes only the terminal journal, canonical complete
staged-prefix inode, and possible digest name. Root identity, pathname binding,
private-file shape, extent, retained authority, and the lease are re-proved.

This exact-name observer grants no capacity, cleanup, namespace-health, or
publication authority. Terminal completion still performs the ordinary complete
store scan immediately before no-replace digest publication. Unexpected
unrelated entries can therefore no longer amplify every hash checkpoint, but
they still block final publication.

## Bounded receiver-local pulse

One reconciliation apply can advance at most 32 fixed terminal steps, or 1 GiB
at the shipping 32 MiB step size. The work is receiver-local and source-byte-
free. The exact operation cursor remains outstanding until publication.
Diagnostic accounting now reports total terminal steps, local continuation
steps, and pulse exhaustion through apply results, TLS aggregation, and both
shipping CLI JSON surfaces.

Payloads larger than 1 GiB can still require another payload-cold peer apply.
Rev1005 does not claim a background scheduler or complete elimination of peer-
turn coupling.

## Adjacent audit: exact budget enforcement

The first local-pulse integration could exceed its configured frontier when one
response completed several ranged files: each ordinary range-staging call could
start a terminal step before the local pulse ran.

A new narrow deferred-terminal range API closes that hole. It durably commits
the authenticated range but performs no terminal SHA-256 step after the apply
budget is spent. A completed byte prefix remains exact progress at total size
until a later ordinary local continuation verifies and publishes the exact
staged inode. The service checks that every staging and local-continuation path
stays at or below the configured maximum.

## Focused regressions

- Intermediate exact-name continuation proceeds despite an unrelated unexpected
  entry; final publication rejects that entry through the complete store scan.
- Deferred terminal staging performs zero hash steps and publishes nothing;
  ordinary continuation later verifies and publishes exact bytes.
- A one-step service frontier yields after exactly one step, reports exhaustion,
  and completes on the next exact payload-cold apply.
- The real 64 MiB-plus-tail process transfer publishes on its second response
  with three receiver-local terminal steps; one small exact-cursor response
  then confirms completion without source payload access.

## Product boundary

A 4 TiB file can still require up to 4,096 verification applies under the 1 GiB
shipping pulse. First journal admission and final publication retain complete
store scans, and source manifest construction can still read a whole source in
one owner call. Multi-terabyte measurement and, if justified, a bounded durable
receiver-local background scheduler remain next.

Rev1005 does not add a durable/global chunk index, rename/move identity,
complete directories, Android support, selective placeholders or automatic
eviction, ENOSPC qualification, or public-route performance proof.

## Release cutpoint

Validation: `Exact rev1005 source passed a fresh GCC 14.2 Debug complete graph with 555/555 configured build edges and exact-source no-work re-attestation; all 289/289 registered tests were accounted for across bounded immutable invocations, and the complete 48/48 product set was accounted for through aggregate and isolated heavy-test runs. Focused GCC proofs passed 20 terminal-state-codec, 706 payload-store, 4,999 reconciliation-protocol, 196 reconciliation-service, 536 folder-owner, 397 SQLite-owner, and 2,044 TLS-transport checks. Source audits passed 24/24 targeted-terminal/local-pulse, 38/38 terminal-continuation, 27/27 response-memory-shape, 34/34 direct-source-frame, 21/21 bounded-history-access, and 575/575 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 266/266 configured edges with no-work re-attestation; all 48/48 product tests were accounted for with leak detection and halt-on-error, including serial isolation of the two memory-heavy suites and the remaining lifecycle process tests. Focused sanitizer proofs passed 706 payload-store, 196 reconciliation-service, and 536 folder-owner checks; payload-store and folder-owner peak RSS were 729,432 KiB and 1,707,948 KiB. No compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic remained in passing evidence. The exact rev1004 parent SHA-256 matched 26c3fa06faeac08f6086d7154a76f05d536443067a941d7adf37579ca0f796d1 and passed 41/41 wrapper-aware package checks. The final active implementation projection contains 619 files / 28,550,115 bytes with SHA-256 5be67041b1b0254d8524a9ce05b0262a524f235d764601008398b9b95b69d778. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excludes interrupted aggregate CTest wrappers, one concurrent sanitizer lifecycle fixture whose precondition was invalidated by test concurrency but which passed serially on the same binaries, remount-vanished unsealed worktrees, and obsolete validator branches and builds.`

Archive: `AnonSync-rev1005-2026.08.05.19.37-targetedterminal-localpulse-exactcursor-goshenite.zip`

Codename: `goshenite`
