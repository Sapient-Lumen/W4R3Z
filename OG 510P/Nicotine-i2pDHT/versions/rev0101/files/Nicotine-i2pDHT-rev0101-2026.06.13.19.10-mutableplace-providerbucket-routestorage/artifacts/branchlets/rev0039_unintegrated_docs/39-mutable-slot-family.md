# Mutable slot family

rev0002 and rev0003 inserted BEP44/BEP46-style mutable records early.  rev0004 broadens the design: mutable records should be born as a **family** of validators rather than a single record class.

## Single-writer head

The base primitive remains:

```text
target = H(pubkey || salt)            # BEP44 facet, 160-bit
native = SHA256(domain || pubkey || salt)
value  = small canonical payload
seq    = monotonic integer
sig    = Ed25519 over salt/seq/value
```

Use cases: mutable torrent head, update head, directory head, signed pointer.

## Delegated head

A long-term identity signs a delegation to a writer key.  The writer key updates the slot until delegation expiry.

Use cases: safer operational rotation, team publishing, revocation experiments.

## Merkle feed

The mutable value points to a Merkle/log tip.  The DHT only stores the current small head.  The body lives elsewhere as provider-addressed content.

Use cases: changelogs, social-ish feeds, package/update streams, append-heavy directories.

## CRDT registry

A mutable value points to a canonicalized multiwriter state root.  Storage nodes only validate the head signature/root shape; consumers resolve and merge the body.

Use cases: distributed directories, group indexes, room heads, community-maintained maps.

## Design constraint

Storage nodes must not need app semantics.  They need validator semantics: target, signature, sequence/root monotonicity, size, expiry, and namespace.

## Python surface

`mutable_family.py` encodes the target-separation and validator-name idea.  It is scaffolding, not a full multiwriter record system.
