# 01 — Boot Compression Contract (BCC) / Wire Format (v0.19)

Goal: every agent output is an **anytime packet** the router can salvage under truncation.

## Required ordering
1. `@CTRL` (must be first and early)
2. Optional `@VOTE` (often inside CTRL)
3. Optional `@PROPOSE` (claims/tasks/tests/CE/reqs)
4. Optional `@EXPORT` (patch summary or artifact pointer)
5. Optional `@NOTES` (ledger-only, capped)

## Minimal `@CTRL` fields (tagged line format)
- `CURSOR=<last_seen_cursor_or_?>`
- `MODE_SUGGEST=<none|recorder|gatekeeper|patchonly|freeze|jailer>`
- `DONE=<yes|no>` and/or `NO_FURTHER_THOUGHTS=<yes|no>`
- `TOUCH=<comma-separated file/component tags or empty>`
- `NEEDS=<what you need next: view|lease|evidence|clarify>`
- Optional: `CAP=<capability refs>` (rare)
- Optional: `CTRLJSON={...}` single-line JSON for header-only constrained decoding (optional tier)

Example:
@CTRL CURSOR=128 DONE=no TOUCH=src/parser.py NEEDS=view MODE_SUGGEST=gatekeeper
@VOTE patch{P7=5,P3=2} floor{A2=4} hot{C12=3} ce_admit{CE4=5}

## Top-K sparse votes (to avoid context bloat)
- Only list non-zero allocations (K<=4 per vote type).
- Implicit zeros everywhere else.
- Router enforces budgets (including quadratic costs if enabled) without extra tokens.

## Promotion rule (strict WS)
- If `@CTRL` missing/unparseable:
  - Entire message goes to Ledger.
  - Router may issue 1 bounded **header-only repair** ask.
- Only structured objects with IDs (C#, T#, P#, CE#, E#, REQ#, LEASE#, CAP#, SUM#) are eligible for WS.

## Bounded repair loop (router-initiated)

Before re-asking, if `CTRLJSON` is present, the router may attempt **local JSON healing** (see 32_json_healing_and_header_repair.md).
- At most 1 re-ask per slice:
  - “Re-emit ONLY @CTRL and @VOTE in the required format; max 6 lines.”
- If repair fails again: ledger-only, no WS promotion.

## No raw logs in WS
- Logs belong in Ledger.
- WS gets **Evidence Cards**: status + signal lines + pointers.

## Caps (defaults; configurable)
- `@CTRL + @VOTE`: <= 12 lines total
- `@PROPOSE`: <= 20 lines
- `@EXPORT`: <= 25 lines (prefer pointer to diff file)
- `@NOTES`: <= 60 lines (ledger-only)
