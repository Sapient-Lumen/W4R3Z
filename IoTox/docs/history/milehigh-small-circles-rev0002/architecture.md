# IoToxmutorr architecture

## Design center

IoToxmutorr is a headless, self-owned device agent and replication experiment. Tox is the first encrypted peer connection substrate. Mutorr is the application overlay that decides which few peers cooperate for each mutable namespace.

```text
sensors / actuators / local applications
                  |
       structured local API                         [planned]
                  |
        +--------------------------------+
        |         IoToxmutorr            |
        |                                |
        | ownership / authorization      |          [planned]
        | namespace membership epochs    |          [planned]
        | Mutorr Cube topology            |          [implemented]
        | rendezvous custodians           |          [implemented]
        | mutable linked heads            |          [implemented]
        | Merkle objects / anti-entropy   |          [planned]
        | durable queues and object store |          [planned]
        | protocol frame                  |          [implemented]
        | identity state store            |          [implemented]
        +---------------+----------------+
                        |
              bounded peer commands
                        |
            one Tox owner thread                     [implemented]
                        |
          c-toxcore runtime adapter                   [implemented]
                        |
      lossless packets / future file transfer
                        |
                    Tox network
```

The `iotox::mutorr` layer has no dependency on toxcore. It accepts stable 256-bit IDs and produces topology and placement decisions. This permits deterministic C++ tests, simulations, fuzzing, and benchmarks before live-network behavior is introduced.

## One Cube per namespace

A Cube is not a global chatroom. It is a snapshot of the devices authorized for one namespace. Different directories can therefore have different membership and replication:

```text
home/config:       controller, hub, thermostat, owner phone
family/chat:       phones, tablets, home hub
camera/archive:    cameras, NAS, two selected custodians
workshop/sensors:  workshop nodes only
```

Every peer with the same member set sorts the same IDs, takes the same ring neighbors, and selects the same custodians. The default four-neighbor topology bounds application relationships while retaining a connected gossip path.

## Announcement and object lanes

Control announcements and object bytes have different economics.

```text
small control lane:
  mutable head, inventory summary, want, object offer
  -> Tox lossless custom packets

bulk lane:
  immutable object/chunk bytes
  -> planned Tox file-transfer manager
```

A new head should be announced to circle neighbors only. A receiver deduplicates it, evaluates whether it advances a known stream, forwards the announcement, and asks one available peer for missing immutable objects. Once received and validated, that peer can serve the same objects onward.

## Mutable state model

The only mutable item is a signed head. Objects beneath it are intended to be immutable and addressed by cryptographic digest.

The head includes a namespace, writer key, generation, current root, previous root, and metadata. rev0002 provides canonical bytes and progression rules but deliberately leaves signing and digest implementations behind future adapters.

Single-writer namespaces can advance one linked chain. Multi-writer conversations should use one append-only chain per writer and merge the view. A true collaboratively edited directory requires explicit conflict handling or a CRDT; writer generations are not globally comparable.

## The owner-thread rule

No module outside the toxcore adapter may call a toxcore API. `ToxTransport` owns the worker thread, loaded library, and `Tox*`. Public calls enqueue work and wait for typed results. Callbacks are copied into an event queue before consumers see them.

The rule gives one place to reason about callback reentrancy, savedata snapshots, shutdown order, and later bounded command queues. Mutorr logic runs above this boundary and uses stable identities rather than transient toxcore friend numbers.

## Runtime adapter

The adapter resolves only the c-toxcore symbols consumed by this revision and requires the 0.2 ABI line at patch 23 or later. It currently covers identity lifecycle, savedata, iteration, callbacks, explicit friend acceptance, and lossless custom packets. Bootstrap, TCP relay, and file transfer are still absent.

## Transport versus route

Application peer transport and route remain separate axes:

```text
transport:  Tox | future I2P-direct | future Tor-direct
route:      native | future I2P route | future Tor route
```

Only Tox/native is implemented. Reserved choices fail explicitly and never silently fall back.

## Persistence

The Tox identity store uses a randomized temporary file, mode `0600`, file flush, atomic rename, and parent-directory flush. Durable Mutorr heads, objects, membership epochs, inbox/outbox records, and a known-good recovery slot remain future work.

## Dependency direction

```text
CLI / future IPC / future filesystem facade
                    |
     authorization + membership + Mutorr core
                    |
          protocol + durable persistence
                    |
              peer transport API
                    |
           c-toxcore runtime adapter
```

Dependency arrows do not point upward. Tox friendship is connectivity, not authorization. A Cube must be built from an explicitly authorized namespace membership set.
