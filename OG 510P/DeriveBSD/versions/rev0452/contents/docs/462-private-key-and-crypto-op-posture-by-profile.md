# Private-key and crypto-operation posture by profile

**Tier:** C (Optional lane)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, supply-chain, operability  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

DeriveBSD already has a strong **crypto broker** story.
What this doc decides is narrower and more important for coherence:
**what is the default private-key / crypto-operation posture for each product shape?**

This is intentionally **not** a backend choice.
It is a product-default decision.

See also:
- ADR: `adrs/ADR-0052-private-key-and-crypto-op-posture-by-profile.md`
- crypto lane: `docs/306-crypto-operations-portal-and-split-keys.md`
- key policy surface: `docs/392-crypto-key-policies-and-nonexportable-handles.md`
- split-key pattern: `docs/437-split-secrets-brokers.md`
- multiparty approvals: `docs/288-multiparty-approvals-and-separation-of-duties.md`

## Why this needs a hard decision

Every serious system eventually accumulates private keys:

- SSH / operator auth keys
- release / package signing keys
- decryption keys
- service identity keys
- workstation user keys for mail, code signing, or auth workflows

If the archive leaves this as “implementation detail”, real deployments drift toward:

- file-based long-lived keys copied into hosts and apps,
- agent sockets that can sign anything in the background,
- desktop apps quietly holding raw private-key bytes,
- or factory/release keys living in places they should never exist.

That breaks all four product shapes differently.
So we decide the **default authority model** now, while leaving backend and receipt detail work open.

## Product-shape defaults

### A) Secure fleet host (`fleet_host`)

Default: `brokered-nonexportable-headless-policy-gated`

- Headless hosts use brokered, non-exportable keys by default.
- User presence is not assumed; policy or quorum gates are the authority model instead.
- Long-lived exportable private-key files on workload hosts are not the baseline.
- Compatibility agent paths, if used, stay adapter-shaped and killable.

### B) Secure workstation (`workstation`)

Default: `brokered-nonexportable-user-presence-vault-preferred`

- Human-facing keys prefer a split-key vault, platform keystore, smartcard, or similar non-exportable handle.
- Risky apps get crypto **operations**, not raw private-key bytes, by default.
- High-value interactive key use should require user presence.
- Remembered permissions still need lease/policy semantics rather than ambient background signing.

### C) General-purpose OS (`general_os`)

Default: `brokered-preferred-explicit-file-key-adapter`

- Brokered/non-exportable key use is the preferred path for derived workloads.
- File-backed keys and classic agent sockets may exist only as explicit adapter fallbacks.
- Compatibility remains reviewable and killable rather than silently redefining the default trust model.

### D) Appliance factory / regulatory (`appliance_factory`)

Default: `offline-or-hsm-quorum-nonexportable`

- Production/manufacturing/release keys stay offline, hardware-backed, or in isolated vault/KeyVM compartments by default.
- Quorum/two-person controls are the default for high-value signing lanes.
- Interactive convenience prompts are not the authority model for production or evidence-bearing flows.
- Exportable private-key files in production/factory images are out of scope by default.

## Cross-profile invariants

Regardless of profile:

- no ambient “sign anything” background authority
- key use is scoped by purpose and policy, not just possession of bytes
- non-exportable handles are the default; exportability is exceptional and explicit
- receipts should record digests/policy/lease context, not plaintext secrets
- adapter paths may exist, but they stay killable and reviewable
- compatibility agents stay explicit local-session projections instead of ambient standing authority
- remembered approvals stay same-lease-only rather than surviving as agent folklore

## What this does *not* decide

Still open:

- the exact per-op receipt redaction/aggregation defaults
- the stable destination-tag vocabulary for sign/decrypt/auth requests
- which key classes require quorum by default beyond the product-shape baseline
- how platform keystores, TPMs, PKCS#11 tokens, and KeyVM backends map into one receipt surface

That work stays implementation-level.
This doc only fixes the product-default boundary so the archive can make progress without drifting.

Last updated: 2026-03-23r434
