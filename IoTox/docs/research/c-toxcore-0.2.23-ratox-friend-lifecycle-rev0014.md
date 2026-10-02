# Research note — c-toxcore 0.2.23 and ratox friendship lifecycle, rev0014

- Reviewed: 2026-08-14
- IoTox revision: rev0014
- Method: pinned release/header reading plus ratox README/implementation reading
- Evidence class: upstream source contract and static implementation analysis; no official
  c-toxcore provider executed in this cloudtainer

## Primary sources

```text
https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
https://toktok.ltd/spec.html
https://github.com/pranomostro/ratox
https://raw.githubusercontent.com/pranomostro/ratox/master/README
https://raw.githubusercontent.com/pranomostro/ratox/master/ratox.c
```

The dependency pin is c-toxcore tag `v0.2.23`, released 2026-06-03. The release reports a critical
bug fix and other stabilization work. IoTox therefore treats source pinning, reproducible builds,
rapid update ability, and containment as product obligations.

Ratox is read as interface history and implementation evidence. It is not the current c-toxcore API
contract and no ratox source is imported into IoTox.

## 1. One Tox instance must be serialized

The public header permits independent `Tox` instances on separate threads but requires API access to
one instance to be synchronized. Getter-size/read pairs can also lose validity after intervening
mutation.

IoTox consequently performs iteration, callback registration, friend lookup/add/delete, inventory,
profile, text, packets, files, and savedata on one exclusive owner thread. FIFO workers and the local
control socket submit typed operations; they never call a raw `Tox*`.

## 2. Tox address, public key, and friend number are different objects

Pinned public sizes and limits:

```text
public key                    32 bytes
Tox address                   38 bytes
  public key                  32 bytes
  nospam                       4 bytes
  checksum                     2 bytes
maximum friend-request body  921 bytes
```

`tox_friend_add` consumes the full address and a nonempty bounded message. The address is required so
nospam and checksum can be validated.

`tox_friend_add_norequest` consumes only the public key. The header names accepting a received friend
request and mutual addition under one controlling entity as intended uses.

A friend-request callback supplies the sender public key and message. It does not add a friend and it
does not expose a persistent provider request handle.

A `Tox_Friend_Number` is local to one `Tox` object. The header warns that applications must not rely
on numeric patterns, that numbers may differ after save/reload, and that a deleted gap may be filled
by a later addition. Numeric friend number is therefore live provider state, not durable identity.

## 3. Outgoing request contract

`tox_friend_add` provides typed failures for conditions including:

```text
null input
request too long
empty request
own key
already sent or already a friend
bad address checksum
changed nospam for an existing key
allocation failure
```

This supports one typed IoTox operation carrying exact 38-byte address and exact bounded message.
A future ordinary FIFO must converge on that operation rather than parsing a lossy shorthand.

The Tox protocol documentation says the user/application must authenticate the Tox ID out of band;
Tox cannot prevent replacement of an unauthenticated address before friend addition. IoTox must not
claim that a syntactically valid address proves the intended physical device.

## 4. Incoming request and rejection

The friend-request callback is application notification. The provider does not expose a list or
object that can later be deleted as “rejected.” The Tox protocol describes refusal as ignoring the
request.

IoTox must therefore own any operator-visible request inbox. In rev0014 it is bounded, live, and
cleared on restart. `reject` deletes only that IoTox record. It does not need or pretend to perform a
provider mutation.

The protocol notes that requests are resent with increasing intervals and that the sender cannot know
whether the receiver refused. IoTox must not offer a remote rejection acknowledgement it cannot
observe.

## 5. Acceptance

The correct primitive for a received request is:

```c
tox_friend_add_norequest(tox, sender_public_key, &error)
```

The operator decision must remain bound to the same live sender key that produced the callback. A
stale request directory must not become an unrestricted administrative add by key.

