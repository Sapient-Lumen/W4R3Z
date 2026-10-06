# RFC-0119: Attenuating delegation tokens lane (Macaroons / Biscuit adapter)

Status: **draft**

## Motivation

DeriveBSD wants least-authority crossings:
- portals/powerbox for mediated dynamic access
- qrexec-shaped policy for cross-compartment RPC
- credential brokers to keep raw secrets out of workloads/builders

In practice, distributed systems still need to **delegate** authority through chains of helpers.
If that delegation is expressed as identity-based ACLs, we accumulate confused-deputy risk and overbroad permissions.

Token formats that support **offline attenuation** provide a usable primitive: the holder can *shrink* authority before forwarding.

## Goals

- Offer a clearly scoped, optional lane for attenuating tokens.
- Prefer token issuance via brokers (not baked into apps).
- Preserve DeriveBSD’s explainability: store *digests and metadata*, not secret token bytes.

## Non-goals

- Mandating any particular token format ecosystem-wide.
- Replacing portals with tokens (portals remain the acquisition boundary).
- Storing bearer secrets in the content-addressed store.

## Proposal

### 1) Support an adapter model

DeriveBSD should support **adapters** for at least:
- Macaroons (caveats)
- Biscuit (blocks + logic)

Adapters are used by:
- the credential broker
- portal services that return token capabilities
- the derive-rpc layer when a request needs delegated authority

### 2) Evidence object: capability token metadata (redacted)

Add an optional evidence object `capability.token` that records:
- token digest (sha256:... of raw token bytes)
- format (`macaroon` | `biscuit` | `ucan` | `opaque`)
- expiry
- caveat summary (structured, no secret material)
- binding context (plan digest / policy decision digest)

Schema: `spec/capability.token.schema.json`.

### 3) Operational constraints

- token TTL should be policy-bound (default short)
- token forwarding should be encouraged to *always attenuate*
- receiving services should verify channel binding when possible

## Security considerations

- Bearer tokens are theft-sensitive; leakage must be assumed fatal.
- Evidence objects must avoid embedding token bytes.
- Caveat summaries must be redaction-aware (no secrets in caveats).

## References

- Macaroons paper (NDSS 2014): https://theory.stanford.edu/~ataly/Papers/macaroons.pdf
- NDSS abstract page: https://www.ndss-symposium.org/ndss2014/ndss-2014-programme/macaroons-cookies-contextual-caveats-decentralized-authorization-cloud/
- Biscuit intro (offline attenuation): https://doc.biscuitsec.org/getting-started/introduction.html
- Biscuit third-party blocks explainer: https://www.biscuitsec.org/blog/third-party-blocks-why-how-when-who/
