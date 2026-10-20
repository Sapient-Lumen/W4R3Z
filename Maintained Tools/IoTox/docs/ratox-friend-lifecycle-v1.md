# IoTox ratox-successor friendship lifecycle façade v1

**Revision:** rev0015  
**Version:** 0.15.0  
**Codename:** Ordinary Request  
**Status:** implemented in the one-binary C++20 product and exercised against the exact consumed
c-toxcore ABI mock. Separate dated evidence verifies the pinned source-linked provider and genuine
normal-native and TCP-only two-peer lifecycles on the founding host.

## 1. Purpose

This contract freezes the ordinary Unix interface for outgoing and incoming Tox friend requests and
established-friend removal. It preserves ratox's useful proposition—write one small object and inspect
a peer-shaped directory—while making two boundaries explicit:

```text
c-toxcore friend number is not durable identity
Tox friendship is not IoTox ownership or authorization
```

The stable local transport selector is the uppercase 64-hex Tox public key. A numeric friend number
is current provider evidence and compatibility input only. An outgoing invitation uses the complete
76-hex Tox address because nospam and checksum are part of that operation.

## 2. Runtime surface

At runtime root `RUNTIME`:

```text
RUNTIME/
├── friendship.help
├── request                               # mode-0600 FIFO
├── request.help
├── friend-events
├── friend-events.previous                # only after rotation
├── requests/
│   └── <64-UPPERCASE-HEX-PUBLIC-KEY>/
│       ├── public-key
│       ├── message
│       ├── message-bytes
│       ├── received-unix-ms
│       ├── request.help
│       ├── accept                        # mode-0600 FIFO
│       └── reject                        # mode-0600 FIFO
└── peers/
    └── <64-UPPERCASE-HEX-PUBLIC-KEY>/
        ├── lifecycle.help
        ├── remove                        # mode-0600 FIFO
        └── ...                           # text, command, file, and read surfaces
```

The runtime root, `requests`, request directories, `peers`, and peer directories are private,
same-user directories. All ingress objects are private mode-`0600` FIFOs. Help and evidence objects
are private regular files.

The tree is a disposable live projection. It is not c-toxcore savedata, a durable request queue, the
authorization ledger, or proof of remote observation.

## 3. Common FIFO contract

A producer MUST write one complete record and terminating LF in one `write(2)` call. The write,
including LF, MUST be no larger than the opened FIFO's actual `_PC_PIPE_BUF`.

The monitor:

```text
opens without following symlinks
requires a FIFO owned by the daemon user with mode 0600
verifies the opened inode matches the inspected inode
queries the opened FIFO's actual _PC_PIPE_BUF
requires the lane's complete maximum record to fit atomically
bounds all buffered bytes
expires abandoned partial records before another writer can complete them
rejects empty, malformed, wrong-lane, and oversized records
rescans and safely adopts a valid replacement inode
keeps readiness false when a promised root lane is missing
```

FIFO reads are byte-stream reads; reader calls do not reveal writer-call boundaries. Atomic producer
writes plus bounded LF framing are therefore part of the public contract, not an implementation
accident.

A successful `write(2)` proves only that the kernel accepted bytes. Semantic result appears later in
`friend-events` or through the structured one-binary client.

## 4. Outgoing request

The ordinary root record, excluding LF, is:

```text
<76 hexadecimal Tox address characters><TAB><1..921 message bytes>
```

Including LF:

```text
minimum = 76 + 1 + 1 + 1 = 79 bytes
maximum = 76 + 1 + 921 + 1 = 999 bytes
```

The address is the complete 38-byte Tox address:

```text
32-byte public key
4-byte nospam
2-byte checksum
```

Address hex may be uppercase or lowercase. The parser decodes exactly 76 characters and requires one
literal horizontal TAB at byte 77. It does not search for whitespace, apply shell quoting, trim,
case-fold, or invent a default message.

After TAB, every non-LF byte is message data. TAB, NUL, CR, spaces, and bytes at or above `0x80` are
preserved. LF is the local finite-record delimiter and is not sent. A client needing embedded LF must
use the framed structured local operation or a future explicitly length-bearing adapter.

Example:

