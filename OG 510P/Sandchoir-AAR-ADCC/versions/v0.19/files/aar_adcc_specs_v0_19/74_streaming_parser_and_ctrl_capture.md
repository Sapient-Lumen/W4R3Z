# 74 — Streaming Parser + Early CTRL Capture (v0.19)

Unknown slice counts mean we must extract control information early.
The parser is a streaming component that processes output incrementally.

## 1) Parsing goals (in order)
1) Detect `CTRLJSON=` or `@CTRL` as early as possible.
2) Extract sparse votes and proposed object IDs.
3) Detect “DONE=yes” to allow early stop.
4) Capture bounded “artifact pointers” (patch path, exec id, repro recipe) without slurping huge blobs.

## 2) Incremental scanning algorithm
Maintain a ring buffer of the last N bytes/lines (e.g., 32 KB or 200 lines).
On each chunk:
- append to ring
- run cheap scans:
  - look for `CTRLJSON=`
  - look for `@CTRL`
  - look for terminator tags (if any)

If found:
- attempt parse:
  - if CTRLJSON: isolate the JSON substring and run repair ladder
  - if tagged lines: parse key=value patterns with strict allowlist

## 3) JSON isolation heuristics
If output contains:
`CTRLJSON={ ... }`
- extract from first `{` after `CTRLJSON=` to the matching `}` using a stack (bounded)
- if no match: try repair on the partial; mark `json_incomplete=true`

Do NOT attempt to parse arbitrary JSON from the whole output; only the header payload.

## 4) Repair ladder (recap)
- Tier 0: valid JSON parse
- Tier 1a: local JSON repair library (no model calls)
- Tier 1b: heuristics (quote keys, remove trailing commas) if safe
- Tier 2: re-ask agent in strict mode (expensive; avoid)

## 5) Early stop policy (“stop-after-CTRL”)
Once CTRL is parsed:
- Option A (default): keep draining for K more lines (bounded) for context
- Option B (bandwidth collapse): stop reading and move on

This is per-agent configurable and can be learned from telemetry.

## 6) Debuggability
Store:
- parse outcome (ok/repaired/failed)
- reason codes
- byte offsets where CTRL was found
Expose in gearbox “parse inspector.”

JSON repair stack: see 77_json_repair_stack_recommendations.md.
