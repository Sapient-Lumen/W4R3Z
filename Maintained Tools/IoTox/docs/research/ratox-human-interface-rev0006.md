# Ratox human interface reading — rev0006

**Evidence class:** source-reviewed design inheritance  
**Reviewed:** 2026-08-13 America/New_York

## Primary sources

- https://git.2f30.org/ratox/file/README.html
- https://git.2f30.org/ratox/log.html
- https://raw.githubusercontent.com/pranomostro/ratox/master/ratox.c

## What remains beautiful

Ratox runs in a directory and turns Tox into ordinary Unix objects. Its documented peer tree
includes nickname, online state, user state, status message, text input/output, file input/
output, removal, and call state. Global paths expose identity, profile mutation, nospam, and
friend-request handling. Its examples demonstrate that small shell programs can compose a
network client without embedding the network library.

That ordinary surface is the inheritance IoTox wants to strengthen, not erase.

## What rev0006 now reconstructs

The single `iotox` executable now provides:

```text
self address, name, status message, and presence
friend request, accept, list, remove
peer public key, local number, connection, online, name, status, typing
normal and action text plus receipts
finite native Tox file transfer with explicit safe paths
raw lossless packets and a structured IoTox HELLO frame
private global event journal
private per-peer human-message journal
private per-peer decoded-IoTox-protocol journal
stdin-backed exact-byte Unix composition
```

The runtime tree is read-oriented and private. Mutations pass through the bounded local
control socket so the daemon can return an error and preserve a versioned request contract.
This is less magical than immediately making every path writable, but it avoids promising
semantics that a FIFO cannot carry by itself.

## Deliberate departures

Ratox friend directories use the public key and that remains the right stable transport
handle. IoTox does not elevate the friend index into durable identity.

Ratox writes text and file streams through FIFOs. IoTox first provides text/hex/stdin command
forms and exact finite path transfers. A future FIFO façade must translate into structured
requests rather than become the authoritative queue.

Ratox combines a very broad client in one C file and event loop. IoTox keeps one product
binary but separates owned C++ modules: toxcore adapter, owner thread, local protocol,
runtime projection, file manager, frame codec, agent policy, and CLI.

Ratox friendship is sufficient for chat semantics. IoTox explicitly refuses to treat
friendship, profile, or text receipts as ownership or actuator authority.

## A modern ratox-successor target

The desired outside remains small:

```text
run
pair or accept
name a peer by public key
message or action
watch peer traffic
send or receive a file
inspect connection and state
stop
```

The inside must add what physical-device control requires:

```text
independent authorization ledger
HELLO/capability negotiation
application signatures and ownership epochs
durable command inbox/outbox
expiry and idempotency
received/started/succeeded/failed results
safe restart and power-loss behavior
explicit route policy
```

rev0006 is the first cube in which the ordinary human lane and the structured IoTox lane are
both visible through the same executable. It is still a construction site, but it is now
recognizably a stronger ratox successor rather than only a test harness around toxcore.
