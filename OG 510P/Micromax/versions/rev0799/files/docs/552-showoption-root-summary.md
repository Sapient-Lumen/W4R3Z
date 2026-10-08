# Rev611 – `showoption` root summary keeps current config visible

## Why

- root exact inspectors should not go generic right before or right after Enter
- `showoption NAME` already had strong exact detail, but plain `showoption` still hid the live option inventory behind generic command/help text
- current-buffer option state is especially worth keeping visible because local overrides are part of Micromax's trust story

## What changed

- added `_option_inventory_preview_summary()` as one tiny shared root summary substrate
- plain `showoption` command-bar completion now reuses that summary instead of generic command metadata
- raw runtime `showoption` now prints the same summary before `usage: showoption NAME`
- the sample picker prefers changed local overrides before calmer default-local rows, then falls back to the first visible canonical option

## Shape of the summary

- compact inventory count: `N options`
- one representative sample: `NAME=value`
- explicit local state when relevant: `NAME=value (local)`

That keeps the root entry point small while still making current config truth visible.

## Coverage

- `tests/test_editor_option_words_set_toggle_show.py`
- `tests/test_editor_prompt_completion_hostcalls.py`
- `tests/test_mxcontext.py`
- `tests/test_mkrevzip.py`

## Follow-up stance

- keep exact inspectors usage-shaped, but make their root rows/reporting reuse live inventory truth whenever Micromax already has it
- prefer shared helper substrates over duplicated formatting so prompt and runtime stay aligned
