# Policy engine options (OPA/Cedar/custom) + decision traces

DeriveBSD policy must be:
- **pure**: decision = f(policy_bundle, context_json) → result
- **deterministic**: same inputs → same decision digest
- **explainable**: minimal, stable traces for review + LLMs

## Policy layers (keep separable)

1) **Authorization** (“who may do what”)
- who may activate a host generation?
- who may publish to a channel / sign a cache?
- who may launch a workload in a high-assurance zone?

2) **Constraints** (“what is allowed”)
- which target kinds are permitted (microVM/wasm/…)
- network permissions, secret delivery rules, resource profiles
- allowed impurity knobs for builds

## v1 baseline (recommended)
Start with **schema-defined constraint policy**:
- allow/deny matchers over context (keys, channels, target_kind)
- explicit obligations (“must attach attestation X”, “must deny network”)
- no general-purpose evaluation language in core Derive (ADR-0025)

This aligns with `docs/30-policy-engine.md`.

## Option: Cedar for authorization
Cedar is an authorization-focused policy language (ABAC/RBAC class) with a Rust implementation and strong tooling.
It is a good candidate for the *authorization* layer only.

## Option: OPA/Rego for complex org policy
OPA uses Rego, a declarative policy language designed for querying structured documents.
It is powerful but increases surface area. If adopted:
- run as an *optional* policy backend
- keep DeriveBSD’s core policy schema stable
- treat OPA as “one evaluator among many”, not the source of truth

## Option: policy modules compiled to WebAssembly (Wasm)

If we want richer policy without embedding a full evaluator in core, we can treat policy as a **compiled artifact**:
compile a policy language to a Wasm module and run it in a strictly sandboxed runtime.

Key constraints for a DeriveBSD-compatible lane:
- the module must be a pure function (no ambient I/O)
- the runtime is pinned and resource-bounded (fuel + memory)
- the decision trace records module digests invoked

See: `docs/186-policy-modules-wasm.md` (RFC-0121).

## Decision traces (LLM-friendly)

Trace schema: `spec/policy.trace.schema.json` (see also `docs/416-policy-trace-format-and-explain-surfaces.md`).

Every policy decision emits (either inline in the decision record or stored separately and referenced by `trace_digest`):
- `decision = allow|deny`
- `reason_code` (stable enum)
- `matched_rules[]` (rule ids + minimal bindings; no secrets)
- `obligations[]` (machine-checkable actions)
- `decision_digest` (JCS-hashed)

Traces must not include secrets; secrets are referenced by digest only.

## Non-goals (v1)
- embedding a Turing-complete evaluator
- “policy = arbitrary code”
- opaque explain output

See RFC-0055 and ADR-0026.
References in `docs/32-curated-references.md`.

Last updated: 2026-02-27r124
