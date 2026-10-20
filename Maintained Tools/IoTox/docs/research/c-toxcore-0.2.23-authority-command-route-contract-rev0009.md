# c-toxcore 0.2.23 contract review for signed sessions and first commands

**Reviewed:** 2026-08-14  
**Scope:** official v0.2.23 release and headers; ratox interface lineage  
**Maturity:** source/API review, not genuine-network execution in this container

## Primary sources

- https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
- https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
- https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox_options.h
- https://github.com/TokTok/c-toxcore
- https://toktok.ltd/changelog/c-toxcore.html
- https://github.com/rofl0r/ratox

## Findings that constrain IoTox

### Pin 0.2.23, but keep the adapter narrow

v0.2.23 was released 2026-06-03. The release reports a critical bug discovered by manual audit,
other memory-safety fixes, and no removed or modified public API. It also adds granular iterate
options. The published `c-toxcore-0.2.23.tar.gz` SHA-256 is the value frozen in
`dependencies.lock`.

The security-fix history reinforces the current design: all toxcore knowledge stays behind one
small provider and one owner thread, while application authorization is independently signed.

### Lossless custom packets fit bounded control records

The official header defines 1373 bytes as the maximum custom packet. A lossless packet's first
byte must be 69 or 160 through 191; IoTox reserves `0xA0`. Tox describes lossless packet
behavior as reliable and in order, packet-framed rather than a byte stream.

IoTox's 41-byte outer header leaves 1332 payload bytes. Fixed HELLO, confirmation, authority,
command, and description records all fit without fragmentation. Large artifacts still belong
on toxcore file transfer.

### `SENDQ` is a local admission failure

`TOX_ERR_FRIEND_CUSTOM_PACKET_SENDQ` means the packet queue is full. It is distinct from
`FRIEND_NOT_CONNECTED`. Neither indicates that the packet was accepted. IoTox therefore may
retry only the exact frozen bytes after those local failures. Once `tox_friend_send_lossless_packet`
succeeds, this layer does not infer remote execution and does not resend automatically.

### The iterate loop remains product-owned

The official introductory client shows callback registration followed by repeated
`tox_iteration_interval` / `tox_iterate` calls. IoTox keeps all calls for a `Tox*` on one owner
thread, with bounded command/event queues around it. The optional experimental thread-safety
setting is not used as a substitute for that invariant.

### Future Tox routes have explicit knobs but are not proven

The official options API exposes UDP enablement, local discovery, DHT announcements, proxy
host/type/port, and experimental DNS disablement. Those controls make a future TCP/proxy-only
Tox-over-Tor experiment plausible. They do not prove that the route is leak-free, reachable, or
operationally acceptable, and they do not establish an I2P route. Reserved routes must continue
to fail closed until a genuine fixture verifies their complete policy.

### Ratox's interface lesson remains valid

Ratox's filesystem/named-pipe approach makes Tox ordinary to Unix tools. IoTox keeps that
human-facing simplicity as a private projection and future façade, while moving request IDs,
authorization, retries, bounded decoding, and persistence underneath a structured local socket.

## Consequences for rev0009

- Keep Tox as the primary connection substrate.
- Keep `0xA0` and the 1332-byte application payload ceiling.
- Treat queue acceptance, remote principal proof, application admission, and operation result as
  four separate facts.
- Do not advertise durable commands because the first read-only request is process-local.
- Do not silently route Tor/I2P selections over native networking.
- Preserve runtime-loaded mock validation and continue the source-linked/genuine-peer handoff.
