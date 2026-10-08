# 73 — ANSI + Terminal Control Handling (v0.19)

Multi-agent CLI orchestration lives and dies on reliable parsing.
Terminal output often contains:
- ANSI colors
- cursor movement
- progress spinners
- OSC sequences (some tools emit machine-readable progress codes)

Policy: **parse from a cleaned stream** but **retain raw** for the Ledger.

## 1) Two streams per agent
- `raw_stream`: exact PTY bytes (for debugging/ledger)
- `clean_stream`: ANSI/control sequences removed or normalized (for parser)

The router logs both:
- WS references only the cleaned summary lines
- Ledger can link to the raw blob for full fidelity

## 2) Stripping ANSI escape sequences
Default: strip for parsing and for stable diffs.

Implementation options (Rust):
- `strip-ansi-escapes` (bytes -> bytes)
- CLI tools like `ansi-stripper` / `strip-ansi-cli` if you need shell-side cleanup

## 3) OSC and structured terminal signals
Some tools emit OSC sequences (e.g., build progress). Treat these as:
- a separate signal lane (optional)
- never mixed into WS bodies
If you parse them, store as telemetry/events.

## 4) Safety and operator experience
- Never “strip” the raw log. Humans need it to debug weirdness.
- Always show “parser view” in the gearbox to explain why CTRL wasn’t detected.

## 5) Parsing-friendly defaults
If you control invocation:
- disable colors: `NO_COLOR=1` or `TERM=dumb` (if compatible)
- prefer deterministic output over fancy UI
But: don’t rely on this; clients vary.

## 6) Failure handling
If clean stream loses structure:
- fall back to raw search for CTRL markers (bounded scan)
- mark truncation heuristics
- let repair ladder attempt salvage
