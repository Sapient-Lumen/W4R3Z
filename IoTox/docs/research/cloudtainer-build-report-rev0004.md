# Cloudtainer build report — rev0004

## Scope

This report records the rev0004 ratox-successor code built and exercised in the
provided Linux cloud container. Raw outputs and convenience binaries are retained under
`artifacts/`; this prose is an index, not a replacement for evidence.

## Environment observed

- x86-64 Linux container;
- GCC 14.2.0;
- Clang 17.0.0;
- CMake and Ninja;
- Linux Unix `SOCK_SEQPACKET`, `SO_PEERCRED`, `eventfd`, `dlopen`, `fsync`, process,
  ownership, and mode APIs.

Exact tool and kernel output is retained in `artifacts/reports/build-info.txt`.

## Buildable product slice

The default C++20 build now produces:

- `iotox_core`, the ratox-successor core library;
- `iotoxd`, a foreground device agent;
- `iotox`, a same-user control client;
- exact loadable c-toxcore and Argon2 ABI mocks;
- a 25-test C++ runner;
- a separate daemon/client process-lifecycle fixture;
- over-Tox frame and local-control fuzz targets.

Mutorr remains buildable only through explicit incubator options and is absent from the
default product, CLI, tests, and current artifact set.

## Checked lanes

The final matrix passed:

```text
GCC 14 debug                     7/7 CTest
GCC 14 release                   7/7 CTest
Clang 17 debug                   7/7 CTest
Clang 17 ASan + UBSan            7/7 CTest
GCC 14 TSan                      7/7 CTest
Mutorr preservation build        9/9 CTest, explicit opt-in
```

Both active decoder fuzz targets completed retained 100,000-run Clang
libFuzzer+ASan+UBSan smoke campaigns without a crash:

```text
iotox_frame_fuzzer               100,000 runs
iotox_local_control_fuzzer       100,000 runs
```

The separate binary fixture starts the actual `iotoxd`, controls it through the actual
`iotox` process, configures mock bootstrap and relay endpoints, adds a transport peer,
sends a HELLO frame, verifies metadata-only diagnostics, shuts down over local IPC,
restarts from savedata, and confirms address continuity.

## Defects found and corrected

The facility found two rev0004 defects before packaging:

1. Clang rejected an option-parser loop whose index could advance in two places. The
   parser was rewritten as a single-step `while` loop, making consumption rules
   explicit.
2. The operator mock-lifecycle script sent a packet and stopped immediately. The daemon
   was correct, but the script raced the next toxcore iteration and could inspect the
   event journal too early. The script now waits with a bounded liveness check for the
   packet event before shutdown.

The new tests also enforce:

- refusal to remove a regular file occupying the control-socket path;
- denial when peer credentials cannot be authenticated;
- metadata-only packet event logging;
- bracketed IPv6 and strict bootstrap/relay endpoint syntax;
- identity continuity across separate daemon processes;
- fail-closed reserved routes;
- one ordinary archive entrance.

## External-source limitation

No real c-toxcore source or binary was retrieved, built, bundled, or executed in this
container. The adapter targets the official 0.2.23 ABI surface and passes against an
exact loadable C++ test double. That is meaningful IoTox evidence but not Tox-network
evidence.

The retained maturity statement is:

```text
local daemon/client architecture             binary-verified
local control protocol and filesystem tree   unit/binary-verified
c-toxcore ABI boundary                        adapter-verified
Tox/native with real c-toxcore                not verified
real bootstrap, DHT, NAT, and relay behavior  not verified
Tox/Tor and Tox/I2P routes                    reserved; fail closed
```

## Evidence map

Important raw records:

```text
artifacts/reports/build-matrix.log
artifacts/reports/*-ctest.log
artifacts/reports/unit-tests-detail.log
artifacts/reports/binary-process-lifecycle.log
artifacts/reports/mock-node-lifecycle.log
artifacts/reports/fuzzer-smoke.log
artifacts/reports/negative-and-layout.log
artifacts/reports/runtime-dependencies.txt
artifacts/reports/mock-exported-symbols.txt
artifacts/reports/real-toxcore-status.txt
artifacts/reports/checksum-verification.log
artifacts/reports/prebuilt-smoke.log
```
