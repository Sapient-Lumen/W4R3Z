# Rev0779 — Prompt origin and delayed-submit authority boundary

## Audit finding

Prompt objects are delayed command/action/file-open authority.  Rev0778 guarded
runtime registries, and the first rev0779 macro work guarded saved macro slots,
but a lower-authority script could still prepare or mutate a prompt and leave it
for a later direct submit path.  Without explicit prompt provenance, that later
submit could look like a trusted UI action even though the command text or picker
selection was produced by script-originated code.

The same audit exposed an implementation bug in the transient scratch boundary:
`Editor.script_context()` had the intended input-snapshot hook, but the helper
module was not imported in the live editor path.  The boundary therefore failed
at runtime instead of restoring action-input scratch state.

## Change

Prompt state now carries script/plugin provenance fields matching the deferred
callback model: script-context status, plugin package root, plugin generation,
and script-origin id.  Prompt creation, prompt text mutation, completion, and
picker navigation performed inside script context stamp that origin onto the
prompt.  `Editor.submit_prompt(...)` then routes captured lower-authority prompts
through `run_script_origin_callback(...)`, even if a later direct UI-style path
submits the prompt.

`Editor.script_context()` also now imports and executes the transient input
snapshot/restore helper so script-originated prompt work cannot leave stale
scratch input behind for a later trusted action.

## Concrete fixes

- Script-created prompts submit later under their captured script/plugin origin.
- Script-mutated prompt text remains tainted for delayed submit.
- Script-triggered prompt completion and picker navigation taint the prompt before
  it can be submitted later.
- A later trusted-looking UI submit no longer launders a script-produced prompt.
- The transient input scratch rollback path is wired in the live editor module.

## Validation

Focused rev0779 regressions covered prompt delayed-submit taint, prompt
completion/navigation taint, macro recording provenance, transient input rollback,
and the bounded default doctor lane.

## Remaining risk

Prompt provenance is intentionally conservative.  Once lower-authority code
prepares or mutates a prompt, later user edits do not automatically clear that
origin.  That can make some flows stricter than necessary, but it avoids turning
prompt editing into a subtle authority-laundering judgment call.
