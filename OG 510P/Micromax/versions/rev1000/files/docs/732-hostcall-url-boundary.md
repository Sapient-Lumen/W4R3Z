# Rev0778 — Hostcall denial stack, URL scheme, and staged reload boundaries

## Audit finding

The previous readonly-hostcall work fixed direct text mutation failures so they
reject protected buffers before consuming operation arguments.  Adjacent
host-boundary calls were less disciplined: denied calls such as `ed.fs-read`,
`ed.open`, `ed.require`, `ed.shell`, and `ed.open-url` popped their path/command
argument before checking whether the capability was enabled.  That made failed
script requests harder to inspect and made the hostcall boundary inconsistent
with the newer edit-boundary rule.

A second nearby trust issue was URL dispatch.  The docs and UI describe the URL
opener as an external-link path for `http`, `https`, and `mailto`, but the
low-level `open_url(...)` helper accepted whatever URI scheme the host browser or
desktop opener would handle.  With `cap.open-url` enabled, a script or command
could request schemes such as `file:` and hand them to the host opener even
though that is outside the documented safe external-link loop.

Validation also exposed an adjacent runtime-registration policy bug: the core
plugin bootstrap repeats some built-in prompt bindings so minimal embedders and
plugin-loaded embedders share one script, but the script-origin mutation guard
treated even identical repetitions as attempts to overwrite trusted bindings.
That made core plugin loading fail before URL keybindings such as `Alt-o` were
installed.

A later validation pass exposed one more risky boundary in the same trust area.
The plugin generation guard from rev0777 correctly stopped stale callbacks from
borrowing authority from a newer plugin generation, but it was also blocking
transactional plugin reload staging from replacing that same plugin's old command
and key registrations.  The failure happened before the candidate source reached
its real load error, so the reload path could report the policy guard instead of
the bad replacement source and could not fully exercise the rollback boundary.

## Change

Rev0778 adds:

`src/micromax_editor/hostcall_boundary.py`

It provides tiny reusable guards for capability checks and stack preflighting:

- `require_option_enabled(...)`
- `peek_stack_arg(...)`
- `peek_str_arg(...)`
- `pop_str_arg(...)`

`src/micromax_editor/micromax_bridge.py` now uses those helpers for the
host-facing capability calls where an operation argument exists:

- `ed.open-url`
- `ed.shell`
- `ed.fs-read`
- `ed.fs-list`
- `ed.fs-stat`
- `ed.open`
- `ed.require`

It also uses preflight guards for script-denied `ed.opt-set` and
`ed.opt-set-local`, so a blocked attempt to mutate a protected option leaves the
name/value pair on the VM stack.

Rev0778 also adds:

`src/micromax_editor/url_policy.py`

The shared URL policy accepts only `http`, `https`, and `mailto`, rejects
control/whitespace characters, requires hosts for `http(s)`, and requires a
recipient/query for `mailto`.  `Editor.open_url(...)`,
`Editor.begin_open_url_confirm(...)`, docs `helpfollow`, and explicit
`urlopen URL` now all use the same validation witness.

`Editor.bind_key_checked(...)` now treats an identical re-registration of an
existing binding as a no-op before applying destructive mutation policy.  A
lower-authority script/plugin can repeat a trusted built-in binding without
taking ownership of it, but changing the action or description still fails with
the same trusted-registration guard.

The staged plugin reload path now carries an explicit replacement-generation
witness through plugin source and lifecycle execution.  The runtime-registration
policy permits a plugin-manager-created stage group such as
`plugin:alpha#reload1` to replace registrations from the immediately previous
`plugin:alpha` generation.  Ordinary scripts and stale callbacks still cannot
claim that authority: the allowance requires the same plugin root, the expected
previous generation, and the plugin manager's reload-stage group shape.  If the
staged source or lifecycle later fails, the existing reload transaction snapshot
restores commands, keys, hooks, timers, and VM dictionary state.

## Concrete guarantees

- Capability-denied hostcalls for URL, shell, filesystem read/list/stat, open,
  and require leave their operation argument on the stack; only the `hostcall`
  word itself has consumed the hostcall name.
- Type-invalid enabled filesystem read requests are preflighted before the bad
  argument is popped.
- Script-denied `ed.opt-set` / `ed.opt-set-local` attempts leave the option name
  and requested value visible on the stack.
- `urlopen file:///...` is refused before confirmation and before invoking the
  host opener.
- Direct `ed.open-url` hostcalls also reject unsupported schemes before invoking
  the host opener.
- `mailto:` remains supported as the documented non-HTTP external-link scheme.
- Core plugin loading can repeat built-in prompt bindings without taking
  authority over those trusted bindings, so later URL keybindings such as
  `Alt-o` still install.
- Staged plugin reloads may replace only the immediately previous generation's
  same-plugin registrations while the reload transaction is active; failed
  staged loads still roll back to the old runtime.

## Refactor value

This is a small seam, but it is deliberately placed where future hostcalls should
copy policy from.  Capability gates are not just boolean checks; they should also
preserve debugging evidence and avoid launching host integrations before input
shape and authority are known.

The URL policy is separated from command/UI code so command-bar, docs browser,
keybinding, and raw hostcall paths cannot quietly drift on what “external URL”
means.

The plugin reload change is deliberately a policy seam rather than a blanket
exception to generation checks.  Reload staging is a short-lived transaction
owned by the plugin manager, not a new right that deferred callbacks or scripts
can synthesize by choosing a clever group name.

## Validation

New regressions live in:

- `tests/test_editor_hostcall_boundary.py`
- `tests/test_editor_url_under_cursor.py`

Focused validation proved the hostcall stack-preservation cases, protected
option write preservation, unsupported URL rejection, malformed HTTP URL
rejection before confirmation, `mailto:` success, idempotent keybinding no-op
behavior, successful core plugin URL keybinding installation, and staged plugin
reload rollback after a replacement source failure.

`tools/mxdoctor.py` now includes both risk files in the bounded default lane.

## Remaining risk

`cap.shell` still intentionally grants synchronous shell execution when trusted
configuration enables it; this revision only fixes denial stack hygiene.  The URL
scheme policy is conservative and fixed for now.  A future host might want a
trusted-user option for additional schemes, but that should be treated as another
host-adjacent protected option rather than silently passing arbitrary URI
schemes to the desktop opener.

The staged reload allowance is intentionally narrow.  It does not make arbitrary
plugin generations interchangeable, and it should stay covered by rollback tests
whenever command/key/hook/timer registration internals change.
