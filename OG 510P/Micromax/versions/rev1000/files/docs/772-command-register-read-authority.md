# Rev813 — command register read authority

## Why this mattered

The protected-register work had sealed buffers, prompts, history, marks, macros,
keybindings, options, and several delayed interaction surfaces.  Command
registrations were still a quieter read-side leak: lower-authority script code
could enumerate command names, docs, groups, and source spans through hostcalls,
`showcmd`, help/topic discovery, prompt completion, and command-palette rows.

Command registration mutation already carried runtime provenance.  The missing
piece was using that same provenance when a script *reads* command-register
metadata.  Command docs and groups can reveal plugin/user configuration, and
source spans can reveal local file layout.  Command discovery also feeds delayed
execution paths, so it should have an explicit trust decision instead of being a
public side channel by accident.

## What changed

New module:

- `src/micromax_editor/command_policy.py`

New capability:

- `cap.command-read` / `ed.command-read`

New editor-facing helpers:

- `Editor.command_names()`
- `Editor.command_rows()`
- `Editor.command_detail_row(..., strict_denial=True)`

Script-origin command read behavior now follows the same shape as keybinding
read behavior, with one deliberate compatibility exception for immutable built-in
command docs:

- trusted/interactive callers keep normal command visibility;
- built-in core command names/docs remain public so prompt completion, help, and
  command-palette UX do not collapse in script-owned prompts;
- scripts can read commands they registered themselves;
- dynamic trusted/user or other-origin script/plugin commands are hidden by
  default;
- `cap.command-read` is the explicit unsafe override;
- exact denied hostcalls preserve the queried command name on the VM stack.

The direct hostcalls now use the filtered editor helpers instead of raw dispatcher
state:

- `ed.cmds`
- `ed.cmd-rows`
- `ed.command-detail-row`

The shared command-discovery surfaces now also flow through the same filter:

- `showcmd` exact detail;
- command palette rows and section rows;
- help/topic name discovery;
- root command completion and `showcmd` completion;
- compact command inventory summaries.

## Validation

Focused regression coverage lives in:

- `tests/test_editor_command_authority.py`

It covers same-origin command visibility, hiding trusted and other-origin
commands, `cap.command-read`, command-palette filtering, exact-hostcall stack
evidence preservation, and capability registry advertisement.

## Remaining risk

`cap.command-read` is intentionally broad.  It should only be enabled for trusted
automation that is expected to inspect the whole dynamic command registry.  Core
built-in command docs are still public by design.

Command execution remains a separate policy question.  Individual dangerous
commands are still capability-gated by their own host/file/buffer boundaries, but
this revision is a read/discovery seal, not a universal `ed.command` execution
capability.
