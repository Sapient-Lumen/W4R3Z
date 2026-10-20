# ADR 0049 — The root request FIFO is an exact complete-address adapter

- Status: accepted
- Revision: rev0015
- Date: 2026-08-14
- Extends ADR 0003, ADR 0023, ADR 0027, ADR 0040, and ADR 0048

## Context

ratox made outgoing friendship ordinary: write a Tox address and message to one global request FIFO.
That surface is central to the successor goal. IoTox already had the typed
`transport-peer-request` control operation, but the projected root `request` inode was dormant. A
script therefore needed the structured client for the first relationship even though later
accept/reject/remove decisions were ordinary writes.

The historical ratox parser split its input at the first whitespace and supplied a default message.
That is convenient but ambiguous: spaces and TABs are not distinguished, missing message behavior
is implicit, arbitrary bytes cannot be represented faithfully, and parse boundaries depend on C
string operations. IoTox also cannot send a request from a public key alone. c-toxcore requires the
complete 38-byte Tox address: 32-byte public key, 4-byte nospam, and 2-byte checksum.

A FIFO is a byte stream. Writer success proves only kernel admission. Multiple writers preserve a
record boundary only when each writes the whole record once and the write does not exceed that
FIFO's actual `PIPE_BUF`. c-toxcore success means the request entered local Tox state; it does not
prove network transmission, remote receipt, remote acceptance, or application authorization.

## Decision

IoTox exposes these private mode-0600 root objects:

```text
<RUNTIME>/request
<RUNTIME>/request.help
<RUNTIME>/friend-events
```

`request` is an LF-framed FIFO. The exact v1 record, excluding LF, is:

```text
<76 hexadecimal Tox address bytes><TAB><1..921 message bytes>
```

The contract is:

- hexadecimal may be uppercase or lowercase;
- the address field is exactly 76 characters and decodes to exactly 38 bytes;
- byte 77 is one literal horizontal TAB;
- the message contains 1..921 bytes;
- after the separator, TAB, NUL, CR, and bytes at least `0x80` are message data;
- LF terminates the local record and is not sent in the request message;
- the record is 78..998 bytes excluding LF and at most 999 bytes including LF;
- a producer writes the entire record including LF in one `write(2)`;
- startup fails if the actual FIFO cannot provide `PIPE_BUF >= 999`;
- partial records expire and malformed/oversized records are rejected;
- replaced FIFOs are accepted only after the same no-symlink, inode, owner, mode, and `PIPE_BUF`
  checks as the original inode.

The parser performs exact hexadecimal decoding. It does not reimplement c-toxcore's friend-add
policy. `tox_friend_add` remains authoritative for checksum, own-key, duplicate/already-sent, and
changed-nospam results.

The FIFO and structured control operation call one shared Agent method serialized with the other
friendship lifecycle mutations. On success, IoTox refreshes the public-key-selected peer projection
and appends a `request-send` event. On rejection it appends the exact parse or provider disposition.
If a malformed record does not contain a trustworthy 64-hex public-key prefix, the event explicitly
renders `public-key=unknown`; no all-zero or magic peer identity is fabricated.

Tox friendship remains transport recognition only. Sending a request grants no owner status, role,
capability, recovery authority, or operation permission in the independent IoTox authorization
ledger.

## Consequences

The first relationship can be initiated by an ordinary Unix write without adding another daemon or
another product binary. Scripts that need ordinary text can use `printf`. Programs that need NUL or
other arbitrary bytes can construct the same finite record and make one direct write. The typed CLI
remains useful and converges on identical Agent and owner-thread semantics.

The grammar is intentionally less permissive than ratox. There is no whitespace search, default
message, shell grammar, or silent trimming. That makes byte ownership and error evidence stable.

The FIFO is not a durable outbox. A successful write is not a remote acknowledgement. `friend-events`
is bounded process-local operational evidence, not a signed durable audit log. Offline request
queueing, cancellation, expiry, and durable lifecycle history require separate decisions.

The root-lane support generalizes the hardened FIFO monitor without weakening public-key directory
validation. Root lanes are promised process-wide inodes; startup requires every configured root
lane, and aggregate friendship readiness becomes false when the promised request lane is absent.

## Rejected alternatives

### Keep outgoing requests typed-only

Rejected because the ratox successor should make the complete friendship lifecycle available through
ordinary files, not require the structured client for the first step.

### Copy ratox's first-whitespace parser and default message

Rejected because it creates ambiguous byte ownership, implicit behavior, and a C-string-shaped
protocol. Convenience belongs in a caller, not in the durable local grammar.

### Accept only the 32-byte public key

Rejected because `tox_friend_add` requires the complete address and its nospam/checksum semantics.
`tox_friend_add_norequest(public_key)` is for accepting an incoming request or mutually managed
peers; it is not equivalent to sending an outgoing request.

### Use spaces, JSON, shell words, or environment variables

Rejected for the v1 ordinary lane. TAB provides one fixed boundary while leaving spaces untouched.
JSON or shell parsing would add escaping and Unicode policy to a transport operation that already has
finite binary fields. The structured control protocol remains available for richer local clients.

### Treat FIFO write completion as request success

Rejected because FIFO delivery, parser acceptance, local toxcore mutation, network delivery, remote
acceptance, and IoTox authorization are distinct events.

### Make the request FIFO a persistent queue

Rejected because a kernel FIFO has no restart, expiry, cancellation, identity, duplicate, or storage
contract. A future durable outbox must be a separately named product facility.
