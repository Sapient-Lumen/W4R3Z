# Rev818 — Action register read/run authority

## Why this was risky

The protected-register audit had sealed commands, keybindings, hooks, timers,
plugins, visible VM words, macros, marks, buffers, prompt state, and other
long-lived editor registers. The adjacent action registry was still looser.

Built-in editor actions are intentionally public UI vocabulary, but dynamically
registered actions can disclose local extension/test/plugin names, docs, and
Python source spans through `ed.action-detail-row`, `showaction`, help/topic
rows, palette rows, and action-spec completion. They can also execute arbitrary
Python callbacks. A lower-authority script should not be able to inspect or run
those dynamic trusted callbacks just because it can reach the action register.

## What changed

New policy seam:

`src/micromax_editor/action_policy.py`

New capabilities:

`cap.action-read` / `ed.action-read`
`cap.action-run` / `ed.action-run`

`Editor` now records the installed built-in action callable set after default
action installation. Those default actions remain public so keybinding docs,
completion, the command palette, and ordinary help do not collapse in script
context.

Dynamic actions are protected in script context by default:

- `Editor.action_names()` returns only public core actions unless
  `cap.action-read` is enabled;
- `Editor.action_detail_row(..., strict_denial=True)` raises before consuming
  denied exact operands;
- command-palette action rows, `showaction` completion, action-spec completion,
  and topic/help action rows route through the filtered action helpers;
- direct `run_action(...)` refuses dynamic trusted/user actions in script context
  unless `cap.action-run` is explicitly enabled.

## Semantics

- Trusted/interactive callers keep normal action visibility and execution.
- Built-in core actions remain public to scripts.
- Dynamic trusted/user actions are hidden from script-origin inventory/detail and
  completion surfaces unless `cap.action-read` is enabled.
- Dynamic trusted/user actions cannot be invoked directly from script context
  unless `cap.action-run` is enabled.
- `cap.action-run` is intentionally unsafe. It lets a script trigger a dynamic
  Python callback, but the call still occurs while the caller is in script
  context, so editor-side capability/option guards remain active.
- Denied exact `ed.action-detail-row` calls preserve the action-name operand on
  the VM stack.

## Tests

New focused coverage:

`tests/test_editor_action_authority.py`

It covers protected dynamic action discovery, exact hostcall operand
preservation, capability registry advertisement, direct run denial, and explicit
`cap.action-run` execution.

## Remaining risk

The action registry still does not carry a full provenance sidecar for dynamic
registrations. The current conservative rule treats dynamic actions as protected
trusted/user state unless future Python/plugin registration APIs attach richer
script/plugin ownership. That is safer than leaking local action metadata or
letting lower-authority scripts run arbitrary callbacks by default.
