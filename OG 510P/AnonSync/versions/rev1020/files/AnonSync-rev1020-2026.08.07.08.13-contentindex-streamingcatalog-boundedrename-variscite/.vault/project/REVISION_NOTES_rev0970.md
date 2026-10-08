# Revision notes — rev0970

## Product move

Rev0970 adds an explicit causal-metadata history mode:

```text
anonsync_sync versions --socket ABSOLUTE_SOCKET \
    --inspection-mode metadata
```

It lists bounded retained causal predecessors without opening or scanning the
private payload store. The existing default `--inspection-mode exact` remains
unchanged and continues to report exact retained-payload availability.

## C++ implementation

- Added the shared `SyncReplicaHistoricalVersionInspectionMode` authority type
  and one canonical name/parser used by CLI, local protocol, service identity,
  status, and source cutpoints.
- Preserved exact v1 source tokens and added mode-bound
  `v2:metadata:<operation-set-digest>` tokens.
- Rejected source cutpoints whose mode differs from the query.
- Split folder-owner inspection before the payload-store call: exact mode keeps
  the complete bracketed payload snapshot, while metadata mode stops at the
  immutable causal snapshot.
- Changed payload-derived inventory and entry fields to `std::optional`, making
  unknown mechanically distinct from false or zero.
- Advanced live and terminal status to `anonsync.peer-service.status.v15`.
- Advanced owner-only history responses to
  `anonsync.local-historical-versions.response.v4`.
- Added a strict five-field mode-bearing `versions-query` frame while retaining
  legacy exact request forms.
- Added `--inspection-mode exact|metadata` to the shipping CLI, defaulting to
  exact for compatibility.

## Adjacent audit/refactor

The prior bounded page still paid for one complete payload-namespace snapshot,
regardless of path or page size. Rev0970 removes that work only when the caller
explicitly chooses causal metadata. It does not weaken the exact v1 contract.

The audit also removed a subtler authority ambiguity: metadata mode does not
serialize unavailable evidence as `false` or zero. Payload snapshot digest,
scan accounting, aggregate availability counts, and per-entry
payload/restore-ready values are all null until an exact payload observation
exists.
It also corrected an adjacent C++ regression that used `std::optional<bool>`
in boolean context and therefore tested engagement rather than the contained
exact availability value.

## Compatibility

- CLI default behavior remains exact.
- Exact v1 source tokens are byte-for-byte compatible with rev0968/rev0969.
- `versions\n`, three-field, and four-field local query frames remain accepted
  as exact mode.
- New clients send the canonical mode in a five-field frame and require the v4
  local response.
- This is a local owner-control/status change, not a reconciliation
  wire-protocol generation change.

## Validation

Exact rev0970 source passed the complete GCC 14.2 Debug graph (527/527 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 296 SQLite-owner, 406 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 123 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 260/260 checks. A clean-root Clang 17 Debug product dependency graph completed 238/238 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 406-check folder-owner suite in 18.02 seconds at 1,370,916 KiB peak RSS and the 123-check local-control suite. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0969 parent SHA-256 matched f06573e09238174517eb8cef22fd5df19276665665edcba71cb151527daa1d6b and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 14/14 changed active files and the complete 568-file projection byte-for-byte and by mode. The final active implementation projection contains 568 files / 26,027,982 bytes with SHA-256 4c1be1a1ff28901e0a9d769316dc258a7eceb2ce99794b332c07bf638e380fb8.

## Nonclaims

Rev0970 does not add selective sync, placeholders, remote history transfer,
retention policy, version pins, chronology, conflict browsing, batch restore,
directory restore, quotas, garbage collection, or a page-proportional exact
availability scan. Metadata-only output cannot authorize restore; restore still
re-proves all mutable authorities.
