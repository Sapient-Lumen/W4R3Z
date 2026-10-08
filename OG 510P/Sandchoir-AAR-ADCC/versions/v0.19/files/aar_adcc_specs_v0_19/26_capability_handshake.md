# 26 — Capability Handshake (CAP#) (v0.19)

CAP# is the **only** place where local-stack features (structured outputs, streaming, git, etc.) are declared in a machine-parseable way.
It is advisory; the system must degrade gracefully when CAP# is missing or wrong.

## Why this exists
- Avoid guessing what each CLI client/model supports.
- Let the Bandwidth Adapter and MetaLLM choose *per-agent* tactics (e.g., enable header-only constraints for one agent that keeps failing @CTRL).
- Keep this out of the kernel wire format: CAP# is a WS object, not a protocol rewrite.

## CAP# schema (minimal)
- `id`: CAP# (router assigns)
- `agent`: A1..A5
- `supports` (set of enums):
  - `streaming_read` (router can read partial output)
  - `ctrljson_schema` (agent can emit `CTRLJSON={...}` reliably)
  - `guided_choice` / `guided_regex` / `guided_grammar` / `guided_json_schema`
  - `structural_tag` (tag-bounded schema constraints)
  - `git_diff`
  - `verifiers`
- `limits` (optional):
  - `max_output_tokens`
  - `typical_truncation` (soft)
  - `time_to_ctrl_ms_p50` (measured)
- `last_probe_cursor`

## Probe protocol (slice-safe)
1. Human or MetaLLM: `cap probe --agent=A2 --mode=fast`
2. Router asks agent to emit:
   - `@CTRL` + (optional) `CTRLJSON` line
   - a tiny `supports=` declaration (or “unknown”)
3. Router posts/updates CAP# with measured parse+timing stats.

## Router behavior
- If CAP supports guided decoding: router may enable Tier-4 for `@CTRL` only.
- If CAP lacks it: router sticks to Tier-0/Tier-1 ladder.
- CAP claims can be overridden by observed telemetry (truth > claims).

## Telemetry tie-in
- `cap.probe_started`, `cap.probe_finished`
- `bcc.ctrl_seen.t_ms` becomes the primary empirical “capability.”
