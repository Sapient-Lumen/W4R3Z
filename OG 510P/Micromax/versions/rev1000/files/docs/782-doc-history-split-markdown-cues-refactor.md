# Rev823 living-doc history split and markdown/docs-cues refactor

This landing attacks two forms of risk that were easy to keep postponing: the living docs had become multi-hundred-KB append-only ledgers, and the docs/help markdown scanner was still embedded in the already-large editor class file.

## What changed

- The old README, TODO, worklist, LLM-start, and repo-map bodies were preserved under `docs/history/*-through-rev0822.md`.
- The current README, TODO, `docs/43-worklist.md`, `docs/01-llm-start-here.md`, and `docs/02-repo-map.md` were rewritten as short current entry points.
- `tests/test_docs_living_hygiene.py` now prevents those living docs from silently returning to multi-hundred-KB ledgers.
- Markdown/docs helper functions moved from `src/micromax_editor/editor.py` to `src/micromax_editor/markdown_docs.py`.
- The large `_docs_cues_model_from_parts` implementation moved from `Editor` to `src/micromax_editor/docs_cues.py`, with `Editor` retaining a thin delegating method for compatibility.
- `src/micromax_editor/tui.py` now imports markdown helpers from the extracted markdown module instead of reaching through the editor monolith.
- `tests/test_installed_runtime_resources.py` now separates the package declaration check from a fast fake-target runtime layout check, avoiding a slow pip build inside the default pytest lane while preserving the installed-resource behavior probe.

## Why this mattered

Rev0822 made root `docs/*.md` install as runtime help resources. That made the living-doc bloat operationally visible: `docs/01-llm-start-here.md`, `docs/02-repo-map.md`, and `docs/43-worklist.md` were being packaged as help docs even though most of their bytes were historical handoff archaeology. Moving the old bodies under `docs/history/` preserves the archaeology in source archives while keeping installed root help docs focused.

The code extraction is intentionally mechanical. No markdown behavior was rewritten; helpers and the docs-cues model were moved behind the same public names and focused regressions were run. This reduces future merge/edit risk and creates a clearer next seam for prompt completion.

## Measured impact

Before rev823, the largest living docs were roughly:

```text
TODO.md                   ~943 KB
README.md                 ~846 KB
docs/43-worklist.md       ~837 KB
docs/01-llm-start-here.md ~704 KB
docs/02-repo-map.md       ~414 KB
```

After rev823, the current versions are small orientation files, while the archived versions remain available under `docs/history/`.

The editor monolith also shrank by moving roughly 3.8k lines of markdown/docs-cues code into focused modules:

```text
src/micromax_editor/markdown_docs.py
src/micromax_editor/docs_cues.py
```

## Boundaries

- Compatibility imports from `micromax_editor.editor` remain available for tests and older callers that import markdown helpers from the editor module.
- `docs/history/` is preserved in source archives but is not matched by the current `pyproject.toml` `docs/*.md` installed-data pattern.
- The docs-cues extraction leaves the `Editor._docs_cues_model_from_parts(...)` method in place as a delegating compatibility seam.

## Next cuts

Prompt completion is now the highest-value extraction target. The likely first methods are `_prompt_commandish_suggestion_rows` and `_prompt_command_token_candidates`, backed by command-palette, path-completion, prompt-completion, and picker-navigation tests.
