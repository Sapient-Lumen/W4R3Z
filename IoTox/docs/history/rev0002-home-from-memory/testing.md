# Testing strategy

## rev0002 facilities

The project uses no external C++ test framework. A small registry and assertion harness keeps the build self-contained and runnable in a minimal container.

Two shared-library boundary doubles are built entirely from C++:

```text
libtoxcore-iotox-mock.so
libargon2-iotox-mock.so
```

Neither is a production implementation. They exist to exercise exact C ABI calls, symbol loading, error paths, and parameter contracts under GCC, Clang, and sanitizers.

## Toxcore boundary test

The toxcore mock exercises:

- runtime symbol loading;
- reported version validation;
- options allocation and savedata loading;
- instance lifecycle;
- callback registration;
- the iteration loop;
- explicit friend acceptance;
- lossless packet send and callback receipt;
- savedata snapshot and reload.

The mock echoes sent lossless packets on the next iteration, giving the C++ owner thread and event queues a deterministic integration path.

## RecallRoot-v1 boundary test

The Argon2 mock rejects any context that differs from the frozen contract:

- Argon2id context call;
- version 19;
- 65,536 KiB memory;
- three iterations;
- four lanes and threads;
- fixed 16-byte salt;
- 32-byte output;
- no secret or associated-data inputs;
- password-clear flag enabled;
- expected canonical public test phrase.

It then returns a deterministic noncryptographic byte pattern so the unit suite can verify the boundary without pretending that the mock implements Argon2.

A separate CTest loads the real system `libargon2.so.1` and verifies the retained public known-answer output. This ensures the actual algorithm implementation and the C++ contract agree in this container.

## Word-list tests

The C++ loader verifies:

- exactly 7,776 lines;
- ordered five-dice codes from `11111` through `66666`;
- one tab separator per line;
- unique words;
- restricted lowercase ASCII/hyphen syntax;
- representative first, hyphenated, and final entries.

Package checksums retain the exact SHA-256 digest. The parser additionally tests case/whitespace canonicalization, exact eight-word count, foreign-word rejection, malformed punctuation rejection, and non-ASCII rejection.

## Compiler matrix

rev0002 targets:

```text
GCC debug, strict warnings
Clang debug, strict warnings
Clang debug with AddressSanitizer and UndefinedBehaviorSanitizer
GCC debug with ThreadSanitizer
GCC release
```

ThreadSanitizer runs separately from ASan/UBSan. The container's Swift-flavoured Clang 17 ThreadSanitizer runtime cannot link because it expects libdispatch/Blocks symbols, so the verified TSan lane uses GCC 14.

## Why mocks use exact ABI types

An early rev0001 toxcore mock used independently declared namespaced opaque struct names. Ordinary builds happened to work, but UBSan correctly reported that the C++ function-pointer type did not exactly match the exported function definition.

Both external boundaries now use official headers when available and exact global fallback declarations otherwise. Their C++ mocks force the fallback and export matching global functions. The standard is not merely “the representation looks compatible”; sanitizer-visible C++ function types must be exact.

## Current CTest layers

The ordinary CTest run includes:

1. the registered unit/integration runner with both ABI mocks;
2. CLI network/status smoke;
3. recovery-contract metadata smoke;
4. real Argon2 known-answer derivation.

The detailed C++ runner includes the original nine tests plus three recovery tests in rev0002.

## Next test layers

### Real toxcore ABI test

Build a pinned c-toxcore revision and run the same lifecycle against it. Compile an ABI-verification translation unit against official headers.

### Two-node local test

Run two real Tox instances in an isolated fixture, exchange identities, add each other, send IoTox `HELLO` frames, and verify persisted restart behavior.

### Memory re-entry test

Derive a deterministic Tox controller identity under a reviewed domain-separated KDF. Remove the controller friend list and ordinary savedata, recreate it from the recall phrase, and test whether a previously owned device can reintroduce itself without vendor inventory.

### Bootstrap and relay test

Use controlled bootstrap/TCP-relay services. Verify native UDP, TCP-only fallback, reconnect, node rotation, and owner-operated server deployment without depending on the public network.

### Fault injection

Inject short writes, `fsync` failures, rename failures, invalid savedata, missing symbols, wrong library versions, event-queue saturation, command timeout, callback bursts, Argon2 allocation failure, malformed word lists, and shutdown during queued work.

### Protocol fuzzing

The current fuzzer targets only the fixed frame decoder. The decoder translation unit is compiled directly into the fuzz executable with `-fsanitize=fuzzer,address,undefined`; linking the ordinary uninstrumented static core would exercise the harness while giving misleadingly low decoder coverage. rev0002 found and corrected exactly that test-facility failure.

Future targets should cover CBOR payloads, durable queue records, claim messages, recovery knocks, ownership transitions, manifests, and file-transfer state machines.

### Long-running tests

Exercise days-long idle operation, repeated network loss, suspend/resume, full disk, clock rollback, thousands of identity saves, and repeated memory-root re-entry.

## Definition of “works”

A feature is not complete because an option can be set or a key can be derived.

- Tox/native reaches `network-verified` only after real bootstrap, peer exchange, reconnect, and persisted restart tests.
- Tox/Tor or Tox/I2P reaches `route-verified` only after tests prove bootstrap, peer connection, reconnect, and no forbidden DNS/native fallback.
- Memory re-entry reaches `re-entry-verified` only when a newly reconstructed controller rediscovers and authenticates real previously paired devices.
