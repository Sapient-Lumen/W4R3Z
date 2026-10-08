# Rev0776 — Script option policy for host-adjacent knobs

## Problem

Rev0772 closed the obvious self-escalation route where script-originated code could run `set cap.fs-save true` and immediately call back into `save`. Rev0775 then carried that lower-authority script label through deferred plugin callbacks.

The remaining risk was quieter: not every dangerous host knob is named `cap.*`. A script that could not set a capability could still mutate ordinary options that decide *how* an already-enabled host surface behaves later. Examples include external clipboard command overrides, URL confirmation, persistence file paths, and save conflict/atomicity settings. Those writes are dangerous because they can be delayed. A script-created keybinding, macro, hook, timer, or command can plant policy state now, and a later user action can execute it as normal editor behavior.

The sharpest examples were:

- `clipboard.external.cmd` / `clipboard.external.readcmd`: a script could seed a future executable used by interactive copy/paste.
- `clipboard` / `clipboard.osc52`: a script could switch clipboard export channels for later user copies.
- `open-url.confirm`: a script could disable a user confirmation barrier after `cap.open-url` had been granted.
- `recent.file`, `history.file`, `savecursor.file`, and related persistence toggles: a script could redirect editor-owned persistence.
- `save.checkexternal`, `save.atomic`, `mkparents`, and `autosave`: a script with some file authority could relax data-loss protections or arm later ambient writes.

## Changes

New module:

`src/micromax_editor/option_policy.py`

It contains the shared script-origin option mutation policy:

- capability options still fail with the existing `capability option` message category;
- host-adjacent non-capability options fail with `protected option`;
- plain editor options such as `ignorecase` remain script-mutable.

`Editor._guard_option_mutation(...)` now delegates to that module after resolving aliases, so all existing mutation routes share the same policy:

- command-bar `set`, `setlocal`, `toggle`, `togglelocal`;
- hostcalls `ed.opt-set`, `ed.opt-set-local`;
- immediate Micromax option words `set`, `toggle`, and alias forms such as `savehistory`.

The protected non-capability set now covers external/terminal clipboard policy, open-url confirmation, persistence-path/toggle policy, and save/readonly/autosave data-loss policy.

## Concrete guarantees

- Script-context code still cannot mutate any canonical `cap.*` option.
- Script-context code cannot seed external clipboard command overrides for later user copy/paste.
- Script-context code cannot redirect or enable editor-owned persistence files through aliases like `savehistory`.
- Script-context code cannot disable URL confirmation or lower save freshness/atomicity policy.
- Direct interactive commands and trusted init/config VM evaluation retain normal user authority.
- Plain low-risk editor options remain script-mutable, avoiding an accidental blanket ban.

## Validation

Focused validation during the rev0776 turn:

```text
139 passed: script-context filesystem caps, persistence, file-read/list/stat, and file-save regressions
29 passed: external/terminal clipboard, URL confirmation, readonly, and option set/toggle regressions
```

Additional handoff validation is recorded in the packaged revision notes.

## Remaining risk

This is still an application-level trust boundary. It prevents script-originated policy seeding through the known option mutation paths, but any new option that controls host execution, host filesystem persistence, or data-loss behavior must be added to `option_policy.py` when introduced. Future option registration could grow a first-class `script_protected=True` metadata field so the policy is declared next to each option rather than maintained as a central exact-name list.
