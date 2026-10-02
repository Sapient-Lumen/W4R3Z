# Person multidevice and group delivery

Status: v4 implemented.
Updated 2026-10-01.

This is the IoTox-owned layer above Tox routes. It keeps three identities
separate on purpose:

```text
self-swarm roster       private owner-local list of my machines
person delivery card    public signed route set for reaching one person key
group descriptor        signed conversation membership above route delivery
messenger stores        local contacts, transcript, receipt, and outbox state
```

Tox remains the carrier. IoTox person signatures decide who spoke.

## What Toxcore gives us

Toxcore has friend messaging, file transfer, conferences, and the newer
groupchat API. IoTox can use those as useful carriers, but not as the
authority model. Copying one Tox savedata/key to every machine would make one
stolen laptop a stolen person. One Tox key per device preserves retirement, but
contacts still need one human address.

IoTox therefore uses:

```text
one RecallRoot-derived person key
many independently revocable device route keys
public owner-signed delivery cards
person-signed or delegated-device-signed envelopes
optional signed group descriptors above delivery
```

The native front door for the current command surface is:

```sh
iotox person quickstart
```

It prints the recipe-first path before the stable command fields: create a
public delivery card from the private self roster, pin a contact card, plan a
send before mutating transport, use a delegated device key for daily sends, and
run the background messenger worker under the service porch. The command is
content-free; it explains how to operate the stores and cards without exposing
messages or secrets.

Primary references reviewed for this boundary:

- Tox protocol specification: <https://toktok.ltd/spec>
- c-toxcore public API header: <https://github.com/TokTok/c-toxcore/blob/master/toxcore/tox.h>

## Normal Tox compatibility bridge

IoTox now has a native bridge for normal Tox text/action compatibility, with
stock Toxic as the supported compatibility baseline. It is not Tox
multidevice. The outside normal Tox client still sends or receives ordinary
Tox friend messages. Inside IoTox, one self device signs an observation:

```text
external Tox key X said/saw normal text Y
observed by self device D
under person delegation P→D
```

The founding live gates cover both the default public Tox route and a
forced-TCP route through public Tox TCP relays. The default gate proves Toxic
can initiate friendship with IoTox via `/add`; the forced-TCP gate proves the
inverse setup path, where IoTox sends the friend request and Toxic accepts it
with stock `/accept`. In both cases the compatibility claim is the same:
ordinary normal Tox text moves across the Toxic edge, while IoTox self devices
exchange signed bridge observations internally.

That signed bridge envelope can then be fanned out to the owner's other active
self routes through ordinary `message-hex` transport. A receiving self device
verifies the bridge envelope against the expected sender delegation and commits
it to a separate Tox-bridge store, not to the signed person/group transcript.

Review inbound normal Tox compatibility after a bridge device observed an
incoming normal Tox message:

```sh
iotox --identity ~/.local/state/iotox/device.identity \
  person tox-bridge-plan-in-delegated \
  --bridge-store ~/.local/state/iotox/tox.bridge \
  ./me.person.card ./desktop.person.delegate \
  EXTERNAL_TOX_KEY_HEX message "hello from a normal Tox client"
```

The plan prints a signed `payload-hex`, exact self-fanout commands, and, when
`--bridge-store` is supplied, the exact local commit command:

```text
self-fanout-command=iotox message-hex key:SELF_ROUTE PAYLOAD_HEX
local-bridge-commit-command=iotox person tox-bridge-receive PAYLOAD_HEX ...
```

For a live inbound bridge worker on a connected device:

```sh
iotox --identity ~/.local/state/iotox/device.identity \
  --runtime ~/.local/state/iotox/runtime \
  person tox-bridge-fanout-in-delegated \
  --bridge-store ~/.local/state/iotox/tox.bridge \
  ./me.person.card ./desktop.person.delegate \
  EXTERNAL_TOX_KEY_HEX message "hello from a normal Tox client"
```

Live fanout resolves the running Agent's current Tox route key and prints a
`self-skip ... reason=current-runtime-route` line for that route. A device does
not need to be, and cannot usefully be, its own Tox friend. Offline plans still
print every route so the complete public card can be reviewed before live
delivery. With `--bridge-store`, a successful live fanout also commits the
sender's own bridge observation to the local bridge store.

