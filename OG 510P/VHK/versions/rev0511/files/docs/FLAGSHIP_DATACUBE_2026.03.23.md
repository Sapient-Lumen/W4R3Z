# Flagship datacube — i3/X11 runtime-first contract (2026.03.23)

This is the shortest repo-level description of what VHK is optimizing for **right now**.

VHK is not being shaped as a generic Linux automation umbrella. The active lane is:

- **desktop target:** i3 on X11
- **runtime:** session-bound long-lived user service
- **dispatch path:** thin emitters (`vhk-emit`, i3 bindings, wrapper scripts) into resident `vhk busd`
- **authoring loop:** record -> cleanup -> replay -> inspect -> refine
- **advanced caller:** a private LLM that edits canonical macro source and drives runtime/receipt surfaces without scraping prose

Everything else is judged by whether it sharpens that lane.

## The five axes

## 1) Runtime lane

Question: **is the resident lane healthy on this exact X11/i3 session?**

Read, in order:

- `bin/warm_runtime_ticket_json.sh`
- `bin/check_runtime_json.sh`
- `bin/status_runtime_json.sh`
- `bin/latest_runtime_repair_json.sh`

Healthy means all of these are true at once:

- the daemon is reachable now
- the daemon is bound to the current graphical session, not a stale one
- the daemon is serving the current watcher/runtime contract
- the warm path is still within the fast-path budget

If this axis is unclear, do **not** trust dispatch receipts as current proof.

## 2) Selected-macro lane

Question: **what is the sharpest next move for the macro in focus?**

Read, in order:

- `bin/primary_macro_work_ticket_json.sh`
- `bin/macro_author_loop_json.sh <macro>`
- `bin/macro_dispatch_gate_json.sh <macro>`
- `bin/macro_latest_dispatch_json.sh <macro>`

The selected-macro lane should collapse the big stack into one bounded answer:

- current blocking stage
- current best command
- current source path
- current verify step
- whether the sharper next hop is authoring, replay repair, checked dispatch, receipt inspection, or runtime repair

## 3) Source-of-truth lane

Question: **what can be edited, and what must only be regenerated or refreshed?**

Canonical editable truth:

- checked-in project files, especially macro YAML surfaced by `bin/macro_source_json.sh <macro>`

Read-only or generated truth:

- `control-plane.json`
- generated `bin/*.sh` wrappers
- recorder sidecars
- dispatch receipts
- runtime snapshot JSON helpers

Rule: **edit source, then regenerate/re-run review helpers; do not edit generated helpers as if they were source.**

## 4) Execution lane

Question: **should VHK dispatch through the warm lane or fall back to a direct run?**

Read:

- `bin/macro_dispatch_gate_json.sh <macro>`
- `bin/dispatch_macro_checked.sh <macro>`
- `bin/run_macro.sh <macro>`
- `bin/latest_dispatch_json.sh`

Execution policy:

- prefer checked warm dispatch when the gate is clear
- prefer direct run when the gate says the resident lane or current proof is not ready
- prefer receipt/runtime inspection over re-dispatch when the newest receipt is already telling you what drifted

## 5) Proof lane

Question: **is the newest replay or dispatch proof still current?**

Read:

- `bin/macro_replay_board_json.sh`
- `bin/macro_dispatch_history_board_json.sh`
- `bin/macro_acceptance_ledger_json.sh`
- `bin/macro_latest_run_json.sh <macro>`

Proof is only current when it still matches:

- current macro source
- current recorder/selector assumptions where relevant
- current resident runtime witness
- current X11/i3 desktop-session witness

That means replay proof, dispatch receipts, and durable acceptance are all allowed to go stale for honest reasons.

## What gets demoted

These can remain in the repo, but they are not allowed to blur the flagship story:

- broad Wayland parity
- portal-first activation as the default runtime narrative
- app-native adapters that do not materially improve the i3/X11 core
- generalized cross-desktop ambition that makes the core runtime harder to reason about

Preserve those lanes in `vault/` or behind explicit “secondary” framing when they are useful research, fallback knowledge, or future leverage.

## Product decisions this implies

- keep the runtime warm and long-lived
- keep emit/dispatch paths cheap and boring
- keep X11/i3 control explicit and testable
- keep recorder cleanup and replay proof first-class
- keep one-read machine-readable control-plane surfaces for humans and a private LLM
- demote abstractions that mostly exist to serve non-flagship directions
