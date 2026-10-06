# Policy decision records (bind policy to the Plan)

DeriveBSD’s policy must be more than “checked at runtime”.
It must be **hash-bindable** to the derivation so that:
- every artifact can prove **which policy allowed it**
- enforcement can be replayed (audits, rebuilds) without ambiguity
- a consuming host can reject artifacts that were produced under the wrong policy inputs

## What it is

A **policy decision record** is a small, canonical JSON object produced during **Lock → Plan**.
It captures:
- an optional `trace_digest` (or inline `trace`) for stable explanations
- an optional `decision_instance_id` for profiles that must distinguish independently issuable decision instances even when the rest of the record would otherwise hash the same
- the **policy engine identity** (name/version/digest)
- the **policy inputs** that can change outcomes (e.g., vulnerability DB snapshot digests)
- the **decision** (allow/deny) and the **effective constraints** applied to the Plan/runtime
- a stable **decision trace** for explanations

The record is hashed (JCS) and its digest becomes part of the Plan identity chain. Profiles that need single-use or re-issuable decisions may use `decision_instance_id` to keep separately issuable records from collapsing to the same digest.

## Where it fits in the identity chain

- `spec_digest`
- `lock_digest`
- `policy_decision_digest`  ⟵ **new**
- `plan_digest = H(lock_digest || policy_decision_digest || evaluated_dag_digest || env_norm_digest || …)`

The policy decision record does **not** need to embed `plan_digest` (avoid circularity).
Instead, the Plan binds the decision record by **including its digest**.

## Why this matters

Without an explicit record, “policy-governed” is hard to prove:
- policy engines may depend on external datasets (vuln feeds, allowlists)
- policy may gate optional impurities (network, time, cache trust)
- runtime constraints (network modes, passthrough devices, resource ceilings) must be enforced

The decision record makes these dependencies explicit and verifiable.

## Signing (optional but strongly recommended)

The digest is always checked.
Policy may additionally require a signature over the decision record digest:
- signed by a **policy authority key** for a given environment/tenant
- optionally countersigned by a builder/CI key (but builder signatures are not trusted alone)

This separates:
- *what policy says is allowed* (policy authority)
- *who executed the build* (builder / CI)

## Storage and distribution

- the decision record is stored as a content-addressed store object
- the Plan references it by digest
- runtime manifests for microVMs should carry the `policy_decision_digest` for audit

See: `spec/policy.decision.schema.json`, `spec/policy.trace.schema.json`, and examples under `spec/examples/`.

## Explain surfaces

A stable command must exist:
- `derive explain-policy --plan <plan-digest>`

The output should be the decision record plus any policy proofs required by the current trust policy.

Pointers:
- trace format + explain surfaces: `docs/416-policy-trace-format-and-explain-surfaces.md`
- policy engine interface + traces: `docs/85-policy-engine-options-and-traces.md` (RFC-0055)
- runtime enforcement surfaces: `docs/94-runtime-blast-radius-contract.md`
- canonical hashing: `docs/80-canonical-json-hashing-jcs.md`

Last updated: 2026-03-18r281
