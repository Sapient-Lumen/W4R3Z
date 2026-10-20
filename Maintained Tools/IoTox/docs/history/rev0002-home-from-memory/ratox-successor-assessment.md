# Ratox successor assessment retained for IoTox

## Engineering call

Ratox’s idea should survive; its internals should not become IoTox’s product core. IoTox is a clean successor around current c-toxcore, not a rewrite of Tox and not a long patch series against ratox.

The core principle is:

> Keep ratox’s soul: a tiny, scriptable, self-owned interface to Tox. Replace the internals that need durable protocol semantics, authorization, persistence, testing, and safe concurrency.

## What ratox got right

Ratox exposes a Tox identity and peers as a filesystem-shaped control surface built from ordinary files and named pipes. That creates rare and valuable qualities:

- shell scripts and small processes can compose it;
- it avoids a large client framework;
- identity and state remain local;
- networking looks like ordinary I/O;
- ordinary Unix supervision works;
- Tox can carry chat, files, audio, streams, and service-like workflows.

This philosophy is a strong fit for self-owned appliances. Owners should be able to operate a device locally, inspect it, replace a controller application, back up its identity, and continue using it without a vendor cloud.

IoTox therefore preserves an optional ratox-compatible or ratox-inspired façade, but places it over a structured core.

## Why not evolve ratox directly

### Coupling

Ratox concentrates Tox lifecycle, peers, calls, files, FIFOs, persistence, and event-loop behavior in a small C program. That compactness is beautiful for a Unix utility. A production IoT agent, however, needs changes that cross nearly every one of those concerns:

- one-thread Tox ownership;
- peer and local-client lifecycles;
- durable queues;
- authorization;
- protocol framing;
- firmware transfers;
- identity persistence;
- observability;
- recovery after power loss.

Untangling all of that while preserving old assumptions amounts to a new core hidden inside an old program.

### FIFOs are not sufficient as the primary application API

A FIFO write does not intrinsically carry a request ID, response destination, authorization context, deadline, version, idempotency key, structured error, or durable-delivery contract. A pipe is also not an offline message queue.

For IoT, these facts must be distinct:

```text
a caller wrote a command
IoTox parsed it
IoTox authorized it
IoTox durably accepted it
the device began it
the device completed it
the result reached the caller
```

The future FIFO façade can translate into structured requests, but it cannot define these semantics by itself.

### Chat and file operations are not a device protocol

A device needs explicit versioned forms such as `HELLO`, `CAPABILITIES`, `COMMAND`, `COMMAND_RESULT`, `STATE_SNAPSHOT`, `STATE_EVENT`, `ACK`, `ERROR`, pairing, revocation, and OTA manifests.

Tox lossless custom packets are the planned control plane. Tox file transfer is the planned bulk plane for firmware, diagnostic bundles, exports, and larger media. Application messages need request IDs, expiry, duplicate handling, and compatibility rules above Tox.

### Transfer management needs product state

A production transfer manager must distinguish peer, direction, Tox file number, and an application-level transfer ID. It also needs explicit states, hashes, storage reservation, cancellation, timeouts, restart recovery, and policy checks before accepting executable content.

### Persistence must tolerate power loss

The identity update sequence should be:

1. serialize new state;
2. encrypt it when a platform-protected key is available;
3. write a mode-0600 temporary file;
4. flush the file;
5. validate the serialized state where possible;
6. atomically rename it over the live state;
7. flush the parent directory;
8. retain a recovery slot or known-good backup.

rev0001 implements the write, flush, rename, and directory-flush portion.

### Tox API access needs a boundary

Current c-toxcore options should be allocated and modified through accessor functions rather than by relying on a public structure layout. IoTox goes further: only the adapter knows toxcore types and symbols. Everything else speaks IoTox-owned types.

## The replacement shape

```text
hardware and local applications
            |
structured local IPC
            |
IoTox core
  - ownership and authorization
  - protocol codec
  - durable inbox/outbox
  - state synchronization
  - transfer and OTA manager
  - secure identity store
  - metrics and audit events
            |
bounded commands
            |
one Tox owner thread
            |
c-toxcore
```

