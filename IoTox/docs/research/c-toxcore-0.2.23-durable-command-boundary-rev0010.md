# c-toxcore 0.2.23 durable-command boundary — rev0010

**Reviewed:** 2026-08-14 America/New_York  
**Pinned release:** 0.2.23, released 2026-06-03

## Primary sources

```text
https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
https://github.com/TokTok/c-toxcore/security/advisories/GHSA-42vg-9mg3-399f
https://github.com/TokTok/c-toxcore/blob/v0.2.23/README.md
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox_options.h
https://toktok.ltd/spec.html
```

## API boundary used by IoTox

The public API supplies opaque `Tox*` lifecycle, savedata, friend identity and connection state,
lossless custom packets, ordinary text/presence, file transfer, bootstrap nodes, TCP relays, and
iteration callbacks. The custom-packet maximum exposed by the pinned header is 1,373 bytes; IoTox
reserves one packet discriminator and a 40-byte application header, leaving a bounded payload
ceiling of 1,332 bytes in protocol v1.

`tox_friend_send_lossless_packet` may fail with `TOX_ERR_FRIEND_CUSTOM_PACKET_SENDQ`. IoTox retries
only a byte-identical record that toxcore explicitly rejected. It does not resend a packet after
successful queue acceptance merely because no application result has arrived.

The `Tox*` instance remains owned by one serialized C++ thread. Callbacks are copied into bounded
owned events. Business logic, persistent journals, authorization, receipts, and results do not call
or depend directly on toxcore internals.

## Security posture

The project README characterizes c-toxcore as experimental and notes the absence of an independent
formal audit. Release 0.2.23 includes security fixes from manual review, including the advisory
pinned above. IoTox must retain dependency pinning, rapid update capacity, process hardening,
malformed-input testing, and application signatures/authorization above the transport.

## Route implications

The options API exposes UDP, local discovery, DHT announcements, proxy, and TCP controls useful for
future experiments. Those toggles do not by themselves prove a leak-free Tox/Tor or Tox/I2P route.
The current product implements Tox/native. Reserved private routes fail closed.

## Evidence boundary

The exact runtime ABI subset is compiled against an IoTox mock shared library and exercised under
GCC, Clang, sanitizers, fuzzing, and a process fixture. The cloudtainer cannot resolve the pinned
archive hosts, so official source-linked c-toxcore and two genuine peers remain unexecuted here.
`tools/build-standalone.sh`, `verify-standalone.sh`, and `run-real-peer-smoke.sh` are the prepared
external gate; they are not evidence that the gate has already passed.
