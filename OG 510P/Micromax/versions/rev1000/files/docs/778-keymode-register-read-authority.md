# rev0819 — keymode register read authority

## Why this was risky

Keymode execution already carried provenance: a mode pushed by script-origin code made later keypresses run under script authority, and scripts could not pop/replace trusted active modes. The remaining gap was read-side. Raw hostcalls such as `ed.keymodes`, `ed.keymode-rows`, `ed.keymode-inventory-rows`, `ed.keymode-detail-row`, and status fields could still expose trusted/user active modes and dynamic known mode names to lower-authority scripts.

That matters because active modes are delayed interaction state. Seeing `qreplace`, `openurl`, a private prefix map, or a plugin/user mode name can reveal workflow state even when the binding specs themselves are protected.

## What changed

New seam:

`src/micromax_editor/keymode_policy.py`

New capability:

`cap.keymode-read` / `ed.keymode-read`

Default behavior now:

- trusted/interactive callers keep ordinary keymode visibility;
- `global` remains public baseline state;
- scripts can inspect same-origin script/plugin keymodes;
- trusted/user and other-origin active or known keymodes are hidden by default;
- exact denied `ed.keymode-detail-row` calls preserve the mode-name operand;
- `cap.keymode-read` reveals protected mode names/state but does not also reveal key/action specs;
- binding specs still require `cap.keybinding-read`.

Status-model keymode fields now use visible keymodes when running under script authority, so `ed.status` no longer leaks a trusted active mode name to a script.

## Validation

Focused new tests:

`tests/test_editor_keymode_authority.py`

They cover trusted active/known mode hiding, operand preservation on exact denial, same-origin script keymode visibility, and the separation between `cap.keymode-read` and `cap.keybinding-read`.

## Remaining risk

The active-buffer text surface is still deliberately public to current-buffer automation. This revision only seals keymode register metadata; future work should keep auditing remaining session surfaces that expose trusted/user state without an explicit public-vs-protected decision.
