# Rev814 — plugin register read authority

## Why this mattered

The protected-register audit had already sealed buffers, prompts, options,
commands, keybindings, marks, macros, recent rows, messages, undo/redo, and
several delayed interactions.  Plugin inventory was still a nearby read-side
hole.

Plugin rows are not just harmless labels.  They expose runtime code-load state:
loaded/candidate/error names, dependency lists, versions, descriptions, and load
errors.  The richer `plugin info` path can also expose local plugin roots and
entry files.  A lower-authority script that cannot read arbitrary files or
protected option values should not get those details through plugin inventory as
a side channel.

## What changed

New module:

- `src/micromax_editor/plugin_policy.py`

New capability:

- `cap.plugin-read` / `ed.plugin-read`

New/changed editor helpers:

- `Editor._all_plugin_names()` keeps the unfiltered manager view for trusted
  internal operations.
- `Editor.plugin_names()` now returns names visible to the current runtime
  authority.
- `Editor.plugin_detail_row(..., strict_denial=True)` can raise on protected
  exact hits so hostcalls preserve the queried plugin name on the VM stack.
- `Editor._plugin_read_allowed(...)` and `Editor._guard_plugin_read(...)` are
  the shared guard for exact plugin metadata reads.

Script-origin plugin read behavior now follows the protected-register pattern:

- trusted/interactive callers keep normal plugin visibility;
- a currently executing loaded plugin may inspect its own loaded plugin row;
- plain scripts, other plugin generations, candidate-only plugins, and broken
  plugin rows are hidden by default;
- `cap.plugin-read` is the explicit unsafe override;
- denied exact `ed.plugin-detail-row` hostcalls preflight before consuming the
  plugin-name operand.

Filtered surfaces now include:

- `ed.plugin-inventory-rows`;
- `ed.plugin-detail-row`;
- `ed.plugin-section-rows` and summaries;
- `plugin.list` and `plugin.errors` hostcalls;
- `plugin list`, `plugin info`, and `plugin errors` command paths;
- `showplugin`, `showplugins`, plugin picker rows, and plugin-name completion.

I also fixed a latent hook-read-policy integration issue found during the same
audit: the editor was calling the generic `hook_access_policy(...)` name, while
`hook_policy.py` only exported handler-specific helpers.  `hook_access_policy`
is now an explicit alias/helper, and the existing hook-authority tests are part
of the validation set.

## Validation

Focused regression coverage lives in:

- `tests/test_editor_plugin_authority.py`

It covers hiding trusted/candidate/error plugin rows from plain scripts, allowing
a loaded plugin to see only its own row, `cap.plugin-read` reveal behavior,
exact-hostcall stack evidence preservation, command-path filtering, and capability
advertisement.

Adjacent hook authority coverage lives in:

- `tests/test_editor_hook_authority.py`

## Remaining risk

`cap.plugin-read` is intentionally broad.  It should only be enabled for trusted
automation that is expected to inspect plugin manager state, plugin load errors,
and dependency metadata.  `cap.fs-require` remains the separate code-load/reload
capability; reading plugin inventory does not imply permission to reload code,
and reloading a known plugin does not automatically make broad plugin discovery
public.

The next adjacent read-side decision is the VM word/action dictionary.  Built-in
core words/actions are probably public editor documentation, but dynamically
loaded words and action source spans should get the same explicit public-vs-
protected treatment rather than remaining accidental side channels.