Review outbound normal Tox compatibility before sending to a normal Tox friend:

```sh
iotox --identity ~/.local/state/iotox/device.identity \
  person tox-bridge-plan-out-delegated \
  --bridge-store ~/.local/state/iotox/tox.bridge \
  ./me.person.card ./desktop.person.delegate \
  EXTERNAL_TOX_KEY_HEX message "hello to normal Tox"
```

The outbound plan prints both the ordinary normal-Tox command and the self
fanout commands. A live bridge sender can send the normal Tox message and then
fan out the signed observation to self devices:

```sh
iotox --identity ~/.local/state/iotox/device.identity \
  --runtime ~/.local/state/iotox/runtime \
  person tox-bridge-send-out-delegated \
  --bridge-store ~/.local/state/iotox/tox.bridge \
  ./me.person.card ./desktop.person.delegate \
  alias:normal-tox-friend message "hello to normal Tox"
```

Receiving self devices still commit bridge envelopes explicitly:

```sh
iotox person tox-bridge-receive \
  PAYLOAD_HEX ./desktop.person.delegate ~/.local/state/iotox/tox.bridge

iotox person tox-bridge-status ~/.local/state/iotox/tox.bridge
```

The bridge store is contentful and owner-private. `tox-bridge-status` is
content-free. Duplicate bridge payloads are idempotent.

Important boundary: the external Tox public key is an external route identity,
not an IoTox person key. A bridge record says “my delegated device observed
this normal Tox communication.” It does not say “the external user signed an
IoTox person envelope,” and it does not turn Tox read receipts into IoTox
person/all-device receipts. This bridge covers one-to-one Toxic-compatible
normal friend messages/actions that fit the IoTox single-message body bound.
It is not a normal Tox conference/group bridge, chunked-file bridge, or
multi-device Tox identity implementation.

Current bridge qualification is deliberately narrower than “all routes.” The
Toxic proof covers default native Tox strongly. Forced-TCP/native-relay mode is
kept as an explicit evidence label and follow-up-soak claim rather than silently
folded into the default bridge claim; current readiness still names that brake
as `default-qualified-forced-tcp-degraded` until retained smooth follow-up
evidence graduates it. Tor and I2P bridge qualification are evidence-gated
separately, so bridge plans keep printing the ordinary
`route-policy=not-carried-by-person-card` warning. A public card tells contacts
which Tox route keys can receive a person envelope; it does not authorize
native/Tor/I2P downgrade, fallback, or anonymity claims.

The native graduation porch for the bridge is:

```sh
iotox person tox-bridge-graduation-check \
  --bridge-store ~/.local/state/iotox/tox.bridge \
  --evidence toxic-native=toxic.default \
  --evidence toxic-forced-tcp=toxic.tcp \
  --evidence inbound-fanout=lab.inbound \
  --evidence outbound-send=lab.outbound \
  --evidence identity-boundary=review \
  --evidence bridge-store=content-free \
  --evidence transcript-commit=transcript \
  --evidence route-nonclaims=routes \
  --evidence operator-review=owner
```

With no labels it fails closed and prints the exact Toxic default,
forced-TCP, and three-device multidevice lab commands. With all labels it says
`toxic-bridge-graduation=operator-attested`, not “Tox understands IoTox person
identity.” Normal Tox clients remain normal Tox clients.

The route side is separately summarized by:

```sh
iotox route-qualification-check --scope toxic \
  --evidence toxic-native=toxic.default \
  --evidence toxic-forced-tcp=toxic.tcp \
  --evidence toxic-tor=tor.route \
  --evidence toxic-i2p=i2p.route \
  --evidence route-nonclaims=review \
  --evidence operator-review=owner
```

This prints `anonymity-certified=0` and `silent-fallback-authorized=0` even
when the operator evidence is complete.

## Public delivery cards

Create a public card from a verified self-swarm roster:

