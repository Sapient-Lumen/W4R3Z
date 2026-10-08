# Rev0779 — Macro registry and recording authority boundary

## Audit finding

The rev0778 runtime-registration guard protected command callbacks, keybindings,
timers, and hook handlers from lower-authority script takeover.  The saved macro
registry was still a delayed-execution registry without the same ownership rule.

That left two concrete risks:

- a script could replace a trusted/user macro slot with script-origin steps and
  wait for a later user replay to run the poisoned automation;
- a script could start macro recording, return to the caller, and let later
  user/editor actions be captured as if they were trusted user-created macro
  steps.

The second case was worse than a normal macro overwrite because recording is a
long-lived mode.  Provenance has to belong to the recording session and to the
individual step producer, not just to the moment a step is replayed.

## Change

Rev0779 adds:

`src/micromax_editor/macro_policy.py`

The module treats saved macros as a runtime registry.  It infers the durable
owner of a macro slot from its stored steps and reuses the same authority shape
as the command/key/timer/hook guard:

- trusted slots are protected from script-context mutation;
- plain script-owned slots can be updated only by the same script-origin token;
- plugin-owned slots must carry a consistent plugin root and generation;
- mixed or incomplete provenance fails closed for lower-authority writers.

`Editor.set_macro(...)`, `macro record`, `macro stop`, and `macro cancel` now
route through that policy.  A script can create a new macro slot or update its
own slot, but it cannot overwrite a trusted macro or delete another script
origin's macro.

Macro recording also now captures its owner at `start_macro(...)`.  Recorded
steps use the lower-authority side whenever either the recording owner or the
step producer is script-originated:

- script-started recordings stamp later user actions as script-origin steps;
- user-started recordings stamp timer/hook/script callback actions as
  script-origin steps;
- script code cannot stop or cancel a trusted user recording;
- trusted user/editor code can still cancel a script-started recording as a
  recovery action.

## Concrete fixes

- `ed.macro-set` / `Editor.set_macro(...)` cannot overwrite trusted saved
  macros from script context.
- Independent script contexts cannot mutate each other's saved macro slots.
- Script-originated `macro record NAME` refuses to shadow an existing trusted
  `last` macro or trusted target macro.
- A macro recording started by a script does not turn later user actions into
  trusted replay steps.
- A macro recording started by a trusted user does not turn later script/timer
  callback activity into trusted replay steps.
- Script-originated code cannot stop/cancel a trusted active recording.

## Validation

Focused regressions added to `tests/test_editor_deferred_authority.py` cover:

- blocked script overwrite of a trusted saved macro;
- same-script update and different-script denial for script-owned macro slots;
- blocked script recording when the default `last` slot is already trusted;
- script-started recording stamping later user actions as script-originated;
- user-started recording stamping script callback actions as script-originated;
- script denial for stopping/canceling trusted recordings.

Representative validation:

- `tests/test_editor_deferred_authority.py`
- `tests/test_editor_macros_named.py`
- `tests/test_editor_script_context_fs_caps.py::test_script_origin_macro_set_does_not_later_gain_user_authority`
- `tests/test_runtime_registration_policy.py`

## Remaining risk

This is still in-process application policy, not a sandbox.  Trusted user init,
trusted plugins, and direct interactive command use can still create or replace
macros.  The key guarantee is narrower: macro slots and live recordings no
longer form a lower-authority delayed-execution registry that sits outside the
script/plugin provenance policy.
