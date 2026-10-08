# Control-plane surface classes

The generated i3/X11 warm-runtime stack now classifies every helper in `control-plane.json` so a shell caller or private LLM can tell **what kind of truth** each surface exposes before it acts.

## Classes

- `canonical_project_source` — checked-in editable project truth; change the source here, then re-render, lint, validate, or replay through generated helpers
- `generated_review_surface` — generated review wrappers and recorder evidence surfaces; inspect or compare here, but do not treat them as the canonical source of truth unless the helper explicitly writes back into source
- `runtime_snapshot` — read-only live state such as readiness, health, inventory, recommended next actions, or fused stack truth; refresh by running the helper again
- `runtime_actuation` — execution/control entrypoints that run macros, dispatch to the warm runtime, record, reload, stop, or otherwise mutate runtime or source
- `runtime_observability` — read-only operator/forensics surfaces for latest runs, artifacts, traces, history, and logs

## Non-claims

The control plane now also carries explicit `non_claims` so callers do not overread generated surfaces:

- generated review helpers and runtime snapshots are **not** canonical editable project source
- recorder review warnings are advisory triage signals, **not** automatic proof that a macro cannot run
- recommended next actions are prioritized guidance, **not** exclusive authority to mutate source

## Why this matters

This prevents a private LLM from collapsing unlike surfaces into one bucket. `macro_source_json.sh` is the place to find and edit project truth, `macro_author_queue_json.sh` is the place to decide which macro should enter the author loop next, `macro_runtime_board_json.sh` is the place to decide what is fit for warm dispatch now, `macro_acceptance_ledger_json.sh` is the place to inspect explicit operator signoff, `optimize_macro.sh` is the place to inspect a generated cleanup proposal, `stack_state_json.sh` is the place to inspect live fused truth, and `dispatch_macro.sh` is the place to execute.

That distinction is part of the flagship product shape: the warm runtime is useful because it exposes **bounded, typed, reviewable surfaces** instead of forcing every caller to rediscover authority and mutability from raw files or ad hoc shell grammar.


## Checked dispatch gate

`macro_dispatch_gate_json.sh <macro>` is a runtime snapshot surface. `dispatch_macro_checked.sh [--force] <macro>` is a runtime actuation surface that consults that gate before emitting.
