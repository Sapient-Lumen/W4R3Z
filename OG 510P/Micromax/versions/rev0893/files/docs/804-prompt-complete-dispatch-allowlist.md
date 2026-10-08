# Prompt complete dispatch allowlist

Rev0846 removes the remaining hard-coded picker prompt-kind allowlist from `Editor.prompt_complete()`.

## Problem

Rev0845 centralized active picker refresh dispatch, but `prompt_complete()` still carried a separate tuple of completable prompt kinds. That was the same class of drift that previously let help link, help outline, and help navigation prompts be declared completable while Tab could not reseed their suggestions after a clear.

## Change

`prompt_complete()` now treats the command prompt as the only special token-completion prompt. Every other completable picker prompt is admitted by the active picker refresh dispatcher:

```text
command prompt -> token-aware command completion path
picker prompt  -> `_picker_prompt_refreshers()` membership + active refresh path
unknown prompt -> false
```

A focused test installs a synthetic picker refresher on an editor instance and verifies that `prompt_complete()` accepts it through the dispatch map. That keeps future picker kinds from requiring two separate allowlist edits.

## Boundary

This is intentionally not a broad prompt registry. The dispatch map still lives near the bound editor refresh callbacks, and command completion remains independent. The refactor only removes duplicate truth about which picker prompt kinds can be completed.
