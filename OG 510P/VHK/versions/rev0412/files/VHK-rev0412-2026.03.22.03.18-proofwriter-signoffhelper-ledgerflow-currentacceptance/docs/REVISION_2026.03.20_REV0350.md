# Revision 0350

This revision keeps VHK narrow and takes only the strongest discipline upgrades from the comparison datacubes.

## 1. Recorder review debt now carries claim boundaries

`vhk macro-review-queue-json` still emits a stable issue taxonomy, but each issue now also declares:

- `scope_class`
- `truth_effect`
- `non_claims`

Per-item queue entries repeat those fields.

This means VHK can say "stale recorder evidence" or "missing recorder sidecar" without accidentally implying that the macro is invalid, that replay must fail, or that warm-runtime dispatch has to stop.

## 2. Next-action recommendations now explain themselves

`bin/next_action_json.sh` now emits:

- `review_queue_source`
- `recommendation_trace`

The trace includes the selected action, the fixed selection policy, helper inputs, facts, considered actions, advisory notes, and explicit non-claims.

This turns next-action from an opaque assertion into a reviewable recommendation surface for an operator or private LLM.

## 3. Fused stack state now carries truth boundaries directly

`bin/stack_state_json.sh` now includes:

- fused `review_queue_source`
- fused `next_action_trace`
- `control_plane.surface_classes`
- `control_plane.non_claims`
- `control_plane.helper_surface_contracts`

So a caller can interpret the fused stack snapshot without reopening `control-plane.json` separately.

## 4. Pretty wrappers now use temp-file handoff

`bin/next_action.sh` and `bin/stack_state.sh` no longer push the full JSON payload through shell argument plumbing. They materialize a temp file and let the embedded Python read from that file.

This makes the human-readable wrappers less fragile while keeping the JSON helpers authoritative.

## Why these changes were worth taking

Across the comparison datacubes, the most reusable ideas were not new runtime breadth but better epistemic discipline:

- explicit claim boundaries
- explicit source-of-truth / published-surface distinctions
- explicit recommendation provenance
- explicit traceability for why an advisory exists

Those ideas strengthen VHK’s flagship i3/X11 warm-runtime + recorder-review control plane without pulling it back toward generic Linux automation sprawl.
