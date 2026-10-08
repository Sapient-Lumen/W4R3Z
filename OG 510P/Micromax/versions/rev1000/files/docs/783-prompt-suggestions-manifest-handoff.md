# Rev824 prompt suggestions extraction and manifest handoff

Rev824 continues the rev0823 cleanup by cutting a second large behavior cluster out of `Editor` and making full-suite evidence easier to hand off without raw pytest scrollback.

## What changed

- Added `src/micromax_editor/prompt_suggestions.py`.
- Moved the command-ish suggestion-row builder and command-token candidate builder out of `editor.py`.
- Kept the old `Editor._prompt_*` methods as compatibility delegates so existing tests and callers do not need to move all at once.
- Added automatic manifest-first summary output after `tools/mxtest.py --run-chunks ...`; pass `--no-run-summary` to keep the older quieter behavior.
- Added mxtest regressions for the default summary, the suppression flag, and interrupted isolated-file checkpoint preservation.

## Prompt extraction boundary

The extraction is deliberately behavior-preserving. `prompt_suggestions.py` still takes an editor object and calls existing row/detail helpers, but it removes roughly one thousand lines from the monolith and gives future work a single module for prompt command completion policy.

This is the next sensible place to make the code more pure later:

1. keep row formatting in `prompt_suggestions.py`;
2. move read-only inventory collection into small query helpers;
3. replace broad editor-object calls with a narrow protocol only after tests cover the new seam.

## mxtest handoff behavior

Before rev824, a complete chunked run required a second command to print the useful compact evidence:

```bash
python tools/mxtest.py --manifest-summary .artifacts/mxtest-all.json
```

That command still works. Rev824 adds the same summary automatically after chunked runs:

```bash
python tools/mxtest.py --run-chunks 8 --strategy segment --isolate-files --resume --json .artifacts/mxtest-all.json
```

The final output now includes:

- aggregate status and completeness;
- selected/collected/chunk counts;
- source and environment digests;
- slowest chunks;
- slowest isolated files when present;
- manifest verification issues when the aggregate is structurally inconsistent.

Use this only as a compact handoff. The JSON manifest remains the evidence of record.


## Interrupted isolated-file checkpointing

The full-suite audit in this cloudtainer exposed another mxtest waste: when an isolated-file run was interrupted, the manifest could record the chunk as partial while losing the completed per-file rows inside that chunk. Rev824 now lets isolated-file runs publish progress snapshots before each file and after each terminal file result. On interruption, the current file is recorded as `partial` with its signal, and completed prior file rows remain in the JSON.

This matters because a cloudtainer timeout should not erase the useful narrowing evidence that was already paid for.

## Validation run in rev824

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python -m pytest -q tests/test_editor_prompt_completion_hostcalls.py --durations=10
# 258 passed
```

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python -m pytest -q tests/test_mxtest.py --durations=10
# 82 passed
```

```bash
python tools/mxlint.py
# mxlint: ok
```

## Remaining risk

The prompt module is extracted, not purified. It should not be rewritten until the next pass can reduce the editor-object surface with narrow protocols and focused prompt-row tests. The full aggregate mxtest run was attempted but interrupted by the cloudtainer during chunk 2; with the new isolated-file checkpointing, future reruns should preserve better narrowing evidence. The next large editor seams remain command registration, hostcall registration, and core-word registration.
