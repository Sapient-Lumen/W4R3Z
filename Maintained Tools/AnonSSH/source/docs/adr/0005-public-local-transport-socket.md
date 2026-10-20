# 0005: Add a public local transport socket with named peer services

Status: implemented; mixed packaged evidence complete, ecosystem extensions pending

## Context

The public Rust API exposes ABP sessions and streams, but an application that merely
wants a private byte stream should not need to own anonymous-network routers, derive
identities, assemble providers, or link Rust. A local Unix socket is a language-neutral
boundary that can reuse the resident broker, warm router pool, destination sessions,
adaptive scheduling, and process supervision.

The existing broker also uses a Unix socket, but its request format is privileged
implementation detail. It carries raw destination arrays and a bond key, controls the
broker, and transitions directly into SSH transport. Publishing that format would
freeze product internals, expose excessive authority, and make safe service dispatch
impossible.

## Decision

AnonSSH will expose a second, public, versioned local protocol called ALP. The private
broker control socket remains private and may change with the binary. ALP v1 has a
bounded setup phase followed by a raw full-duplex stream:

1. the client connects to an owner-only Unix `SOCK_STREAM` endpoint;
2. client and daemon exchange a length-prefixed `ALP1` request and one result record,
   with bounded progress records reserved for a compatible extension;
3. one successful result is the exact framing boundary; and
4. every subsequent byte belongs to one independent BondedStream until half-close or
   reset.

The request names an already authorized recovery target, a symbolic peer service, one
of ABP's traffic classes, an optional locally permitted transport profile, and a bounded
deadline. It never supplies a provider endpoint, bond key, remote TCP address, or peer
filesystem path. A controlling-terminal operation authorizes a target into the broker's
memory after deriving its descriptors and bond key. An explicitly unlocked resident
service may do the same under its existing credential policy. Authorization expires on
broker restart, credential lock, or bounded inactivity.

The peer service is also symbolic. `ssh` is reserved for the current Dropbear adapter.
Other names resolve only through local operator configuration or a same-UID dynamic
registration whose lease remains open. A registered Unix socket must be owned by the
server user, be a socket rather than a symlink, and satisfy configured connection,
traffic-class, and lifetime limits. A remote caller cannot choose `host:port` or a Unix
path.

ABP capability negotiation advertises native service multiplexing before either side
uses it. Each accepted ABP stream then begins with a bounded encrypted service preface
and receives an explicit accept or rejection before application bytes are exposed. Old
peers continue to use the legacy SSH-only stream behavior; native service requests fail
clearly rather than being guessed from payload bytes or downgraded to an unintended
service. Direct Tor/I2P SSH fallback does not imply native-service fallback.

The local socket lives under the user's private runtime directory, is created without
following symlinks, has mode 0600, and verifies Linux peer credentials in addition to
filesystem permissions. Setup length, time, connection count, target count, service
count, and per-service concurrency are bounded. Public status and progress use redacted
identifiers; secrets and provider destinations never appear in the ALP schema.

## Language boundary

ALP, not a C ABI or Rust object layout, is the compatibility surface. Rust, C, Python,
and Go clients implement the same small setup codec and then return each language's
ordinary connected-stream type. Shared black-box fixtures validate malformed records,
version failure, progress ordering, ready transition, half-close, reset, and structured
errors. Bindings expose traffic class and deadlines but not scheduler knobs or anonymous
network credentials.

## Consequences

One application connection maps to one logical stream, so unrelated applications avoid
ordered head-of-line blocking while sharing physical routers and sessions. Explicit
`Realtime` and `Bulk` streams give native software better semantics than opaque SSH can
provide. The high-throughput path has no per-byte JSON or local framing overhead after
setup.

This is not OpenSSH Unix-socket forwarding, a SOCKS proxy, a TUN device, or an arbitrary
network exit. Those have different endpoint and authorization contracts. Broker or
server process loss still terminates active streams; subsequent dials recover through
the existing restart behavior.
