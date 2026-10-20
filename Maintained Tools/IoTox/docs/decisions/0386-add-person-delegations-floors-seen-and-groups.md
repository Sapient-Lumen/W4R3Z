# ADR 0386: Add person delegations, card floors, seen stores, and group descriptors

Status: accepted
Date: 2026-09-19

## Context

ADR 0385 made public person delivery cards and direct person-signed fanout
real. That proved the core separation:

```text
Tox route key != human identity
```

The remaining multidevice gap was daily use. A person should not type
RecallRoot for every chat message, contacts need a way to refuse stale or forked
cards, duplicate fanout should not produce duplicate local conversation events,
and group conversations need membership state above Tox routes.

## Decision

Extend the native `iotox person ...` layer with four more record families.

### Person-signed sender delegation

`person delegate-recall-stdin SELF_SWARM_ROSTER ALIAS DELEGATION
[verification options]` signs a rostered active device principal as an allowed
sender for the person key:

```text
iotox-person-sender-delegation-v1
person=PERSON_PUBLIC_KEY_HEX
device=STABLE_DEVICE_PUBLIC_KEY_HEX
generation=SELF_SWARM_GENERATION
roster-digest=SELF_SWARM_ROSTER_DIGEST_HEX
label=ALIAS
expires-unix-ms=0
signature=PERSON_SIGNATURE_HEX
```

The matching `--identity DEVICE_ID` may then create
`iotox-person-device-message-v1` envelopes. Verification requires both the
device signature and the person-signed delegation.

### Contact-side delivery-card floor

`person card-floor-commit FLOOR PERSON_CARD` records a local high-water
generation/digest for a contact's public card. `person card-verify PERSON_CARD
--floor FLOOR` rejects stale generations and same-generation forks.

The floor is owner-private local state, not an independent rollback witness.

### Local seen store

`person seen-commit SEEN_STORE PAYLOAD_HEX` recognizes direct person, delegated
person, direct group, and delegated group payloads and commits one sorted local
message-id entry. Repeating the same signed payload returns `duplicate=1`.

This is duplicate suppression only. It is not a read receipt or group
transcript authority.

### Signed group descriptor and group payloads

`person group-create-recall-stdin GROUP TITLE [MEMBER_PERSON_HEX...]` creates a
creator-signed `iotox-person-group-v1` descriptor with sorted person-key
membership. Direct and delegated group message plans produce signed
group-message envelopes, and verification checks group membership plus sender
delegation where applicable.

`person group-fanout-plan GROUP PAYLOAD_HEX PERSON_CARD...` deliberately stays
a porch: it validates the group payload and member cards, then prints exact
`message-hex key:...` commands. It does not run a background group transport.

## Consequences

IoTox now has a coherent first complete multidevice conversation substrate:

- one person key can publish many current device routes;
- one rostered device can sign daily person/group messages through a
  person-signed delegation;
- contacts can pin public delivery-card freshness locally;
- receivers can suppress repeated fanout payloads by message id; and
- group membership is signed IoTox state, not Tox group peer identity.

The remaining nonclaims are explicit:

- no background card refresh;
- no durable all-device delivery guarantee while devices are offline;
- no aggregate person-level read receipt;
- no transcript consensus/order beyond stable message IDs;
- no independent witness custody for person-card or group freshness; and
- no automatic Tox group/conference adapter yet.

## Evidence

- `include/iotox/person_multidevice.hpp` and `src/person_multidevice.cpp`
  implement canonical codecs, hashes, signatures, freshness floors, seen-store
  persistence, and group/direct/delegated verification.
- `src/cli.cpp` exposes the new native `iotox person` commands.
- `tests/test_person_multidevice.cpp` covers device sender delegation,
  delegated messages, card floor stale/fork refusal, duplicate suppression,
  signed groups, and delegated group messages.
- `ctest --test-dir build/gcc-debug -R iotox.unit-and-integration
  --output-on-failure` passes with the pinned libsodium environment.

Docs:

- `docs/person-multidevice.md`;
- `docs/self-mode.md`;
- `docs/roadmap.md`;
- `docs/open-questions.md`;
- `docs/architecture.md`.
