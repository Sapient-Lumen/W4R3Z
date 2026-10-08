# Rev0778 — Runtime registration, script `cd`, and dirty-buffer discard boundary

## Audit finding

The recent script/deferred-authority work made callbacks retain their script or
plugin origin when they run later.  The adjacent registries were still too
trusting: lower-authority script code could register or remove command-bar
commands, keybindings, hook handlers, or timers, and those mutated registries
would then be encountered by later user/editor execution.  That is a delayed
privilege problem even when the callback itself remains script-originated.

Two smaller host-boundary issues were found in the same pass:

- scripted `cd` still used ambient process-directory authority instead of the
  same `cap.fs-root` discipline as script file reads/writes;
- force-discard paths such as `close!`, `closeall!`, `only!`, `quit!`, and
  `revert!` could discard dirty in-memory buffers from script context without a
  dedicated buffer-data capability.  The bang aliases were also brittle because
  several aliases pointed at the same functions without injecting the force flag.

## Change

Rev0778 adds:

`src/micromax_editor/runtime_policy.py`

This module defines `RuntimeRegistrationAuthority` and
`script_runtime_mutation_policy(...)`.  The policy lets trusted/interactive code
keep normal editor authority, but script-originated mutation of an existing
registration must now match the existing registration's durable origin:

- same plain `script_origin_id` for ordinary script-created registrations;
- same plugin root and generation for plugin-created registrations;
- a narrow plugin-manager reload-stage allowance for replacing the immediately
  previous same-plugin generation during transactional reload.

The policy is applied through editor-owned checked mutators:

- `Editor.register_command_checked(...)` / `remove_command_checked(...)`;
- `Editor.bind_key_checked(...)` / `set_key_binding_desc_checked(...)` /
  `unbind_key_checked(...)`;
- `Editor.cancel_timer_checked(...)`;
- `Editor.guard_hook_handler_mutation(...)`.

`Command`, `Binding`, `TimerTask`, and `HookHandler` now preserve script origin
metadata, and bridge/command/core call sites route through the checked helpers.
This blocks script code from overwriting trusted registrations, from deleting a
user binding, from cancelling unrelated timers, and from clearing hook handlers
it does not own.

Rev0778 also adds:

`src/micromax_editor/buffer_scriptops.py`

Script-originated dirty-buffer discard now requires:

`cap.buffer-discard`

The guard covers forced close/quit/only/closeall and forced revert paths.  It is
separate from filesystem capabilities because losing unsaved editor memory is a
user-data event even when no disk write happens.

Finally, script-originated `cd` now requires:

`cap.fs-chdir`

and routes through `file_access.chdir_contained(...)`, which opens/binds the
intended directory on capable POSIX hosts, checks the opened target against
`cap.fs-root`, and then changes cwd through the fd.  That keeps process-global
`cd` from becoming a path escape around the file capability root.

## Concrete fixes

- `ed.cmd-add` can no longer overwrite a trusted command such as `save` from
  script context.
- `ed.cmd-rm` cannot remove trusted commands from script context.
- `bind`, `unbind`, `ed.bind-doc`, and related hostcalls cannot mutate trusted
  keybindings from script context.
- `ed.cancel-timer` cannot cancel trusted timers from script context.
- `hook-clear`, `hook-rm`, and group removal paths cannot delete trusted or
  unrelated hook handlers from script context.
- Independent script contexts do not share registration ownership; nested script
  contexts inherit the same origin token.
- Plugin `deinit` can still remove its own command/key/hook/timer registrations.
- Transactional plugin reload can still stage same-plugin replacements while
  stale callbacks from old generations stay blocked.
- `close!`, `closeall!`, `only!`, `quit!`, and `revert!` are real force forms
  again and require `cap.buffer-discard` when called from script context.
- Scripted `cd` requires `cap.fs-chdir` and respects `cap.fs-root` for relative
  and absolute paths.

## Validation

Focused validation added/updated:

- `tests/test_runtime_registration_policy.py`
- `tests/test_editor_script_context_fs_caps.py`
- `tests/test_editor_capabilities_registry.py`

Representative regressions prove:

- script contexts cannot overwrite/remove trusted commands;
- scripts cannot mutate trusted keybindings or keybinding docs;
- scripts cannot cancel trusted timers or clear trusted hooks;
- script-owned registrations can update themselves but not another script
  origin's registrations;
- plugin `deinit` can clean up its own runtime registrations;
- dirty force close/quit/only/closeall/revert require `cap.buffer-discard`;
- scripted `cd` requires `cap.fs-chdir` and remains inside `cap.fs-root`;
- the capability registry advertises `ed.chdir` and `ed.buffer-discard`.

## Remaining risk

This is application-level provenance inside one Python process, not an OS
sandbox.  A malicious native extension, arbitrary Python plugin code, or host
process compromise remains outside this policy.  The policy also guards the
registries known today; any future runtime registry must either use the same
checked helper pattern or add an equivalent policy seam.
