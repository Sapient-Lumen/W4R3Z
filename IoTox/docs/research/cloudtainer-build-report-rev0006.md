# Cloudtainer build report — IoTox rev0006

**Date:** 2026-08-13 America/New_York  
**Revision:** rev0006  
**Version:** 0.6.0  
**Codename:** One Binary Speaks  
**Evidence class:** C++20 compilation, exact mock-ABI execution, and one-binary process execution  
**Northstar:** a standalone-capable modern ratox successor

## Result

rev0006 advances the public `iotox` executable from a packet/file transport shell into a
usable Tox client surface while preserving a separate IoTox device-protocol lane.

The one executable now provides:

```text
iotox run                         own toxcore, state, runtime surface, and local IPC
iotox profile                     inspect self presentation state
iotox profile name ...            set byte-preserving Tox nickname
iotox profile status-message ...  set byte-preserving status message
iotox profile status ...          set available / away / busy
iotox text ...                    send normal Tox text
iotox action ...                  send Tox action text
iotox typing ...                  publish local typing state
iotox peer-messages ...           read a peer's private text/receipt journal
iotox peer-watch ...              follow that journal
iotox hello ...                   send a structured IoTox HELLO frame
iotox peer-protocol ...           read decoded IoTox frame records
iotox peer-protocol-watch ...     follow decoded frame records
iotox file-send / file-receive    finite native Tox file transfer
```

Every existing-peer command accepts the peer's 32-byte Tox public key as the preferred
stable handle. A toxcore friend number remains a local-process convenience, not an operator
identity.

## What was implemented

### Current c-toxcore presentation and text boundary

The narrow ABI table now consumes the c-toxcore 0.2.23 functions and callbacks needed for:

- runtime maximum name, status-message, and message lengths;
- self name, status message, presence, and typing state;
- friend name, status message, presence, and typing state;
- normal and action text;
- per-friend message identifiers and read receipts.

The implementation keeps all calls on the existing single toxcore owner thread. No product
service calls c-toxcore directly.

### Human lane versus device-protocol lane

rev0006 freezes two distinct uses of Tox:

```text
Tox profile and normal/action text   human and ratox-compatible presentation lane
IoTox lossless custom packets        structured device protocol lane
```

Friendship, text, typing, and a Tox receipt do not grant or prove IoTox authorization. A
receipt means that toxcore reports delivery of a Tox text message to that friend; it is not
hardware execution, durable command acceptance, or business completion.

### Byte-preserving one-binary Unix input

Name, status-message, and normal/action text support exact standard-input forms. This lets a
shell pipeline carry bytes including NUL and newline without placing them in argv. Hex forms
are also available. Input is bounded before allocation or local-protocol encoding.

Writable ratox-style FIFOs remain future compatibility surfaces. They will translate into
the structured local request protocol rather than becoming an uncorrelated command system.

### Private peer journals

The runtime tree now has distinct bounded journals under each public-key peer directory:

```text
messages           outgoing/incoming Tox text and receipts
messages.previous  one rotated segment
protocol           valid outgoing/incoming IoTox frames
protocol.previous  one rotated segment
```

Records are owner-only and one-line escaped. The global event journal deliberately records
metadata and payload lengths without copying human text or protocol bodies.

Outgoing IoTox frames are journaled only after toxcore accepts them for queueing. Incoming
packets beginning with the IoTox packet discriminator are strictly decoded before they are
journaled. A malformed candidate creates a diagnostic rather than an apparently valid
protocol record.

### Exact mock expansion

The loadable C++ mock preserves the exact consumed C ABI and now models profile persistence,
friend presentation callbacks, normal/action echo, typing mutation, message IDs, and
receipts in addition to the existing lifecycle, friendship, savedata, lossless-packet, and
finite-file paths.

It remains a deterministic adapter fixture. It does not implement Tox cryptography, DHT,
NAT traversal, relay routing, congestion, or hostile network timing.

## Process evidence

The separate process fixture forks the actual `iotox run` executable and drives it with
other invocations of that same binary. The retained path verifies:

