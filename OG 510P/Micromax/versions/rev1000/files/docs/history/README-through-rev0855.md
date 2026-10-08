# Archived `README.md` through rev0855

Preserved during the rev0856 mission/context reset. The corresponding living document now contains only current handoff material.

---

Rev0855 note: docs-cues risk work landed a zero-viewport schema fix before any wider parser split.

Latest landing (rev0855): `docs_cues_model(0, 0)` now returns the same top-level metric keys as an active docs-cues model, with every metric zeroed instead of missing newer counters.

# Micromax

Micromax is a small concatenative language, a reference Python VM, and a headless-plus-curses editor substrate used to explore capability-scoped editor automation. The Python implementation is the reference implementation and test oracle for future ports.

## Current risk picture

The riskiest completed items are the rev0822 package-resource fix, the rev0823 docs-history split, the rev0824 prompt-suggestion extraction, the rev825 hostcall/core registry extraction, the rev826-rev828 command-dispatcher extractions, the rev829-rev0835 mxtest evidence runway, the rev0836 handoff-manifest shortcut alignment, the rev0837 chunk source-dependency / installed-help boundary, the rev0838 doctor handoff-manifest/timeout fix, the rev0839 manifest-summary next-incomplete view, the rev0840 doctor safe-timeout teardown, the rev0841 full aggregate evidence pass, the rev0842 prompt refresh provider seam, the rev0843 prompt row budget seam, the rev0844 prompt refresh kind guard seam, the rev0845 picker refresh dispatch seam, the rev0846 prompt-complete dispatch allowlist cleanup, the rev0847 workflow/test-config source-dependency plus interrupt-preservation fix, the rev0848 cloudtainer-safe aggregate runtime budget, the rev0849 doctor-chunked Makefile passthrough, the rev0850 doctor/test-all budget parity fix, the rev0851 living-doc/context truth refresh, the rev0852 living-doc guard/context derivation plus prompt submit target seam, the rev0853 helpnav/helpoutline row submit seam, the rev0854 recent picker raw-open guard, and the rev0855 docs-cues zero-schema guard. The highest-risk open item is keeping aggregate evidence current after narrow runtime seams while continuing to reduce repeated prompt/editor plumbing; the latest runtime audit shows stale suggestion authority can become a correctness bug, and the AST audit still flags `docs_cues_model_from_parts()` and the editor hostcall installer as the next largest split candidates. The evidence lane now has bounded, resume-safe progress at file, node-id span, subprocess-batch, per-test checkpoint, wall-clock runtime, signal-interruption, archive-carried-manifest, selected-test-progress, Makefile-default-manifest, doctor-chunked-manifest, doctor-child-timeout, budget-remainder-preservation, and chunk source-dependency granularity.

## Quick start

Run the language REPL:

```bash
python -m micromax.repl
```

Run the editor in headless command mode:

```bash
python -m micromax_editor
python -m micromax_editor path/to/file.txt
python -m micromax_editor --help-doc 00-vision --dump-screen 24 80
```

Run the curses TUI:

```bash
python -m micromax_editor --tui
python -m micromax_editor --tui path/to/file.txt
python -m micromax_editor --tui --help-doc 00-vision
```

## Development workflow

```bash
make bootstrap
make test
make doctor
make context
python tools/mxcontext.py --check
python tools/mxlint.py
```

Bounded aggregate evidence lane, using the default archive-carried manifest:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make test-all-chunks
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make test-verify-current
```

Equivalent explicit command:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxtest.py \
  --run-chunks 64 \
  --strategy segment \
  --isolate-files \
  --resume \
  --checkpoint-tests \
  --max-new-tests 120 \
  --max-new-files 8 \
  --test-batch-size 0 \
  --file-timeout 180 \
  --max-runtime-seconds 25 \
  --json .artifacts/mxtest-all-64.json \
  --durations 0
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxtest.py \
  --verify-current .artifacts/mxtest-all-64.json
```

Build a handoff archive:

```bash
make pack
make revzip TAG=manifestshortcut-cloudaudit-docdigest-codename
```

The archive filename convention is:

```text
Micromax-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip
```

## Current entry points

Read these first, in this order:

1. `TODO.md` — current checklist and next high-leverage work.
2. `docs/43-worklist.md` — current work lanes without historical noise.
3. `docs/01-llm-start-here.md` — short handoff for the next agent.
4. `docs/02-repo-map.md` — current source map and seams.
5. `docs/revision-index.json` — structured revision history.

The historical append-only docs are preserved under `docs/history/`.
