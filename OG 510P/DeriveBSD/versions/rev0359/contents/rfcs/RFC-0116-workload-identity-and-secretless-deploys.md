# RFC-0116: Workload identity + secretless deploys (SPIFFE/SPIRE-shaped lane)

Status: **draft**

## Motivation

DeriveBSD’s store/closure model strongly discourages secrets in images, but practical systems still drift toward:

- long-lived credentials mounted into multiple compartments
- privileged control planes that can read everything
- ad-hoc per-app auth implementations

If we want DeriveBSD to stay capability-first at scale, we need a primitive that answers:

> What workload is this, right now, and can it be trusted to receive capability X?

## Goals

- Provide a **host-local** API for workloads (jails/microVMs) to obtain **short-lived identity**.
- Bind identity issuance to **derived plan truth** (deployment refs + closure/runtime digests).
- Enable **secretless patterns**: access is granted based on identity + policy, not static credentials.
- Emit signable **evidence objects** for issuance/renewal suitable for audit and promotion gates.
- Keep the lane **optional**: deployments that don’t want identity infrastructure shouldn’t pay for it.

## Non-goals

- Implementing a full service mesh.
- Replacing all existing PKI.
- Defining a universal secret store. (We define the *broker interfaces and evidence*.)

## Proposal

### Components

1) **Workload Identity Agent (WIA)**
   - Runs host-local (service-jail or dedicated microVM).
   - Exposes a local-only **Workload API** via:
     - `vsock` for microVMs, and/or
     - Unix domain socket for jails.

2) **Derived workload registrations**
   - During planning/activation, Derive produces a small registration object per workload:
     - workload name
     - closure digest
     - runtime manifest digest
     - allowed selectors (e.g., channel/namespace)
     - desired identity (SPIFFE-style id string)
   - The WIA only issues identity when the running workload matches a registration.

3) **Node attestation input (optional)**
   - The WIA may incorporate host identity and optional measured-boot evidence.
   - For high-assurance channels, identity issuance may be conditional on verifier receipts.

### Identity format

Use SPIFFE ID semantics as the default naming model:

- `spiffe://<trust-domain>/<workload-path>`

DeriveBSD can derive `<trust-domain>` from namespace/channel trust roots, but the exact mapping is policy.

### Issued credentials

The WIA supports one or both:

- **X.509 SVID style**: short-lived cert whose URI SAN encodes the SPIFFE ID
- **JWT SVID style**: short-lived JWT with subject = SPIFFE ID

The minimum viable v1 can be “X.509 only”, with JWT as future/adapter.

### Evidence objects

When identity is issued or renewed, produce `workload.identity.grant`.

Required fields:
- issued_at, expires_at
- spiffe_id
- subject selectors (closure digest, runtime manifest digest, compartment id)
- issuer identity (host id / key id)
- credential kind + digests (no private key material)

Schema: `spec/workload.identity.grant.schema.json`
Example: `spec/examples/workload.identity.grant.json`

### Policy integration

- The WIA is a *mechanism*, not a decider.
- Authorization decisions (which workloads may obtain which identities and which broker operations) are derived from:
  - `trust.policy`
  - capability routing manifests
  - policy decision records

The WIA should be able to run in a “strict mode” where it requires a signed policy decision record for each issuance class.

### Relationship to secrets

Secrets remain **references**, not store content.

The recommended pattern is:

1) workload obtains short-lived identity from WIA
2) workload requests **brokered operations** (factotum-style) using that identity
3) broker issues scoped tokens or performs operations without releasing raw keys

Docs:
- secrets delivery baseline: `docs/63-secrets-sealing-and-delivery.md`
- credential broker: `docs/151-factotum-style-credential-broker.md`

## Implementation sketch (v1)

- WIA listens on `vsock://cid:2 port:xxxx` (microVM) and `/run/derive/wia.sock` (jails).
- A tiny guest/jail-side library (`libwia`) requests:
  - SVID + trust bundle
  - renewal when TTL is near expiry

Selector sources:
- runtime provides: instance name, compartment id
- Derive plan provides: closure digest, runtime manifest digest

The WIA verifies the selector tuple against derived registrations, then issues the credential.

## Security considerations

- **Key handling**: prefer in-compartment key generation when feasible; if the WIA manages keys, isolate its key store (ZFS encryption + key-use evidence optional).
- **API surface**: Workload API must be capability-scoped (only exposed to the intended compartment).
- **Revocation**: lean on short lifetimes + renewal checks; explicit revocation lists are optional.
- **Replay**: bind grants to a nonce and include issuer signatures; store minimal issuance state.

## Alternatives

- Static host-level secrets with per-workload ACLs (simpler, but high blast radius).
- Kubernetes SA tokens / cloud workload identity adapters (useful, but pushes trust to external orchestration).

## References

- SPIFFE overview: https://spiffe.io/docs/latest/spiffe-about/overview/
- SPIRE concepts (node + workload attestation): https://spiffe.io/docs/latest/spire-about/spire-concepts/
- Working with SVIDs: https://spiffe.io/docs/latest/deploying/svids/
