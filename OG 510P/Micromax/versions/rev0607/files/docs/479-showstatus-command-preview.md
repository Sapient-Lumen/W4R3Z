# `showstatus` command-bar preview (rev537)

## Why

Micromax already knew the portable status summary through `showstatus`, `ed.status-summary`, and the structured `status_model()` snapshot. But plain `showstatus` in the command bar still looked like a generic exact-command row right before Enter.

That was a small trust/headless-first seam: the command existed precisely to expose one deterministic human-readable status summary, yet the command bar hid that same summary until after execution.

## What changed

- new `Editor._prompt_showstatus_command_row(...)` reuses `status_summary(include_prompt=False)`
- `status_summary()` now accepts `include_prompt=False` so preview callers can suppress transient command-bar state
- exact command completion for plain `showstatus` now keeps the ordinary command doc while replacing the generic info hint with the same portable summary the command is about to emit

## Examples

- `showstatus` with a dirty buffer can preview as:
  - `mode=normal buffer='a' dirty=1 readonly=0 pos=1:1 cursors=1/1 sels=0 selchars=0`
- while the command bar is open, the preview intentionally omits transient `prompt=` / `interaction=` / `capture=` fields so the row stays close to the post-submit `showstatus` message instead of echoing the command bar itself

## Tests

- `tests/test_editor_prompt_completion_hostcalls.py::test_prompt_complete_showstatus_command_previews_portable_summary`
- `tests/test_mxcontext.py`
- `tests/test_mkrevzip.py`
