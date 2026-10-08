# Rev0843 prompt row budget seam

Rev0843 continues the prompt refresh extraction without rewriting command completion. The repeated picker row providers in `Editor` no longer own the common query/limit/browse-budget policy.

## Changed

- `prompt_refresh.py` now exposes `prompt_rows_from_grouped_sections()` for section-backed pickers.
- `prompt_refresh.py` now exposes `prompt_rows_from_direct_or_grouped_sections()` for help-style pickers that use direct query rows but grouped browse rows for an empty query.
- `Editor` row providers now wire providers into these helpers instead of repeating query stripping, positive limit coercion, grouped section lookup, and browse-budget selection.

## Why this is worth the evidence cost

The repeated row-provider boilerplate was small per method but broad across palette, topic, binding, buffer, mark, jump, plugin, recent, docs, helplink, helpoutline, and helpnav. Leaving it duplicated made each picker behavior fix vulnerable to only landing in some prompt families.

This revision keeps the refactor narrow: providers remain query-only, prompt mutation remains centralized in the previous `begin_prompt_suggestion_rows()` boundary, and command-token completion is untouched.

## Handoff risk

This touches runtime source, so the archive-carried aggregate manifest must be refreshed before claiming a current-source full pass. If evidence recovery gets interrupted, resume `.artifacts/mxtest-all-64.json` with the standard 64-chunk command rather than adding more source churn.
