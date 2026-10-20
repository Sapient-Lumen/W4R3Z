# Cloudtainer build report — IoTox rev0010

**Date:** 2026-08-14 America/New_York  
**Revision:** rev0010  
**Version:** 0.10.0  
**Codename:** Durable First Word  
**Northstar:** one installed C++20 ratox-successor executable  
**Strongest evidence:** owned implementation compiled under GCC and Clang; exact consumed-ABI peer fixture; one-binary process/restart transaction; sanitizer, race, and bounded fuzz-smoke lanes

## Result

rev0010 moves the first authorized IoTox machine operation from process-local correlation into a signed durable command transaction. The one public executable can reserve a `device.describe` command, commit its exact canonical request before transport, distinguish toxcore queue acceptance from remote application receipt, retain the exact terminal result, replay duplicates without inventing another logical operation, and recover the same sender identity and record after process restart.

The product surface remains exactly:

```text
bin/iotox
```

Internal libraries, exact provider doubles, tests, fuzzers, and preserved research programs remain build/evidence components. They are not additional installed products.

The strongest honest statement for this revision is:

> The owned C++20 product path crosses one capability-gated read-only command through a distinct exact-ABI peer, commits both directional records before their next externally visible step, survives injected toxcore `SENDQ` pressure with byte-identical retry, emits and observes an application `RECEIVED` receipt, retains a canonical terminal result, replays exact duplicates, and proves command identity and evidence continuity after a full one-binary process restart.

This is not yet a genuine Tox-network result. Official source-linked c-toxcore and libsodium did not compile in this cloudtainer because the shell could not resolve the pinned archive hosts. No public bootstrap, NAT, relay, Tor, or I2P path ran.

## Product work completed

### Durable command identity

A command no longer depends on toxcore's process-local friend number or one connection epoch. Its sender-defined identity is:

```text
sender Tox public key
persistent nonzero sender epoch
nonzero sender message id
```

The local journal also includes direction so an incoming command and an outgoing command with the same remote key/epoch/message tuple remain distinct records.

The local sender epoch is created once with operating-system randomness, stored under the stable IoTox device signature, and reused across restart. Retrying a command after local queue pressure, disconnect, or restart reuses the exact canonical frame instead of manufacturing a second operation.

### Signed bounded command store v2

The new private `IOTXCMD2` store retains:

```text
stable-device public key and Ed25519 signature
nonzero journal generation
persistent local sender epoch
canonical incoming and outgoing records
exact request, receipt, and result bytes
operation and terminal outcome
authority principal and ledger-head evidence
independent receipt/result delivery state
send attempts and last local send error
created and nondecreasing updated timestamps
```

Every mutation validates a complete candidate snapshot, increments its generation, writes a private temporary file, synchronizes it, atomically renames it over the live store, synchronizes the parent directory, and only then publishes the candidate in memory. A failed persistence transaction leaves the previous in-memory and on-disk state authoritative.

Load is fail-closed for symlinks, foreign ownership, permissive modes, excessive size/counts, malformed or noncanonical bytes, duplicate locators, invalid transitions, signature failure, and a device principal different from the local stable identity.

The implementation is intentionally bounded at 1,024 records and 8 MiB by default. At the record ceiling it may prune the oldest terminal evidence, but it never discards unfinished work merely to admit another command.

The store is signed plaintext. It does not yet provide confidentiality, old-valid-snapshot rollback detection, hardware monotonicity, incremental append durability, low flash write amplification, or multi-process writer coordination.

### Application receipt and result separation

rev0010 freezes the eight-byte `ICA1` acknowledgement payload. The only emitted stage is:

```text
RECEIVED
```

It means the receiver has durably committed the exact request and exact receipt. It does not mean the principal was admitted, execution started, execution completed, or the result reached the sender.

That preserves three different facts:

```text
toxcore accepted exact bytes into its local queue
remote IoTox committed the exact command and returned RECEIVED
remote IoTox produced a terminal COMMAND_RESULT
```

The receiver commits a valid incoming request before sending its receipt, records authority admission before execution, records start before the handler, and commits the exact terminal result before asking toxcore to send it. An exact duplicate replays frozen evidence. Different bytes reusing one durable key produce conflict and do not rewrite the first record.

### Restart behavior

`device.describe` is explicitly marked read-only and restart-safe. On session recovery, IoTox can:

```text
retry an unfinished outgoing request using its exact stored bytes
resume an unfinished incoming read-only request after current authority admission
resend a pending frozen receipt or terminal result
reconstruct accepted peer-description state from durable evidence
preserve the local sender epoch and journal generation
```

