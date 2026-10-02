# Ratox-successor live text FIFO v1

Revision: rev0012  
Status: implemented research contract  
Authority: ADR 0043

## Purpose

The live text FIFO surface preserves the most useful ratox property: a peer can be spoken to with an
ordinary Unix write. It does not turn chat into an IoT command language and does not pretend that a
kernel FIFO is durable delivery.

For each projected Tox public key:

```text
peers/<PUBLIC-KEY>/message
peers/<PUBLIC-KEY>/action
peers/<PUBLIC-KEY>/message.help
peers/<PUBLIC-KEY>/message-events
peers/<PUBLIC-KEY>/messages
```

`message` sends `TOX_MESSAGE_TYPE_NORMAL`. `action` sends `TOX_MESSAGE_TYPE_ACTION`.

## Writer contract

A FIFO record is one body followed by LF:

```sh
printf '%s\n' 'hello' > "$RUNTIME/peers/$PEER/message"
printf '%s\n' 'waves' > "$RUNTIME/peers/$PEER/action"
```

The exact contract is:

| Property | Value |
|---|---|
| Body length | 1 through 1372 bytes |
| Delimiter | LF, removed before toxcore |
| Other bytes | preserved exactly, including NUL, CR, and bytes >= 0x80 |
| Local validation | bounded byte span; no UTF-8 validator in this adapter |
| Interoperability contract | valid UTF-8 human text, as defined by the Tox protocol |
| Atomic writer rule | body and LF in one `write(2)` |
| Maximum recommended write | 1373 bytes |
| Runtime gate | actual `_PC_PIPE_BUF` must be at least 1373 |
| Embedded LF body | not representable through this adapter |
| Durability | none |
| Automatic retry | none |

A shell variable cannot contain NUL. The same `iotox` executable can exercise the exact bounded
adapter with stdin or hex input:

```sh
printf 'a\0b\nc' | iotox --runtime "$RUNTIME" message-stdin "$PEER"
iotox --runtime "$RUNTIME" action-hex "$PEER" 6100620A63
```

Those structured paths enter the same C++ send helper and produce the same transport events. They
do not redefine native Tox text as a general binary protocol. Use IoTox lossless custom packets or
Tox file transfer for arbitrary machine data.

## Evidence ladder

Do not collapse these observations:

```text
write succeeded
    The kernel accepted FIFO bytes.

message-events: accepted
    IoTox framed a complete record, resolved the current peer, and c-toxcore
    accepted it into its local send queue with the recorded message id.

messages: outgoing
    The transport callback/journal observed that same local acceptance.

messages: receipt
    c-toxcore reported the remote friend received the corresponding text message.

application effect
    Not defined by this lane. Human text has no IoT command authority.
```

The receipt correlation exists only while c-toxcore retains its per-friend receipt entry. Upstream
c-toxcore 0.2.23 clears pending text receipts when the friend transitions offline. IoTox mirrors
that lifetime: on disconnect it removes every still-pending local message-kind correlation for the
friend and emits a diagnostic naming the abandoned count. A reconnect cannot resurrect the old
receipt, and the absence of a receipt is not proof that the peer failed to display or process text.

Inspect ingress:

```sh
iotox --runtime "$RUNTIME" peer-message-events "$PEER"
iotox --runtime "$RUNTIME" peer-message-events-watch "$PEER"
```

Inspect transport lifecycle:

```sh
iotox --runtime "$RUNTIME" peer-messages "$PEER"
iotox --runtime "$RUNTIME" peer-watch "$PEER"
```

The journals are bounded runtime projections. They can rotate, disappear at restart, and be removed
without altering authoritative product state.

## `message-events` format

One escaped line contains:

```text
unix-ms=<u64>
ingress-sequence=<u64>
kind=normal|action
disposition=accepted|rejected
error-code=<integer>
message-id=<u32>|unassigned
bytes=<size>
body="<escaped bytes>"
detail="<escaped text>"
```

The fields are rendered on one physical line. `message-id=0` is valid. The implementation stores an
explicit `has_message_id` flag so zero cannot be confused with failure.

Representative accepted event:

```text
unix-ms=... ingress-sequence=1 kind=normal disposition=accepted error-code=0 message-id=0 bytes=5 body="hello" detail="text message accepted by c-toxcore; read receipt is separate"
```

Representative offline rejection:

```text
unix-ms=... ingress-sequence=2 kind=action disposition=rejected error-code=4 message-id=unassigned bytes=5 body="waves" detail="text-message peer is not connected (c-toxcore error 3)"
```

Numeric IoTox error codes are process-contract details in rev0012. Callers should prefer the CLI
exit status and textual classification until a stable machine-readable journal schema is frozen.

## Security and local-path rules

The peer directory is a daemon-owned real directory with no group or other access. Each FIFO is a
daemon-owned mode-`0600` FIFO. The monitor rejects symlinks, regular files, ownership changes,
permission widening, and inode substitution using pre-open and post-open metadata checks.

The monitor opens a nonblocking reader and a separate nonblocking hold writer. It does not rely on
Linux's nonportable FIFO `O_RDWR` behavior. A partial or rejected record expires after bounded
inactivity so one abandoned writer cannot prefix another writer's future message.

The local surface is same-user access control, not multi-tenant isolation. A process with the daemon
user's authority can read or write the runtime tree. Stronger local principal separation requires a
future authenticated local broker or separate OS users.

## Non-goals

This contract does not provide:

- offline mail;
- persistence across daemon restart;
- automatic retry after `SENDQ` or disconnect;
- receipt persistence across a friend disconnect;
- human-message splitting;
- application acknowledgement;
- command parsing;
- capability grants;
- confidentiality from other processes running as the daemon user;
- proof that real c-toxcore networking has been exercised in this cloudtainer.
