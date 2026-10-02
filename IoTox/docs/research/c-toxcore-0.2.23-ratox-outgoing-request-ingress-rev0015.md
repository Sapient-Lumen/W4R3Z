# Research note — c-toxcore 0.2.23 and ratox outgoing-request ingress, rev0015

- Review date: 2026-08-14 America/New_York
- IoTox revision: rev0015
- Scope: the ordinary outgoing friend-request entrance only
- Primary upstream contract: c-toxcore v0.2.23

## 1. Sources reviewed

```text
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
https://raw.githubusercontent.com/pranomostro/ratox/master/ratox.c
https://raw.githubusercontent.com/pranomostro/ratox/master/ratox.1
https://raw.githubusercontent.com/pranomostro/ratox/master/README
https://man7.org/linux/man-pages/man7/fifo.7.html
https://man7.org/linux/man-pages/man7/pipe.7.html
https://pubs.opengroup.org/onlinepubs/9699919799/functions/write.html
https://pubs.opengroup.org/onlinepubs/9699919799/functions/fpathconf.html
```

The c-toxcore source is pinned rather than inferred from a moving branch. Ratox is reviewed as the
human-interface precedent, not as a current provider contract.

## 2. c-toxcore facts that bind the local record

The pinned header states:

- one Tox instance may be used by several threads only when access is synchronized; no more than one
  API function may operate on one instance at a time (lines 56–67);
- a Tox address is 38 bytes: 32-byte long-term public key, 4-byte nospam, and 2-byte checksum (lines
  249–267);
- the maximum friend-request message length is 921 bytes (lines 287–293);
- an outgoing message must contain at least one byte and no more than the maximum (lines 857–860);
- `tox_friend_add` consumes a complete `TOX_ADDRESS_SIZE` address and the caller-supplied message
  bytes/length (lines 872–882);
- provider errors distinguish empty/oversized messages, own key, already sent/already friend, bad
  checksum, changed nospam, and allocation failure (lines 806–853);
- friend numbers are lifecycle-local handles: gaps may be reused and numbers may change after
  savedata reload (lines 862–867);
- accepting an incoming request is a distinct operation, `tox_friend_add_norequest`, taking only the
  32-byte public key (lines 884–902).

Therefore an ordinary outgoing-request record must carry all 38 address bytes and a nonempty bounded
message. It cannot substitute a public key, a friend number, or an application principal.

IoTox keeps the provider call on its exclusive toxcore owner thread. The root FIFO and typed control
operation converge before `tox_friend_add`, so local syntax does not create a second threading or
friendship model.

## 3. What ratox proved

ratox describes itself as a Tox client whose interface consists only of FIFOs, files, and directories.
Its manual exposes one global request slot. Its README demonstrates:

```text
echo LONGASSID yo dude add me > in
```

The implementation reads up to `PIPE_BUF`, finds the first whitespace, splits address from message,
uses `"ratox is awesome!"` as an initial default, calls `tox_friend_add`, creates the friend
projection, saves data, and logs success (`ratox.c` lines 1727–1773).

The important inheritance is not that exact parser. The important inheritance is that initiating a
secure peer relationship can feel like writing one ordinary object. That simplicity is worth
preserving.

## 4. What IoTox deliberately changes

### 4.1 Exact boundary instead of whitespace search

The v1 record uses one TAB at one fixed byte. Address spaces cannot occur because the address is
hexadecimal; message spaces remain untouched. The parser never searches for arbitrary whitespace and
never uses NUL termination or `strlen` to discover message length.

### 4.2 No default request message

The provider requires at least one message byte. IoTox requires the caller to supply it. A hidden
default would make an incomplete record produce a valid network mutation and make audit evidence less
specific.

### 4.3 Full-address syntax, public-key projection

The input contains the 76-character complete address. After successful decode/provider admission,
the resulting runtime peer directory is named by the uppercase 64-character public key. The full
address is an invitation target; the public key is the stable transport selector after addition.

