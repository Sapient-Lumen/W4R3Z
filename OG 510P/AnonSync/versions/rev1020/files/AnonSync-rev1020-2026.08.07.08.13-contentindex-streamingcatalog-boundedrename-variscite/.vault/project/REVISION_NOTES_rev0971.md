# Revision notes — rev0971

## Product move

Rev0971 makes every accepted historical-version page publishable through the
owner-only status channel. A valid `versions --limit 1024` request can no longer
produce an unbounded multi-megabyte inventory that collides with the socket's
1 MiB response cap.

## C++ implementation

- Added one canonical history query/inventory JSON module shared by exact byte
  counting and live/terminal emission.
- Added a non-allocating counting stream buffer and a deterministic largest-
  prefix search.
- Reserved at most 256 KiB for one retained history inventory.
- Preserved the exact operation-ID continuation cursor and source cutpoint when
  the byte frontier omits a suffix.
- Added independent entry-limit and byte-limit stop reasons through `entry_limit_frontier_reached`, `status_byte_limit`, and
  `status_byte_frontier_reached` fields.
- Kept the folder owner's causal entry-count page unchanged; byte bounding is a
  service presentation cutpoint, not synchronization or restore authority.
- Advanced live and terminal status to `anonsync.peer-service.status.v16`.

## Adjacent audit/refactor

The completed history inventory had been serialized twice in one status object:
once as stable `historical_versions.last_inventory` and again inside generic
`last_step`. Rev0971 removes the generic copied inventory while retaining action
generation and typed failure correlation there. Shipping clients already use
the stable history domain, so the change removes waste without adding a second
result protocol.

The byte counter and emitter now share one implementation. This avoids a future
field or escaping change making a counted page larger when it is finally
serialized. The shipping status path uses the stream form directly rather than
allocating a second inventory-sized JSON temporary.

## Compatibility

- CLI and owner-only request/acceptance protocols are unchanged.
- Exact v1 and metadata v2 source cutpoints are unchanged.
- Existing `maximum_entries` behavior remains; byte truncation may return fewer
  entries and is explicitly reported.
- Pagination continues through `next_start_after_operation_id`.
- Reconciliation protocol generation 2 is unchanged.
- Status consumers must accept v16 and the three new inventory fields.

## Validation

Exact rev0971 source passed the clean GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 296 SQLite-owner, 406 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 132 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 267/267 checks. A clean-root Clang 17 Debug product dependency graph completed 239/239 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 406-check folder-owner suite in 18.93 seconds at 1,371,184 KiB peak RSS and the 132-check local-control suite in 0.57 seconds. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0970 parent SHA-256 matched 57cb832afa5b63c3b7ab63028873855ec18c6e2ec90059c7ac7b64200ba2e7d7 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 13/13 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,058,026 bytes with SHA-256 11b2a46a3fc169546819c71172347dc64bb6f05bbca16d58ff5a790d21e239a8.

## Nonclaims

Rev0971 is not retention policy, history garbage collection, chronology,
selective sync, remote history transfer, conflict-copy UX, or a global proof
that future unbounded status fields cannot be introduced. The fixed 1 MiB local
socket validation remains the final envelope guard.
