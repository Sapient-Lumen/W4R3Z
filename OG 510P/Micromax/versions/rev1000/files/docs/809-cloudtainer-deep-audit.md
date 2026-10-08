# Rev0851 — cloudtainer deep audit and repo-map freshness

This revision is a docs/evidence-truth correction, not a runtime behavior change. The incoming rev0850 archive already had the important mxtest/Makefile parity work; the severe problem found during the deep read was that at least one living handoff document still told the old rev0836 story.

## What went severely wrong

The stale `docs/02-repo-map.md` was the most dangerous mismatch. A second context drift was that `tools/mxcontext.py` listed recent revision docs only through rev0798, so the handoff context omitted rev0799-rev0851 notes until this revision. It still identified itself as rev0836, showed the old 240-second aggregate command, said complete aggregate evidence was pending, said source attestation still needed partitioning, and described installed help as broad/unpruned. Those claims contradicted the current Makefile, `.artifacts/mxtest-all-64.json`, source-dependency partitioning, and `docs/installed-help-manifest.txt`.

That kind of drift is cloudtainer-wasteful because it steers the next operator toward the wrong command shape. The project has already paid for bounded checkpointing; handoff docs must not send future runs back toward long outer-timeout behavior.

## What is missing

- A focused living-doc freshness test for `docs/02-repo-map.md`: catch stale current-rev headers, old runtime-budget values, pending-evidence wording, and claims that installed help/source dependencies are still unsolved.
- A small source-scale audit command or report target that prints the top files, top functions/classes, import cycles, duplicate numbered docs, current manifest state, and largest source partitions.
- An incremental typecheck lane for `src/micromax_editor`; the existing typecheck script covers `src/micromax` and tests but not the largest editor substrate.
- CI packaging/test workflow. Local cloudtainer evidence is good, but a repository-grade project should have at least lint, focused tests, aggregate manifest verification, build, and twine/check metadata gates.
- Packaging metadata polish: project URLs, classifiers, keywords, and modern license metadata.
- Evidence-cost accounting that distinguishes current invocation wall-clock from cumulative resumed chunk cost. The manifest can prove completeness, but operators also need to see where time is being spent across resumptions.

## What changed in rev0851

- Rewrote the living repo map to match current evidence commands and seams.
- Brought `tools/mxcontext.py` forward through `docs/809-cloudtainer-deep-audit.md`.
- Added a `test_mxcontext` guard that top revision-index docs appear in context output.

## What should change next

1. Add the living-doc freshness guard before a broad runtime seam.
2. Continue the existing narrow prompt seam work through `prompt_refresh.py` and `prompt_suggestions.py` rather than rewriting `Editor`.
3. Split `install_editor_hostcalls()` by hostcall family with a thin registry boundary and focused bridge tests.
4. Extract model-building families from `Editor` only when tests already pin the view/model behavior being moved.
5. Add a cheap `make audit-metrics` lane for file/function/import-cycle/doc-prefix/manifest summaries.
6. Add a first CI workflow that reuses existing commands instead of inventing new doctrine.
7. Refresh packaging metadata after evidence is current, not before a runtime extraction.

## Current audit measurements from the incoming archive

- The source manifest covered 1,112 source files and about 11.9 MB.
- The unpacked archive had 1,113 files before generated caches; docs dominated by count and bytes.
- `src/micromax_editor/editor.py` was about 24,000 lines and carried more than 1,000 methods/functions inside the `Editor` class family.
- `tools/mxtest.py`, `src/micromax_editor/micromax_bridge.py`, `src/micromax_editor/docs_cues.py`, and `src/micromax/core.py` also had multi-thousand-line installer/model functions.
- The carried aggregate manifest reported 2,207 selected tests passed, zero failures, zero timeouts, zero partials, and no remaining selected tests before this docs edit.
- A manual doctor preflight attempt in the session passed many subgroups but did not complete before the external container command timeout; the bounded aggregate lane is the safer handoff evidence source.

## Speculative direction

The project is converging on a good shape: a small VM, a headless editor model oracle, and a capability-scoped automation bridge. The main risk is not lack of tests; it is allowing the large editor/bridge/test-runner objects and large handoff docs to absorb unrelated responsibilities. Keep cutting narrow seams, keep the archive manifest current, and make stale living-doc claims mechanically visible.
