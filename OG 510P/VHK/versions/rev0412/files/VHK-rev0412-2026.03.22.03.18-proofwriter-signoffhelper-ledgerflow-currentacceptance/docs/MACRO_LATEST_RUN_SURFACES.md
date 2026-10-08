# Macro latest-run surfaces

## Scope

This lane is for the flagship VHK path:

- i3 on X11
- a warm session-bound runtime
- recorder -> cleanup -> replay -> inspect
- a private LLM or operator who is already looking at one macro

It exists so macro-scoped replay inspection does not fall back to project-wide history commands.

## Surfaces

- `vhk macro-latest-run-json <project> <macro>`
- `bin/macro_latest_run_json.sh <macro>`
- `bin/macro_report_latest.sh <macro> [extra report args...]`
- `bin/macro_trace_latest.sh <macro> [out.json] [extra trace args...]`

## Contract

`macro-latest-run-json` answers one narrow question: *what is the newest matching run for this macro right now?*

It returns:

- macro identity and source path
- newest matching run metadata, if any
- that run's health summary
- macro-scoped replay posture (`verified_recent`, `warning_recent`, `failed_recent`, `unverified`)
- preferred next entrypoints for latest-run JSON, report, and trace export
- a small next-step hint

The generated report/trace wrappers then jump directly to that same log path.

## Why this exists

`latest_run_json.sh`, `report_latest.sh`, and `trace_latest.sh` are still useful project-level observability surfaces, but they answer the project's newest-run question, not a macro's newest-matching-run question.

Once VHK added the replay board, the next practical gap was obvious: a private LLM could identify the right macro, but still had to reopen project-wide history/report helpers to inspect that macro's newest run.

These macro-scoped wrappers close that gap and keep replay inspection aligned with the replay board, author queue, author loop, and runtime board.
