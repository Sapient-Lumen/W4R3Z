# RFC-0117: Capability leases + revocation (revocable dynamic grants)

Status: **draft**

## Motivation

DeriveBSD’s security story depends on least authority being *operationally usable*.
Portals/powerbox brokers (`docs/179-portals-and-powerbox.md`) solve dynamic access, but without a revocation story
we get long-lived authority accretion and “debug exceptions that never go away”.

Capsicum-style kernel capabilities are intentionally hard to revoke once handed out.
We therefore need an explicit **revocable grant** abstraction that stays fail-safe and auditable.

## Goals

- Make every dynamic grant a **lease** with a stable identifier.
- Support **revocation** in a way that is:
  - fail-safe (broker down => capability use fails)
  - evidence-bearing (revocation is explainable)
- Keep the mechanism small and reusable across:
  - file/log export portals
  - cross-compartment RPC
  - brokered secret-ops

## Non-goals

- Perfect revocation of raw kernel primitives (e.g. already-open FDs).
- Global “revoke everything” (that’s a restart/shutdown boundary).
- Designing a desktop UX.

## Proposal

### 1) Lease identifiers

Every portal grant that is intended to outlive a single operation includes:

- `lease_id` (opaque, unique)
- `expires_at` (required for leases)

One-shot/raw grants MAY omit `lease_id`.

### 2) Revocation evidence

Introduce a new evidence object: `portal.revoke`.

It records:
- `lease_id`
- `grant_digest` (or request digest) to bind the revoke to an earlier grant
- `revoked_at`
- optional `reason`
- signature

Schema: `spec/portal.revoke.schema.json`

### 3) Mediated handles

A lease is revocable only if the resource is delivered through a **mediated handle**.
Three delivery patterns are standardized:

A) **proxy capability** (default for long-lived)
- operations are served by a broker that enforces lease validity

B) **fresh-open** per action
- each action re-authorizes through the broker

C) **raw + short TTL** (debug/workstation lane)
- explicitly one-shot with strict byte/time limits

### 4) Policy linkage

Leases MUST be explainable via existing DeriveBSD policy objects:
- a `portal.grant` includes `policy_decision_digest` when relevant
- revocation includes the revoker identity and can optionally cite a policy decision

## Where this plugs in

- Portals/powerbox: `docs/179-portals-and-powerbox.md`
- qrexec/RPC policy: `docs/135-qrexec-style-rpc-policy.md`
- capability routing manifests: `docs/140-capability-routing-manifests.md`

## Security considerations

- Leases should be short-lived by default (minutes), renewable under policy.
- Revocation should be authoritative and local: do not depend on remote connectivity.
- Proxy-based revocation is intentionally fail-safe; it can reduce availability during broker failures.

## Alternatives

- “Never revoke” and rely on restart boundaries (simple, but encourages over-granting).
- ACL-based revocation everywhere (reintroduces ambient naming and state).

## References

- Portal/powerbox concept (Capsicum context): https://www.engr.mun.ca/~anderson/publications/2017/towards-oblivious-sandboxing.pdf
- Flatpak portals overview: https://flatpak.github.io/xdg-desktop-portal/
