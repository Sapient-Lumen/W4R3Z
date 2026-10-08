# rev0007 — sovereignty entrance, bridgeback, and key-ban guess

This revision lets the distant Nicotine-shaped future back into the room, but only as a design pressure.
The substrate DHT remains the center.
The new guess is that a populated legacy P2P network can become a sovereignty ramp if every willing client can distribute signed I2P/DHT contact cards while the central servers still exist.

The bargain:

1. A client gets a persistent I2P Destination and a DHT signing key.
2. It shares a signed contact card through existing social/client paths: direct invites, buddy lists, rooms, search-result hints, garden seed gates, and cached last-good contacts.
3. Those cards seed entrance to the DHT without making the old central service the DHT's authority.
4. A default-off I2P-only mode lets users start from cached/imported/garden/public seeds without touching the classic servers.
5. Garden nodes may offer classic-client bridge service: a compatibility shim that lets older clients reach DHT-backed peers/results from the other side.
6. Maintainers may ship signed policy capsules that ban keys from official surfaces, bridges, and default seed lists, but these capsules are subjective trust inputs rather than DHT truth.

## The central-server bridge is not a betrayal

The practical path is not ideological purity on day one.
A classic network that already works is a powerful contact-distribution machine.
The mistake would be treating it as the permanent root.
The right use is transitional: while the legacy path is available, clients opportunistically exchange DHT contact cards, grow local caches, introduce friends, teach garden nodes, and slowly make central entrance less necessary.

This cube calls that **soverseed**: sovereignty through redundant seeding, not one heroic hard cutover.

## The contact card

A contact card is the atomic entrance gift:

```text
I2P Destination
DHT public key
node id derived from Destination + key + work nonce
issued_at / expires_at
capabilities
bootstrap hints
signature by the DHT key
```

The card should be small enough to ride weird old paths, copy/paste invites, local contact files, room hints, and future DHT records.
It should be signed, expiring, and easy to discard.
It is not a profile and not a permanent biography.

## I2P-only mode

I2P-only mode should exist and should be default off.
It should mean what it says: no classic server login, no silent fallback to central, no accidental username registration.
It starts from a local bootstrap portfolio: cached cards, imported invites, signed public seed lists, garden seed gates, and optional policy capsules.

The UX should be blunt:

```text
Mode: I2P/DHT only
Classic server: disconnected by policy
Entrances: 38 valid, 5 gardens, 4 channels
Policy: maintainer default enabled
```

A client should not offer I2P-only as a confident button until its entrance cache has enough diversity.
The cube's prototype readiness check uses contact count, garden count, channel count, and freshness.
Those thresholds are guesses, not doctrine.

## Bridgeback to classic clients

The bridgeback idea matters.
If the new DHT is healthy, it should not only ask legacy users to migrate.
It should serve them.

There are three bridge shapes:

```text
localhost compat shim       # one user runs a local fake-classic server pointed at the DHT
private invite gateway      # a garden serves invited classic clients
public garden gateway       # a high-resource garden serves a public compatibility surface
```

A public bridge is high-risk and high-value.
It can make the DHT useful to people who have not changed clients yet, but it becomes a moderation, rate-limit, metadata, and abuse surface.
That is where policy capsules and garden budgets become very useful.

## Ban keys, not the DHT

The uncomfortable guess: maintainers probably need a way to ban keys from official surfaces.
That may be fairer than pretending a FLOSS client has no stewardship obligations.

But the ban must be scoped.
A maintainer-signed policy capsule can say:

```text
this key is not allowed in official seed lists
this key is not allowed to use official/public bridges
this key should not be selected as a garden helper by default
this key should be warned/ignored in app defaults
```

It should not say:

```text
this key cannot exist in the DHT
this key's signed mutable records are invalid by protocol truth
all users must obey this forever
```

Protocol truth remains cryptographic validity.
Application trust remains subjective policy.
Official surfaces may refuse service.
That is the compromise.

## Strongest current guess

The DHT should be built with four entrance planes from the beginning:

```text
contact-card plane       # signed peer/garden entrances
seed-list plane          # signed public defaults, replaceable by users
policy-capsule plane     # signed subjective deny/warn/refuse rules
bridge-service plane     # optional classic-client gateway service
```

The best future is not central-free fantasy.
It is centrality made optional, replaceable, and progressively less relevant.