No generic restart rule is granted to future physical operations. Actuators require operation-specific effect reservation, idempotency, cancellation, compensation, expiry, and power-loss contracts.

### One-binary ratox-successor surface

The generic operator entrance is now:

```text
iotox command FRIEND device.describe
```

`device-describe` remains a compatibility alias. The operation registry already records canonical name, feature bit, required capability, read/write class, and restart policy. Only one harmless operation is registered, so the surface is generic while the internal execution mechanics remain partially specialized and are the next extraction target.

Inspection is available through the same executable:

```text
iotox command-store
iotox command-record DIRECTION PEER_PUBLIC_KEY SENDER_EPOCH MESSAGE_ID
iotox peer-description FRIEND
iotox status
```

The private runtime tree projects signed-journal generation, sender epoch, incoming/outgoing/pending counts, and per-peer durable records. The projection is replaceable observation state; it is not the command database and cannot authorize or mutate a command by being edited.

## Exact one-binary fixture

`tests/test_cli_process.cpp` and `tools/run-mock-node.sh` start the actual `iotox run` process and use that same executable for every local operator request. The loadable toxcore ABI fixture is a distinct IoTox endpoint with its own Tox perspective, session nonce, stable Ed25519 principal, persistent sender epoch, command journal, authority challenge/proof behavior, application receipt, terminal result, and audit log.

The fixture crosses:

```text
create Tox savedata, stable device identity, signed owner ledger, and signed command store
accept one peer by public key
recover exact HELLO, CAPABILITIES, authority challenge, and authority proof after injected SENDQ
confirm one canonical session transcript in both directions
prove stable principals in both directions
observe peer device.describe denial before its principal is authorized
admit and execute the same exact request after current authority proof
commit and replay an exact incoming receipt/result
issue local `iotox command ... device.describe`
inject command SENDQ and retry the exact frozen request
observe remote RECEIVED separately from the terminal result
inspect exact 49-byte request/receipt and 121-byte successful result evidence
stop the process cleanly
restart from Tox savedata, stable identity, signed authority ledger, and signed command store
verify Tox address, friend list, profile, device principal, owner ledger, sender epoch, and exact durable command record remain continuous
```

The process test also verifies the install/runtime claim that one binary is both daemon and operator.

## Upstream contract research applied

Primary-source review retained c-toxcore 0.2.23 as the pinned target. Relevant public-header facts applied in this revision are:

- one `Tox*` must be externally synchronized; IoTox continues to serialize it behind one owner thread;
- lossless custom packets are reliable and ordered after acceptance into toxcore's local queue;
- the custom-packet maximum is 1,373 bytes, leaving 1,332 bytes after IoTox's discriminator and frame header;
- `TOX_ERR_FRIEND_CUSTOM_PACKET_SENDQ` means local queue exhaustion, so a rejected send may retry exact bytes while successful queue acceptance is not treated as remote durable admission;
- toxcore file identifiers can persist across restart whereas file numbers are per-friend session coordinates, reinforcing the general rule that process-local transport coordinates are not durable application identity;
- `tox_bootstrap` and explicit TCP relay configuration remain distinct operations, and bootstrap may still attempt UDP even when ordinary UDP operation is disabled; future Tor/I2P route policy therefore requires explicit leak tests rather than a proxy checkbox.

Ratox remains the human-interface inspiration: ordinary files, FIFOs, public-key-first peers, small process, and no mandatory cloud. IoTox places structured bounded control, signed authority, and durable command state beneath that surface rather than pretending a FIFO write is a delivery guarantee.

## Build and verification matrix

The final clean matrix exited successfully on 2026-08-14 in this cloudtainer:

| Lane | Result |
|---|---|
| GCC 14.2 debug | 8/8 CTest entries passed |
| GCC 14.2 release | 8/8 CTest entries passed |
| Clang 17 debug | 8/8 CTest entries passed |
| Clang 17 AddressSanitizer + UndefinedBehaviorSanitizer | 8/8 CTest entries passed |
| GCC 14.2 ThreadSanitizer | 8/8 CTest entries passed |
| Clang 17 libFuzzer | five targets completed 5,000 units each; 25,000 total |
| GCC 14.2 with system-linked `libargon2.so.1` | 8/8 CTest entries passed |
| Mutorr preservation build | 10/10 CTest entries passed |