1. creation of a private runtime and persistent Tox identity;
2. peer acceptance and public-key projection;
3. profile mutation from stdin and restart persistence;
4. normal/action text containing NUL and newline;
5. outgoing, echoed incoming, and receipt journal records;
6. typing mutation;
7. HELLO encode, queue, callback echo, strict decode, and protocol journals;
8. one-binary read and follow commands for both journal classes;
9. file send, receive, cancel, and peer removal by public-key selector;
10. clean shutdown, savedata reload, address continuity, and friend continuity.

This is product-process evidence over the exact mock ABI, not real-network evidence.

## Final retained matrix

```text
GCC 14 debug                         build=pass  CTest=7/7
GCC 14 release                       build=pass  CTest=7/7
Clang 17 debug                       build=pass  CTest=7/7
Clang 17 ASan + UBSan                build=pass  CTest=7/7
GCC 14 ThreadSanitizer               build=pass  CTest=7/7
Mutorr preservation                  build=pass  CTest=9/9
Clang frame libFuzzer                build=pass  smoke=5000 runs
Clang local-control libFuzzer        build=pass  smoke=5000 runs
registered default C++ checks        48, failures=0
registered preservation checks       61, failures=0
public product executables           1 (`iotox`)
```

An initial all-lanes invocation with unconstrained parallelism exceeded the cloudtainer
command window during compilation. Each lane was then completed with bounded parallelism.
The per-lane retained logs are authoritative.

## Reliability finding in final rerun

A deliberately loaded preservation rerun exposed a timing weakness in one end-to-end
assertion. The assertion allowed only two seconds for all of these steps:

```text
local request -> owner-thread c-toxcore call -> mock callback -> bounded transport queue
-> agent event pump -> private runtime journal -> observing test
```

The complete path was not proven broken; the observer could expire before the disk-backed
projection became visible. The test now permits ten seconds on slow or instrumented builders
while preserving the same eventual-path requirement. Every compiler and sanitizer lane
passes afterward.

This is not a claim that ten seconds is acceptable product latency. It records an
implementation pressure: transient runtime projection and event batching should be measured
and optimized independently of durable savedata and durable future command acceptance.

The final operator rehearsal also found that `tools/run-mock-node.sh` configured its source
by absolute path but invoked a build preset relative to the caller's working directory. It
now builds the configured directory by absolute path and passes when started from `/`.

## Research reconciliation

The implementation was checked against primary sources for c-toxcore 0.2.23 and ratox. The
review reinforces these choices:

- serialize all access to one `Tox` instance;
- obtain runtime size limits through the public API;
- keep public keys stable and friend numbers local;
- preserve normal/action text as useful human behavior;
- interpret receipts narrowly;
- use lossless custom packets for bounded IoTox control frames;
- preserve ratox's ordinary Unix composability without inheriting FIFO ambiguity as the core
  protocol.

## Important boundary

No real c-toxcore source tree or library was available in this container. Shell DNS could
not resolve the upstream host for normal command-line fetch/build work. Accordingly rev0006
does not prove:

- official-header or official-target compilation;
- real Tox cryptographic sessions;
- public bootstrap or DHT convergence;
- NAT traversal;
- TCP relay behavior;
- real message receipts or file timing;
- reconnect and offline behavior;
- Tor-routed Tox or I2P-routed Tox;
- target-device resource fitness.

The strongest honest labels are **mock-ABI-tested** and **process-tested**. Tox/native remains
implementation-forward but not real-peer-tested.

## Next construction gates

The next office holder should continue writing product code rather than pausing at the test
boundary. In priority order:

1. compile the same provider against pinned official c-toxcore source and headers;
2. run two genuine local peers through controlled bootstrap and TCP-relay fixtures;
3. implement incoming friend-request accept/reject commands in the public CLI;
4. add the independent authorization ledger above friendship;
5. freeze signed command/result/ack semantics, deadlines, replay, and idempotency;
6. add durable bounded inbox/outbox storage;
7. expose a ratox-compatible FIFO façade over structured local requests;
8. measure and batch transient runtime projection without weakening saved identity durability;
9. add signed OTA and diagnostic bundle flows over Tox file transfer;
10. test native Tox on the first named hardware and network classes before route expansion.
