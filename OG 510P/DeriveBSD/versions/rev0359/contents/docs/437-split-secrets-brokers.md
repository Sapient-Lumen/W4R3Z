# Split secrets brokers (Split GPG / Split SSH style)

**Tier:** C (Optional lane)
**Profiles:** A, B, C, D
**Pillars:** isolation, operability, supply-chain
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace, Bundles

“Split secrets” is a **least-authority** pattern: keep private key material in a *more trusted, network-isolated compartment* and allow less-trusted compartments to request **bounded crypto operations** (sign/decrypt/ssh-auth) via a policy-governed broker.

This reduces blast radius when a risky app compartment is compromised: the attacker can’t trivially exfiltrate keys, and every operation can be **consented, rate-limited, and receipted**.

## What we steal (ecosystem lesson)

Qubes OS popularized “smart card as a VM” workflows:

- Split GPG: a client qube delegates crypto operations to a vault qube, keeping secret keys out of the client.
- Split SSH: a client qube uses an ssh-agent socket bridged to a vault qube, so the client never holds the private key.

DeriveBSD already has the primitives to do this **without forks**: microVMs/jails for isolation, capability-brokered portals for cross-boundary operations, and typed receipts for every sensitive action.

## DeriveBSD translation (tight)

### Actors

- **Vault compartment** (jail or microVM):
  - holds the private key material (or a hardware-backed key handle)
  - exposes a brokered portal endpoint for crypto ops
  - is network-isolated by default (policy may allow explicit egress)

- **Client compartment** (jail or microVM):
  - runs risky apps (mail, browsers, dev tools)
  - holds *no* long-lived private keys
  - requests ops via a broker lease + portal session

### Artifacts (reuse existing types)

Use the existing crypto portal types as the stable diff surface:

- Requests: `spec/crypto.op.request.schema.json`
- Receipts: `spec/crypto.op.receipt.schema.json`
- Portal sessions/grants/consent:
  - `spec/portal.session.schema.json`
  - `spec/portal.grant.schema.json`
  - `spec/portal.consent.schema.json`

Each operation is:

1) **Broker→Lease**: a short-lived lease authorizes a narrow operation class (e.g., “SSH auth only”).
2) **Portal session**: the client binds to an explicit portal session constrained by policy (who/what/when).
3) **Plan→Receipt**: the vault executes the crypto op and emits a typed receipt.

### Evidence UX (receipts are the product)

- Every operation yields a `crypto.op.receipt` that records:
  - key identity (content-addressed id or policy id), operation class, client identity, lease id
  - consent outcome (if required), timestamps, and result metadata (not secrets)
- Receipts are included in:
  - support bundles (for incident response)
  - drift bundles (when policy or sandbox posture changes)
  - exports (subject to export policy + transparency lanes)

This makes “who used the key, when, under what authority?” queryable without scraping logs.

## Interop discipline (killable adapters)

Most ecosystems expect a local agent socket (e.g., `gpg-agent`, `ssh-agent`). DeriveBSD should follow **Adapter→Shadow→Replace**:

1) **Adapter (Tier E)**: provide a compatibility socket in the client that forwards to the vault via a brokered portal.
2) **Shadow (Tier C)**: run both paths; compare receipts and behavior; migrate tooling gradually.
3) **Replace (Tier B/C)**: make first-class `crypto.op.request/receipt` the primary path; keep the adapter killable by policy.

Interop must remain removable: if policy disables the adapter, the client should fail closed with a clear receipt/event.

## Gates and review surfaces (where this plugs in)

- Sandbox posture drift is reviewable via `sandbox.profile.diff` (client cannot silently gain new portals/egress).
- Export boundary drift is reviewable via `export.policy.diff` (receipts and bundles leaving the system remain governed).

Suggested gates (profile-dependent):
- **A/D**: require consent (or two-person) for signing operations outside an allowlisted target set.
- **B**: interactive consent + rate limits for high-risk ops.
- **C**: default off; enable per-user or per-app profile.

## Open questions (keep it honest)

- What is the minimal “broker identity” surface for receipts (unit digest, attester identity, user identity)?
- How do we express “operation-scoped” leases without policy bloat?
- How do we prevent confused-deputy via portal routing (client cannot pick a different vault)?

If these grow, do an RFC; keep this doc as the stable lane shape.

## Sources (ecosystem anchors)

- Qubes Split GPG: https://doc.qubes-os.org/en/latest/user/security-in-qubes/split-gpg.html
- Qubes Split GPG-2: https://doc.qubes-os.org/en/latest/user/security-in-qubes/split-gpg-2.html
- Qubes qrexec (cross-domain RPC framework): https://doc.qubes-os.org/en/latest/developer/services/qrexec.html
- Qubes qrexec socket-based services (server in a VM): https://doc.qubes-os.org/en/latest/developer/services/qrexec-socket-services.html
- Qubes Split SSH app/scripts: https://github.com/henn/qubes-app-split-ssh

Last updated: 2026-02-28r154
