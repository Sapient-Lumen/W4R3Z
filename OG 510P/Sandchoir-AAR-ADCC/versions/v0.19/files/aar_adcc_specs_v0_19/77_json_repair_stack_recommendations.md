# 77 — JSON Repair Stack Recommendations (v0.19)

You want repair without wasting turns.
This doc recommends a layered JSON repair stack for CTRLJSON.

## 1) Rust options
- `json-repair` crate
- `llm_json` (ported from python json_repair; LLM-friendly repairs)
- `jsonrepair` (fast, low-dependency) — consider for hot path

## 2) Python option (if you prototype in Python)
- `json-repair` PyPI

## 3) Selection guidance
- Use a fast, low-allocation repair library in the hot path.
- Keep a slower but more permissive repair as fallback if needed.

## 4) Guardrails
- Only repair CTRLJSON, not the whole output.
- Validate result against schema:
  - allowlist keys only
  - cap array sizes
  - clamp vote values
- If schema validation fails: treat as parse failure, not “best effort.”
