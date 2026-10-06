# Crypto compatibility agents stay local-session projections and not ambient remote authority

**Tier:** C (Optional lane)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability, supply-chain  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

The archive already decided that private keys should prefer brokered, non-exportable use.
This page closes the next smaller loophole:
classic compatibility sockets may exist, but they do **not** become the real authority model.

See also:
- ADR: `adrs/ADR-0293-crypto-compatibility-agents-stay-local-session-projections-and-not-ambient-remote-authority.md`
- crypto portal lane: `docs/306-crypto-operations-portal-and-split-keys.md`
- split-key broker pattern: `docs/437-split-secrets-brokers.md`
- product defaults: `docs/462-private-key-and-crypto-op-posture-by-profile.md`
- helper artifacts: `spec/crypto.op.request.schema.json`, `spec/crypto.op.receipt.schema.json`

## Accepted boundary

### 1) Compatibility sockets are adapters over the broker

When DeriveBSD exposes an `ssh-agent` or `gpg-agent`-shaped socket, that socket is a **projection** over the brokered crypto path.
The authority object remains the lease + policy + broker decision, not the existence of a Unix socket.

### 2) `projection_scope` is `local-session-only`

The first reviewed scope is intentionally narrow:

- the projection belongs to one local login/session surface
- it is killable when that session ends
- it does not become a host-global standing capability
- “the agent kept running” is not a reason to preserve authority

### 3) remembered approval stays `same-lease-only`

Remembered approval is allowed only in the smallest bounded form:

- it may suppress repeated prompts inside the same active lease
- it does not survive into a later lease
- it does not bless later remote forwarding
- it does not silently become durable local policy

### 4) remote forwarding is not baseline truth

DeriveBSD does not treat forwarded compatibility agents as the normal answer for cross-machine crypto use.
That path is too good at hiding where authority really lived.
If a future remote lane is worth having, it needs its own explicit artifact family and review surface.

### 5) the proof surface is typed

`crypto.op.request` and `crypto.op.receipt` can now carry:

- `compatibility_projection.adapter_protocol`
- `compatibility_projection.projection_scope`
- `compatibility_projection.remembered_approval_scope`

That is enough for support, policy explain, and future migration work to talk about the projection path without turning adapters into folklore.

## Why this helps all four product shapes

- **A / secure fleet host:** keeps headless policy authority on the broker instead of on forwarded sockets or daemon leftovers.
- **B / secure workstation:** allows practical legacy app interop while keeping remembered prompts bounded and explainable.
- **C / general-purpose OS:** preserves compatibility without letting the compatibility path redefine the product.
- **D / appliance/factory/regulatory:** keeps high-value signing lanes out of ambient agent-forwarding convenience.

## First spec cut

The first implementation-shaped cut is deliberately small:

- `spec/crypto.op.request.schema.json` gains optional `compatibility_projection`
- `spec/crypto.op.receipt.schema.json` gains optional `compatibility_projection`
- first canonical examples show `ssh-agent` with `local-session-only` and `same-lease-only`

That is enough to hold the line in schemas and examples without pretending the entire UX is finished.

## Related docs

- `adrs/ADR-0293-crypto-compatibility-agents-stay-local-session-projections-and-not-ambient-remote-authority.md`
- `docs/306-crypto-operations-portal-and-split-keys.md`
- `docs/392-crypto-key-policies-and-nonexportable-handles.md`
- `docs/437-split-secrets-brokers.md`
- `docs/462-private-key-and-crypto-op-posture-by-profile.md`
- `spec/crypto.op.request.schema.json`
- `spec/crypto.op.receipt.schema.json`
- `spec/examples/crypto.op.request.compat-agent.json`
- `spec/examples/crypto.op.receipt.compat-agent.json`

## References

- OpenSSH release notes (forwarded-agent PKCS#11 provider loading risks): https://www.openssh.com/releasenotes.html
- OpenBSD `sshd_config(5)` (`AllowAgentForwarding` caveat): https://man.openbsd.org/sshd_config
- GnuPG agent forwarding notes: https://wiki.gnupg.org/AgentForwarding

Last updated: 2026-03-23r434
