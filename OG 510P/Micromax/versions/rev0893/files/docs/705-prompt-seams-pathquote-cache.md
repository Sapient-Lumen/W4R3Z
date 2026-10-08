# Rev761 prompt seams, path quoting, and hot-row cache audit

Rev761 keeps the rev759/rev760 performance lane moving, but deliberately spends most of the change budget on code seams rather than another registry pass. The risky surface is prompt completion: it is hot, user-facing, and historically easy to bloat because every new command preview wants ranking, grouping, provenance, and docs metadata.

## What changed

- Prompt ranking helpers moved out of `editor.py` into `src/micromax_editor/prompt_rank.py`: fuzzy subsequence matching, common picker-row scoring, multi-term field scoring, and the shared sort-key types.
- Prompt grouping and section-summary helpers moved into `src/micromax_editor/prompt_rows.py`: row normalization, section grouping, section budget limiting, flattening, summary detail assembly, and summary-row filtering.
- Command-prompt token/path completion moved into `src/micromax_editor/prompt_completion.py`: shell-ish token scanning, cursor-local token context, path completion rendering, plugin row overlays, and exact-common-candidate preference rules.
- Picker selection/position helpers moved into `src/micromax_editor/prompt_model.py`: current-row normalization, row-index movement, section-start discovery, next/previous section jumps, and current-position summaries.
- `editor.py` now delegates those seams instead of hosting another layer of inline prompt policy. The file is still too large, but this cut removes roughly five hundred lines from the monolith and turns previously private prompt behavior into direct unit-test targets.

## Correctness fixed now

Command prompt path completion used to autoquote whitespace and double quotes, but not single quotes or backslashes. That meant completing a real filename like `alpha's.txt` could generate `open alpha's.txt `, which the command parser treats as an unterminated quote, and a filename containing `\` could be parsed back as a different path. Rev761 quotes those names with double quotes, escapes backslashes/double quotes inside the rendered candidate, and switches away from user-started single quotes when the completed filename itself contains a single quote. Regression tests now complete those filenames and parse the generated command line back to the intended argument.

Path completion also now sorts matches before applying the item cap, with directories first. That avoids returning an arbitrary filesystem-iteration slice in large directories.

## Waste corrected

The rev759 fix stopped repeated docs scans, but command completion could still call `doc_prompt_rows()` repeatedly while building many topic/detail rows. Rev761 adds a tiny batching guard so a single completion pass warms docs prompt rows once and then reuses the populated cache while row metadata is assembled.

A smaller display-path cache now memoizes `_display_path(...)` during prompt/detail rendering. The built-in `cd` command clears the cache after changing directories, and a regression test covers both docs-root and display-path cache reset.

The fast `mxdoctor` preflight now includes the four pure prompt seam test files, so this extraction is covered in the normal handoff check rather than only in a bespoke validation command.

## Audit note

The prompt surface has been growing by accretion: ranking, rows, summaries, exact details, path rendering, docs metadata, and picker navigation all lived inside one editor class. That is risky because hot completion paths become expensive through innocent-looking formatting calls. Rev761 does not solve the editor monolith, but it separates four prompt seams with focused tests so future changes can ask: is this ranking, rows, token/path completion, or picker state?

## Remaining risk

`prompt_complete(...)` itself is still large and still coordinates built-in candidates, filesystem candidates, plugin candidates, row metadata, common-prefix insertion, and suggestion sessions. The next high-leverage split is a command-completion planner that returns a small result object for the editor to apply. That would make plugin/builtin/path merge behavior testable without entering the full editor object.

`prompt_rows.py` and `prompt_model.py` intentionally stay tiny, but they both operate on the same four-column prompt row convention. If the row shape changes, the convention should become one named data structure rather than more list indexing.

## Validation notes

Focused validation in this cloudtainer:

- `PYTHONPATH=src python -m py_compile src/micromax_editor/editor.py src/micromax_editor/command_dispatcher.py src/micromax_editor/prompt_completion.py src/micromax_editor/prompt_model.py src/micromax_editor/prompt_rank.py src/micromax_editor/prompt_rows.py tools/mxcontext.py tools/mxdoctor.py tests/test_prompt_completion.py tests/test_prompt_model.py tests/test_prompt_rank.py tests/test_prompt_rows.py tests/test_editor_prompt_path_completion.py tests/test_editor_doc_prompt_cache.py tests/test_mxdoctor.py` passed.
- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_prompt_rank.py tests/test_prompt_rows.py tests/test_prompt_model.py tests/test_prompt_completion.py tests/test_editor_prompt_path_completion.py tests/test_editor_doc_prompt_cache.py tests/test_mxdoctor.py --durations=10` passed: 49 tests in 0.76 seconds.
- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_editor_prompt_completion_hostcalls.py tests/test_prompt_grouping_sections.py tests/test_command_palette_path_completion.py tests/test_editor_mx_commands_and_completion.py --durations=20` passed: 349 tests in 11.28 seconds.
- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_editor_pickers_buffers_marks.py tests/test_editor_jumppick.py tests/test_editor_helpoutlinepick.py tests/test_editor_helplinkpick.py tests/test_tui_prompt_display_items.py tests/test_tui_prompt_display_lines_counts.py tests/test_tui_prompt_display_lines_sticky_header.py tests/test_tui_prompt_match_spans.py --durations=20` passed: 79 tests in 1.54 seconds.
- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q tests/test_revision_index.py tests/test_mxcontext.py tests/test_mkrevzip.py tests/test_mxdoctor.py --durations=10` passed: 16 tests in 6.37 seconds.
- `PYTHONPATH=src python tools/mxdoctor.py` passed: `mxlint` ok and 76 bounded preflight tests in 3.38 seconds.
- `PYTHONPATH=src bash scripts/lint.sh` and `PYTHONPATH=src python tools/mxcontext.py --check` passed.
- `PYTHONPATH=src python tools/mxtest.py --plan --chunks 8 --strategy segment --json /mnt/data/micromax_rev0761_promptseams_mxtest_plan.json` collected 1565 tests into eight segment chunks.

Full-suite validation is still not claimed by this note; use the chunked mxtest lane for aggregate evidence.
