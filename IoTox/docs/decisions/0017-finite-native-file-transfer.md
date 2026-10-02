# ADR 0017: Use c-toxcore file transfer for finite path operations

**Status:** accepted and implemented in rev0005

## Context

Ratox made file movement a first-class local operation. Fragmenting bulk data through IoTox
custom packets would duplicate c-toxcore functionality and consume the control lane.

## Decision

Mirror c-toxcore’s file offer/control/seek/id/chunk API in the transport boundary. Build a
higher C++ manager for finite regular files only.

Incoming offers stay paused until an explicit no-clobber destination has a private temporary
file. Outgoing files are opened without following the final symlink and must remain the same
device, inode, size, and modification time throughout service. Files, chunks, active
transfers, and pending offers are bounded.

## Consequences

IoTox gains useful ratox-style file movement while retaining exact Tox semantics. Streams,
durable resume, content verification, authorization, and OTA remain later layers.
