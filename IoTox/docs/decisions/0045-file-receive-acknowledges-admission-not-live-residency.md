# ADR 0045 — File receive acknowledges admission, not live-map residency

- Status: accepted
- Revision: rev0012
- Date: 2026-08-14
- Extends ADR 0017, ADR 0018, ADR 0019, and ADR 0042

## Context

A local operator accepts a paused finite Tox offer with:

```text
iotox file-receive PEER FILE_NUMBER /absolute/destination
```

IoTox first validates the destination, creates a private temporary file in the same directory, and
installs receiver state. It then sends `TOX_FILE_CONTROL_RESUME` through the serialized toxcore owner
thread. c-toxcore defines RESUME as acceptance of the incoming request and delivers bytes and final
completion later through `file_recv_chunk` callbacks. It does not promise that a small file cannot
finish before a different IoTox thread returns the local control response.

The earlier implementation sent RESUME, then looked up the transfer again in the live map to render
the response. The event pump could receive the entire file, safely publish it, and remove terminal
live state before this lookup. The operator then received `not_found` even though admission and
completion had both succeeded.

## Decision

`file-receive` has an explicit admission boundary:

```text
validated destination policy
+ secured private temporary file
+ installed receiver state
+ successful toxcore RESUME
= accepted local receive request
```

After successful RESUME, `FileTransferManager::receive_to_path()` returns the frozen accepted record
without requiring the transfer to remain in the live map. The returned state is `active` and means
“the receive was admitted”; it is not a completion receipt and not a guarantee that the transfer is
still active when observed.

Completion remains a separate asynchronous boundary:

```text
all ordered bytes received
+ exact finite-size completion callback
+ file fsync
+ no-clobber publication
+ directory fsync
= safely published incoming file
```

A caller that needs completion must observe the destination and/or transfer-event and runtime
projection convergence. Later transfer failure is likewise asynchronous evidence and cannot be
retroactively folded into the already returned admission response.

## Consequences

A tiny transfer may legitimately be absent from `iotox files` immediately after a successful
`file-receive` response because it has already completed. This is not data loss.

The local API no longer produces a false failure merely because the event pump is faster than the
control reply. The exact mock deliberately schedules an immediate four-byte transfer after RESUME,
and the separate-process fixture exercises that race.

This decision does not make file transfer durable across daemon restart, add an offline spool, or
claim public-network interoperability. Future peer-local file FIFOs and journals must preserve the
same distinction between admission, progress, and safe publication.
