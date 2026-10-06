# CapTP / OCapN lesson: remote object capabilities without ambient authority

DeriveBSD’s local story leans on **object-capability RPC** (`docs/183-object-capability-rpc.md`)
so authority moves as explicit references, not “whoever can name the thing.”

When you cross a network boundary, the same discipline matters even more.
CapTP (and the modern OCapN effort) is a family of ideas for **distributed object capabilities**
over mutually suspicious networks.

This is not required for a single-host DeriveBSD, but it is a strong “greenfield bake-in” for:
- cluster control planes
- remote portals (admin tooling, consented exports)
- multi-host capability directories

## What to steal

1) **Capability-carrying links, not API keys**
A remote reference is an object handle with:
- an origin (who minted it)
- attenuation (caveats, leases)
- revocation strategy (indirection)

2) **Vats / compartments as the unit of isolation**
Remote object systems model “who owns what” via vats (compartments).
This aligns with DeriveBSD’s jail/microVM compartment model.

3) **Sturdy references are explicit**
Long-lived references (“bookmarks”) are not accidental.
They are minted, stored, rotated, and revoked deliberately.

## DeriveBSD adaptation (tight, optional)

### 1) Remote-capability transport as a first-class *lane*
Treat networked capabilities as a separate lane from “local Cap’n Proto over a unix socket”:
- local: file-descriptor / handle oriented (Doors lesson) (`docs/341-doors-lightweight-capability-rpc.md`)
- remote: CapTP-ish object-capability transport with explicit session identity

### 2) Contract digests travel with the wire
Reuse DeriveBSD’s “crossings are contracts” guardrail:
- each exported object surface has a contract digest
- policy can gate exports/imports by (principal, digest, method)

### 3) Receipts for exports, links, and revocations
Every time you:
- export a remote handle
- persist it as a bookmark
- rotate/revoke it
…you emit a receipt into the evidence spine.

## Why bake this in now?

If we don’t, remote control tends to degrade into:
- ad-hoc TLS endpoints
- bearer tokens copied around
- “god API” admin surfaces

Greenfield advantage: define the *shape* of safe remote authority early.

## References
- CapTP overview (E rights): https://erights.org/elib/distrib/captp/index.html
- Spritely explanation (accessible intro): https://spritelyproject.org/news/what-is-captp.html
- Sandstorm note on Cap’n Proto + CapTP lineage: https://sandstorm.io/how-it-works