```sh
cat RECALLROOT.txt | \
  iotox person card-recall-stdin \
    ~/.local/state/iotox/self.swarm \
    ./me.person.card \
    --floor ~/.local/state/iotox/self.floor \
    --min-generation 2
```

Inspect and pin the contact-side freshness floor:

```sh
iotox person card-inspect ./me.person.card
iotox person card-floor-commit ./alice.person.floor ./alice.person.card
iotox person card-verify ./alice.person.card --floor ./alice.person.floor
```

The card includes the person public key, self-swarm generation, roster digest,
active Tox route keys, and signature. It excludes private aliases, stable
device principals, roles, capabilities, sudo policy, and retired routes.
It also does not carry route class policy. `person card-inspect`,
message-fanout plans, group fanout plans, and bridge plans print
`route-policy=not-carried-by-person-card` and point at route-set v2 or explicit
run configuration for native/Tor/I2P selection. This keeps the public card
compatible with ordinary Tox delivery keys while making privacy/fallback
policy an explicit operator choice.

The floor is local contact state. It rejects stale cards and same-generation
forks. It is not recovery custody or an independent witness by itself.

## Person messages

RecallRoot can still sign directly:

```sh
cat FRIEND_RECALLROOT.txt | \
  iotox person message-plan-recall-stdin ./me.person.card "hello"

cat FRIEND_RECALLROOT.txt | \
  iotox person message-fanout-recall-stdin ./me.person.card "hello"
```

Daily use should prefer a person-signed sender delegation, so one device can
sign as the person without asking for RecallRoot on every message:

```sh
cat RECALLROOT.txt | \
  iotox person delegate-recall-stdin \
    ~/.local/state/iotox/self.swarm desktop ./desktop.person.delegate \
    --floor ~/.local/state/iotox/self.floor \
    --min-generation 2

iotox person delegation-inspect ./desktop.person.delegate

iotox --identity ~/.local/state/iotox/device.identity \
  person message-plan-delegated \
  ./desktop.person.delegate ./alice.person.card "hello from this machine"

iotox --identity ~/.local/state/iotox/device.identity \
  person message-fanout-delegated \
  ./desktop.person.delegate ./alice.person.card "hello from this machine"
```

Verify received payloads independent of the route that carried them:

```sh
iotox person message-verify-hex PAYLOAD_HEX
iotox person message-verify-delegated-hex PAYLOAD_HEX ./desktop.person.delegate
```

Both direct and delegated envelopes carry a random nonce, stable message id,
bounded body, and signature. Delegated envelopes additionally bind the
person-signed delegation digest and the device signing key.

The ordinary receive porch composes verification, local transcript commit,
duplicate suppression, and optional device receipt creation:

```sh
iotox --identity ~/.local/state/iotox/device.identity \
  person receive PAYLOAD_HEX \
  --seen ~/.local/state/iotox/person.seen \
  --transcript ~/.local/state/iotox/person.transcript \
  --delegation ./desktop.person.delegate \
  --receipt ./message.receipt \
  --receipt-store ~/.local/state/iotox/person.receipts

iotox person messenger-status \
  --contacts ~/.local/state/iotox/person.contacts \
  --seen ~/.local/state/iotox/person.seen \
  --transcript ~/.local/state/iotox/person.transcript \
  --outbox ~/.local/state/iotox/person.outbox \
  --receipts ~/.local/state/iotox/person.receipts

iotox person messenger-plan \
  --contacts ~/.local/state/iotox/person.contacts \
  --seen ~/.local/state/iotox/person.seen \
  --transcript ~/.local/state/iotox/person.transcript \
  --outbox ~/.local/state/iotox/person.outbox \
  --receipts ~/.local/state/iotox/person.receipts \
  --dead-letter ~/.local/state/iotox/person.dead-letter \
  --card ./me.person.card \
  --floor ~/.local/state/iotox/person.card.floor

iotox person read-mark \
  ~/.local/state/iotox/person.read-state MESSAGE_ID_HEX \
  --reader desktop

iotox person read-status \
  ~/.local/state/iotox/person.read-state \
  --message-id MESSAGE_ID_HEX \
  --expect-reader desktop

iotox person transcript-convergence \
  ~/.local/state/iotox/person.transcript \
  ~/.local/state/iotox/laptop.person.transcript

iotox person group-status ./operators.group \
  --transcript ~/.local/state/iotox/person.transcript \
  --receipts ~/.local/state/iotox/person.receipts \
  --read-state ~/.local/state/iotox/person.read-state
```

