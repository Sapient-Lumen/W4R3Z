# IoTox architecture

## Design center

IoTox is a headless, self-owned device agent. Tox is the first peer transport and connection substrate. Local applications, hardware drivers, recovery flows, and future user interfaces should not call c-toxcore or Argon2 directly.

```text
remembered / printed recall phrase
                  |
          RecallRoot-v1 adapter             [implemented testbed]
                  |
      domain-separated owner hierarchy      [planned]
                  |
       ownership + authorization ledger      [planned]
                  |
sensors / actuators / local applications
                  |
       structured Unix-domain API            [planned]
       SOCK_SEQPACKET or framed stream
                  |
        +---------------------------+
        |           IoTox           |
        |                           |
        | device identity           |       [planned]
        | ownership epochs          |       [planned]
        | roles and capabilities    |       [planned]
        | protocol codec            |       [seeded]
        | durable inbox/outbox      |       [planned]
        | state synchronization     |       [planned]
        | transfer / OTA manager    |       [planned]
        | identity state store      |       [seeded]
        | audit / metrics           |       [planned]
        +-------------+-------------+
                      |
              bounded commands               [planned]
                      |
           one Tox owner thread               [implemented]
                      |
         c-toxcore runtime adapter            [adapter-verified]
                      |
      lossless packets / file transfer
                      |
                 Tox network                  [not yet network-verified]

optional compatibility surfaces:
  - ratox-style files and FIFOs               [planned]
  - command-line client                       [seeded]
  - local web/mobile bridge                   [planned]

reserved Tox routes:
  - native                                    [adapter-verified]
  - Tor                                       [reserved]
  - I2P                                       [reserved]
```

## Root of ownership versus routes

IoTox now distinguishes four concepts that must not collapse into one key:

```text
Recall root
    reproduces owner-side authority from memory

Application owner identity
    signs delegation, ownership transitions, and route bindings

Device identity
    identifies the physical/logical device across endpoint changes

Transport endpoint identity
    Tox/native, Tox/Tor, Tox/I2P, or future direct transport keys
```

Tox remains responsible for authenticated encrypted peer sessions and reachability. IoTox remains responsible for deciding whether a message is authorized to operate a physical device.

## RecallRoot-v1 boundary

The recovery adapter dynamically loads the reference-compatible Argon2 C ABI and invokes `argon2id_ctx` with a frozen versioned context. This keeps the algorithm implementation outside IoTox while making every parameter visible and testable.

The product code accepts only a `RecallPhrase` that has passed:

- exact eight-word count;
- canonical ASCII normalization;
- membership in the pinned 7,776-entry list.

The current code is a derivation testbed, not a production phrase-entry facility. Callers can still leave copies in terminal, UI, string, allocator, swap, or crash-dump memory. A secure owner-controller application must provide a stronger input and memory boundary.

The next hierarchy should domain-separate at least:

```text
owner application signing
native Tox secret key
native Tox no-spam
Tor Tox secret key
Tor Tox no-spam
I2P Tox secret key
I2P Tox no-spam
local encrypted storage
recovery/device certificate wrapping
```

The exact KDF and contexts are deliberately not frozen in rev0002.

## The owner-thread rule

No IoTox module outside the toxcore adapter may call a toxcore API. A `ToxTransport` owns a worker thread, the loaded library, and the `Tox*`. Public calls enqueue work and wait for a typed result. Callbacks execute on the owner thread and are copied into an event queue before consumers see them.

This rule is stricter than merely placing a mutex around toxcore. It provides one place to reason about callback reentrancy, savedata snapshots, shutdown order, and future bounded command queues.

The current queues are still provisional and unbounded. Before hardware-affecting commands use them, queued operations need explicit IDs, deadlines, cancellation, bounded capacity, backpressure, and shutdown semantics that prohibit a timed-out command from executing unexpectedly later.

## c-toxcore runtime adapter

The adapter loads a shared library with `dlopen`, resolves only the symbols needed by the current revision, and validates the reported version. rev0002 targets the 0.2 ABI line at patch 23 or later.

The consumed surface remains intentionally small:

- library version;
- options allocation, release, native UDP/local-discovery settings, and savedata loading;
- instance creation and destruction;
- savedata snapshot;
- iteration interval and iteration;
- self address;
- connection, friend-request, and lossless-packet callbacks;
- friend acceptance by public key;
- lossless custom-packet send.

Bootstrap, TCP-relay, secret-key import, no-spam setters, and self public/secret key access are not yet in the consumed set. They should be added with official-header verification and real integration tests.

## Memory re-entry hypothesis

Normal savedata remains a fast cache containing friend and network state. The recovery system should not attempt to recreate that opaque file byte-for-byte from memory.

Instead:

1. derive the owner application identity and Tox controller secret from the recall root;
2. construct toxcore from the 32-byte secret key and deterministic no-spam value;
3. let previously owned devices contact that stable address;
4. validate each device's owner-signed certificate;
5. rebuild the controller's local roster and new savedata.

This is not yet proven. The next real-toxcore fixture must determine whether the device-originated friend/recovery request path works after the controller loses its friend list.

## Transport versus route

IoTox distinguishes two axes:

```text
application peer transport:  Tox | I2P-direct | Tor-direct | future
route beneath Tox:            native | I2P | Tor
```

The current family is:

```text
Tox/native
Tox/I2P
Tox/Tor
```

The following is separate future work:

```text
I2P-direct
Tor-direct
```

Encoding the distinction in C++ types prevents `--network tor` from ambiguously meaning either “Tox through Tor” or “replace Tox with a Tor-native protocol.”

## Protocol layers

Transport reliability and device-operation completion are different facts. Tox lossless packets provide reliable ordered packet transport while a peer is connected. The IoTox application protocol must provide:

- version and capability negotiation;
- stable message IDs;
- correlation IDs;
- expiry;
- deduplication;
- durable receipt acknowledgement;
- execution state and terminal result;
- authorization decisions;
- ownership epoch;
- state snapshots and incremental events.

The code implements only the fixed envelope and validation. The durable semantics remain documents and tests-to-be-written.

## Persistence

The Tox identity is state that should survive power loss. The state store writes a randomized temporary mode-0600 file, flushes it, atomically renames it over the live file, then flushes the containing directory.

Future persistence must separately handle:

- ordinary Tox savedata cache;
- authorization ledger;
- device certificates;
- ownership transition history;
- durable inbox/outbox;
- root-derived local encryption keys;
- known-good backup and corruption recovery;
- platform keystore/secure-element integration where present.

The recall phrase is not stored as ordinary daemon state.

## Local interface

The primary future programmatic interface should be a Unix-domain packet socket or framed stream with request IDs, responses, deadlines, authorization context, and structured errors.

A ratox-like filesystem remains desirable because it is beautiful, inspectable, and composes with shell tools. It should be an adapter over the structured API, not the durable command queue.

```text
/run/iotox/
|-- identity
|-- connection
|-- recovery-state
|-- peers/
|   `-- <device-id>/
|       |-- online
|       |-- route
|       |-- events
|       `-- command
`-- metrics
```

## Dependency direction

```text
CLI / future IPC / future filesystem façade
                    |
               IoTox core types
                    |
      ownership + protocol + persistence
                    |
              peer transport API
                    |
           c-toxcore runtime adapter
```

The dependency arrows never point upward. Tox friend numbers must not become durable product identities. Long-term application keys, device IDs, ownership epochs, and signed endpoint bindings belong above the adapter.
