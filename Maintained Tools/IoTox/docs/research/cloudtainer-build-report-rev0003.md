# rev0003 cloud-container build report

**Revision:** rev0003  
**Version:** 0.3.0  
**Codename:** Small Circles, One Home  
**Date:** 2026-08-13  
**Language boundary:** C++20 for all IoTox-owned implementation, tests, mocks, fuzzers,
simulations, and benchmarks

## Input branch

rev0003 reviewed and absorbed the user-supplied Milehigh archive:

```text
IoToxmutorr-rev0002-2026.08.13.11.41-cpp20-small-circles-rendezvous-mutorr-cube(1).zip
SHA-256: 3e0406bf91ca1afaf2437463a39e0eac3398e75191b6108d3c1df34a973b1d7d
```

The original documents and text reports are retained under history. IoTox remains the
product; `iotox::mutorr` is an optional namespace replication subsystem.

## Build matrix

The retained matrix passed all six configured CTest commands in each lane:

```text
GCC 14.2.0 debug                  6 / 6 passed
Clang 17.0.0 debug               6 / 6 passed
Clang 17.0.0 ASan + UBSan        6 / 6 passed
GCC 14.2.0 ThreadSanitizer       6 / 6 passed
GCC 14.2.0 release               6 / 6 passed
```

The detailed compiled C++ runner reports 25 tests and zero failures.

## Defect found during the matrix

A Clang debug run exposed a real startup publication race in the Tox owner-thread
boundary. Initialization succeeded and the startup promise was fulfilled before the
worker stored `running=true`. A caller waking immediately from `start()` could then see
“transport is not running” from `accept_friend()`.

The worker now publishes the running state before fulfilling successful startup. The
integration test explicitly asserts that a successful `start()` already implies
`running()` on both first creation and savedata reload. The full matrix passed after the
fix.

This was a concurrency contract defect even though ordinary earlier runs usually hid
it. It is retained here because failures found by the test facility are stronger
evidence than an uninterrupted green log.

## Fuzz smoke

Clang libFuzzer with AddressSanitizer and UndefinedBehaviorSanitizer completed:

```text
IoTox outer-frame decoder:       5,000 runs, no crash
Mutorr mutable-head decoder:     5,000 runs, no crash
```

The retained corpora contain valid, truncated, malformed, and boundary-sized records.
This is a smoke run, not a security proof.

## Functional evidence

- deterministic thirty-member Cube: sixty undirected edges, degree four, diameter eight;
- deterministic preferred-custodian selection with a three-replica default;
- fixed 221-byte mutable head fits in one IoTox lossless control frame;
- RecallRoot-v1 exact C ABI mock and real Argon2 known-answer pass;
- mock toxcore identity persists across restart with mode-0600 state;
- reserved Tox/Tor route exits explicitly instead of silently falling back to native;
- Tox owner-thread lifecycle, friend acceptance, packet echo, callbacks, and save/reload
  pass through the exact consumed mock ABI.

## What is not proven

The container has no real c-toxcore shared library. rev0003 therefore does not claim:

- a controlled two-real-peer test;
- public bootstrap, DHT, NAT traversal, or TCP relay behavior;
- real Tox file transfer;
- live RecallRoot re-entry or authorization;
- live Mutorr gossip, object replication, signatures, encryption, or repair;
- Tox-over-Tor or Tox-over-I2P operation;
- target-device memory, power, flash, thermal, or long-duration reliability.

The next decisive transport gate remains a pinned c-toxcore build using official headers
and a controlled two-peer native fixture. The next decisive Mutorr gate is a deterministic
failure simulator with membership epochs, bounded queues, deduplication, object custody,
and repair metrics.
