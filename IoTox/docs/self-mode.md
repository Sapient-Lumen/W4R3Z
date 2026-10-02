# Self mode and multidevice

Status: self-mode activation, signed self-swarm roster v1, and person
delivery-card/message fanout v1 are implemented.
Updated 2026-09-19.

## Product meaning

`--mode self` is the IoTox mode for machines the owner treats as their own
machines. It flips the Ratox/SSH-like surface from “manual opt-in role flags”
to “this Agent is allowed to be a self-machine terminal host and local
terminal controller by default.”

That is the important default flip:

```sh
iotox init plan --root ~/.local/state/iotox --mode self --enable-sync
iotox init write-config --root ~/.local/state/iotox --mode self --enable-sync
iotox config-lint ~/.local/state/iotox/agent.conf
```

In a direct Agent invocation, `--mode self` also enables the Ratox host and
same-user terminal controller. If the profile store is omitted, it defaults
beside the savedata path under `ratox/`; if the helper executable is omitted,
the running `iotox` executable is used as the helper path. The init porch
persists those paths explicitly so the file-backed config stays reviewable.

## What self mode does not change

Self mode is not “friendship means shell.” It does not install a shell profile,
bind a profile to a principal, grant `interactive.terminal`, enable sudo,
select a privacy route, or let a remote peer choose executable, argv,
environment, cwd, profile, port forwarding, or sudo policy.

The ordinary self-machine shell path is still:

```sh
iotox terminal doctor
iotox terminal profile plan shell self-shell "$USER" \
  --store ~/.local/state/iotox/ratox

# After reviewing, installing, and binding that profile to the self peer:
cat RECALLROOT.txt | \
  iotox authority-delegate-self-recall-stdin alias:laptop operator interactive.terminal

iotox run-check --config ~/.local/state/iotox/agent.conf
iotox run --config ~/.local/state/iotox/agent.conf
iotox terminal alias:laptop --reconnect
```

`RECALLROOT.txt` is only a placeholder for a local stdin ceremony. Do not put
the phrase in argv, environment variables, logs, or support bundles.

Sudo remains separate. A sudo-capable self-machine profile must be deliberately
planned and reviewed:

```sh
iotox terminal profile plan sudo self-admin "$USER" \
  --store ~/.local/state/iotox/ratox
```

That profile starts from the chosen non-root account and delegates elevation to
the host's existing sudoers/PAM policy. IoTox does not grant root by connection.

## Multidevice problem statement

Tox multidevice is not the product answer. IoTox should treat multidevice as
an owner/authority problem above Tox: if the owner possesses the relevant
IoTox self key, they should be able to bring a new machine into their self
domain and then reach their other machines without a vendor account or a Tox
account synchronization story.

The intended human sentence is:

```text
I logged into both ends. I have the owner key. This machine joins my self swarm.
Now I can SSH-like into my machines over IoTox.
```

The implemented foundation is now coherent enough for a reviewed, explicit
self-swarm workflow:

- stable device principals are separate from Tox route identities;
- RecallRoot reconstructs the owner principal;
- the authority ledger can grant `interactive.terminal`;
- peer aliases can name machines locally;
- Ratox can provide the SSH-like terminal once profile and authority are in
  place; and
- `--mode self` makes Ratox host/controller activation the product default for
  self machines.

## Self-swarm roster v1

`iotox self-swarm ...` is the native binary surface for self-machine
membership. It does not create a Tox account, synchronize Tox savedata, or make
friendship authoritative. It creates and mutates one owner-signed roster that
names:

- the RecallRoot-derived owner public key;
- a monotonically increasing roster generation;
- a previous-roster digest, so ordinary mutations form a visible chain;
- each self-machine alias;
- each self-machine stable principal;
- the expected Tox route public key for that machine;
- the role and narrow capabilities that should be granted; and
- active versus retired membership.