`person receive` is idempotent for local transcript and seen stores. Replaying
the same payload reports duplicates instead of appending new records. When
`--delegation` and `--receipt` are supplied together it writes one delegated
receipt after the local receive state is valid; it refuses to overwrite an
existing receipt path. Supplying `--receipt-store` also commits that receipt to
the durable aggregate receipt store in the same native receive pass.
`person messenger-status` is content-free store health: counts, next sequence,
receipt count, pending routes, and absent/corrupt store state. It does not
prove that two devices share a canonical transcript order, or that a remote
human read it.
`person messenger-plan` is the daily porch around the same stores. It prints
the status command, bounded background runner, retry/expiry/dead-letter path,
card-refresh command, and receive command while keeping the semantics explicit:
device receipts mean device-received, not human-read; transcript sequence is
local order, not cross-device consensus; group payloads are IoTox signed
envelopes, not normal Tox group identity.
`person read-mark` and `person read-status` are deliberately local. They make
the UX state “this operator/device has read this message id” durable and
queryable, but they do not become a remote read receipt or delivery proof.
`person transcript-convergence` compares signed message identities and payload
digests across transcript files so devices can detect missing/diverged
transcripts without pretending there is a global total order. `person
group-status` summarizes signed group membership, local group transcript
entries, delegated receipts, and local human-read marks while preserving the
same boundary: IoTox group identity is the signed envelope, not a Tox
conference identity.

## Native messenger stores

IoTox now has the first ordinary local messenger substrate. Stores are
ordinary owner-private files; the signed payloads are contentful, while the
status commands stay content-free. Transport sending can still be reviewed as
exact route commands, but it no longer requires an external script loop:
`person background-run` is a native bounded retry/expiration worker that can be
run once, looped for a fixed number of cycles, or supervised by a service
manager.

Pin a contact card and keep the public route cache with the same stale/fork
rules as the card floor:

```sh
iotox person contact-upsert \
  ~/.local/state/iotox/person.contacts alice ./alice.person.card

iotox person contact-list ~/.local/state/iotox/person.contacts
iotox person contact-show ~/.local/state/iotox/person.contacts alice
```

Commit signed direct/delegated/group payloads to a local transcript:

```sh
iotox person transcript-commit \
  ~/.local/state/iotox/person.transcript out PAYLOAD_HEX

iotox person transcript-status ~/.local/state/iotox/person.transcript
```

The transcript stores message identity, endpoint or group identity, payload
digest, sequence, direction, and bounded body. It deduplicates repeated
message IDs locally. It is contentful and owner-private; it is not a
cross-device ordering protocol.

Create a device receipt for one received payload under this device's
person-signed sender delegation:

```sh
iotox --identity ~/.local/state/iotox/device.identity \
  person receipt-create-delegated \
  ./desktop.person.delegate PAYLOAD_HEX ./message.receipt

iotox person receipt-inspect ./message.receipt ./desktop.person.delegate
iotox person receipt-commit \
  ~/.local/state/iotox/person.receipts ./message.receipt ./desktop.person.delegate
iotox person receipts-status ~/.local/state/iotox/person.receipts \
  --message-id MESSAGE_ID_HEX \
  --expect-person PERSON_PUBLIC_KEY_HEX \
  --expect-device DEVICE_PUBLIC_KEY_HEX
```

This proves one delegated device signed “I received this message id at this
time.” The receipt store deduplicates those records and `receipts-status`
answers the content-free aggregate question “have the specific expected
devices produced receipts for this message?” It is still not a human read
receipt and does not invent an expected device set; the caller must name the
person key and device keys it wants to check.

Queue an outgoing payload against a recipient's current card:

