# 0390 — Add normal Tox compatibility bridge

Date: 2026-09-19

Status: accepted

## Context

IoTox person multidevice deliberately does not copy one Tox savedata/key across
machines. One compromised machine must not become the whole person's Tox
identity. Instead, IoTox uses one person key, many revocable device route keys,
delivery cards, and delegated device senders.

Normal Tox users still exist. They send and receive ordinary friend text or
action messages. IoTox needs to communicate with them without claiming that a
normal Tox public key is an IoTox person key, and without making Tox read
receipts into all-device person receipts.

## Decision

Add a normal Tox compatibility bridge at the person layer.

The outside edge remains normal Tox:

- outbound bridge sends ordinary `message`/`action` bytes to one normal Tox
  friend; and
- inbound bridge starts from an ordinary Tox friend message already observed by
  one IoTox device.

The inside edge is a signed IoTox bridge envelope:

```text
direction=in|out
tox-kind=message|action
observer-person=PERSON_KEY
observer-device=DEVICE_KEY
delegation-digest=...
external-tox-key=...
observed-unix-ms=...
body=bounded normal Tox bytes
signature=DEVICE_KEY over canonical bridge envelope
```

Receiving self devices verify the envelope against the expected
person-signed sender delegation and commit it to a separate
`iotox-person-tox-bridge-store-v1`. Live bridge commands may also receive a
`--bridge-store BRIDGE_STORE` path so the observing/sending device commits its
own bridge store during the successful live command. Bridge observations are
never committed to the signed IoTox person/group transcript.

The native CLI surface is:

- `person tox-bridge-plan-in-delegated`;
- `person tox-bridge-fanout-in-delegated`;
- `person tox-bridge-plan-out-delegated`;
- `person tox-bridge-send-out-delegated`;
- `person tox-bridge-receive`; and
- `person tox-bridge-status`.

## Consequences

IoTox can now interoperate with stock Toxic contacts in a reviewable way:

- Toxic contacts receive normal Tox text/action messages;
- self devices receive signed delegated bridge observations;
- duplicates are idempotent in the local bridge store; and
- content-free bridge status is available for operators.

The nonclaims are important:

- an external Tox public key is still an external route identity, not an IoTox
  person key;
- a bridge observation says one delegated self device observed or sent normal
  Tox text, not that the external user signed an IoTox envelope;
- normal Tox read receipts remain route-level transport evidence, not
  aggregate person/all-device receipts; and
- messages longer than the current bridge envelope bound require future
  chunking rather than truncation.

Route qualification is separate from compatibility. The bridge command output
therefore reports the current scope:
`tox-bridge-route-qualification=default-qualified;forced-tcp-degraded;tor-i2p-open`.
Default native Toxic operation is accepted as the strong ordinary compatibility
route. Forced-TCP/native-relay Toxic operation has founding passes and repeated
long-loop passes but is degraded pending a boring follow-up soak. Toxic over
`tox/tor` and `tox/i2p` need their own route gates before they become claims.

## Validation

The owned unit registry covers bridge envelope creation, canonical
decode/verify, wrong-delegation refusal, tamper refusal, store commit, and
duplicate suppression.

The human CLI regression starts a temporary mock-backed daemon to create a real
device identity, uses that identity as a self-swarm member principal, creates a
sender delegation, runs inbound/outbound bridge plans, commits the signed bridge
payload, checks duplicate idempotence, and verifies content-free bridge status.

The live Toxic gate is `tools/run-toxic-compat-bridge-lab.py`. It starts a
fresh source-linked IoTox daemon and a fresh stock Toxic profile, drives Toxic's
TUI through first run, establishes real friendship over the public Tox network,
proves normal text in both directions, then uses the actual Toxic public key
and observed Toxic text for the delegated bridge receive/status/outbound-plan
proof. The default-route pass uses Toxic `/add` followed by IoTox
`request-accept`. The forced-TCP pass launches Toxic with `-t`, IoTox with
`--native-tcp-only`, feeds Toxic a compact lab-local `DHTnodes.json` compatible
with its exact parser, sends IoTox's friend request to Toxic, and accepts it
with stock `/accept`. The plan path also proves `--bridge-store` prints the
exact local commit command. The 2026-09-19/2026-09-20 founding-machine runs are
summarized in `docs/evidence/2026-09-19-toxic-compat-bridge.md`.

The multidevice Toxic gate is
`tools/run-toxic-multidevice-bridge-lab.py`. It starts three independent IoTox
devices plus one Toxic client, friends Toxic to every IoTox route, builds a
full IoTox self-route mesh, creates a three-route person card, proves
Toxic-to-A inbound fanout to B and C, and proves A, B, and C can each send
delegated normal-Tox bridge messages back to Toxic with Toxic read receipts,
Toxic-side log/display evidence, and outbound self-fanout to the other devices.
Live fanout skips the sender's current route instead of requiring a device to
be its own Tox friend, and `--bridge-store` commits the sender's local bridge
store during each successful live bridge command. The forced-TCP variant runs
all three IoTox devices TCP-only and has each route initiate friendship to the
one Toxic identity before proving the same fanout/status invariants. Offline
plans still print every route for review.