The roster is reviewable text and signed by the owner key reconstructed from
stdin. Creation is no-clobber. Join and retire operations rewrite the roster as
a new signed generation. The roster is an owner-local coordination artifact, not
a second constitutional authority ledger: actual effects still go through the
existing signed authority commands.

Create the first member:

```sh
cat RECALLROOT.txt | \
  iotox self-swarm create-recall-stdin \
    ~/.local/state/iotox/self.swarm \
    desktop DESKTOP_PRINCIPAL_HEX DESKTOP_TOX_KEY_HEX \
    operator interactive.terminal
```

Join another self machine:

```sh
cat RECALLROOT.txt | \
  iotox self-swarm join-recall-stdin \
    ~/.local/state/iotox/self.swarm \
    laptop LAPTOP_PRINCIPAL_HEX LAPTOP_TOX_KEY_HEX \
    operator interactive.terminal,sync.subscribe
```

Inspect or verify the roster before trusting it:

```sh
iotox self-swarm inspect ~/.local/state/iotox/self.swarm \
  --min-generation 2 \
  --expect-member laptop LAPTOP_PRINCIPAL_HEX \
  --expect-route laptop LAPTOP_TOX_KEY_HEX

iotox self-swarm verify ~/.local/state/iotox/self.swarm \
  --min-generation 2 \
  --expect-owner OWNER_PUBLIC_KEY_HEX
```

The explicit expectations are the fail-closed fence. A stale generation, wrong
owner, wrong stable principal, or wrong route key exits nonzero before any plan
is rendered.

Commit a local durable high-water floor after accepting a roster generation:

```sh
iotox self-swarm floor-commit \
  ~/.local/state/iotox/self.floor \
  ~/.local/state/iotox/self.swarm \
  --min-generation 2 \
  --expect-owner OWNER_PUBLIC_KEY_HEX

iotox self-swarm verify ~/.local/state/iotox/self.swarm \
  --floor ~/.local/state/iotox/self.floor
```

The floor records owner, generation, and roster digest. It refuses older
generations and same-generation forks. It is local rollback resistance, not an
independent witness; copy or back it with independent custody if the threat is
administrator-level rollback of the whole machine.

Plan reciprocal narrow grants:

```sh
iotox self-swarm grant-plan ~/.local/state/iotox/self.swarm \
  --from desktop \
  --floor ~/.local/state/iotox/self.floor \
  --prove-routes
```

`--prove-routes` asks the running Agent to resolve each active roster alias and
fails if the live alias points at a different Tox public key than the rostered
route. It is a live operator guard against stale alias state; it is not a
cryptographic transport transcript.

Fan out the signed roster to active self machines:

```sh
iotox self-swarm fanout-plan ~/.local/state/iotox/self.swarm \
  --from desktop \
  --floor ~/.local/state/iotox/self.floor

iotox self-swarm fanout ~/.local/state/iotox/self.swarm \
  --from desktop \
  --floor ~/.local/state/iotox/self.floor \
  --prove-routes
```

The plan prints exact `file-send` and receiver-side verify/floor-commit
commands. The live `fanout` command pre-resolves all target aliases before it
queues any file transfer, then sends the signed roster over the existing Tox
file lane. Receivers still verify and commit their own floor before trusting
the file.

Ask for a redacted “are we ready for the next layer?” summary:

```sh
iotox self-swarm readiness ~/.local/state/iotox/self.swarm \
  --from desktop \
  --floor ~/.local/state/iotox/self.floor
```

This emits counts and gate states only: generation, active/retired counts,
floor state, optional route-proof state, and fanout target count. It does not
print member aliases, stable principals, or route keys. A floor-backed, valid
roster is now the input to the public person delivery-card layer; it still
explicitly says that self-machine readiness is not groupchat semantics.

For daily operation, use the dashboard form:

```sh
iotox self-swarm daily-status ~/.local/state/iotox/self.swarm \
  --from desktop \
  --floor ~/.local/state/iotox/self.floor
```

