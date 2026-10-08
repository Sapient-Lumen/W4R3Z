# Rev811 — keybinding read authority boundary

Rev811 closes the next protected-register gap after rev810's buffer/option work: keybinding mutation already carried runtime provenance, but keybinding *read* surfaces still exposed full action specs, groups, source spans, and derived descriptions to lower-authority scripts.

## Why this was risky

Keybindings are executable session/configuration state. A binding action can contain command-bar text, filesystem paths, shell-ish helper invocations, plugin command names, or other local workflow details. Even when a script could not overwrite a trusted binding, it could still inspect rows such as:

- `ed.bindings`
- `ed.binding-detail`
- `ed.binding-detail-row`
- `ed.binding-modes`
- `ed.binding-rows-for`
- `ed.binding-info-for`
- `ed.available-bindings`
- `ed.available-binding-info`
- `ed.available-binding-inventory-rows`
- `ed.resolve-key`
- `ed.resolve-key-info`
- `showkey`, `showbindings`, `whichkey`
- binding prompt/section rows and `showkey` completions

That made trusted/user keybinding action text a free script-readable side channel.

## What changed

New policy seam:

`src/micromax_editor/binding_policy.py`

New unsafe capability:

`cap.keybinding-read` / `ed.keybinding-read`

Behavior now follows the protected-register pattern used for macros, marks, buffers, prompts, recent rows, messages, and search:

- trusted/interactive code keeps ordinary keybinding visibility;
- lower-authority scripts can inspect same-origin bindings they created;
- trusted/user bindings and other-origin script/plugin bindings are hidden by default;
- `cap.keybinding-read` explicitly grants broad read access to protected keybinding specs;
- exact hostcalls such as `ed.binding-detail-row`, `ed.resolve-key`, and `ed.resolve-key-info` preflight before consuming the key operand, so denied calls preserve stack evidence;
- binding prompt rows, section rows, and command-line `showkey`/`showbindings` share the same filtered editor helpers instead of reading the raw keymap directly;
- statusformat key lookup now uses filtered resolved bindings, so script-context status rendering cannot discover protected shortcuts.

## Compatibility decision

Command/action names remain public editor dictionaries for this revision. The sensitive part fixed here is the user's executable keybinding layer: action specs and binding source spans are no longer ambient script-visible state. A future audit can decide whether command/action docs and source spans need a separate read capability or should stay intentionally public.

One existing hostcall integration test now opts into `cap.keybinding-read` when it intentionally exercises a script-created binding picker over protected bindings. Without the capability, script-created binding prompts see only same-origin rows.

## Validation

Focused validation during the revision included:

- `tests/test_editor_keybinding_authority.py`
- `tests/test_editor_deferred_authority.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
- `tests/test_editor_mx_commands_and_completion.py`
- capability registry and option-authority tests

The focused prompt/command/keybinding regression set passed `343` tests after the compatibility update.

## Remaining risk

This is still editor-runtime provenance, not an OS sandbox. A script with `cap.keybinding-read` can intentionally inspect protected keybinding specs. Physical key dispatch remains allowed to execute the resolved binding; this revision protects script-readable inventory/detail surfaces, not normal user keypress behavior.

The next adjacent audit should decide whether command/action discovery rows are public documentation or need their own protected read boundary.
