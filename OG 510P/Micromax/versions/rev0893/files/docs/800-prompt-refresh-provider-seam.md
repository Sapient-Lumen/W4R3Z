# Prompt refresh provider seam (rev0842)

Rev0842 makes the first deliberately runtime-touching prompt seam change after the full aggregate witness.

## What changed

- Added `src/micromax_editor/prompt_refresh.py` as the shared prompt-row-to-suggestion-session boundary.
- Replaced repeated picker prompt mutation blocks in `Editor` with `_refresh_picker_prompt_suggestions(kind, row_provider, limit=...)`.
- Kept existing row provider methods and prompt-kind entrypoints intact, so callers such as `_refresh_buffer_prompt_suggestions()` and `_refresh_helpnav_prompt_suggestions()` keep the same private API.
- Added focused tests in `tests/test_prompt_refresh.py` for row application, empty-row no-op behavior, and wrong-kind provider suppression.

## Why this was worth invalidating runtime evidence

The broad `Editor` prompt area had many repeated blocks that mixed three responsibilities:

1. verifying the active prompt kind;
2. asking a provider for rows;
3. mutating prompt suggestion state.

That made future prompt provider extraction riskier because every picker mode carried its own copy of the state-mutation contract. The new helper creates a small, tested boundary: row providers can remain query-only while the mutation path is centralized.

## What did not change

- Prompt rows are still the same `[insert, kind, menu, info]` shape.
- Existing picker refresh method names remain available.
- The command prompt completion path is not rewritten.
- `prompt_suggestions.py` still has broad editor-object access; rev0842 only narrows the picker refresh boundary before deeper provider work.

## Remaining risk

Touching `src/` invalidates runtime-sensitive aggregate evidence. After this revision, `.artifacts/mxtest-all-64.json` must be refreshed and verified before claiming a current-source full pass.
