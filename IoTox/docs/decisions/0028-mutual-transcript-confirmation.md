# ADR 0028: Application traffic waits for mutual transcript confirmation

**Status:** accepted and implemented in rev0008

## Context

rev0007 established one canonical HELLO for every true Tox online epoch. HELLO answers whether
both transport endpoints advertise a compatible IoTox protocol range, feature set, frame
ceiling, and finite-file ceiling. A locally computed match is not yet a mutually committed
machine session: the two implementations could retain different advertisements, derive
different selected values, or accidentally admit application traffic at different points.

Tox lossless custom packets provide a reliable ordered packet lane after toxcore accepts a
packet. That transport property does not define the IoTox handshake boundary, nor does it turn
a Tox friendship into application authority. IoTox needs one exact, inspectable commit barrier
before any later machine message can enter the application dispatcher.

## Decision

Capability-session-v1 has two messages in one lossless custom-packet lane:

```text
HELLO         exact 64-byte IHL1 advertisement, sequence 1
CAPABILITIES  exact 256-byte ICF1 transcript confirmation, sequence 2
```

Each endpoint sends one canonical HELLO for the current online epoch. After both HELLOs are
valid and compatible, each sends a CAPABILITIES confirmation. Endpoints are canonically
ordered by their raw 32-byte Tox public keys. The confirmation binds:

```text
both transport public keys
both exact HELLO payloads
both session nonces
selected protocol version
shared feature mask
negotiated frame-payload ceiling
negotiated finite-file ceiling
sender role in canonical key order
```

The outer confirmation frame must use the negotiated protocol version, a nonzero message ID,
zero flags and expiry, sequence two, and a correlation ID equal to the peer's first accepted
HELLO message ID. Reserved payload bytes must be zero.

The first local HELLO and confirmation records are canonical for the epoch. Their message IDs
are chosen once before the first send attempt and are reused after a local send rejection. The
first accepted peer HELLO and confirmation bodies are frozen. Byte-identical retries are
idempotent; changed same-epoch transcript material is a protocol conflict and closes the
application gate.

A packet that toxcore accepted into its lossless queue is not retransmitted by IoTox merely
because no reply has yet appeared. `TOX_ERR_FRIEND_CUSTOM_PACKET_SENDQ` and a temporarily
offline peer are different: those failures mean the packet did **not** enter toxcore's send
queue. The agent may retry that frozen unsent protocol record after subsequent toxcore
iterations. All retries retain the same message ID and exact bytes. A true offline transition
ends the epoch; the next online epoch receives a new nonce and new IDs.

IoTox admits a non-session application frame only when both confirmations have been accepted
and the frame:

```text
uses the exact negotiated protocol version
has a nonzero message ID
fits the negotiated payload ceiling
is neither HELLO nor CAPABILITIES
```

The resulting state is `confirmed` and renders:

```text
application-ready=1
authorization=none-transport-session-only
```

## Consequences

IoTox has a precise transport-session commit point rather than using “compatible” as a synonym
for “ready.” Incoming and locally injected IoTox application frames share the same gate, so the
raw lossless operator seam cannot bypass establishment. Malformed, pre-confirmation,
version-mismatched, oversized, or handshake-type application attempts fail closed.

The fixed v1 confirmation carries exact transcript bytes rather than introducing another hash
or signature primitive. It remains directly inspectable, reproducible, fuzzable, and well
below c-toxcore's custom-packet limit. A future signed authorization exchange can hash and bind
this canonical transcript under a stable IoTox application identity.

The confirmation is not an application signature and adds no independent owner authentication
beyond the underlying Tox friendship. Stable device identity, owner/controller identity,
roles, capabilities, delegation, revocation, and command signatures belong to the independent
authorization ledger. No actuator or firmware path may treat `confirmed` as authority.


## Local enqueue and retry companion decision

The exact retry and local-acceptance classification is governed by
[ADR 0029](0029-custom-packet-acceptance-and-retry.md). In particular, a transient local
`SENDQ` rejection means toxcore did not accept the record; it does not authorize changing the
record, assigning a new message ID, or resending a record that toxcore already accepted.
