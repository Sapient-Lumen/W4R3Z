# Rev0855 docs-cues zero-schema refactor

## Problem

`docs_cues_model_from_parts()` had accumulated new top-level counters in the full viewport path without keeping the early zero-viewport return in lockstep. The normal model included newer keys such as heading-level, fragment-source, fenced-code-role, raw-HTML, escaped-markdown, and literal counters. A zero-sized viewport returned the older subset instead.

That is risky because headless consumers should be able to treat `docs_cues_model()` as a stable schema regardless of whether the active window has paintable rows. A terminal resize to zero rows, a dump-screen probe, or a downstream UI bridge should not need special-case `dict.get()` fallback for counters that exist during normal rendering.

## Change

Rev0855 introduces `DOCS_CUE_ZERO_METRIC_KEYS` and `_zero_docs_cue_metrics()` in `src/micromax_editor/docs_cues.py`. The initial docs-cues payload now starts from the same zero-valued metric schema used by the normal full-output model, then overlays geometry and row data.

This removes the hand-maintained stale initial counter block and shrinks `docs_cues_model_from_parts()` from 2,081 lines to about 1,928 lines without moving row scanning, parsing, or rendering semantics.

## Coverage

`tests/test_editor_screen_layout.py::test_docs_cues_model_keeps_zero_viewport_metric_schema` opens a real help doc, compares the key set from `docs_cues_model(0, 0)` with a normal active model, and checks every zero-metric key is present and zero in the zero-viewport model.

Focused docs-cues CLI/layout tests were rerun around literal-source metadata, block metadata, and the new zero-schema path. The aggregate manifest must still be refreshed because this is a runtime/test/docs source change.

## Audit note

This is the safest first `docs_cues.py` cut because it fixes a real schema-completeness bug and reduces duplicated initialization without splitting the row scanner itself. The next docs-cues refactor should still be preservation-first: extract one model-output-neutral sub-builder at a time, with active-model key and value snapshots before moving parsing logic.