Acceptance creates a transport friend only. c-toxcore APIs express no IoTox stable principal, role,
capability, owner, firmware authority, or actuator authority.

## 6. Public-key-bound deletion

The relevant provider functions are:

```c
tox_friend_by_public_key(tox, public_key, &error)
tox_friend_delete(tox, friend_number, &error)
```

Because friend numbers may be reused, this sequence is unsafe when split across independently queued
operations:

```text
lookup key A -> number 7
A disappears
key B is added -> number 7
later delete number 7
```

rev0014 adds the exact lookup symbol to runtime and linked provider tables. The transport adapter
performs lookup and delete inside one owner-thread command. It returns the removed friend number only
as evidence and captures the public key before deletion for normalized events.

The exact mock reuses the lowest available friend slot so the regression facility exercises this
upstream warning instead of accidentally relying on append-only fake numbers.

## 7. Deletion is local and silent

The public header states that `tox_friend_delete` does not notify the friend. The local client appears
offline afterward and can no longer communicate through that friendship, but there is no remote
application acknowledgement.

IoTox evidence may truthfully say:

```text
local provider accepted deletion of the current friend for public key X
```

It may not say:

```text
remote peer deleted us
remote user saw the removal
a stable IoTox principal was revoked
old application data was erased
```

Transport removal and authorization revocation are separate operations.

## 8. Ratox precedent

Ratox's README exposes:

```text
request/in                 send Tox ID plus request message
request/out/<ID>           write a small value to decide an incoming request
<friend-key>/remove        write a small value to remove a friend
```

This proves the practical value of an ordinary scriptable lifecycle surface.

Ratox's implementation reads one-byte truth values. Per-friend removal uses the numeric friend number
already held in its in-process object. Its incoming response path calls `tox_friend_add_norequest` for
both acceptance and rejection, then immediately deletes on rejection.

IoTox preserves the gesture but strengthens the semantics:

```text
word tokens rather than opaque truthy bytes
public-key directories rather than operator-visible numeric identity
accept only with a matching live callback record
reject by forgetting the record, without temporary add/delete
remove by key-bound lookup/delete in one owner-thread turn
bounded explicit lifecycle evidence
friendship and authority kept separate
```

## 9. Mapping to rev0014 code

```text
include/iotox/toxcore/abi.hpp
  exact friend-by-public-key error and function types

src/toxcore/dynamic_library.cpp
src/toxcore/linked_api.cpp
  runtime and official-header provider population

src/toxcore/transport.cpp
  one owner-thread public-key lookup plus deletion

include/iotox/local/runtime_tree.hpp
src/local/runtime_tree.cpp
  request/peer lifecycle projection, help, status, and bounded journal

src/agent.cpp
  same-key lifecycle serialization, request ownership, FIFO/control convergence,
  projection/session cleanup, authority non-mutation

src/local/control_protocol.cpp
  protocol minor 15 and operation 30 transport-peer-remove-key

tests/mock_toxcore.cpp
  exact lookup symbol and lowest-gap friend-number reuse
```

## 10. Design conclusions

1. Keep Tox friendship. It is the reachability relationship the product wants.
2. Keep the ordinary ratox gesture.
3. Use public key as the local lifecycle selector.
4. Treat friend number as ephemeral evidence.
5. Accept a request only while its live callback record remains.
6. Reject by local ignore, not temporary provider mutation.
7. Perform lookup and delete in one serialized provider operation.
8. Do not claim remote acknowledgement for rejection or deletion.
9. Do not couple friendship to the signed authorization ledger.
10. Re-review these conclusions whenever the c-toxcore pin or official headers change.

## 11. Evidence boundary

This review shaped executable code and exact-double tests. It does not prove that the dynamic table,
callback timing, savedata mutation, public network, or remote client behavior matches official
c-toxcore in this cloudtainer. The next networked CLI must compile the pinned source, run two genuine
peers, and test request/accept/remove across restart and numeric-handle changes.
