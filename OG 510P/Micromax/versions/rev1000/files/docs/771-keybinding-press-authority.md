# Rev812 — keybinding synthetic replay authority

Rev812 finishes the riskiest half of the rev811 keybinding audit. Rev811 sealed keybinding *read* surfaces, but script-origin code could still call `ed.press-key` and ask the editor to resolve a trusted/user keybinding. The old dispatch path then ran that trusted binding with trusted authority.

## Why this was risky

Keybindings are executable delayed state. A trusted binding can contain an action chain such as:

```text
command:set cap.fs-save true
mx:... package-local helper code ...
command:save
```

A lower-authority script is not allowed to mutate `cap.*` options directly, overwrite trusted keybindings, or replay protected macros. But `ed.press-key` was still a synthetic replay surface. That meant a script could potentially invoke a trusted binding and borrow the authority of the user/editor code that created it.

The adjacent case was also unsafe: one script could synthesize a keypress for another script/plugin generation's binding and have it run with that other origin's authority.

## What changed

The keybinding authority seam now covers replay as well as read:

- `src/micromax_editor/binding_policy.py` adds `binding_press_policy(...)`.
- `Editor._run_key_binding(...)` now checks synthetic/script-origin replay before executing the resolved binding.
- `ed.press-key` can still trigger same-origin script-created bindings.
- Trusted/user or other-origin bindings are refused by default and report `cap.keybinding-press` in the denial.
- New capability: `cap.keybinding-press` / `ed.keybinding-press`.
- When `cap.keybinding-press` is enabled, the protected binding's action spec is replayed under the caller's current script authority, not under the target binding's trusted or other-origin authority.

That final point is important. The capability allows trusted automation to intentionally reuse a protected binding's action text, but it does **not** make a script trusted. For example, replaying a trusted binding whose action is `command:set cap.fs-save true` still fails under script option policy.

## Read-side consolidation kept

The rev0810 archive already carried unlinked rev811 keybinding-read material. Rev812 keeps and validates that work while adding the missing replay boundary:

- filtered binding rows and binding prompts;
- `cap.keybinding-read` / `ed.keybinding-read`;
- operand-preserving exact read hostcalls;
- default doctor coverage for the new focused keybinding authority file.

## Validation

Focused validation during this revision included:

- `tests/test_editor_keybinding_authority.py`
- `tests/test_editor_keybinding_provenance.py`
- `tests/test_editor_keymap_discovery.py`
- `tests/test_editor_keybinding_docs.py`
- `tests/test_editor_transient_keymodes.py`
- `tests/test_editor_query_replace.py` script-keymode provenance regressions
- `tests/test_editor_script_context_fs_caps.py` keybinding authority regressions
- `tests/test_editor_hostcall_boundary.py`
- `tests/test_runtime_registration_policy.py`
- `tests/test_editor_deferred_authority.py`
- `tests/test_editor_capabilities_registry.py`
- `tests/test_mxdoctor.py`

## Remaining risk

Command/action dictionaries remain public discovery surfaces in rev812. That may be the right product decision because commands/actions are closer to public editor documentation than user-owned register state, but it still needs an explicit audit note and tests so future maintainers do not confuse public dictionaries with protected executable registers.

Full-suite confidence still requires a complete chunked `mxtest` aggregate manifest.
