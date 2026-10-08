# Subjective key bans and maintainer authority

This is the hard social layer.
A FLOSS client can be decentralized and still have maintainers.
A DHT can be open and still let official builds refuse keys from official surfaces.

The cube's guess: use signed **policy capsules**.

## What a policy capsule is

```text
authority name
authority public key
sequence
issued_at / expires_at
entries[]
signature
```

Each entry targets a public key and scopes the refusal:

```text
official_bootstrap
garden_service
classic_bridge
app_default_warn
app_default_ignore
dht_store_deny, local only
```

A capsule is not a protocol law.
It is a subscribed policy.

## What maintainers can fairly control

Maintainers can fairly control:

```text
keys shipped as default seeds
keys allowed on official bridge surfaces
keys recommended as default gardens
keys accepted by official public infrastructure
warnings/ignores in default app policy
```

They cannot honestly control:

```text
what keys exist in the DHT
whether a cryptographically valid mutable record is valid by protocol
what every third-party build or fork must accept
what private users choose to trust
```

That split feels like the fair tradeoff.

## Why keys, not names

Names are cheap, ambiguous, and culturally loaded.
DHT keys are at least cryptographic handles.
If a key is compromised, abusive, poisoning providers, flooding bridges, or attacking official infrastructure, official surfaces can refuse that key.
A user can still disable the maintainer capsule or subscribe to another one.

## Ban-list shape

Policy capsules should:

```text
expire
have monotonic sequences
include scoped reasons
include evidence hashes where possible
support temporary holds
allow replacement-key notes where appropriate
be mirrored by gardens but signed by the authority
be visible in the UI
```

The DHT can distribute policy capsules as mutable signed records.
Garden nodes can cache and mirror them.
They do not author them unless they are the subscribed authority.

## The warning

This is centralization pressure.
It is also probably necessary for official builds, public bridges, and maintainer legitimacy.
The design answer is not denial; it is explicit scoping, replaceability, transparency, and refusal without pretending to rewrite protocol truth.
