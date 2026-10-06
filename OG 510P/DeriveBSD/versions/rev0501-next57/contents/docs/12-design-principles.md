# Design principles (guardrails against monster growth)

1. **Single workflow** (Spec→Lock→Plan→Artifact→Activate/Launch)
2. **Data-first** (typed manifests; deterministic merge semantics)
3. **Policy, not magic** (every exception is explicit and recorded)
4. **Introspection is product** (why/what/where-from is a first-class surface)
5. **Hermetic by default** (sandbox builds; deny network; log impurities)
6. **BSD leverage without core contamination** (use jails/ZFS/pf/Capsicum, keep the Derive core small)
7. **Boring versioning** (stable formats; hashable objects; schema evolution)
8. **Reproducibility is measured** (record impurities, don’t hide them)

Day-0 defaults are tracked as a behavioral checklist:
- `docs/97-non-negotiable-behaviors.md`

## 9) Evidence is a product (receipts everywhere)

If an action is security- or reliability-relevant, it should produce a **typed receipt**:
- configuration applies (`config-receipt`)
- change execution (`change-receipt`)
- platform posture verification (`attestation-receipt`)
- firmware/state/storage/time/pki operations (their respective receipts)
- structured events (`event.record`) instead of log strings

This is how we keep the system explainable, supportable, and audit-friendly without turning every incident into archaeology.

See: `docs/229-evidence-spine-overview.md`.

## 10) Crossings are contracts (interfaces are review surfaces)

Any boundary-crossing interface (RPC, portal, broker, device backend) must be:
- **typed** (schema/IDL)
- **digest-bound** (part of the runtime manifest)
- **policy-keyed** (rules can name it)
- **diffable** (surface changes show up in blast-radius diffs)

This is how we prevent “stringly-typed admin APIs” from becoming an ambient authority backdoor.

See: `docs/183-object-capability-rpc.md`, `docs/339-singularity-manifests-and-contract-channels.md`, `docs/341-doors-lightweight-capability-rpc.md`.


## 11) Authority is engineered (attenuation + revocation are required)

If the system is capability-first, then *authority engineering* is not optional.
Every new capability type or broker must have:

- an **attenuation story** (how to grant less than you hold)
- a **revocation story** (how granted authority stops working)
- a **deep-attenuation story** if returned values can carry authority (membranes)

Default patterns are: **revocation by indirection**, **leases**, and **membranes**.

See: `docs/357-capability-attenuation-revocation-and-membranes.md`, `docs/397-pattern-catalog.md`.


## 12) Kernel UAPI is a contract surface (register + diff + gate)

Syscalls are not the only kernel boundary.
If a surface can be depended on by userspace, it must be treated like a contract:
- registered
- digest-bound
- diffed in review
- gated when it grows authority or parsing surface
- backed by conformance + fuzz harness plans

See: `docs/362-uapi-surface-registry-and-compat-gates.md`.

## 13) Deprecations are explicit (no silent removals)

Removing a surface is as risky as adding one.
If something is going away, the ecosystem must get **advance notice**, a migration path, and a bounded EOL window.

Greenfield advantage: represent deprecations as first-class objects (`deprecation.notice`) and require removals to be auditable via receipts/diffs.

See: `docs/385-deprecation-policies-and-removal-receipts.md`, `spec/deprecation.notice.schema.json`.


## 14) Crypto drift is reviewable (registry + diff + gate)

Cryptography is a long-lived surface.
If the platform does not make crypto choices reviewable, components drift into inconsistent defaults and legacy suites appear by accident.

Greenfield advantage: treat protocols/suites/blessed libraries/key policies as a registered surface (`crypto.registry`) and make changes show up as `crypto.diff` (and optionally in blast-radius diffs).

See: `docs/391-crypto-surface-registry-and-agility-gates.md`, `spec/crypto.registry.schema.json`, `spec/crypto.diff.schema.json`, `spec/crypto.key.policy.schema.json`.


## 15) Policies ship with regression vectors (no silent authority expansion)

Policies evolve over time. Without regression vectors, refactors can silently widen authority.

Greenfield advantage: treat policy test suites and reports as first-class artifacts, and gate high-blast-radius policy changes on passing evidence.

See: `docs/393-policy-tests-suites-and-mutation.md`, `spec/policy.test.suite.schema.json`, `spec/policy.test.report.schema.json`.


## 16) Review starts from one object (drift bundles)

As the system grows, review fails when security-relevant diffs are scattered across many tools and formats.

Greenfield advantage: produce a single, typed **drift bundle** (`drift.bundle`) that summarizes and links the underlying diffs (authority/UAPI/parser/contract/trust/crypto/etc.) and attaches required evidence (tests/fuzz/proofs).

See: `docs/395-drift-bundles-and-review-summaries.md`, `spec/drift.bundle.schema.json`.


Last updated: 2026-02-27r113
