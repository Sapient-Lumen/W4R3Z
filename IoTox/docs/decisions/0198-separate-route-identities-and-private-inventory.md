# ADR 0198: Separate route identities and keep inventory private

Status: accepted; route-scoped primary defaults implemented, 2026-08-27.

## Context

A Tox public key is observable anywhere that endpoint is used. Reusing one savedata identity on
native networking and through Tor makes those presences trivially linkable even if the Tor socket
itself is perfectly contained. Deriving route keys from the stable IoTox device identity would
create the same correlation by construction.

IoTox already has the right authority hierarchy: one stable device principal signs a route set of
replaceable Tox identities, while the authority ledger grants capabilities above friendship. The
remaining policy question is which transport contexts may share a Tox identity and when another
party may learn that several route identities belong to the same device.

The current route-binding-v1 exchange carries the complete signed route set on each auxiliary Tox
friendship after application transcript confirmation. Its receiver accepts the set only when an
independently authority-authenticated primary association matches, but the sender does not have
that reciprocal authority fact before transmitting the bytes. That construction is sufficient for
the qualified same-context multi-route laboratory. It is not a private cross-context route-discovery
protocol.

## Decision

1. Each externally distinguishable route context uses independent random Tox savedata by default.
   `tox/native`, `tox/tor`, and a future `tox/i2p` are separate contexts. Relay or circuit changes
   within one `tox/tor` context do not themselves rotate the endpoint.
2. The stable device identity, RecallRoot ownership, authority ledger, durable command semantics,
   and signed application objects remain above those route keys. Tox keys are never deterministically
   derived from the stable principal. Rotation is a new random Tox identity admitted by a newer
   stable-device-signed route-set generation.
3. The ordinary CLI default is now route scoped: native uses `device.toxsave`, Tor uses
   `device.tox-tor.toxsave`, and the reserved I2P context owns `device.tox-i2p.toxsave` under the same
   state directory. Because stable identity and authority defaults are directory scoped, this split
   does not create a second owner or device principal. Explicit `--state` and `IOTOX_STATE_PATH`
   remain compatibility overrides and therefore an explicit linkability decision.
4. A cross-route inventory is private authorization material, not discovery metadata. There is no
   public route roster, stable-principal lookup, DHT announcement, bootstrap extension, or
   unauthenticated response that links route keys. Local `routes` output remains same-user and
   content-free.
5. Before mixed native/privacy operation can be qualified, the full signed remote inventory must be
   exchanged only across an already transcript-confirmed and authority-authenticated primary
   association. Auxiliary routes must then disclose only a member-scoped, transcript-bound proof
   for the exact route key already expected from that private inventory. A future wire revision may
   use a signed member statement or equivalent proof, but must not send the complete cross-context
   roster merely because a Tox friend completed HELLO.
6. Route-binding v1 stays byte-for-byte frozen. A v1 route set may continue serving the accepted
   same-context construction, but a set spanning native and privacy-routed identities cannot satisfy
   the M8 privacy exit and must not be represented as doing so.
7. Existing unlabeled savedata has no trustworthy historical route provenance. This revision does
   not silently claim otherwise. The new filenames prevent accidental reuse for fresh default
   starts; explicit legacy paths remain operator-reviewed compatibility inputs until a separately
   designed signed provenance/adoption ceremony can fail closed across upgrades and copied files.

## Consequences

- A first default `tox/tor` start has a different Tox address and friend list from the native
  default. That is the intended privacy boundary, not an identity-loss bug.
- Authorized peers may learn deliberately shared route membership after the private primary
  association; unrelated friends and public observers must not receive the cross-route roster.
- Separate keys reduce one deterministic correlation signal. They do not prove anonymity: timing,
  traffic shape, relay choice, peer behavior, host compromise, or the authorized binding itself can
  still correlate activity.
- The existing generic-SOCKS, operator-Tor, impairment, and total-loss evidence remains valid because
  every accepted cell binds its explicit savedata and makes no cross-context unlinkability claim.
- The next cross-route protocol slice is now sharply bounded: private primary inventory delivery,
  member-scoped auxiliary proof, replay/generation fencing, and a two-IoTox actual-Tor capture. It
  does not require a second authority ledger or a new device identity.
