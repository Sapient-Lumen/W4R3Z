# ADR 0387: Add person messenger stores

Status: accepted
Date: 2026-09-19

## Context

ADRs 0385 and 0386 made the signed person layer real: one person key can
publish multiple active route keys, a rostered device can sign daily person or
group messages through an owner-signed delegation, contacts can reject stale or
forked cards, and group payloads can be delivered through member cards.

That still left the messenger surface too ephemeral. Operators could produce
and verify signed payloads, but the repo did not yet have native local state
for “this is my contact card floor,” “this signed payload is in my transcript,”
“this delegated device received this message,” or “this exact message still
needs to be sent to these route keys.”

## Decision

Extend `iotox person ...` with four native owner-private store families.

### Contact book

`person contact-upsert CONTACT_BOOK NAME PERSON_CARD` loads a signed public
delivery card, verifies it, computes its card digest, and commits a local
contact entry:

```text
name
person public key
card generation
card digest
active public route keys
```

The contact book is also a freshness floor. Reusing a name for a different
person, reusing a person under another name, moving backward in card
generation, or presenting a same-generation fork fails closed. The file is
canonical on load and rejects noncanonical route ordering or duplicate routes.

### Transcript

`person transcript-commit TRANSCRIPT in|out PAYLOAD_HEX` recognizes signed
direct person, delegated person, direct group, and delegated group payloads,
then commits one local transcript entry with a monotonic local sequence,
direction, scope, endpoint or group id, message id, payload digest, and bounded
body.

The transcript is contentful owner-private state. It deduplicates repeated
message IDs locally, but it is not a cross-device ordering protocol.

### Delegated device receipt

`person receipt-create-delegated DELEGATION PAYLOAD_HEX RECEIPT
[RECEIVED_UNIX_MS]` signs a receipt with this device identity after proving
that `--identity` matches the person-signed sender delegation device. The
record binds:

```text
message id
group id when applicable
recipient person key
recipient device key
delegation digest
received time
device signature
```

This proves one delegated device made a receipt. It is not an aggregate
“the person received it” or “all devices received it” proof.

### Reviewed outbox

`person outbox-enqueue OUTBOX PERSON_CARD PAYLOAD_HEX` stores the exact signed
payload with the recipient card generation/digest and the card's active route
keys as pending routes. `person outbox-plan OUTBOX` prints exact
`iotox message-hex key:ROUTE PAYLOAD_HEX` commands. `person outbox-send OUTBOX`
is the native one-shot/timer-friendly worker: it resolves each pending route as
a current Tox friend, sends through the local control socket, and moves that
route from pending to sent only after local Tox transport acceptance.
`--dry-run` preserves the old reviewed plan behavior. `person outbox-mark-sent`
remains the explicit manual accounting override.

The outbox is durable local planning and route accounting. It is not remote
receipt and not an always-on retry daemon.

## Consequences

IoTox now has a first native manual messenger substrate:

- contact cards can be retained and pinned in one canonical file;
- inbound and outbound signed payloads can be committed to a local transcript;
- one delegated device can issue a signed receipt for one payload; and
- outbound messages can survive local restart as exact reviewed per-route send
  plans and can now be advanced by a native one-shot sender.

The remaining nonclaims are explicit:

- no background card refresh;
- no always-on scheduler, retry, or expiration policy;
- no durable all-device delivery guarantee while devices are offline;
- no aggregate person-level or all-device receipt;
- no cross-device transcript consensus/order beyond stable message IDs;
- no independent witness custody for person-card, delegation, group, or
  transcript freshness; and
- no automatic Tox group/conference adapter yet.

## Evidence

- `include/iotox/person_multidevice.hpp` and `src/person_multidevice.cpp`
  implement canonical contact, transcript, receipt, and outbox records.
- `src/cli.cpp` exposes native `contact-*`, `transcript-*`, `receipt-*`, and
  `outbox-*` commands under `iotox person`, including `outbox-send`.
- `tests/test_person_multidevice.cpp` covers contact floors and fork refusal,
  transcript deduplication, delegated receipt verification, and outbox
  pending/sent route accounting.
- `ctest --test-dir build/iotox-nix-debug -R '^iotox\\.unit-and-integration$'
  --output-on-failure` passes.

Docs:

- `docs/person-multidevice.md`;
- `docs/self-mode.md`;
- `docs/architecture.md`;
- `docs/roadmap.md`;
- `README.md`.
