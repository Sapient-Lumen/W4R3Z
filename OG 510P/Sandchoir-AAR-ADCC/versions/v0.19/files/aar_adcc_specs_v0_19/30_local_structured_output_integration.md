# 30 — Local Structured Output Integration Notes (v0.19)

This system does **not** require structured decoding, but can opportunistically use it to improve CTRL parse reliability.

## Principle: constrain headers only
- Constrain only `@CTRL` (or `CTRLJSON`) lines.
- Never constrain full responses.

## Candidate stacks (examples)
- vLLM: guided decoding supports choice/regex/json/grammar/structural_tag.
- Ollama: structured outputs via JSON schema in `format`.
- llama.cpp: grammar (GBNF) constraints.

## Compatibility strategy
- CAP# declares what each agent/stack supports.
- Router chooses Tier 0–4 per agent (see 16_structured_output_ladder.md).
- Always fall back to Tier 1 repair.

## Practical recommendation
If you build only one structured-output lane first:
- implement `CTRLJSON` as a single-line JSON object (schema-constrained where possible)
- router translates CTRLJSON into canonical CTRL fields
