# Rev0844 prompt refresh kind guard

Rev0844 finishes the small prompt-refresh extraction started in rev0842 and rev0843: the active-prompt kind guard now lives next to the row-to-suggestion mutation helper instead of remaining open-coded in `Editor`.

## Changed

- `prompt_refresh.py` now exposes `refresh_prompt_suggestion_rows()`.
- The helper owns the `prompt is not None` and `prompt.kind == expected kind` checks.
- `Editor._refresh_picker_prompt_suggestions()` now just adapts its existing limit-aware row providers to that helper.
- `tests/test_prompt_refresh.py` covers wrong-kind provider suppression and matching-kind query flow without constructing a full `Editor`.

## Why this is worth the evidence cost

The previous seam had centralized row application and row budgeting, but one high-risk branch still lived in `Editor`: a stale prompt kind could call the wrong provider unless every caller preserved the same guard. Moving that guard next to `begin_prompt_suggestion_rows()` makes the refresh contract self-contained: callers provide prompt, expected kind, and a query-only provider; the helper decides whether prompt mutation may happen.

This is intentionally not a prompt registry rewrite. The existing private refresh entrypoints remain, and command-token completion is untouched.

## Handoff risk

This touches runtime source, so the aggregate manifest must be rebuilt against rev0844 source before claiming a current-source pass. Keep source frozen after this change and resume `.artifacts/mxtest-all-64.json` with the standard 64-chunk path until `--verify-current` reports `manifest-passed true`, `source ok`, `environment ok`, and `resume-safe true`.
