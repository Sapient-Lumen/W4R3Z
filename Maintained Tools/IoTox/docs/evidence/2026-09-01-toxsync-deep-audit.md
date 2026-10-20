# toxsync deep audit — 2026-09-01

## Scope

This pass reviewed the complete independently buildable `components/toxsync` 0.7.0 tree: public
headers, all 21 library translation units, CLI, native tests/fuzzers/benchmarks, CMake/Nix packaging,
security/architecture documentation, and the exact source subset embedded by current IoTox. It did
not treat the historical IoToxsync daemon as current product code.

The key architecture finding is a healthy separation, now written down explicitly: IoTox directly
compiles hash/index/planner/apply, treepack, content-store/paged-fabric, multisource, and range-source
primitives, but owns the production device-signed HEAD, authority-ledger v3 policy, durable attempt
and FileId state, epochs, quota/retention truth, activation, transport records, and route policy. The
standalone component signer, wire records, publication convenience transaction, pin journal, and CLI
remain useful laboratory/reference surfaces and do not create a second IoTox trust root.

## Findings closed

1. Re-adding an existing offline `ContentScheduler` source set it online without restoring the
   `online_sources` statistic. The transition now increments exactly once; a new regression covers
   offline, re-add, hint update, and idempotent repeat.
2. Retained publication inputs were moved individually into their final revision directory. A crash
   after that directory existed but before HEAD-last completion made an exact retry fail. Publication
   now assembles one private retained directory, optionally synchronizes it, atomically renames it,
   and validates exact entries, types, sizes, and signed-HEAD SHA-256 identities on both first use and
   retry. Exact retry and corrupt-retained-negative tests were added.
3. Standalone `head-keygen` could overwrite an existing key and could leave a private half if public
   output failed. Unix outputs now use `O_EXCL|O_NOFOLLOW`, complete-write handling, exact descriptor
   permissions, and partial-pair rollback. The CLI transaction proves no replacement and rollback.
4. Two tests overstated their coverage: a content-fabric fixture omitted its staging parent, and the
   publication sort budget no longer forced an external spill for the current path fixture. Both now
   construct the state their names require.
5. Test temporary directories used predictable process-local names. They now use exclusive creation,
   a monotonic/atomic sequence plus entropy, and owner-only permissions.
6. CTest previously checked only the native binary and CLI version. A durable command transaction now
   proves range index/sync/verify plus paged content build/scan/reconstruct in every crypto lane. The
   OpenSSL lane additionally proves signed HEAD/key/publication/activation/pin/GC behavior. The
   portable builtin-SHA lane does not skip core CLI behavior merely because Ed25519 is intentionally
   absent.
7. The component architecture, Nix, integration, and Ratox/SSH documents contained historical
   statements that no longer described the current embedding or test boundary. They now distinguish
   founding history, standalone component behavior, current product ownership, and explicit
   nonclaims.

No wire or on-disk format changed. The component remains 0.7.0 with an unreleased hardening section;
range-v1 and flat/paged content-v2 compatibility are preserved.

## Qualification result

The final post-change source matrix used the pinned Nix environment: GCC 15.3.0, Clang 21.1.8,
CMake 4.3.4, Ninja 1.13.2, and OpenSSL 3.6.3.

| Lane | Result |
|---|---|
| GCC Debug, OpenSSL/SSE2, warnings fatal | 125/125 native; 3/3 CTest routes |
| GCC Release, OpenSSL/SSE2/LTO, warnings fatal | 125/125 native; 3/3 CTest routes |
| GCC portable Release, builtin C++ SHA/scalar/LTO | 125/125 registered; 3/3 routes, signed cases intentionally unavailable |
| Clang Debug, OpenSSL/SSE2, warnings fatal | 125/125 native; 3/3 CTest routes |
| Clang ASan + UBSan + leak detection | 125/125 native; 3/3 CTest routes |
| Clang TSan | 125/125 native; 3/3 CTest routes |
| Clang static analyzer over library and CLI translation units | no findings |
| Nix `path:` package build with `doCheck` | pass |
| libFuzzer wire / metadata / filesystem decoders | 10,000 final post-change runs each, no crash |

The reusable command is:

```sh
nix develop ./components/toxsync --command env \
  IOTOX_MATRIX_JOBS=4 IOTOX_MATRIX_CLEAN=1 TOXSYNC_FUZZ_RUNS=10000 \
  ./tools/build-toxsync-matrix.sh
```

The matrix now includes the TSan preset. Uncommitted package tests must use a path flake so the new
untracked files are not omitted by Git-backed source filtering:

```sh
nix build path:./components/toxsync#toxsync
```

## Remaining nonclaims

- This is not an independent cryptographic or filesystem audit.
- The standalone library matrix does not prove Tox transport, namespace authorization, or IoTox
  multi-node convergence; IoTox-owned deterministic tests and retained Sandwurm evidence own those
  claims.
- This pass did not inject real power loss at every publication/activation/pin/GC synchronization
  boundary or qualify every filesystem and target architecture.
- The non-POSIX CLI fallback cannot offer the same kernel-enforced two-path no-clobber guarantee as
  the audited Unix path.
- Content is integrity-protected, not confidential at rest; metadata completeness and automatic
  conflict merging remain outside the standalone component.
- Conservative GC still requires an embedding-owned retention witness/policy. IoTox deliberately
  does not expose the standalone pin journal as product authority.
