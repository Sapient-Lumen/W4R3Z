# Policy trace format + explain surfaces (stable, receipted, LLM-friendly)

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** operability, supply-chain, reproducibility
**Patterns:** Registry→Diff→Gate, Capsule  

DeriveBSD policy is only real if it is **explainable**, **replayable**, and **hash-bound** to the artifacts we ship.

This doc tightens the “decision trace” story by making a stable trace shape a first-class artifact.

## Goals

- Keep policy decisions **reviewable** at plan time and **auditable** after the fact.
- Make policy explanations **machine-usable** (LLMs, UIs, gates) without scraping text.
- Prevent trace output from becoming a secret-leaking debug channel.

## Artifacts

### Policy decision record
The Plan binds a **policy decision record** (hashable) produced during `Lock → Plan`.

See: `docs/93-policy-decision-records.md`, `spec/policy.decision.schema.json`.

### Policy trace
A policy trace is an optional, stable explanation artifact.

- Schema: `spec/policy.trace.schema.json`
- Example: `spec/examples/policy.trace.json`

A decision record MAY either:
- embed a trace inline under `trace` (small, safe), OR
- reference a separately stored trace by `trace_digest`.

This supports two common needs:
- **tiny decisions** that can carry trace inline
- **heavy decisions** (many matched rules) where we want a content-addressed trace object without bloating the decision record

## Trace shape (what it must contain)

The trace format is intentionally small and stable:

- `decision.allowed` plus an optional stable `reason_code`
- `matched_rules[]` with minimal bindings (never secrets)
- `obligations[]` for machine-checkable follow-ups
- `inputs_used[]` so “policy depended on X” is explicit
- `redactions[]` if the engine withheld sensitive fields

This is the minimum set needed to make explanations **durable** and **comparable** across engines.

## Secret safety

Traces MUST:
- never emit secret values
- reference secrets by digest only
- prefer “I redacted field X” over leaking data

If an engine cannot prove a field is safe, it should omit it and emit a `redactions[]` entry.

## Explain surfaces (CLI contract)

### `derive explain-policy`

Must exist and support stable JSON:

- `derive explain-policy --plan <plan-digest> --json`
  - emits a JSON document matching `spec/policy.decision.schema.json`

- `derive explain-policy --plan <plan-digest> --json --trace`
  - emits a JSON document matching `spec/policy.trace.schema.json`

This aligns with `docs/87-structured-output-contract.md` and `docs/81-llm-facing-interfaces.md`.

### Text output

Human output may be richer, but MUST:
- preserve stable reason codes
- avoid secrets
- provide a deterministic “top N matched rules” summary

## Promotion gates

Policy traces are part of the evidence spine:

- policy gates can require `reason_code` stability
- conformance tests can golden-file the JSON trace
- evidence bundles can include `trace_digest` objects for incident review

See: `docs/166-test-receipts-and-promotion-gates.md`, `docs/229-evidence-spine-overview.md`.

Last updated: 2026-02-27r124
