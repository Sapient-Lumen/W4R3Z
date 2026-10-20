# Tox capability-session research — rev0007

**Reviewed:** 2026-08-13  
**Scope:** c-toxcore 0.2.23 public API, source-linked build target, and prior Tox extension work

## Primary sources

```text
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/CMakeLists.txt
https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
https://github.com/toxext/toxext
https://raw.githubusercontent.com/toxext/toxext/master/DESIGN.md
```

## Findings that constrain IoTox

### One owner for one `Tox*`

The 0.2.23 header permits multiple independent Tox instances on concurrent threads but says
that no more than one API function may operate on one instance at a time. Size/read pairs are
also invalidated by intervening mutation. IoTox's dedicated owner thread remains the most
legible implementation of that contract; a broad mutex would be harder to audit around
callbacks and blocking local operations.

### Custom packets are the correct machine lane

The public maximum custom-packet size is 1,373 bytes. IoTox reserves one lossless packet ID
and consumes 41 bytes for its envelope, leaving a maximum 1,332-byte application payload.
That is enough for bounded command/state/control records, not firmware or arbitrary object
payloads. Bulk objects continue to use Tox file transfer.

The ToxExt work validates explicit optional extension negotiation, composability, and
future-proofing. It also notes that ordering between ordinary Tox messages and custom packets
should not be assumed. IoTox therefore does not mix human chat text into its machine session.
HELLO and future commands remain in one reliable custom-packet lane.

### HELLO must not infer authorization

Tox identifies the transport friend associated with the callback. It does not define IoTox
ownership or application roles. A capability advertisement can safely answer “can this peer
speak the same machine protocol?” It cannot answer “may this peer unlock, update, delegate, or
reassign this device?” rev0007 makes that boundary visible in every rendered session.

### Bootstrap and relay are route inputs, not owners

`tox_bootstrap` attempts UDP setup even when normal UDP is disabled; `tox_add_tcp_relay`
registers stream relay endpoints. This reinforces the existing route design: native Tox is
the current route, while future Tor/I2P work needs explicit TCP-oriented topology and leak
testing. Bootstrap/relay operators remain roads and receive no ownership authority.

### The pinned source-linked target is real

The 0.2.23 CMake project defines `toxcore_static` when `ENABLE_STATIC` is enabled. IoTox's
standalone path disables unrelated programs/tests, provides a statically built pinned
libsodium, adds the official c-toxcore source tree, links `toxcore_static`, and populates the
same API table used by the runtime provider.

rev0007 strengthens that path with compile-time requirements that canonical c-toxcore headers
are present and API-compatible with 0.2.23. Runtime startup still calls the version functions
and verifies every consumed numeric bound because c-toxcore explicitly excludes integer
constants from its ABI guarantee.

### Upstream risk remains operationally relevant

c-toxcore 0.2.23 was released on 2026-06-03 and reports a critical defect found during manual
audit, plus other fixes, while stating that public APIs were not removed or modified. This is
an argument for pinning, fast update capability, sandboxing, and application-level command
signatures—not for pretending a transport library alone can carry physical authority.

## Design result

rev0007 implements a canonical 64-byte HELLO and per-friend online-epoch registry. The first
valid peer advertisement is frozen; retries are idempotent; in-epoch changes fail closed.
Negotiation is deterministic and symmetric. The agent automatically sends HELLO on online
transition and replies if a peer HELLO arrives before its own send is observed.

The implementation intentionally stops short of claiming mutual transcript confirmation.
The next session message should bind both nonces and the selected result before signed device
commands exist.

## Evidence boundary

```text
source-reviewed:      official API, release, CMake target, ToxExt design
compiled:             GCC/Clang owned implementation and linked-header guard
unit-tested:          codec, negotiation, epoch freeze, rendering, OS CSPRNG
mock-ABI-tested:      automatic send/echo/receive through exact loadable ABI mock
process-tested:       one product binary, Unix socket, runtime tree, restart
source-linked:        not executed here
real-peer-tested:     not executed here
```

Shell DNS resolution was unavailable in this cloudtainer. The immutable release hashes and
fetch/build scripts are retained for the eventual networked CLI rather than replacing real
source with copied declarations.