Optional surfaces include a ratox-style filesystem, a CLI, and local controller bridges.

## Application protocol requirements retained

### Version negotiation

Every peer connection begins with hello and capability exchange. Unknown optional fields can be ignored; unknown required features produce a clear incompatibility response.

### Idempotency

Every hardware-affecting command carries a stable message ID. Retries return the stored terminal result rather than repeating an actuator action unless repetition was explicitly requested.

### Application acknowledgements

Reliable packet delivery says nothing about business completion. The protocol needs received, started, succeeded, failed, and expired states as appropriate.

### Durable offline behavior

Both controller and device need a persistent outbox, retries with backoff, expiry, deduplication, bounded storage, priority, and “replace previous desired state” behavior for selected command classes.

An owner-operated always-on hub may act as mailbox and automation controller without becoming mandatory vendor infrastructure.

### Bulk separation

Ordinary command packets remain below the custom-packet limit. Firmware uses file transfer with a signed manifest, immutable artifact ID, size and digest, hardware constraints, anti-rollback counter, staged write, and post-reboot health confirmation.

An authorized Tox peer is not automatically authorized to install executable code.

## Ownership and authorization above Tox

Tox peer identity is a transport identity. It is not the whole product authorization model.

### Physical claim

A device can ship with its Tox identity, a one-time claim secret, a product identifier, and optionally a manufacturer certificate. QR, NFC, or a local display can carry claim data. Receiving a friend request alone never grants ownership.

### Roles and capabilities

Candidate roles include owner, administrator, operator, viewer, automation controller, and expiring service technician. Candidate capabilities include telemetry read, settings write, actuation, user management, firmware install, log export, and factory reset.

### Revocation and recovery

The design must cover lost controllers, stolen devices, household-member removal, compromised hubs, ownership transfer, self-owned factory reset, and recovery after owner-key loss.

## Lessons to borrow from other Tox work

- Active clients such as Toxic are useful references for current lifecycle, transfer edge cases, error mapping, build hardening, and tests, but an interactive terminal client is not the IoT daemon architecture.
- ToxExt’s extension negotiation and composable protocol mindset are useful, even if IoTox owns its control protocol.
- Tuntox demonstrates the value of service bridging through Tox but should be treated as experimental evidence, not product infrastructure.
- A C++ or Rust application around current c-toxcore is lower risk than rewriting the Tox stack. IoTox rev0001 chooses C++20 and a narrow adapter.

## Keep and replace table

| Ratox characteristic | IoTox decision |
|---|---|
| Self-owned Tox identity | Keep |
| No mandatory central account | Keep |
| Small supervised daemon | Keep |
| Filesystem/scriptable surface | Keep as optional façade |
| Tox for connectivity and encryption | Keep |
| Monolithic source and shared globals | Replace |
| Direct options-structure access | Replace |
| FIFOs as primary programmatic API | Replace |
| Plain text as device protocol | Replace |
| Friendship as permission | Replace |
| In-place state truncation | Replace |
| Online-only in-memory command behavior | Replace |
| Conflated transfer state | Replace |
| Build-time-only bootstrap configuration | Replace |
| No explicit protocol negotiation | Replace |
| No durable execution acknowledgement | Replace |

## Staged plan retained

1. Prove current c-toxcore on target hardware and real networks.
2. Establish the owner thread, options API, pinned dependency, atomic persistence, structured local socket, events, and custom packets.
3. Add protocol negotiation, durable queues, expiry, deduplication, and state synchronization.
4. Add physical claim, owner identity, roles, capabilities, revocation, transfer, and recovery.
5. Add signed OTA and diagnostic transfer.
6. Add the ratox-style façade only after core semantics are stable.
7. Destructively test power failure, full disks, corrupt state, duplicates, delayed commands, reconnect storms, queue saturation, clock changes, revoked owners, malformed payloads, interrupted firmware, and downgrade attempts.

## Security and licensing posture

c-toxcore describes itself as experimental and not independently formally audited. IoTox therefore needs source pinning, sandboxing, hardening, dependency monitoring, fuzzing, and a reliable security-update channel.

c-toxcore is GPL-3.0-or-later. Licensing is an architecture and business requirement, not a release-week task.
