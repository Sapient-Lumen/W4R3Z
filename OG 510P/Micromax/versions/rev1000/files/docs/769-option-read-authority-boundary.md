# Rev810 — option read authority boundary

Rev810 finishes the open-buffer authority landing with a second adjacent leak: script-origin code was blocked from mutating capability and host-adjacent options, but it could still read the same values through option inspection surfaces.

## Why this was risky

Several option values are host authority or local-environment evidence, not just editor preferences:

- `cap.fs-root` and `cap.persist-root` reveal sandbox/persistence roots.
- `cap.*` values expose which host capabilities are currently enabled.
- `clipboard.external.*` values can expose local command paths and arguments.
- `recent.file`, `history.file`, and `savecursor.file` expose persistence paths.
- save-policy knobs such as `save.checkexternal`, `save.atomic`, `save.fsync`, and `mkparents` affect later data-loss boundaries.

Rev772/rev776 already prevented lower-authority scripts from changing those knobs. The missing read-side rule meant a script could still call `ed.opt-get`, `show cap.fs-root`, option rows, or statusline `$(opt:cap.fs-root)` and learn protected values that the capability model otherwise tried to keep out of script-visible state.

## What changed

New read policy lives next to the existing option mutation policy:

- `src/micromax_editor/option_policy.py` adds `ScriptOptionReadPolicy` and `script_option_read_policy(...)`.
- `cap.*` values and the existing host-adjacent protected option set are hidden from script context unless trusted code enables `cap.option-read`.
- `ed.opt-get` now preflights the read before consuming the option-name operand; denied reads leave the name on the VM stack for debugging/recovery.
- `option_inventory_rows()` and `option_detail_row()` keep option names, kinds, docs, and local-override flags discoverable, but redact protected current/default values as `<protected>`.
- Command surfaces such as `show cap.fs-root` inherit the same redaction through shared option-detail rows.
- Status formatting no longer leaks protected option values through `$(opt:NAME)`, and protected values are falsey for `$(if:opt:NAME|yes|no)` in script context.

## Capability

New unsafe capability:

- `cap.option-read` / `ed.option-read` — allow scripts to inspect protected capability, persistence, external-command, and save-policy option values.

Scripts should prefer `host.feature?` and `host.capabilities` for capability discovery. Those surfaces intentionally expose feature availability without disclosing configured roots, local command strings, or save-policy internals.

## Open-buffer seam fix folded into this revision

The open-buffer register authority work in `docs/768-open-buffer-register-authority.md` also lands in rev810. During validation, that partially landed seam exposed a broken policy signature around active-buffer visibility. The final rev810 policy is explicit:

- the active buffer remains ambient script automation state;
- same-origin script-created buffers are visible/switchable to the creating script;
- trusted/user or other-origin inactive buffers require `cap.buffer-read` for metadata/picker rows;
- switching to protected inactive buffers requires the separate `cap.buffer-switch` replay/navigation capability.

## Validation

Focused rev810 validation includes:

- `tests/test_editor_option_authority.py`
- `tests/test_editor_buffer_authority.py`
- `tests/test_editor_prompt_authority.py`
- `tests/test_editor_capabilities_registry.py`
- option word/show tests
- statusformat/statusline tests
- hostcall state-boundary tests
- `tests/test_mxdoctor.py`

The focused run during the revision passed `138` tests before final packaging validation.

## Remaining risk

The active buffer remains intentionally script-visible for editor-automation compatibility. That is not an OS sandbox boundary. The next protected-register audit should move to broad dictionary/session discovery surfaces such as actions, commands, keymaps, and keymodes, where the right answer may be “public editor dictionary” but should be documented and tested rather than assumed.

Full-suite confidence still requires a complete chunked `mxtest` aggregate manifest.
