# Policy engine (explicit, enforceable, explainable)

Policy is enforcement over Plans and runtime actions.

## Application points
1) Lock-time: sources, keys, allowed registries
2) Plan-time: sandbox policy, impurities
3) Realize-time: build + verification gates
4) Run-time (vmmd): launch authz, resource/net/secrets constraints

## Minimum properties
- versioned text
- deterministic evaluation
- explainable denials (`derive explain-policy`)

## Binding policy to artifacts

Policy outcomes must be captured as a hashable **policy decision record** during planning.
See `docs/93-policy-decision-records.md`.

## v1 stance
Start with declarative allow/deny matchers (signing key, namespace, target kind), add richer engines later if needed.

## Vulnerability gates

See `docs/60-vulnerability-intel-and-gates.md` (RFC-0037).

## Policy backends + traces

Optional extensibility lane: compiled policy modules as Wasm artifacts (keeps core minimal): `docs/186-policy-modules-wasm.md` (RFC-0121).

See `docs/85-policy-engine-options-and-traces.md` (RFC-0055, ADR-0026) for multi-backend options (matchers/Cedar/OPA) and stable decision trace format.

## Test harness pointer

See `docs/88-conformance-tests-kyua-atf.md` (RFC-0058) for invariants-based conformance testing.


Last updated: 2026-02-23
