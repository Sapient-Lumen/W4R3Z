# Revision 0359 — macro-scoped latest-run surfaces

This revision closes the next replay-observability gap after the per-macro replay board.

## What changed

- added `vhk macro-latest-run-json <project> <macro>`
- generated stacks now expose:
  - `bin/macro_latest_run_json.sh <macro>`
  - `bin/macro_report_latest.sh <macro> [extra report args...]`
  - `bin/macro_trace_latest.sh <macro> [out.json] [extra trace args...]`
- per-macro author/runtime followups now prefer those macro-scoped latest-run/report/trace entrypoints over project-wide latest-run history when the question is already about one macro
- generated control-plane and stack docs now treat these wrappers as part of the canonical replay-observability lane

## Why it matters

Revision 0358 fixed replay posture by making it per-macro, but the actual inspection path still forced callers back through project-wide latest-run/report helpers.

That was the wrong shape for a resident runtime and a private LLM. Once one macro is selected, replay inspection should stay on that macro's newest matching log.

This revision makes that lane explicit and generated, so replay board truth and replay inspection now use the same scope.
