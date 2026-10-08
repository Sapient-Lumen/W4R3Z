# AnonSync rev0953 revision notes

## Mission

AnonSync remains one practical C++ replacement for the personal Resilio Sync
workflow: continuous authenticated folder convergence over direct TCP, Tor, and
I2P, with ordinary setup, recovery, lifecycle, and bounded resource behavior.
This revision removes pathological payload work and strengthens truthful final
settlement on that same shipping spine; it does not add a parallel sync engine.

## Product correction: exact-name remote payload access

Rev0952 could bound remote pathname inspection yet still force a complete private
payload-store snapshot for ordinary remote-only file application. That snapshot
enumerates every payload name, validates complete namespace shape/capacity, and
opens/stats every admitted object; restart-cold or changed observations also hash
payload bytes. One remote digest could therefore pay work proportional to all
retained payload history.

Rev0953 introduces one move-only, pass-scoped targeted payload capability. When a
pass does not already own a complete verified payload snapshot, it performs
identity reconciliation and rooted setup once, then uses fresh fail-fast shared
leases and exact marker reproof for each digest probe or selection. Missing
payloads remain unresolved scheduling work and do not block a ready suffix. The
selected descriptor remains open through the existing atomic publisher, which
performs the sole selected-byte SHA-256 proof before visible filesystem or
catalog advancement.

This lane deliberately does not enumerate unrelated payload entries or attest
complete namespace health/capacity. `snapshot_or_throw()` remains the only full
inventory and health oracle. Tests prove the distinction by consuming one valid
digest beside an invalid unrelated entry through targeted access while requiring
a complete snapshot to reject the namespace. Same-size selected-byte corruption
fails at publication and leaves destination/catalog state unchanged.

## Correctness correction: terminal cross-owner fence

A second audit found that catalog scheduling completion needed a real terminal
replica observation, not only the pass's earlier replica snapshot. Rev0953 adds a
complete visible-projection guard backed by replica `BEGIN IMMEDIATE`. While that
guard holds the matching visible digest stable, a catalog `BEGIN IMMEDIATE`
transaction exactly re-proves the terminal catalog head, authenticated local scan
head, and prior remote-work head before publishing the wanted cursor/sweep state.
A mismatch reports `authority_cutpoint_changed` and withholds settlement.

The final audit tightened the pure `sync-once` settlement predicate further. It
now requires the pass's published remote fairness cursor to equal the durable
cursor in the final process cutpoint, in addition to matching terminal catalog
and visible-state digests. Scheduling-only movement between pass return and final
snapshot can no longer be mislabeled as the same settled observation.

## Audit and refactor

The first targeted implementation repeated store identity reconciliation and root
setup for every probe and selection. The pass-scoped capability amortizes that
work while retaining a new lease and exact identity-marker/root proof per
operation; no store lease spans planning or destination I/O.

The POSIX required/optional regular-file component openers now share one
implementation. Optional mode returns absence only for `ENOENT`; symlinks,
non-regular objects, mount crossings, permission failures, unsafe components,
and inode races remain errors. The remote apply path also centralizes selected
payload ownership so a complete snapshot and targeted access cannot be consumed
simultaneously.

The terminal publication path centralizes cross-owner lock ordering and final
head comparison. Both ordinary and speculative-idle completion use the same
helper, and one pure settlement predicate now binds scan completion, remote sweep
completion, deferred work, stop reason, terminal digests, durable cursor, and
inactive continuation journals.

## Observable changes

Pass, folder CLI, service, and one-shot JSON surfaces add:

- `remote_targeted_payload_accesses`;
- `remote_targeted_payload_probes`;
- `remote_targeted_payload_selections`;
- `remote_targeted_payload_selected_bytes`;
- `remote_inspection_terminal_cutpoint_reproved`;
- `remote_inspection_terminal_catalog_digest`; and
- `remote_inspection_terminal_visible_state_digest`.

The optimization is falsifiable: a retained complete snapshot reports zero
targeted activity, while a multi-file remote-only pass must amortize its probes
and selections through one targeted-access birth.

## Validation

Fresh GCC 14.2 Debug completed all 511 build steps, then all 254 registered tests passed in one uninterrupted 63.45-second CTest run and the explicit product lane passed 35/35 in 26.69 seconds. Focused executables passed 92 network-model checks with 41 generated operations, 30 POSIX-resolution checks, 164 payload-store checks, 296 SQLite-owner checks, 347 folder-owner checks, and 110 sync-once checks. The structural audit passed 75/75. A fresh Clang 17 ASan/UBSan product graph completed 222/222 steps; all 35 product tests passed serially with leak detection in 104.58 seconds, and the same focused suites passed under the sanitizers with no retained diagnostic.

## Honest boundary

Targeted lookup is not a durable payload index. A large remote projection still
performs an exact-name lookup per candidate and selected candidates are opened
again. Local/snapshot lanes still perform complete restart-cold payload walks;
the verification cache is process-local; retained history is append-only; and
changed large files still transfer as complete payloads.

The terminal fence is not cross-database or filesystem atomicity. It provides one
writer-serialized observation at scheduling publication and exact final-cutpoint
classification. Filesystem races remain governed by descriptor/root/hash proofs,
and later mutation is ordinary next-cycle work. Multi-process fault/soak
qualification, rotating scrub, retention/restore/garbage collection, rename and
metadata semantics, selective sync, many-share ownership, cross-platform
qualification, and the first named Resilio uninstall workload remain open.

See `TARGETED_REMOTE_PAYLOAD_ACCESS_AUDIT_rev0953.md`,
`TERMINAL_CROSS_OWNER_SETTLEMENT_FENCE_AUDIT_rev0953.md`, and
`REVISION_EVIDENCE/rev0953/`.

## Package

Declared publication name: `AnonSync-rev0953-2026.07.30.18.29-targetedpayload-terminalcursor-crossowner-smokyquartz.zip`

Parent: `AnonSync-rev0952-2026.07.30.14.40-rootedsweep-linearprojection-settlement-aquamarine.zip`

Parent SHA-256: `7b91ee9695b552e8438fcd182da73d34217b513bcdb358b7a6183d9cc9ccd51f`
