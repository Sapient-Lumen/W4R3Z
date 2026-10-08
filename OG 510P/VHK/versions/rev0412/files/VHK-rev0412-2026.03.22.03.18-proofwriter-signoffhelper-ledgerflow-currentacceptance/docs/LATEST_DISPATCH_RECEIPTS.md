# Latest dispatch receipts

The warm i3/X11 stack now writes a durable receipt for each generated-stack dispatch attempt under:

- `build/dispatch_receipts/latest.json`
- `build/dispatch_receipts/history/*.json`

This is the resident-runtime answer to: **what did the last thin-dispatch attempt actually do?**

## Why this exists

VHK already had:

- a project-wide dispatch catalog (`macro_dispatch_catalog_json.sh`)
- a per-macro checked dispatch gate (`macro_dispatch_gate_json.sh`)
- a checked dispatch wrapper (`dispatch_macro_checked.sh`)

But those surfaces still left one operational gap: after an emit or refusal, callers had to infer the latest dispatch outcome from stderr or logs. The receipt lane makes the newest decision explicit and durable.

## Receipt shape

Each receipt stores:

- macro name
- bus event
- result (`emitted` or `blocked`)
- route (`dispatch` or `checked_dispatch`)
- whether the checked gate was used
- whether `--force` was used
- raw and parsed payload JSON
- summarized gate data (availability, blockers, blocker classes, reason, preferred execution mode, `repair_action`, the expected X11/i3 desktop target hint when known, and the likely failed live X11/i3 probe when known)
- stderr text when present
- checked-gate `blocked_message` text when the resident dispatcher refused to emit
- timestamp and receipt id

The generated stack also exposes:

- `bin/latest_dispatch_json.sh`

That helper returns one machine-readable snapshot for the latest known dispatch receipt, including the receipt path relative to the project root.

## Intended use

Use this lane when the resident service, shell tooling, or a private LLM needs to answer:

- what macro did we just try to emit?
- was it blocked or emitted?
- did it go through the checked gate?
- was the emit force-overridden?
- what blocker or reason was attached to the decision?
- what X11/i3 target state was the macro expecting when the checked gate said `desktop_state_mismatch`?
- which live X11/i3 probe from the newest matching run most likely failed before the warm lane refused to emit?

This keeps dispatch observability inside the project/runtime control plane instead of pushing it into ad hoc journal scraping.

## Revision 0366 note

Blocked checked-dispatch receipts now preserve the same refusal text the wrapper returned to the caller instead of collapsing that path to a generic placeholder. That makes `latest_dispatch_json.sh` and receipt history good enough for LLM/operator follow-up without reopening wrapper logs.


Revision 0367 adds `gate.live_probe_hint` to the latest-dispatch surface whenever the newest matching run already points at a likely window/event/focus/i3 probe. Revision 0368 extends that same object with `gate.live_probe_hint.observation`, a bounded snapshot of the actual failed wait/error observation when one is cheaply available from the newest matching run. That keeps the resident receipt lane actionable without reopening macro-scoped run history first.


Revision 0369 adds `gate.repair_action` to both durable receipts and `latest_dispatch_json.sh`, so blocked warm-runtime receipts answer not only *what went wrong* but also *which concrete command should repair or advance the lane next*.
