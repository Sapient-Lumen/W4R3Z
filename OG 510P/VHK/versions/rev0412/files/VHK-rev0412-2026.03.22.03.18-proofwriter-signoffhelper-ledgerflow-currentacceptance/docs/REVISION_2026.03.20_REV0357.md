# Revision 0357 - latest dispatch receipts

This revision reinforces the i3/X11-first warm-runtime lane by making thin dispatch observable after the fact, not just callable.

## What changed

- added `vhk latest-dispatch-json <project>`
- generated `bin/latest_dispatch_json.sh` in the i3/X11 stack
- generated dispatch wrappers now write durable receipts under `build/dispatch_receipts/`
- checked dispatch now records blocked and force-overridden attempts as well as successful emits
- fused `stack_state_json.sh` / `stack_state.sh` now carry latest-dispatch truth
- updated runtime docs so author queue, runtime board, dispatch catalog, checked dispatch gate, and latest dispatch receipts form one coherent resident-runtime control plane

## Why it matters

Before this revision, VHK could explain whether a macro *should* dispatch, but it still made operators and private LLM callers reopen logs to answer what the last dispatch attempt actually did.

Now the warm-runtime lane has a durable, project-local receipt trail with one stable latest snapshot.

## Validation

Focused validation for this revision covered the new CLI, generated wrappers, and fused stack-state path.