```sh
iotox person outbox-enqueue \
  ~/.local/state/iotox/person.outbox ./alice.person.card PAYLOAD_HEX

iotox person outbox-plan ~/.local/state/iotox/person.outbox
iotox [--runtime ~/.local/state/iotox/runtime] \
  person outbox-send ~/.local/state/iotox/person.outbox --max-routes 16
iotox person outbox-mark-sent ~/.local/state/iotox/person.outbox \
  MESSAGE_ID ROUTE_HEX
iotox person outbox-status ~/.local/state/iotox/person.outbox
iotox person outbox-retry-plan ~/.local/state/iotox/person.outbox \
  --max-routes 16 --retry-every 60 --expire-after 604800
iotox person outbox-expire \
  ~/.local/state/iotox/person.outbox \
  ~/.local/state/iotox/person.dead-letter.outbox \
  --expire-after 604800
iotox person card-refresh-plan ./alice.person.card \
  --floor ./alice.person.floor
iotox person background-plan \
  --seen ~/.local/state/iotox/person.seen \
  --transcript ~/.local/state/iotox/person.transcript \
  --receipts ~/.local/state/iotox/person.receipts \
  --outbox ~/.local/state/iotox/person.outbox \
  --dead-letter ~/.local/state/iotox/person.dead-letter.outbox \
  --card ./alice.person.card --floor ./alice.person.floor
iotox person background-run \
  --seen ~/.local/state/iotox/person.seen \
  --transcript ~/.local/state/iotox/person.transcript \
  --receipts ~/.local/state/iotox/person.receipts \
  --outbox ~/.local/state/iotox/person.outbox \
  --dead-letter ~/.local/state/iotox/person.dead-letter.outbox \
  --max-routes 16 --cycles 1 --interval 0
```

The outbox records the exact signed payload, recipient person, card
generation/digest, and per-route pending/sent accounting. `outbox-plan` prints
exact `iotox message-hex key:ROUTE PAYLOAD_HEX` commands. `outbox-send` is the
native one-shot worker form: it walks pending routes in canonical order, sends
through the local control socket, and only moves a route to `sent` after the
Tox transport accepts the payload locally. Every non-dry-run send attempt
durably advances the item's attempt count and last-attempt timestamp before
trying routes, so a crashed sender does not pretend it never tried.
`outbox-expire` never purges; it moves still-pending expired items into a
dead-letter outbox for operator review. `--dry-run` prints the exact send and
accounting commands without touching the store. Marking a route sent is local
accounting of transport attempt success, not remote person receipt.
`outbox-retry-plan`, `card-refresh-plan`, and `background-plan` make the
supervised form explicit; `background-run` is the native bounded loop that
composes status, dead-letter expiration, and one-shot route sending.

## Person messenger graduation

The ordinary “does this person messenger installation look daily-usable?”
porch is native and evidence-gated:

```sh
iotox person graduation-check \
  --root ~/.local/state/iotox \
  --evidence background-delivery=service.loop \
  --evidence offline-retry-expiry=outbox.retry \
  --evidence receipt-summary=receipts.rollup \
  --evidence human-read-semantics=read.policy \
  --evidence transcript-convergence=transcripts.checked \
  --evidence group-semantics=groups.reviewed \
  --evidence service-supervision=systemd.user \
  --evidence route-policy=route-set.v2 \
  --evidence operator-review=owner
```

With no labels it exits blocked and prints the exact status, background,
retry, expiry, human-read, transcript convergence, group status, bridge status,
and service-reality commands. With all labels it reports
`person-multidevice-graduation=operator-attested` and
`messages-reach-devices=operator-attested`.

The boundary is intentionally strict: the labels are content-free operator
evidence for this installation. They do not prove remote human attention, do
not create a global transcript order, do not turn IoTox groups into Tox
conferences, and do not let public person cards carry route fallback/privacy
policy.

## Resident services

For a reviewed always-on setup, use the top-level resident-service porch rather
than inventing host glue by hand:

