# 49 — Structured Headers Integration Matrix (v0.19)

Structured outputs are optional, but if available they can dramatically reduce retries.
Because APIs churn, treat this as a compatibility matrix, not a dependency.

## 1) Supported header formats
- Plain BCC tagged lines (`@CTRL ...`)
- `CTRLJSON={...}` single-line JSON (recommended)
- Optional: schema-constrained CTRLJSON via backend

## 2) Backend capability examples (not exhaustive)
- vLLM: JSON schema / pydantic models; may support multiple structured decoding backends
- Outlines: guarantees structured outputs; can work across providers
- Others: grammar-based (GBNF) / regex / choice constraints

## 3) Policy
- Constrain only CTRLJSON, never full text.
- Always run router-side JSON healing before re-ask.
- Fall back to Tier-1 repair if backend support is missing or unreliable.

## 4) CAP gating
Applied per-agent via CAP#.
