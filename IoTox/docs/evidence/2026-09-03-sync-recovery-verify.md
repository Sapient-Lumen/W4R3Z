# Independent synchronization restore verification evidence

- Date: 2026-09-03
- Host: IoTox founding x86_64 Linux machine
- Decision: ADR 0319

## Direct gate

The changed production binary and complete owned registry were rebuilt and run as:

```sh
nix develop --command cmake --build build/gcc-debug -j2 \
  --target iotox_tests iotox
nix develop --command ctest --test-dir build/gcc-debug \
  -R '^iotox\.unit-and-integration$' --output-on-failure
```

Result: `831/831` passed in `37.27 s`.

The four new checks cover:

- an exact nested ordinary restore with file content plus private owner mode preserved;
- a canonical-manifest mismatch when bytes and mode differ;
- canonical alias, containment, and unresolved `.iotox-conflicts` refusal; and
- the public command's strict match result, byte counts, no-live-state fact, and explicit
  no-independence claim.

The implementation canonicalizes both roots, rejects overlap or inode aliasing, applies the ADR
0318 filesystem contract, alternates two scans of each tree, rechecks the contract, and compares the
complete canonical owner-mode-v2 manifests rather than trusting digest equality alone.

## Complete host gates

The complete GCC surface passed `55/55` in `54.82 s`. The changed code was separately rebuilt under
Clang ASan/UBSan and its complete surface passed `70/70` in `64.01 s`:

```sh
nix develop --command ctest --test-dir build/gcc-debug \
  --output-on-failure -j2
nix develop --command cmake --build build/clang-asan-ubsan -j2 \
  --target iotox_tests iotox
nix develop --command ctest --test-dir build/clang-asan-ubsan \
  --output-on-failure -j2
```

Both complete surfaces retain only the five explicit unavailable delegated-cgroup/PSI skips.

## Evidence boundary

This is same-host source and filesystem evidence. It proves bounded deterministic comparison of two
operator-supplied disjoint trees and no dependence on IoTox live state. It does not prove that the
backup has an independent disk, administrator, authority, version history, immutable retention, or
correct provenance. The alternating scans are not one atomic cross-filesystem snapshot. No
Sandwurm node-loss/reseed ceremony, backup product, physical storage, `fsync` truth, or precious-data
recommendation is qualified here.
