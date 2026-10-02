# ADR 0046 — Ratox file FIFOs name finite local files

- Status: accepted
- Revision: rev0013
- Date: 2026-08-14
- Extends ADR 0003, ADR 0010, ADR 0017, ADR 0019, ADR 0040, ADR 0042, and ADR 0045

## Context

Ratox's beauty comes partly from ordinary operations such as `cat foo > file_in` and
`cat file_out > bar`. In ratox, the named-pipe bytes are the live Tox transfer stream. IoTox already
has a finite-file manager with explicit source validation, exact chunk servicing, paused incoming
offers, private temporary destinations, atomic no-clobber publication, and asynchronous completion.

Making an unbounded FIFO byte stream the authoritative transfer object would discard those
properties. FIFO acceptance is not durable, stream writers can disappear mid-record, restart erases
kernel buffers, and an output FIFO cannot by itself express destination policy or safe completion.

## Decision

The ratox-successor file FIFOs carry **finite path records**, never file payload bytes:

```text
file-send      <absolute-source-path> LF
file-receive   <file-number> TAB <absolute-destination-path> LF
file-control   <file-number> TAB <pause|resume|cancel> LF
```

Each accepted record enters the same typed one-binary file manager used by structured local
commands. Paths are local operator choices. Remote filenames are presentation only and can never
select a local path.

The runtime also exposes a bounded `file-events` journal and atomic disposable
`files/incoming/<NUMBER>` and `files/outgoing/<NUMBER>` projections. Neither is durable authority.

## Consequences

IoTox retains one-write shell composability while keeping finite transfer identity, exact local
policy, no-follow source handling, private receive staging, and safe publication.

A successful FIFO write remains only kernel acceptance. The journal supplies semantic ingress
truth. Incoming destination publication supplies completion truth.

This surface does not reproduce ratox's arbitrary streaming use cases. Streaming, if later added,
will be a separately named and specified facility rather than an ambiguity in finite-file transfer.

The complete c-toxcore file number is preserved as an opaque provider handle. The public grammar
does not add a separate direction field.