```sh
printf '%s\t%s\n' "$TOX_ADDRESS" 'hello from this device' > "$RUNTIME/request"
```

The ordinary record and the typed operation:

```sh
iotox --runtime "$RUNTIME" transport-peer-request \
  <76-HEX-TOX-ADDRESS> 'bounded request message'
```

converge on one `Agent::request_transport_peer` implementation. Under the friendship lifecycle mutex,
IoTox validates local sizes, then queues `tox_friend_add` to the exclusive toxcore owner thread.

IoTox deliberately leaves these rules to c-toxcore:

```text
address checksum
own public key
already sent or already friend
changed nospam state
allocation/provider failure
```

On local provider admission, IoTox records the public-key prefix, current friend number, and a
`request-send disposition=requested` lifecycle event. It reconciles the current public-key peer
projection. This means only:

```text
the local Tox profile accepted tox_friend_add state
```

It does not mean:

```text
the remote peer received the request
the remote peer accepted it
the peer is online
an IoTox session is confirmed
any IoTox role or capability was granted
```

No durable offline outbox, retry, expiry, or cancellation is implied by the FIFO.

## 5. Incoming request projection

A c-toxcore friend-request callback supplies:

```text
32-byte sender public key
bounded request message bytes
```

It does not add a friend and does not create a provider-owned pending-request object. IoTox retains a
bounded in-memory record and transactionally publishes one complete request directory. The directory
becomes visible only after its regular files and FIFOs exist.

The projected message is untrusted remote input. Human rendering is escaped. It must not be passed to
a terminal, shell, path parser, or command evaluator without independent policy.

Incoming request records are live-only in v1. Restart discards them because c-toxcore does not expose
a durable pending-request inventory. Durable history, blocking, spam policy, and replay handling are
separate future decisions.

## 6. Accept

`requests/<KEY>/accept` accepts exactly:

```text
accept<LF>
```

IoTox requires the same public key to remain present in its live request inbox. If the record
disappeared or was already decided, the operation fails `not_found` and does not add a friend.

On a valid pending record, the toxcore owner thread calls:

```c
tox_friend_add_norequest(tox, public_key, &error)
```

IoTox withdraws the request projection, reconciles the public-key peer projection, and records local
provider evidence.

Acceptance means only:

```text
this local Tox profile now recognizes the sender as a transport friend
```

The signed authorization ledger is unchanged.

## 7. Reject

`requests/<KEY>/reject` accepts exactly:

```text
reject<LF>
```

It requires the same key to remain in the live inbox, then withdraws that IoTox record and runtime
directory.

c-toxcore exposes no persistent pending-request object and no remote rejection operation. Rejection
therefore means only:

```text
IoTox no longer presents this received callback record
```

It does not notify, block, or revoke the remote peer. IoTox deliberately does not imitate a historical
add-then-delete rejection path.

## 8. Established peer removal

`peers/<KEY>/remove` accepts exactly:

```text
remove<LF>
```

The public key, not the directory's numeric friend number, is the mutation target. The local control
protocol carries the 32-byte key in operation 30, `transport-peer-remove-key`.

Inside one queued operation on the exclusive toxcore owner thread, IoTox performs:

```c
friend_number = tox_friend_by_public_key(tox, public_key, &lookup_error);
tox_friend_delete(tox, friend_number, &delete_error);
```

Lookup and deletion MUST NOT be split into independently queued operations. c-toxcore may reuse a
vacated friend-number gap. The one-turn operation either removes the current friend for the requested
key or fails without retargeting.

The adapter captures the public key before deletion so cleanup, runtime withdrawal, session cleanup,
and evidence remain bound to the intended key after the provider entry is gone.

Deletion is local and does not notify the remote friend. It neither revokes an IoTox principal nor
erases authority history or application data.

## 9. Lifecycle evidence

`friend-events` is a bounded append journal with at most one previous generation. Records include:

```text
source=toxcore operation=request-received public-key=...
source=local-fifo operation=request-send public-key=... disposition=requested
source=local-fifo operation=request-send public-key=unknown disposition=rejected
source=local-fifo operation=request-accept public-key=... disposition=accepted
source=local-fifo operation=request-reject public-key=... disposition=accepted
source=local-fifo operation=peer-remove public-key=... disposition=accepted
source=toxcore operation=peer-added public-key=... friend-number=...
source=toxcore operation=peer-removed public-key=... friend-number=...
```

