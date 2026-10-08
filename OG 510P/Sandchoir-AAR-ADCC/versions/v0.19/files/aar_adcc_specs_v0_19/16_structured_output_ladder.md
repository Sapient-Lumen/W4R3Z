# 16 — Structured Output Ladder (Optional) (v0.19)

Purpose: improve header parse reliability without changing kernel invariants.

Tier 0: Prompt-only BCC (default; universal)
Tier 1a: Router-side JSON healing for CTRLJSON (cheap local fix)
Tier 1: Header-only repair (bounded re-ask)
Tier 2: Field salvage (router parses partial header, asks for missing fields only)
Tier 3: Header JSON validation (router validates CTRLJSON; re-asks on violation)
Tier 4: Constrained decoding (header-only) if local stack supports schema/grammar

Rule: Tier 4 is optional and CAP-gated. System must always fall back to Tier 1.

See also: 26_capability_handshake.md and 30_local_structured_output_integration.md

See also: 34_guided_decoding_and_structural_tags.md and 32_json_healing_and_header_repair.md

See also: 49_structured_headers_integration_matrix.md

CTRLJSON schema validation: see 78_ctrljson_schema_and_ws_object_schemas.md.
