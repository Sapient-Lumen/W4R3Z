# Rev643: TODO history packaged-rev guard

## What changed

`tools/mxcontext.py` now parses visible `# TODO (revN)` sections as a small handoff-history inventory instead of only inspecting the newest block. It records section-level `package rev...` drift inside the shared revision snapshot that powers both `mxcontext --check` and packaged `MICROMAX-CONTEXT.json`, and the recent stale bullets in `TODO.md` have been repaired to match their own headings.

## Why it matters

The newest checklist is not the only place future humans or LLMs learn from. The top of `TODO.md` is a short handoff trail, and stale packaged-rev bullets in older visible sections can quietly teach the wrong archive lineage even when the newest block is correct. Surfacing section-level drift keeps that trail boringly trustworthy.

## Boundaries

This stays deliberately small:

- parse only explicit `# TODO (revN)` history blocks already present in `TODO.md`
- compare each block's heading rev to its explicit `package rev...` checklist bullet when one exists
- warn through the existing `revision_sources()` / `mxcontext --check` / `MICROMAX-CONTEXT.json` path instead of inventing another manifest or lint pass
- do not require every historic section to contain a package bullet

## Validation

- `pytest -q tests/test_mxcontext.py tests/test_mkrevzip.py`
- `python tools/mxcontext.py --check`