`daily-status` stays redacted, validates the roster and optional floor/route
proofs, and prints the operator commands that usually come next:
`self-swarm readiness`, `fanout-plan`, `grant-plan`, and `retire-plan`.
Unknown, retired, stale-generation, wrong-principal, and wrong-route cases
still fail closed; the command is a humane porch, not a bypass around the
owner-signed roster.

Route proof is intentionally not route privacy. `--prove-routes` verifies that
the live alias/peer surface still matches the owner-signed rostered Tox keys,
which prevents stale local alias mistakes before grants or fanout. It does not
say whether those routes are native, Tor, or I2P. `self-swarm readiness`,
`fanout-plan`, and live `fanout` therefore print
`route-policy=not-carried-by-self-roster`,
`route-policy-authority=route-set-v2-and-explicit-run-config`, and
`privacy-fallback=not-authorized-by-roster`. Route class policy remains a
separate operator-controlled layer.

## Person delivery above the self swarm

`iotox person ...` is the IoTox-owned multidevice layer above the private self
roster. It answers the delivery question:

```text
Someone has my person key/card. How can one message reach every active device
route without making all devices share one Tox private key?
```

Create a public delivery card from the private roster:

```sh
cat RECALLROOT.txt | \
  iotox person card-recall-stdin \
    ~/.local/state/iotox/self.swarm \
    ./me.person.card \
    --floor ~/.local/state/iotox/self.floor \
    --min-generation 2

iotox person card-inspect ./me.person.card
```

The card publishes the owner/person public key, roster generation, roster
digest, active Tox route keys, and signature. It does not publish aliases,
stable device principals, roles, capabilities, sudo policy, or retired routes.

Pin a contact's public card locally so stale cards and same-generation forks
fail closed:

```sh
iotox person card-floor-commit ./friend.person.floor ./friend.person.card
iotox person card-verify ./friend.person.card --floor ./friend.person.floor
```

Plan or perform person-level fanout:

```sh
cat FRIEND_RECALLROOT.txt | \
  iotox person message-plan-recall-stdin ./me.person.card "hello"

cat FRIEND_RECALLROOT.txt | \
  iotox person message-fanout-recall-stdin ./me.person.card "hello"
```

The plan prints one signed person envelope plus exact `message-hex key:...`
commands. The live fanout command resolves every route key to a current Tox
friend before sending anything, then sends the same signed envelope to each
route. A receiver can verify a payload independent of the route:

```sh
iotox person message-verify-hex PAYLOAD_HEX
```

Daily use can avoid RecallRoot by creating a person-signed sender delegation
for a rostered device principal:

```sh
cat RECALLROOT.txt | \
  iotox person delegate-recall-stdin \
    ~/.local/state/iotox/self.swarm desktop ./desktop.person.delegate \
    --floor ~/.local/state/iotox/self.floor \
    --min-generation 2

iotox --identity ~/.local/state/iotox/device.identity \
  person message-plan-delegated \
  ./desktop.person.delegate ./friend.person.card "hello"
```

Signed group descriptors and direct/delegated group message envelopes also now
exist:

```sh
cat RECALLROOT.txt | \
  iotox person group-create-recall-stdin \
  ./operators.group "operators" FRIEND_PERSON_HEX

iotox --identity ~/.local/state/iotox/device.identity \
  person group-message-plan-delegated \
  ./operators.group ./desktop.person.delegate "hello group"

iotox person group-fanout-plan \
  ./operators.group PAYLOAD_HEX ./friend.person.card
```

Receivers can locally suppress duplicate fanout payloads:

```sh
iotox person seen-commit ~/.local/state/iotox/person.seen PAYLOAD_HEX
```

The next native messenger slice is now present too:

```sh
iotox person contact-upsert \
  ~/.local/state/iotox/person.contacts friend ./friend.person.card
iotox person transcript-commit \
  ~/.local/state/iotox/person.transcript in PAYLOAD_HEX
iotox --identity ~/.local/state/iotox/device.identity \
  person receipt-create-delegated \
  ./desktop.person.delegate PAYLOAD_HEX ./message.receipt
iotox person outbox-enqueue \
  ~/.local/state/iotox/person.outbox ./friend.person.card PAYLOAD_HEX
iotox person outbox-plan ~/.local/state/iotox/person.outbox
iotox [--runtime ~/.local/state/iotox/runtime] \
  person outbox-send ~/.local/state/iotox/person.outbox --max-routes 16
```

