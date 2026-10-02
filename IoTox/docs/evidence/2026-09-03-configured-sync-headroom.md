# Configured synchronization headroom evidence

- Date: 2026-09-03
- Host: IoTox founding x86_64 Linux machine
- Decision: ADR 0315

## Direct gate

The changed production binary and complete owned registry were rebuilt and run as:

```sh
nix develop --command cmake --build build/gcc-debug -j2 \
  --target iotox_tests iotox
nix develop --command ctest --test-dir build/gcc-debug \
  -R '^iotox\.unit-and-integration$' --output-on-failure
```

Result: the final direct run passed `821/821` in `34.54 s`. The complete 55-entry CTest surface also
passed in `57.43 s`; five unavailable delegated-cgroup host-capability cases were reported as skips.

The final sanitizer gate rebuilt the changed core and passed all 16 owned-registry shards:

```sh
nix develop --command cmake --build build/clang-asan-ubsan -j2 \
  --target iotox_tests
nix develop --command ctest --test-dir build/clang-asan-ubsan \
  -L owned-registry --output-on-failure -j2
```

Result: `16/16` passed in `26.69 s`.

The four added checks cover:

- exact `--config` loading, stable-device-signed automation selection, a nondefault namespace quota,
  and the strict v2 `managed-storage-headroom=ready` result while v1 stays unchanged;
- content-v2 live incoming-staging occupancy, store/staging/object quota arithmetic, current
  filesystem capacity and availability, an over-quota refusal, and refusal of a nonprivate staging
  entry;
- refusal of an uninitialized namespace without creating its transaction directory; and
- a real reconciled writable tree-v2 worktree, its live immutable object graph, incoming partial
  bytes, and conservative same-filesystem projection reserve.

The separately registered production controller-process target passed in `11.11 s` after its
repeated reconnect fixture was extended. That Ratox result is documented separately from this sync
decision because it does not strengthen storage admission.

## Evidence boundary

These checks prove deterministic local parsing, authentication, bounded inventory, quota arithmetic,
and a real filesystem-space observation on the founding host. They do not reserve the observed
space, emulate ENOSPC or read-only remount, establish representative capacity, prove that storage
honors `fsync`, certify content or backup custody, or authorize precious originals as IoTox's sole
recovery path.
