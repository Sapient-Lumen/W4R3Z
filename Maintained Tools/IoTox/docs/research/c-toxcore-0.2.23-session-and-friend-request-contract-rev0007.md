# c-toxcore 0.2.23 session and friend-request contract — rev0007

**Reviewed:** 2026-08-13  
**Scope:** the exact upstream contracts consumed by IoTox's friend-request inbox, public-key
peer model, connection epochs, custom-packet session, and source-linked build path.

## Primary sources

```text
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox_options.h
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/CMakeLists.txt
https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
https://toktok.ltd/spec.html
https://git.2f30.org/ratox/file/README.html
https://git.2f30.org/ratox/log.html
```

The source review is pinned to tag `v0.2.23`; conclusions below should be rechecked when that
pin changes.

## 1. One serialized owner for one `Tox*`

The public header permits independent Tox instances on separate threads but requires calls on
one instance to be synchronized. It also warns that getter size/read pairs can be invalidated
by intervening mutations. IoTox therefore keeps one thread as the exclusive owner of the
`Tox*`, performs `tox_iterate` and every API call there, and passes bounded typed commands and
events across the boundary.

This is stronger and easier to audit than allowing arbitrary services to call toxcore under a
large shared mutex. The runtime tree, local socket, file policy, session registry, and future
authorization ledger never receive a raw `Tox*`.

## 2. Incoming friend request callback

The friend-request callback supplies:

```text
Tox instance
requesting public key pointer
message pointer
message length
user data
```

The public key is exactly 32 bytes. The message is bounded by
`TOX_MAX_FRIEND_REQUEST_LENGTH`, currently 921 bytes. Callback pointers belong to the callback
invocation; IoTox therefore copies the key and message before returning. This pointer-lifetime
conclusion is an implementation-safety inference from the callback API, not a promise that the
memory remains usable afterward.

Receiving the callback does not add the peer. Acceptance is the application's decision and
uses `tox_friend_add_norequest` with the public key. The request message is presentation/pairing
input only; it does not authenticate an IoTox owner or command.

c-toxcore savedata is not documented as a pending-friend-request mailbox. rev0007 therefore
labels its request inbox live and transient instead of pretending `/run` survives a crash.

## 3. Public key is the durable operator selector; friend number is not

`tox_friend_get_public_key` returns the 32-byte key associated with a local friend number, and
`tox_friend_by_public_key` resolves the reverse mapping. The API explicitly warns that friend
numbers are local indices and can change after savedata is reloaded. IoTox consequently:

- keys runtime peer/request directories by uppercase public key;
- accepts public-key selectors at the CLI;
- resolves to a current friend number only at the toxcore boundary;
- treats friend numbers in logs/protocol control as process-local details.

Neither key form is yet the stable application-level IoTox device identity. That belongs to
the future independent authorization ledger and endpoint-binding design.

## 4. Friend acceptance is not connection establishment

A newly added friend begins offline, and the friend-connection-status callback is not invoked
merely because the friend was added. IoTox must wait for a real transition to TCP or UDP before
starting an online session. rev0007's process fixture exposed exactly this distinction: an
operator accept succeeded before the mock's next iterate delivered the online callback.

The online epoch therefore begins only on `NONE -> TCP|UDP`. A continuous TCP/UDP path change
updates route presentation without starting a new epoch. A transition to `NONE` ends the epoch.
The next real reconnect creates a fresh local nonce and HELLO transcript.

## 5. Reliable custom packets are the machine-session lane

The v0.2.23 API accepts application lossless packet identifiers `69` and `160..191`. The
published maximum custom-packet size is 1,373 bytes. Lossless packets are reliable and ordered
within their lane. IoTox reserves `0xA0` (160) and uses a 41-byte outer frame, leaving exactly
1,332 bytes for bounded protocol payload.

rev0007 uses this lane for a fixed 64-byte HELLO. Human normal/action messages stay in the Tox
message lane, and finite bulk objects stay in Tox file transfer. This avoids depending on
ordering between unrelated lanes and avoids inventing fragmentation for firmware-sized data.

The first valid HELLO payload is frozen for the online epoch. Byte-identical retries are
idempotent; a changed payload in the same epoch is a protocol conflict. Required feature
negotiation fails closed. A compatible result is transport capability only, never authority.

## 6. Source-linked build target

The official v0.2.23 CMake project creates `toxcore_static` when static building is enabled.
IoTox's standalone path pins the upstream release and libsodium, adds the source tree, and
links that target into the single product executable. The linked provider must see canonical
upstream headers; fallback declarations are allowed only for the exact runtime ABI mock and
explicit dynamic integration.

The cloudtainer could not resolve the upstream download hosts during this revision. The fetch
failure is retained as evidence and does not count as a source-linked or real-network pass.

## 7. Tor/I2P route implications

The public 0.2.23 `tox_options.h` declares
`tox_options_set_experimental_disable_dns`. Its documented purpose is to reject hostnames and
let a client resolve endpoints itself, including the Tor use case. It is useful evidence that
leak-aware routing was contemplated upstream, but the name and documentation also mark it as
experimental: IoTox must pin and re-review it rather than treating it as a permanent ABI
promise. rev0007's linked provider references the public setter; the dynamic mock exports the
same consumed symbol.

The Tox protocol specification and options API support TCP relay/proxy-oriented operation, but
Tox's normal native path also uses UDP/DHT behavior. A future Tox/Tor route must therefore be
an explicit TCP-only, proxy/tunnel, relay topology with DNS/UDP leak tests and no silent native
fallback. Tox/I2P likely needs similarly explicit stream tunnels and overlay-reachable
bootstrap/relay infrastructure. These are route experiments for Tox, not reasons to merge
direct Tor/I2P transports into the current enum.

## 8. ratox precedent retained

ratox exposed incoming requests as filesystem/FIFO objects and required an explicit operator
decision. IoTox keeps that simple mental model while replacing ambiguous FIFO-only semantics
with:

```text
bounded callback copy
public-key keyed live record
transactional private projection
versioned local request/response
separate accept and reject operations
explicit transport-only authority label
```

The result should feel ordinary at the shell without claiming more durability or trust than
exists.

## Evidence classification

```text
source-reviewed:        upstream callback, friend, connection, packet, build contracts
compiled/tested:        owned C++ inbox, accept/reject, session registry, runtime projection
exact-mock-ABI-tested:  callback copy, explicit decision, online epoch, HELLO echo
source-linked:          not executed in this cloudtainer
real-peer/network:      not executed in this cloudtainer
```