A malformed outgoing record can carry three levels of identity evidence:

1. no trustworthy key prefix: journal `public-key=unknown` explicitly;
2. exact decodable 64-hex public-key prefix but malformed remainder: record that key as a hint;
3. complete address: record provider disposition against the decoded public key.

IoTox never fabricates an all-zero public key to satisfy the event shape.

Evidence strength is layered:

```text
FIFO write returned             kernel admitted local bytes
parser/lifecycle event          IoTox accepted or rejected one bounded record
provider disposition            c-toxcore accepted or rejected local mutation
provider callback/inventory     live local transport state converged
remote observation              not supplied by this surface
IoTox authority change          never performed by friendship lifecycle
```

The journal is unsigned, rotating, same-user operational evidence. It is not durable audit authority.

## 10. Concurrency and ordering

The root request worker, incoming-request workers, established-peer FIFO worker, structured control
socket, and transport callbacks converge on typed Agent lifecycle methods. rev0015 uses one Agent
friendship-lifecycle mutex, so request/accept/reject/remove decisions are serialized before entering
the provider owner thread.

Only the owner thread may call toxcore. FIFO workers own framing and path hardening only; they never
hold or call `Tox*`, execute machine operations, or mutate the authorization ledger.

Local control timeout does not automatically prove provider cancellation. The general owner-thread
rule remains: a caller must not infer that timed-out work could not later start unless the command
reports pre-start cancellation.

## 11. Restart and persistence

The runtime request tree and `friend-events` journal are disposable. Incoming requests are not
restored after restart. Established friends are restored only through c-toxcore savedata.

A successful add or delete must eventually be reflected in safely replaced savedata. Power-cut
timing, full disk, and immediate mutation persistence remain product hazards until exercised against
official c-toxcore and target filesystems. Runtime projection alone is never persistence evidence.

The authority ledger survives independently. Transport request, acceptance, rejection, and removal
do not rewrite it.

## 12. Security boundary

The runtime directory is a same-user interface, not a privilege boundary against malware running as
the daemon user. Private modes and no-follow/type/inode checks prevent common accidental and
cross-user path abuse; they do not defend against a fully compromised same-user process deliberately
selecting a peer or writing a syntactically valid invitation.

The application security boundary remains:

```text
Tox friendship and connection
    -> IoTox HELLO/transcript confirmation
    -> stable-principal proof
    -> signed authorization ledger
    -> operation capability and durable command policy
```

Friendship lifecycle never skips those layers.

## 13. Required tests

The owned facility MUST cover:

```text
private root request, request-decision, and peer-removal FIFO projection
required root-lane startup and live readiness
transactional incoming-request directory publication
exact 76-hex + TAB + 1..921-byte outgoing grammar
upper/lower address hex and non-LF message byte preservation
minimum/maximum record acceptance
separator, hex, empty, short, oversized, and partial-record rejection
actual PIPE_BUF sufficiency and one-write contract
symlink, regular-file, owner, mode, inode, and replacement handling
explicit keyless malformed evidence
shared typed/FIFO outgoing operation
accept requires a live matching request
reject removes request without adding a peer
accept and outgoing request create public-key peer projections
remove withdraws only the intended public-key peer
friend-number gap reuse cannot retarget removal
unknown key and duplicate decision return not_found
friend-events append, escape, bound, and rotate
status counters remain coherent before, during, and after service lifecycle
authorization ledger sequence/head remain unchanged
separate-process literal root request, reject, and remove through one binary
```

The exact provider double proves only the consumed ABI and controlled event semantics. Official
source-linked and two-genuine-peer tests remain mandatory external gates.

## 14. Non-goals in v1

```text
durable incoming or outgoing request queue
remote request/rejection/acceptance receipt
request block list or spam reputation
compound remove-and-revoke
friendship-based authority
vendor recovery or reassignment
embedded-LF line record
Tor/I2P route containment
public-network proof
```

A later contract may add these only with explicit semantics and an ADR. v1's simplicity is deliberate:
write one exact invitation, inspect the key, write one exact decision, and read what actually happened.
