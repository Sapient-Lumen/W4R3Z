# Rev0863 — plugin unload clears delayed interaction state

Rev0862 protected the cleanup group used for commands, keybindings, timers,
hooks, actions, and marks.  The next audit found a different class of survivor:
plugin code could create delayed interaction state that was not itself a grouped
runtime registration.  An active keymode, command prompt, query-replace session,
or pending URL confirmation can outlive the source evaluation that created it
and later run callbacks or consume user input after `plugin unload NAME` appears
to have removed the plugin.

Rev0863 stamps plugin-originated active keymodes and prompts with the current
loader-owned `plugin:NAME` group.  Plugin cleanup now removes or retags the
delayed interaction state beside the existing registration cleanup: active
keymodes, prompts, query-replace sessions, query-replace capture modes,
selection state created for query-replace, and pending URL confirmations.
Staged reload retags these surfaces from the temporary staging group back to the
active plugin group so a later unload still has a single cleanup key.

## Contract

- Plugin-created active keymodes carry the loader-owned plugin group.
- Plugin-created prompts carry the loader-owned plugin group and prompt
  callbacks run with that authority.
- `plugin unload NAME` removes delayed interaction state whose group is
  `plugin:NAME`.
- Staged plugin reload retags delayed interaction state from the staged group to
  `plugin:NAME` on success.
- Plain non-plugin scripts keep their existing prompt and keymode authority
  behavior.

## Why this matters

A surviving prompt or modal keymode is a recovery failure even when no command or
keybinding survives.  The operator has explicitly asked to unload the plugin;
the editor should not leave a plugin-owned confirmation, query-replace session,
or modal dispatch frame waiting for later user input.  Cleaning delayed
interaction state through the same group transaction keeps the fix auditable
without adding a broader plugin registry.

## Residual risk

This is still in-process cleanup, not hostile-code containment.  Already
evaluated plugin code may have changed ordinary editor state while it was loaded,
and future audits still need to check less obvious delayed state such as capture
scratch, buffer-local data, history stores, and UI adapter queues.
