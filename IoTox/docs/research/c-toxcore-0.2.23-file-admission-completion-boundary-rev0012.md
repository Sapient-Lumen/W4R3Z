# Research note — c-toxcore file admission and completion boundary, rev0012

- Revision studied: c-toxcore v0.2.23
- IoTox revision: rev0012
- Date: 2026-08-14
- Scope: receiving finite files through `tox_file_control(RESUME)` and `tox_file_recv_chunk`

## Primary source

Pinned public header:

```text
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
```

Relevant contract:

- an incoming transfer starts paused;
- the receiver accepts it by sending `TOX_FILE_CONTROL_RESUME`;
- `tox_file_control` returns success when the control command is accepted by the local core;
- later `tox_file_recv_chunk` callbacks carry data;
- a callback with length zero terminates the transfer and releases the file number for reuse;
- completion is successful only when the final position equals the advertised finite size.

The header does not promise a minimum interval between successful RESUME and the first or final chunk
callback. IoTox must therefore tolerate a small transfer completing before the local control caller
has observed the response to its acceptance request.

## IoTox consequence

`FileTransferManager::receive_to_path()` has two distinct boundaries:

```text
admission
    validate destination policy
    create a private no-follow temporary file in the destination directory
    install active receiver state
    receive successful local tox_file_control(RESUME)

completion
    receive all ordered bytes
    receive the zero-length completion callback at the exact finite size
    fsync the temporary file
    publish without replacement by link/unlink
    fsync the destination directory
    remove live transfer state
```

The local `file-receive` response acknowledges the first boundary. It does not promise that the
transfer remains present in the live map by the time the response reaches the caller, and it does not
claim successful publication. A tiny file may already have crossed the second boundary. Completion
truth remains the destination publication plus transfer events/projection convergence.

Requiring a second lookup in the live map after RESUME was incorrect. The event pump could complete
and remove the transfer between successful RESUME and that lookup, causing a false `not_found` result
for a file that had already been safely published. rev0012 now returns the frozen accepted snapshot
created before RESUME, after and only after toxcore accepts RESUME. Asynchronous completion or failure
remains observable separately.

## Evidence boundary

The exact ABI mock intentionally enqueues a four-byte body and a zero-length completion callback as
soon as the receiver resumes. A release-scheduled separate-process test exposed the race. The fixed
path completed repeated one-binary lifecycles and the clean compiler/sanitizer matrix.

This proves the owned admission/completion semantics against the consumed ABI mock. It does not prove
real network latency, congestion, remote sender behavior, or public c-toxcore file-transfer
interoperability.
