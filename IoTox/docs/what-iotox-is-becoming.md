# What IoTox is becoming — rev0015

IoTox is becoming a self-owned, one-binary nervous system for physical things.

A device should boot into an identity it holds locally, speak securely to owner-authorized peers,
remain useful without a vendor account, and expose itself with the ordinary Unix simplicity that
makes ratox beautiful. The durable product claim is not merely “peer to peer.” It is:

> From memory, you can reach your devices; from ordinary files, you can work with them; no vendor
> key can reassign them.

## The ratox inheritance

ratox demonstrates that Tox can feel like a filesystem rather than an SDK ceremony. A peer appears as
a directory. A human or script reads a file, writes a FIFO, and observes what happened. That “just
werx” quality is not cosmetic; it is a product law.

IoTox preserves the ordinary surface but refuses to hide ambiguous semantics underneath it:

```text
ordinary write
    -> exact finite parser
    -> one typed Agent operation
    -> one serialized toxcore owner thread
    -> bounded local evidence
```

The FIFO is not a durable queue. Friendship is not authority. Local provider admission is not remote
receipt. A file arriving is not permission to execute it. The surface stays small because the inner
contracts are explicit, not because the product pretends hard states do not exist.

## What rev0015 changes

The friendship loop is now ordinary in both directions.

Incoming requests already appeared beneath `requests/<PUBLIC-KEY>/` and could be accepted or rejected
with one exact word. Established peers could be removed by public key. rev0015 adds the missing root
entrance:

```text
RUNTIME/request
```

One bounded write carries the complete Tox address and request message:

```text
<76 hexadecimal address characters><TAB><1..921 message bytes><LF>
```

That is deliberately close to ratox's joy—write one object and create the relationship—while being
more exact than a first-whitespace parser. Address checksum, nospam, own-key, and duplicate behavior
remain c-toxcore's job. IoTox records what it can honestly know and projects the resulting peer by its
public key.

The implementation also generalizes the hardened FIFO monitor so process-wide root lanes and
public-key directory lanes share one owner/mode/symlink/inode/`PIPE_BUF`/partial-record contract. The
ordinary surface is becoming a reusable façade rather than a pile of special-case readers.

## The ownership dream

Tox stays. It is a strong and unusually beautiful connection fabric: long-term peer identities,
encrypted sessions, bootstrap discovery, NAT traversal, TCP relays, custom packets, and finite file
transfer. IoTox should contribute bootstrap and relay capacity and make owner-operated contribution
easy.

But a Tox key is not the entire constitution of a device. IoTox adds:

- a stable device identity;
- a permanent RecallRoot derivation contract;
- a signed authorization ledger with roles, capabilities, epochs, and revocation;
- application signatures and replay protection above the transport;
- replaceable route identities and explicit route policy;
- no vendor recovery or reassignment key.

The permanent phrase is intentional. It makes remembered re-entry possible and offline guessing
possible. Therefore generated strength is structural, not optional. IoTox must never soften that
truth with a weak-password checkbox and a reassuring icon.

## The network dream

The same IoTox language should eventually travel as:

```text
Tox over native networking
Tox over Tor
Tox over I2P
```

Those are routes for Tox, not three unrelated application protocols. Native is the only constructed
route today. Tor and I2P remain explicit fail-closed reservations until containment and operation are
proved.

A separate future family may speak IoTox directly over Tor or I2P without Tox. That is a different
transport axis and must not be confused with routed Tox.

Owner-operated hubs, bootstrap nodes, and relays may improve offline delivery, automation, and
reachability. They must remain replaceable aids, never mandatory vendor sovereignty.

## The product shape

The full product is one executable, `iotox`.

It may contain internal C++ libraries and provider adapters, but installation should not force the
owner to understand a fleet of daemons. The one process should be able to:

- own and persist its Tox profile;
- expose its private local control socket and ratox-style tree;
- receive and send friendship requests;
- send human text and finite files;
- negotiate IoTox sessions;
- prove stable authority;
- durably admit machine commands and results;
- eventually bind harmless reads and carefully bounded effects.

The next ordinary surface is self-profile mutation. That closes another visible ratox loop while
forcing the architecture to keep typed and filesystem clients on one implementation seam.

## What success looks like

A useful IoTox device should be understandable without the company:

```text
pair it physically
remember or preserve the permanent owner phrase
inspect its identity and state locally
write ordinary commands and receive explicit results
replace the official controller with another implementation
run or choose bootstrap and relay infrastructure
rotate transport endpoints without losing device identity
re-enter as owner without asking a vendor
```

The project may remain a side project or stop before the whole product ships. Even then, a clean C++
toxcore adapter, a truthful modern ratox successor, reproducible peer fixtures, hardened local Unix
surfaces, owner-reconstructible authority research, and useful upstream fixes are worthwhile things
to leave behind.
