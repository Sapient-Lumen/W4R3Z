# AnonSync rev0976

## Exact transient-namespace retention cutpoint

Rev0976 closes an alias in the deletion-free retention cutpoint without adding
collection authority.

- Added one canonical SHA-256 witness for every staged-prefix, staged-range,
  assembly-residue, and atomic-publication-residue identity observed by a
  complete rooted payload-store scan, including one fixed-width canonical POSIX
  regular-file observation for each exact transient inode.
- Bound the full staged-prefix reservation frontier as well as current physical
  transient bytes.
- Advanced the payload snapshot to domain v4 and the exact deletion-free mark
  to domain v2.
- Exposed the transient namespace digest, entry count, physical bytes, and
  reserved bytes in the retention plan.
- Added explicit payload-store and durable receiver-restart binding claims,
  while keeping active-pass, opened-sender, mutation-batch, and complete
  external-transient-root claims false.
- Advanced live and terminal service status to
  `anonsync.peer-service.status.v21` and the retention-plan acceptance response
  to `anonsync.local-retention-plan.response.v3`.
- Added same-count/same-byte/same-reservation staged-obligation, independent
  reservation-frontier, restart, and publication-residue rename regressions
  proving that stale snapshot and retention cutpoints fail closed.
- Centralized the four canonical transient ordering predicates and reused them
  for both scanner sorting and witness assertions.
- Excluded and removed a stale build whose CMake source authority pointed at a
  divergent rev0976 worktree.

Rev0976 does not add collection authority. The planner remains deletion-free.
Sender descriptors, active passes, in-memory receiver/mutation obligations,
policy, durable mark intent,
collection quarantine, restart revalidation, and unlink authority remain
absent. See
`EXACT_TRANSIENT_NAMESPACE_RETENTION_CUTPOINT_AUDIT_rev0976.md`.

## Validation

Exact rev0976 source passed a fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 601 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 443 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 155 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 320/320 checks. A fresh Clang 17 Debug product dependency graph completed 239/239 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 601-check payload-store suite in 9.26 seconds at 471,604 KiB peak RSS, the 443-check folder-owner suite in 21.26 seconds at 1,435,944 KiB peak RSS, and the 155-check local-control suite in 0.60 seconds at 99,144 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0975 parent SHA-256 matched f702193a48c41b500ded456a901532f18113d183170a86fed4203dcbc0606269 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 15/15 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,404,832 bytes with SHA-256 1e93e8685e695b93153a8a2a4ff05991c67ca5587a11b95f02cf5c95c931a17b. Validation excluded the partially generated unsealed evidence directory, every divergent cache tree, and every interrupted or superseded run.
