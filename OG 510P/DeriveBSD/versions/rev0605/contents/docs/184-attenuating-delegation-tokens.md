# Attenuating delegation tokens (Macaroons / Biscuit lane)

Sometimes you need to delegate authority *through* a chain of compartments/services:
- a UI app asks a broker for access, then hands a narrower capability to a helper
- a fetcher compartment calls into a verifier, which calls into a signer
- a build/test pipeline delegates narrowly scoped read access to an artifact

If this delegation is done with ambient identities ("service A is allowed"), you get **confused deputy** problems and overbroad grants.

This doc captures an optional lane: **attenuating bearer tokens**.

## Lesson to steal

Some token formats support **offline attenuation**: the holder can add restrictions ("caveats") before forwarding, without contacting the original issuer.

Two influential examples:
- **Macaroons**: chained MAC construction; supports decentralized delegation with contextual caveats.
- **Biscuit**: signed blocks + a logic language; supports offline attenuation and third-party blocks.

These tokens act like "capability mail": you can safely pass them around *as long as you keep shrinking them*.

## DeriveBSD mapping

DeriveBSD already models "dynamic authority" as a portal grant (`portal.grant`) and "crossing policy" as qrexec-shaped RPC.
Attenuating tokens fit as a *transport-friendly delegation primitive* for:

- **cross-compartment RPC**: attach a narrowed token to a single request
- **credential broker outputs**: mint short-lived, scope-limited tokens instead of exporting long-lived secrets
- **fleet operations**: delegate one-shot rollout approvals or read-only artifact access

### Recommended posture

- Tokens should be **short-lived** (minutes, not days).
- Prefer **request-bound** caveats (method + arguments + target) instead of broad "scope" strings.
- Treat tokens as **bearer**: require TLS/vsock channel binding where feasible, and assume theft is catastrophic.
- Never store raw tokens in the content-addressed store; only store evidence about their issuance/use.

## Evidence objects (optional)

Two patterns that preserve DeriveBSD’s "explainability" without archiving secrets:

1) **Token issuance evidence** (broker-side)
- record the mint event, token format, expiry, and a digest of the token bytes
- bind to a plan/policy decision digest when relevant

2) **Delegation snapshot evidence** (debug/audit mode)
- record caveat blocks / restrictions applied (redacted)
- record a digest chain so you can prove attenuation happened

Schema sketch (minimal): `spec/capability.token.schema.json`.

## Pointers

- Portal broker (mediated acquisition): `docs/179-portals-and-powerbox.md`
- Leases + revocation: `docs/182-capability-leases-and-revocation.md`
- Object-capability RPC substrate: `docs/183-object-capability-rpc.md`
- Credential broker outputs: `docs/151-factotum-style-credential-broker.md`

Last updated: 2026-02-24
