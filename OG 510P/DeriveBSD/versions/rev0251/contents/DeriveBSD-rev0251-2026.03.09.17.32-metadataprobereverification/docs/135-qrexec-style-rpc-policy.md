# Qrexec-style cross-compartment RPC (policy-governed)

MicroVM-first systems inevitably need *some* cross-compartment operations:
- launch/stop/inspect workloads
- fetch updates (often in a separate “fetcher” compartment)
- deliver non-secret config or sealed secret envelopes
- perform controlled file copy / log export / debug actions

Qubes OS solved a similar problem (strict domain isolation, but required admin-driven actions) with **qrexec**: an RPC mechanism whose calls are mediated by a **policy engine**.

## Lesson to steal

1) **RPC calls have a small, reviewable shape**
- `source` domain
- `target` domain
- `service` name (+ optional argument)

2) **Deny-by-default policy** decides whether a call is allowed.
- “allow” rules can be narrow and auditable
- interactive “ask” is possible, but should be development-only

Operational detail worth copying: policy parsing should be **fail-closed** — if the policy is empty or fails to load, all calls are denied.

Interactive “ask” can be viewed as a special case of a general **portal/powerbox** broker: a typed request is mediated by policy and (optionally) UI, and every grant is evidence-bearing.

3) **The policy decision is evidence**
- every allowed call should yield an evidence object (who/what/when)

References:
- Qubes qrexec overview: https://doc.qubes-os.org/en/latest/developer/services/qrexec.html
- Qubes qrexec policy format: https://dev.qubes-os.org/projects/qubes-core-qrexec/en/stable/qrexec-policy.html

## DeriveBSD mapping

DeriveBSD can implement a minimal “derive-rpc” lane over **vsock/virtio** (microVM) and/or Unix sockets (service jails), with a *qrexec-shaped* contract.

Mechanism note: prefer an **object-capability RPC** substrate so crossings hand out *capability references* rather than relying on ambient global service names. This makes authority easier to route, lease, and revoke. See: `docs/183-object-capability-rpc.md` and `docs/182-capability-leases-and-revocation.md`.

Delegation note: some calls need request-scoped delegation tokens (avoid identity-based "service A" ACLs). Prefer attenuating token formats; see `docs/184-attenuating-delegation-tokens.md`.


With that in mind, the policy contract stays:

- **RPC request**: `{source_instance, target_instance, service, argument, request_digest}`
  - `request_digest` binds the call to a Plan/policy decision context when relevant
- **Policy evaluation**: the policy engine decides `allow/deny/ask`.
  - production default: `deny` unless explicitly allowed
- **Evidence object**: emit `rpc.decision` and `rpc.transcript.digest` (never plaintext secrets)
  - store as content-addressed objects; cite from `derive explain`

### Why this belongs in DeriveBSD

- blast radius minimization isn’t just “VM boundaries”; it’s also **controlled crossings**
- “why did this happen?” becomes answerable: every crossing is a signed/policy-bound decision

## Non-goals (v1)

- building a desktop-style UX
- interactive prompts outside development policy

Candidate RFC: *Cross-compartment RPC policy + evidence objects*.

Last updated: 2026-02-24
