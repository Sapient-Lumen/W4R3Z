# Ratox surface contract for IoTox rev0005

**Source reviewed:** https://raw.githubusercontent.com/pranomostro/ratox/master/ratox.c  
**Purpose:** preserve ratox's local clarity without preserving its internal constraints

## What must survive

Ratox makes a peer network feel like ordinary Unix I/O. IoTox keeps that principle:

- one foreground process suitable for supervision;
- a private, inspectable runtime tree;
- one stable local identity projection;
- peers represented by public-key names rather than vendor account IDs;
- appendable/readable event surfaces;
- commands available to shell scripts and small programs;
- no mandatory GUI, cloud account, or opaque application framework;
- ordinary file transfer as a first-class operation.

The product test is not “does it resemble ratox internally?” It is “can an owner understand and operate it locally with very little machinery?”

## What does not survive unchanged

Ratox's compact implementation couples callbacks, peer records, FIFOs, calls, and limited transfer state. IoTox needs stronger semantics for physical products:

- one serialized toxcore owner rather than calls distributed through the program;
- structured local requests and replies over private `SOCK_SEQPACKET`;
- request IDs, errors, deadlines, and explicit result boundaries;
- independent authorization rather than friendship-as-authority;
- bounded queues and auditable loss policy;
- multiple opaque transfer handles;
- safe destination acceptance and no-clobber publication;
- atomic savedata writes;
- protocol framing independent of chat text;
- explicit native/Tor/I2P route policy;
- test seams and sanitizer/fuzzer facilities.

## rev0005 public process shape

There is one executable:

```text
iotox run [agent options]
iotox [local control command]
```

The `run` mode owns toxcore and the runtime tree. A second invocation connects to the private local control socket. This preserves one product identity without forcing network ownership and command parsing into one thread.

## Current runtime tree

```text
<runtime>/
├── control.sock
├── self
├── status
├── events
├── peers/
│   └── <64-hex-public-key>/
├── requests/
│   └── <64-hex-public-key>/
└── transfers/
    └── <direction>-<friend-number>-<opaque-file-number>/
```

All roots are private to the effective user. Request and transfer entries are assembled in non-public temporary directories and renamed into view only when complete.

The runtime tree is a projection, not an authority database. Deleting a projected file does not mutate toxcore. Mutations go through the structured local control plane and return an explicit result.

## Current command surface

```text
ping
status
address
stop
peers
transport-peer-request
transport-peer-accept
transport-peer-remove
transport-send
transport-hello
file-send
file-receive
file-cancel
files
bootstrap-seeds
```

`transport-peer-add` is retained only as a compatibility alias for `transport-peer-accept`.

## File-transfer behavior

Ratox inspires the visible simplicity; c-toxcore supplies transfer negotiation and chunks; IoTox supplies the missing safety manager.

Outgoing paths are finite, absolute, non-symlink regular files. The open descriptor and frozen metadata define the bytes, not later pathname resolution. Incoming offers remain paused until a destination is explicitly accepted. Existing destinations are never overwritten. A private same-directory temporary file becomes visible only after exact completion and synchronization.

The current product does not expose pipe streams, unknown-size streams, call audio/video, or a general remote shell. Those remain possible future surfaces, not silent rev0005 claims.

## “Just werx” governance

Simplicity is not permission to hide ambiguity. A local command must say whether it was rejected, queued, accepted, completed, cancelled, or timed out. Required semantic events must not disappear merely because an observer was slow. Partial runtime records must not appear. A privacy route must not silently fall back.

The desired experience is ordinary. The implementation may be strict.
