# Rev0782 — Active keymode provenance and delayed key dispatch boundary

## Audit finding

Recent revisions made delayed callbacks carry script/plugin provenance across
keybindings, timers, hooks, macros, command callbacks, and prompts.  Active
keymap modes were still a quieter delayed authority object.

A script could push an existing keymap mode and return.  A later physical
keypress would then resolve a trusted binding in that mode and execute the
binding as ambient user/editor authority, even though the mode activation was
script-originated.  That meant a lower-authority script could indirectly queue a
future trusted command by changing key dispatch state rather than by registering a
new callback.

There was a second adjacent state bug: a script could pop or clear trusted active
key modes, or push a mode above a trusted capture mode.  That could defeat
trusted modal flows such as confirmation/capture interactions without touching
any command/keybinding registry.

## Change

`ActiveKeyMode` now carries the same live provenance shape used by deferred
callback surfaces:

- `script_context`
- `plugin_load_root`
- `plugin_generation`
- `script_origin_id`

`Editor.set_key_mode(...)`, `Editor.push_key_mode(...)`, and prompt/capture mode
activation now stamp active mode entries at the point the mode is activated.
Key dispatch treats the active mode entry as an authority source.  If a later
keypress resolves through a script-originated active mode, the binding runs under
that captured script/plugin origin even when the binding itself was registered by
trusted code.

Public keymode mutation also has a small guard:

- a script cannot pop a trusted active keymode;
- a script cannot clear/replace trusted or other-origin active keymode entries;
- a script cannot shadow a trusted capture mode by pushing another mode above it;
- nested script contexts keep the same script origin and can still manage their
  own active modes.

The visible keymode rows stay stable.  Existing UI/picker/status surfaces still
show the same `[mode, once]` shape; the new provenance is intentionally runtime
policy data, not extra UI noise.

## Cloudtainer preflight correction

While validating this lane, repeated default-doctor child processes exposed a
cloudtainer waste pattern: stale extracted workdirs plus many short pytest
children caused file scans and subprocess churn to dominate the handoff command.
The stale workdirs were removed from `/mnt/data`, and `mxdoctor` now keeps the
bounded risk lane in one isolated no-cache pytest child unless the target set
grows beyond its generous grouping limit.  The full evidence path remains the
explicit chunked `mxtest` aggregate lane.

## Concrete guarantees

- A script-activated one-shot keymode cannot launder a trusted binding into
  ambient user authority on the next keypress.
- A script-activated persistent keymode also keeps script authority across later
  key dispatch.
- Trusted active keymode/capture state cannot be popped, cleared, or shadowed by
  lower-authority script code.
- Trusted interactive/user keymode behavior remains unchanged.

## Validation

Focused regressions added in `tests/test_editor_transient_keymodes.py`:

- script-activated one-shot keymode runs trusted bindings with script authority;
- script-activated persistent keymode runs trusted bindings with script authority;
- scripts cannot pop or clear trusted active keymodes;
- scripts cannot shadow trusted capture modes.

Representative validation for this lane:

- `tests/test_editor_transient_keymodes.py`
- `tests/test_editor_keymap_modes.py`
- `tests/test_runtime_registration_policy.py`
- `tests/test_mxdoctor.py`
- `python tools/mxdoctor.py`

## Remaining risk

This is still an in-process application policy, not an OS sandbox.  Trusted
interactive keymode changes and trusted plugin code remain powerful by design.
The important correction is narrower: active keymode state no longer sits outside
the delayed-authority model that already protects callbacks, prompts, macros,
and runtime registries.
