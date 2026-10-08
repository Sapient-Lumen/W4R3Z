# 32 — JSON Healing + Header Repair Policy (v0.19)

Problem: smaller/open models often emit “json-ish” output (trailing commas, smart quotes, missing braces).
If you always re-ask, you waste slices and bandwidth.

Solution: add a **router-side healing step** before the re-ask.

## Where healing applies
- `CTRLJSON={...}` (preferred)
- optional: a compact JSON vote blob if you ever represent votes as JSON

Do NOT heal:
- patch diffs
- long prose
- arbitrary logs

## Repair ladder extension
- Tier 0: prompt-only BCC
- Tier 1a: router-side JSON healing (attempt to fix trivial syntax defects)
- Tier 1b: schema validate (if you have a schema)
- Tier 1c: only then do a bounded re-ask (header-only)

## Boundedness
- Healing runs once per slice.
- If healing fails: at most 1 re-ask.
- If re-ask fails: ledger-only.

## Why this helps
It converts “cheap, local” errors into successful parse without consuming another agent slice.
This mirrors a real desire in structured-output toolchains: repair before re-ask to reduce expensive retries.

See also: 40_json_repair_tooling_notes.md
