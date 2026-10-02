# ADR 0385: Add person delivery cards and signed message fanout

Status: accepted
Date: 2026-09-19

## Context

ADR 0382 selected IoTox-owned self-machine multidevice instead of relying on
Tox multidevice. ADR 0383 made a private owner-signed self-swarm roster real.
ADR 0384 added local roster floors, explicit roster fanout, and live alias-route
proof.

The next user goal is broader than “my laptop is in my self swarm”:

```text
Anyone who knows my key should be able to send one message to me, and it
should reach all of my devices.
```

Toxcore already has valuable friend messaging, conferences, and groupchat APIs,
but those are transport/client primitives. They do not by themselves provide an
IoTox person identity with many independently revocable devices. Copying one
Tox savedata/private key across machines would make “one key” feel simple, but
one stolen machine would become the whole person. Using one Tox key per device
keeps revocation possible, but it gives contacts several device addresses
instead of one person address.

IoTox therefore needs a person layer above Tox routes and above the private
self-swarm roster.

## Decision

Add a native `iotox person ...` surface with two v1 records.

### Public person delivery card

`person card-recall-stdin SELF_SWARM_ROSTER PERSON_CARD [verification options]`
derives a public card from a verified private self-swarm roster and signs it
with the RecallRoot-derived owner/person key:

```text
iotox-person-delivery-card-v1
person=OWNER_PUBLIC_KEY_HEX
generation=N
roster-digest=SELF_SWARM_ROSTER_DIGEST_HEX
route-count=N
route=TOX_ROUTE_PUBLIC_KEY_HEX
...
signature=OWNER_SIGNATURE_HEX
```

The route keys are active roster Tox public keys, sorted and deduplicated. The
card deliberately excludes private machine aliases, stable authority principals,
roles, capabilities, profile bindings, sudo policy, and retired routes.
It also deliberately excludes route class policy. The public card is a
delivery-key list, not a native/Tor/I2P fallback grant. Rendered inspections
and fanout plans disclose `route-policy=not-carried-by-person-card` and point
operators at route-set v2 or explicit runtime configuration for route-class
selection.

`person card-inspect PERSON_CARD` verifies and renders the card.

### Person message envelope

`person message-plan-recall-stdin PERSON_CARD TEXT` and
`person message-plan-hex-recall-stdin PERSON_CARD HEX` read the sender's
RecallRoot phrase from stdin, sign one bounded person-message envelope, and
print exact `iotox message-hex key:ROUTE PAYLOAD_HEX` commands for every route
in the recipient card.

`person message-fanout-recall-stdin PERSON_CARD TEXT` and
`person message-fanout-hex-recall-stdin PERSON_CARD HEX` do the same signing,
then resolve every recipient route key to a current Tox friend before sending
anything. If any route is not a friend, the command fails before the first send.
If all routes resolve, the same signed envelope is sent over the existing Tox
text-message lane to each route.

`person message-verify-hex PAYLOAD_HEX` verifies a received envelope independent
of the transport route that carried it:

```text
iotox-person-message-v1
from-person=SENDER_PERSON_PUBLIC_KEY_HEX
to-person=RECIPIENT_PERSON_PUBLIC_KEY_HEX
nonce=NONCE_HEX
message-id=MESSAGE_DIGEST_HEX
body-hex=BODY_HEX
signature=SENDER_SIGNATURE_HEX
```

The v1 body limit is small enough that the complete canonical envelope stays
below the ordinary Tox text-message maximum. This deliberately avoids a new
daemon wire opcode while making the person layer usable through existing
`message-hex`.

## Consequences

IoTox now has a concrete answer for “send to my person key and reach all active
device routes,” as long as the sender has a current card and every listed route
is already a Tox friend.

The first version remains intentionally narrow:

- no shared Tox private key across self machines;
- no private roster publication;
- no automatic background card refresh;
- no durable all-device delivery guarantee;
- no aggregate person-level read receipt;
- no duplicate suppression across recipient devices;
- no group membership, transcript ordering, or group policy yet; and
- no daily device-delegated sender keys yet, so signing still uses the
  RecallRoot owner/person key.

That last point is an ergonomics and safety frontier. Daily chat should not
require typing RecallRoot for every message. The next layer should add
person-signed device sender delegations with clear revocation and freshness
floors.

## Evidence

The construction evidence is native and tested:

- `include/iotox/person_multidevice.hpp` and `src/person_multidevice.cpp`
  implement canonical delivery-card and message-envelope codecs, hashes,
  signatures, no-clobber card storage, and tamper rejection;
- `src/cli.cpp` exposes `iotox person help`, card create/inspect,
  message-plan, message-fanout, and message-verify commands;
- `tests/test_person_multidevice.cpp` covers public-card redaction, active-route
  derivation, retired-route exclusion, no-clobber card files, message
  signing/verification, tamper rejection, and body bounds;
- `tests/test_human_cli.py` creates a self-swarm, commits a floor, derives a
  public card, plans person fanout, and verifies the produced payload; and
- `tests/test_docs_coherence.py` keeps the `help person` surface visible.

Docs:

- `docs/person-multidevice.md`;
- `docs/self-mode.md`;
- `docs/roadmap.md`.
