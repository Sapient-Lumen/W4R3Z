# Sync open-descriptor source mutation evidence

- Date: 2026-09-03
- Host: IoTox founding x86_64 machine
- Decision: ADR 0328
- Status: accepted direct gate

## Direct gate

The added owned test is:

```text
tree-v2 store rejects source mutation through an open descriptor
```

It covers the exact scan/store race: a file is scanned at one digest, rewritten through a writer file
descriptor that was opened before the scan, then submitted to CAS installation using the stale scan.
IoTox must reject the store, expose no digest-named object, remove `.install.tmp`, and accept a fresh
rescan of the new bytes.

Accepted validation:

```sh
cmake --build build/gcc-debug -j2 --target iotox_tests
cmake --build build/witness-clang -j2 --target iotox_tests
nix develop --command ctest --test-dir build/gcc-debug -R '^iotox\.unit-and-integration$' --output-on-failure
nix develop --command ctest --test-dir build/witness-clang -R '^iotox\.unit-and-integration$' --output-on-failure
nix develop --command bash -lc 'set -o pipefail; ./build/gcc-debug/iotox_tests --mock-toxcore ./build/gcc-debug/libtoxcore-iotox-mock.so --mock-argon2 ./build/gcc-debug/libargon2-iotox-mock.so --wordlist third_party/eff_large_wordlist_2016-07-18.txt | tail -n 8'
```

Results:

- GCC unit/integration CTest: 832/832 passed in 32.87 seconds.
- Clang witness unit/integration CTest: passed in 31.81 seconds.
- Direct GCC registry count under the Nix development environment: `tests=832 selected=832 shard=0/1 failures=0`.

## Evidence boundary

This is a deterministic source-tree regression gate, not a physical or virtual power-cut campaign.
It proves that stale post-scan source bytes cannot become an immutable CAS object through the normal
store path. It does not prove projection-exchange descriptor behavior, descriptor writes across
read-only remounts, kernel crash durability, corrupt-record recovery, or backup independence.