```sh
iotox service plan \
  --target all \
  --root ~/.local/state/iotox \
  --manager systemd-user \
  --unit-prefix iotox-self \
  --binary /usr/bin/iotox

iotox service render \
  --target all \
  --root ~/.local/state/iotox \
  --manager systemd-user \
  --unit-prefix iotox-self \
  --binary /usr/bin/iotox \
  --raw

iotox service receipt \
  --target all \
  --root ~/.local/state/iotox \
  --manager systemd-user \
  --unit-prefix iotox-self \
  --binary /usr/bin/iotox \
  --accept-operator-responsibility \
  --out ~/.local/state/iotox/resident-service.receipt
```

`--target agent` renders only the long-lived Agent/sync/Ratox side. `--target
person` renders only the person messenger background worker. `--target all`
renders both. The managers are `systemd-user`, `nixos-user`, `nixos-system`,
and `monsternix`. The MonsterNix form is an adapter draft: IoTox prints exact
commands and health checks, while MonsterNix still owns projection, proof,
activation, logs, and rollback.

The receipt is content-free and useful for release evidence or operator notes,
but it is not proof that the unit was installed or is still running. Check the
service manager logs, `iotox overview`, `iotox readiness`, `iotox person
messenger-status`, sync folder health, and terminal activation/graduation
separately.

## Duplicate suppression

Every receiving device can commit a local seen floor:

```sh
iotox person seen-commit ~/.local/state/iotox/person.seen PAYLOAD_HEX
iotox person seen-status ~/.local/state/iotox/person.seen
```

This suppresses duplicate person/group message IDs locally. It is deliberately
not a delivery receipt, transcript authority, or proof that every device saw
the message.

## Group descriptors and group messages

Create a signed group descriptor. The creator is automatically a member:

```sh
cat RECALLROOT.txt | \
  iotox person group-create-recall-stdin \
  ./operators.group "operators" ALICE_PERSON_HEX BOB_PERSON_HEX

iotox person group-inspect ./operators.group
```

Create a group payload:

```sh
cat RECALLROOT.txt | \
  iotox person group-message-plan-recall-stdin \
  ./operators.group "hello group"

iotox --identity ~/.local/state/iotox/device.identity \
  person group-message-plan-delegated \
  ./operators.group ./desktop.person.delegate "hello group"
```

Verify:

```sh
iotox person group-message-verify-hex PAYLOAD_HEX ./operators.group
iotox person group-message-verify-delegated-hex \
  PAYLOAD_HEX ./operators.group ./desktop.person.delegate
```

Deliver through member cards:

```sh
iotox person group-fanout-plan \
  ./operators.group PAYLOAD_HEX \
  ./alice.person.card ./bob.person.card
```

The plan prints exact `iotox message-hex key:ROUTE PAYLOAD_HEX` commands for
every route in the supplied member cards. Live group fanout automation is still
intentionally not backgrounded.

## What “send to my key reaches all devices” now means

For direct person delivery:

1. the sender has a current signed delivery card for the recipient person key;
2. the card passes any local freshness floor or contact-book floor;
3. every route in the card is already a Tox friend of the sender's Agent;
4. fanout resolves all routes before sending anything, or the durable outbox
   records the exact still-pending per-route send plan and retry/expiration
   metadata; and
5. the receiver verifies the IoTox envelope, not the Tox route, then may commit
   local seen/transcript/receipt state; and
6. receipt rollup is only complete when the operator names the expected
   devices and `receipts-status` reports every expected device present.

For group delivery:

1. the group descriptor verifies and names person keys;
2. the group payload verifies against the descriptor and, for delegated
   messages, against the person-signed device delegation;
3. delivery is planned through each member's public person card; and
4. duplicate suppression is local per receiver.

## Still not claimed

- guaranteed delivery to a device that never comes online or is no longer a
  current Tox friend;
- a remote “the person read it” proof; local `read-mark` state is UX state,
  not delivery or remote-attention evidence;
- global transcript total order across a person's devices beyond per-message
  identity/digest convergence checks;
- independent witness custody for card/delegation/group freshness;
- private contact roster synchronization; and
- automatic Tox group/conference transport adapters.

The non-negotiable rule stays: a Tox route or group peer is never by itself the
human identity. The signed IoTox person or group envelope is.