### 4.4 Binary message field with one local delimiter

After TAB, every non-LF byte belongs to the message. TAB, NUL, CR, and high bytes survive the parser.
LF is reserved as the finite FIFO record delimiter and is not sent. Callers needing embedded LF must
use a future framed/length-bearing structured operation rather than pretending the line adapter can
carry it.

### 4.5 Evidence remains layered

```text
write(2) success
    kernel admitted bytes
parser event
    one bounded local record was accepted or rejected
request-send disposition=requested
    tox_friend_add accepted local state
peer projection
    current local friend-list presentation includes the public key
remote acceptance
    not proved by any of the above
IoTox authority
    unchanged by all friendship events
```

## 5. FIFO and atomicity consequences

A FIFO is a byte stream. Reader reads do not preserve writer call boundaries. POSIX atomicity applies
to writes no larger than `PIPE_BUF`; the portable lower bound is insufficient for the largest IoTox
request record, so the daemon queries the actual FIFO with `fpathconf(_PC_PIPE_BUF)`.

The maximum record is:

```text
76 address hex + 1 TAB + 921 message + 1 LF = 999 bytes
```

The hardened monitor refuses a lane whose actual `PIPE_BUF` is less than 999. It opens with
`O_NOFOLLOW`, verifies the opened inode against `lstat`, requires daemon ownership and mode 0600,
holds both FIFO ends to avoid spurious EOF churn, expires incomplete records, rejects overflow, and
rescans replacement inodes under the same contract.

The one-write rule is a producer obligation. `printf` commonly satisfies it for small text but the
formal contract is one `write(2)`, not one shell command or one high-level stream flush.

## 6. Error and identity model

The exact parser can know three different amounts:

1. no trustworthy public-key prefix;
2. a valid 32-byte public-key prefix but malformed remaining record;
3. a complete decoded 38-byte address rejected or accepted by c-toxcore.

The lifecycle journal represents case 1 explicitly as `public-key=unknown`. It never inserts a fake
all-zero key. Case 2 may record the trustworthy uppercase public-key hint while preserving the parse
failure. Case 3 records the provider disposition and friend number as transient evidence.

The current dynamic mock does not claim to reproduce all checksum/nospam behavior. Unit tests freeze
IoTox's parser and process plumbing; official source-linked and genuine-peer gates remain required to
validate the complete provider behavior.

## 7. Applied code map

```text
include/iotox/local/friend_request_fifo.hpp
src/local/friend_request_fifo.cpp
    exact finite record constants and decoder

include/iotox/local/peer_fifo.hpp
src/local/peer_fifo.cpp
    generalized public-key-directory/root-lane monitor

src/local/runtime_tree.cpp
    root request FIFO, help, status, and keyless lifecycle rendering

src/agent.cpp
    one shared request operation for structured and ordinary ingress

tests/test_friend_request_fifo.cpp
    exact bytes, bounds, direct root lane, replacement, required-lane failure

tests/test_agent.cpp
    malformed and successful root records, journal and status

tests/test_cli_process.cpp
tools/run-mock-node.sh
    separate-process one-binary ordinary-write proof
```

## 8. Remaining unknowns

- official c-toxcore has not yet been built or run in this cloud container;
- two genuine peers have not proved remote request delivery or acceptance;
- no durable request outbox, expiry, cancellation, or retry exists;
- `friend-events` is bounded process-local evidence, not a signed audit store;
- embedded LF cannot cross the line adapter;
- the exact mock's global next-send fault injection is order-sensitive and should become
  peer/operation-bound before more concurrent fixture scenarios are added;
- immediate persistence after every friendship mutation still needs genuine full-disk and power-cut
  evidence on target filesystems.

## 9. Research conclusion

The correct successor move is not to abandon ratox's request slot. It is to make the slot exact.
rev0015 now preserves the ordinary write while carrying the complete provider input, respecting the
real FIFO boundary, keeping one toxcore owner thread, and refusing to turn local admission into a
claim about the remote peer or application authority.
