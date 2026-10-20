# ADR 0022: The stable operator peer handle is the Tox public key

**Status:** accepted and implemented in rev0006

## Context

c-toxcore assigns each friend a local `uint32_t` friend number. That number is useful inside
one running profile but is not the durable human or automation identity of the peer. A
ratox-style directory is naturally keyed by the long-term public key, and a restarted or
reconstructed process should not force operators to treat an incidental index as identity.

## Decision

Every public one-binary command that names an existing peer accepts a 64-hex Tox public key
as the preferred selector. A friend number remains accepted as a local convenience and is
resolved only inside the running agent. Runtime peer directories are keyed by uppercase
public-key hex.

This decision applies to text, action, typing, raw lossless packets, IoTox HELLO, file send,
file receive, file cancellation, and friend removal.

## Consequences

Scripts can name the same Tox transport peer consistently across operations and restarts.
The public key is still only a transport identity: it does not become the stable IoTox device
identity or confer authorization. Route-specific endpoint rotation and owner-level identity
remain future application-layer work.
