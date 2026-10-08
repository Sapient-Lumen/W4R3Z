# Rev0780 prompt-origin delayed-submit audit

The macro registry and transient-input work closed two delayed-execution state channels, but the same
shape existed in the prompt surface: a script or plugin could prepare an
interactive prompt and return to the UI loop.  If a later user keypress submitted
that prompt with ambient editor authority, the prompt became a small authority
laundering object.

This document records the follow-up audit/fix packaged with rev0780 alongside the direct-save fd freshness and structured-hostcall preflight work.

## Failure mode

Prompts are deferred execution objects.  Command prompts, palette prompts, topic
prompts, and binding prompts can be created now and submitted later.  Before this
fix, the hostcall submit path itself used `script_context()`, but the prompt
object did not remember who created or last mutated it.

That left these risky shapes:

- script calls `ed.command-edit` with `set cap.fs-open true`, returns, and a later
  ordinary Enter key submits the prepared prompt;
- script modifies an existing prompt with `ed.prompt-set`, returns, and a later
  submit runs the script-provided command text;
- script calls `ed.prompt-complete` or picker navigation to change prompt text or
  selection, returns, and a later submit acts on the script-selected target;
- a plugin-created prompt loses package-local script/plugin provenance before the
  delayed submit.

## Changes

`Prompt` now carries deferred authority metadata:

- `script_context`
- `plugin_load_root`
- `plugin_generation`
- `script_origin_id`

`Editor.enter_prompt(...)` stamps a prompt when it is created under script/plugin
authority.  Prompt mutations also stamp the active prompt when they happen inside
script context:

- `set_prompt_text(...)`
- `set_prompt_text_cursor(...)`
- `prompt_complete(...)`
- `clear_prompt_suggestions(...)`
- picker movement and section-jump helpers

Prompt-creating/mutating hostcalls that are script-facing now enter
`script_context()` before changing prompt state:

- `ed.command-edit`
- `ed.topic-prompt`
- `ed.binding-prompt`
- `ed.command-palette`
- `ed.prompt-complete`
- `ed.prompt-clear-suggestions`

`Editor.submit_prompt()` now checks the prompt's captured origin.  If the prompt
is script-originated, the actual submit runs through
`Editor.run_script_origin_callback(...)`, preserving script-origin id and plugin
root/generation.  A direct later Enter key therefore sees the same capability and
option-mutation policy as the original script.

## Concrete guarantees

- A script-created command prompt cannot later enable `cap.*` through a direct
  user-style `submit_prompt()` call.
- A script-mutated existing command prompt is tainted before later submit.
- Script-triggered prompt completion is also tainting, so completing
  `set cap.fs-open tr` to `set cap.fs-open true` cannot regain user authority.
- A script-created palette prompt cannot later open a path without `cap.fs-open`
  just because the final submit came from an ordinary UI path.

## Validation

Focused regressions were added to `tests/test_editor_script_context_fs_caps.py`
for delayed command-prompt submit, prompt-set tainting, prompt-completion tainting,
and delayed palette path-open denial.

Representative validation for this lane:

- `tests/test_editor_script_context_fs_caps.py`
- `tests/test_editor_transient_state.py`
- `tests/test_editor_hostcall_boundary.py`
- `tests/test_editor_readonly_option.py`
- selected command-palette/topic/binding prompt hostcall regressions

## Remaining risk

This is still in-process application-level authority.  Trusted interactive use
can intentionally submit, edit, or cancel prompts with user authority.  The
important boundary is narrower: a prompt prepared by lower-authority code no
longer turns into a trusted command/action/file-open merely because it is
submitted later.
