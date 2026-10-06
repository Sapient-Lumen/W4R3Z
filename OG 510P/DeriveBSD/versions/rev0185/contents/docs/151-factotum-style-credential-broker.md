# Factotum-style credential broker (protocol-agnostic agent)

Plan 9’s **factotum** is a strong pattern: a small, per-user agent holds keys and mediates authentication so applications don’t embed secret-handling code.
For DeriveBSD, the same idea fits both goals:
- **no secrets in builders** (hostile builders)
- **minimal runtime blast radius** (capability-scoped secret use)

## Why DeriveBSD should care

Even with “explicit injection”, secrets tend to leak into:
- build environments (accidental)
- images (convenience)
- long-lived daemons (scope creep)

A credential broker makes secret use:
- **centralized** (fewer implementations to audit)
- **scoped** (policy decides which compartment can request which operation)
- **observable** (every use can emit evidence)

## DeriveBSD direction

A **credential broker** is a small service (often a service-jail or dedicated microVM) that:
- stores or loads secret material (optionally from a sealed store)
- performs authentication handshakes on behalf of callers
- exposes *operations* (not raw keys) wherever possible

Examples of operations:
- “fetch this Git ref using this identity”
- “establish TLS client auth for this endpoint”
- “sign this digest with this key id”

Concrete OS pattern: Qubes “split GPG” delegates signing/decryption to a more-trusted, isolated domain. DeriveBSD can adopt the same shape as an explicit crypto-domain (see `docs/164-split-crypto-domains.md`).

### Transport

- Prefer local-only transports with strong identity:
  - `vsock` (microVM), or
  - a Unix domain socket inside a service-jail.

### Policy binding

- Requests are authorized by **capability routing** outputs (see `docs/140-capability-routing-manifests.md`).
- The broker never “decides”; it only enforces derived policy.

### Evidence

Each granted operation should emit a small, signable record:
- `cred.use.json`: who/what/when (bounded time), operation type, target, key id (no secret bytes)
- optional transparency lane integration if policy requires it

### Identity binding (recommended)

At scale, prefer issuing brokered capabilities based on **short-lived workload identity** (SVID-style) rather than static credentials.
See: `docs/181-workload-identity-and-secretless-deploys.md`.

## Notes

- This pattern can be **per-user** (interactive operators) and/or **per-system** (service identities).
- Builders should only talk to the broker via policy-approved operations; raw secret bytes should not cross into builder jails.

References:
- Plan 9 factotum manual (agent concept; key attributes; RPC channels): https://9fans.github.io/plan9port/man/man4/factotum.html
- “Security in Plan 9” (factotum + secstore roles): https://www.usenix.org/conference/11th-usenix-security-symposium/security-plan-9
- Plan 9 security paper (factotum consults secstore during bootstrap): https://swtch.com/~rsc/papers/auth.html
- secstore manual (credentials store used by factotum): https://9fans.github.io/plan9port/man/man1/secstore.html