This is still not a complete human messenger. It now has local contacts,
transcripts, device receipts, aggregate receipt stores, reviewed durable
outbox plans, native timer-friendly one-shot sending, dead-letter expiration,
a bounded `person background-run` loop, resident-service render/receipt
commands, local human-read state, transcript convergence checks, and signed
group status summaries. It does not yet provide guaranteed delivery to devices
that never come online, independent witness custody for person/group
freshness, global transcript total order, or automatic Tox group/conference
adapters. See
`docs/person-multidevice.md`.

Then apply one reviewed target at a time:

```sh
cat RECALLROOT.txt | \
  iotox self-swarm grant-recall-stdin \
    ~/.local/state/iotox/self.swarm laptop \
    --min-generation 2 \
    --expect-member laptop LAPTOP_PRINCIPAL_HEX \
    --expect-route laptop LAPTOP_TOX_KEY_HEX
```

The apply command resolves the active roster member and delegates exactly that
member's rostered role and capabilities through the existing
`authority-delegate-self-recall-stdin` machinery. Retired members cannot be
granted.

Retire a lost, sold, reinstalled, or distrusted machine:

```sh
iotox self-swarm retire-plan ~/.local/state/iotox/self.swarm laptop \
  --min-generation 2 \
  --expect-member laptop LAPTOP_PRINCIPAL_HEX

cat RECALLROOT.txt | \
  iotox self-swarm retire-recall-stdin \
    ~/.local/state/iotox/self.swarm laptop \
    --min-generation 2 \
    --expect-member laptop LAPTOP_PRINCIPAL_HEX

cat RECALLROOT.txt | \
  iotox self-swarm revoke-retired-recall-stdin \
    ~/.local/state/iotox/self.swarm laptop \
    --min-generation 3
```

Retirement advances the signed roster generation and marks the member retired.
The revoke apply command refuses active members and revokes only a retired
member's stable principal.

## Remaining self-swarm limits

The current self-swarm is smoother but still deliberately explicit. It has
native roster fanout, a local generation/digest floor, optional live
alias-route proof, and a public person delivery-card/message fanout layer. It
does not silently auto-apply a roster that arrives by file transfer. Each
receiver must still verify owner/generation/member/route facts and commit its
own floor. The floor is local state, not an independent remote witness. It also
does not yet carry a route privacy policy, so Tor/I2P native-fallback refusal
remains route-inventory work.

The person layer now includes public route cards, delegated device senders,
card/contact floors, local duplicate suppression, signed group descriptors,
contact books, transcripts, delegated device receipts, aggregate receipt
stores, durable reviewed outbox plans, native one-shot outbox sending,
dead-letter expiration, a bounded background runner, resident service
artifacts, local read marks, transcript convergence checks, and group-status
summaries. It still does not solve background roster freshness distribution,
delivery to devices that never return online, independent freshness custody,
global conversation ordering, or automatic Tox group/conference carrier use.

Missing profile, missing profile binding, missing `interactive.terminal`, and
sudo refusal remain Ratox/authority/profile checks. That separation is
intentional: membership helps the owner coordinate their machines, but it never
turns a peer into a shell by itself.

## Documentation boundary

Where older docs say “Ratox is default-off,” read that as “manual mode and
ordinary upgrades do not expose Ratox roles.” The current product direction is
more precise:

```text
manual mode: Ratox roles are off unless explicitly enabled
self mode:   Ratox host/controller are selected by default, then
             profile binding and authority decide all effects
```

This distinction matters because IoTox is becoming a self-machine control
tool, not merely a generic Tox peer tool. The more powerful default belongs
only to the explicitly chosen self mode.
