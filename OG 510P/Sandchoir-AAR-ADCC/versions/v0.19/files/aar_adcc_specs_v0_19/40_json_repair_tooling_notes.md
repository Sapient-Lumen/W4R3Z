# 40 — JSON Repair Tooling Notes (v0.19)

Your router-side “JSON healing” step (32_json_healing_and_header_repair.md) can be powered by existing repair libraries.

## Why repair libraries matter here
They reduce expensive re-asks by fixing:
- trailing commas
- single quotes
- missing quotes on keys
- missing closing braces due to truncation
- smart quotes / weird unicode

## Candidate implementations (examples)
- `jsonrepair` (JS): widely used for malformed LLM JSON.
- `fast-json-repair` (Python): Rust-backed “repair + parse” approach.

## Policy rule
Even with repair libs:
- heal only small header JSON (CTRLJSON)
- never heal patch diffs or long content
- do at most one heal attempt per slice

## Concrete library examples
- Python: `json-repair` (PyPI)
- JS: `jsonrepair` / similar (ecosystem)

Rust options: `json-fix`, `llm_json`, `repair_json` (see crates/docs).

Rust: consider `json-repair` (crate) or `llm_json` / `repair_json` for header healing.

Recommended stack and schema guardrails: see 77_json_repair_stack_recommendations.md and 78_ctrljson_schema_and_ws_object_schemas.md.