The five fuzz targets covered the frame, session, local-control, command/receipt, and authority
parsers. None reported a crash or sanitizer finding in the bounded run. The host linker printed
`no .eh_frame_hdr table will be created` for objects from Clang's fuzzer runtime; all five targets
nevertheless linked, executed, and completed their requested units. That line is retained as a
platform warning, not silently removed and not represented as a product failure.

The matrix used CMake 3.31.6 and Ninja 1.12.1. Each ordinary lane ran the separate-process durable
command/restart fixture as part of its registered CTest set; the Mutorr lane additionally preserved
its two incubator checks.

The default suite contains eight CTest entries. Its owned unit/integration executable registers 88 C++ checks. The retained process test crosses the one-binary lifecycle and restart path; the five libFuzzer targets cover outer frames, session records, local-control records, command records/receipts, and authority records.

The release install surface is checked separately and must contain one executable: `bin/iotox`.

## Defects found while constructing rev0010

The matrix was not ceremonial. During the unfinished revision work it exposed and forced correction of at least these implementation/build defects:

1. Clang rejected the first generated embedded RecallRoot word-list representation because one translation-unit string literal exceeded a portable compiler limit. The word list is now emitted in bounded generated pieces while preserving the exact bytes and test vector.
2. The authority fuzzer initially omitted the owned stable-identity implementation from its target closure. The fuzzer target now links the exact production dependencies it exercises rather than relying on incidental linkage from another executable.
3. A separately interrupted release run was isolated at the process binary rather than reported as a program hang. The exact release process fixture completed successfully; the interruption belonged to the command runner, not IoTox.

These corrections are reflected in the final clean matrix rather than hidden as discarded attempts.

## Source-linked standalone attempt

The standalone toolchain pins:

```text
c-toxcore 0.2.23
libsodium 1.0.22
Argon2 reference 20190702
```

The system-linked Argon2 lane can compile and run locally. The complete source-linked product lane could not begin because shell DNS failed while fetching the first pinned archive. The failure is retained as environment evidence only. It is not a successful c-toxcore build and not evidence of two genuine Tox peers.

Prepared external gates remain:

```text
tools/build-standalone.sh
tools/verify-standalone.sh
tools/run-real-peer-smoke.sh
```

The next networked CLI must compile the pinned official headers and sources, launch two source-linked `iotox` processes, cross friendship, transcript confirmation, stable-principal proof, durable COMMAND/ACK/RESULT, disconnect/reconnect, restart, and a TCP-relay path, then correct real API or timing defects in this architecture.

## Current evidence boundary

Established in this cloudtainer:

```text
one C++20 product executable
GCC and Clang warning-clean compilation
exact consumed c-toxcore ABI provider boundary
one serialized toxcore owner thread
canonical protocol/session/authority/command codecs
signed stable identity and authority ledger
signed bounded durable command store
commit-before-send and commit-before-result order
application RECEIVED receipt
exact duplicate replay and conflicting-key rejection
injected SENDQ recovery
one-binary separate-process lifecycle and restart
sanitizer/race lanes and bounded parser fuzz smoke
ratox-style read projections and generic CLI command entrance
```

Not established here:

```text
official source-linked c-toxcore or libsodium build
two genuine Tox peers or public network behavior
NAT traversal, TCP relay, Tor, or I2P route
rollback-resistant or encrypted command storage
trusted-clock expiry or cancellation
safe mutable setting, actuator, GPIO, firmware, or OTA effect
physical-power-failure validation on target storage
independent security audit or production readiness
```

## Next executable work

The current behavior is strong enough to extract rather than redesign. The next product steps are:

1. move outgoing reservation/retry/result and incoming admission/replay mechanics from `agent.cpp` into one reusable durable command engine;
2. keep the operation registry as the policy boundary for capability, read/write class, restart, expiry, and idempotency;
3. add the ratox-style FIFO/filesystem write adapter over the same structured local operation and same signed journal, with bounded framing and explicit abandoned-writer/backpressure behavior;
4. cross the exact path between two official source-linked c-toxcore nodes before adding a mutable device operation;
5. only then design a harmless durable settings operation with explicit crash/retry semantics.

## Decision

Keep Tox. Keep one product binary. Keep ratox's ordinary Unix feeling. Make IoTox own the durable semantics above the network:

```text
commit before transport or effect
stable command identity
independent signed authority
truthful application receipts
exact replay
restart recovery
operator-visible evidence
no vendor sovereign
```

rev0010 is the first revision in which the authorized machine operation is no longer merely a live request. It has a durable first word.
