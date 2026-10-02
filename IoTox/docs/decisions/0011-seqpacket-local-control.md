# ADR 0011: Unix SOCK_SEQPACKET is the primary local control boundary

**Status:** accepted and implemented in rev0004 for Linux

## Context

Ratox FIFOs compose beautifully with shell tools but do not themselves preserve request
boundaries, correlation, protocol versions, structured errors, peer credentials,
timeouts, or future authorization context.

Unix `SOCK_SEQPACKET` preserves message boundaries while retaining a small local POSIX
surface.

## Decision

The primary local control protocol uses a private Unix `SOCK_SEQPACKET` socket.

- Each datagram contains exactly one bounded versioned request or response.
- A non-zero request ID correlates the response.
- The daemon validates the connected process with Linux `SO_PEERCRED` and currently
  accepts only the same effective user.
- Runtime directories are `0700`; the socket and status artifacts are private.
- Ratox-like files/FIFOs will translate to this protocol rather than replacing it.

## Consequences

The local interface remains compact and scriptable through the `iotox` client while the
core has explicit framing and errors. Portability beyond Linux needs a credential
strategy for each supported platform.

## Revisit when

A target platform lacks reliable sequenced-packet Unix sockets, or multi-user policy
requires a broker and richer local credentials. Do not fall back to an unframed byte
stream without adding explicit length framing.
