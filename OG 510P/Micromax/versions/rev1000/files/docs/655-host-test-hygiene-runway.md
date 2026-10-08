# Rev714 - host test and hygiene runway

## What changed

Micromax now keeps its local maintenance commands more isolated from host-machine noise.

- `scripts/test.sh` exports `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` by default before running pytest.
- `scripts/test.sh` forwards any extra arguments to pytest, so future work can use focused runs like `bash scripts/test.sh tests/test_mxlint.py` without bypassing the repo runner.
- `tools/mxdoctor.py` uses the same default pytest-plugin isolation for its test step while still respecting an explicit caller override.
- `tools/mxlint.py` and `tools/mxformat.py` skip local virtualenvs, cache directories, build/dist output, generated zip archives, root dotfiles, and `.tmp*` scratch trees.
- `tools/mkrevzip.py` skips `.venv` trees so a post-bootstrap archive does not accidentally vendor third-party packages.
- The current fallback lint baseline is clean again: `docs/02-repo-map.md` has its final newline back and `docs/610-macro-play-root-default-slot-summary.md` no longer carries a blank trailing-space bullet.

## Why it matters

This is not a product feature. It is runway trust.

A small archive like Micromax should behave the same way in a fresh container, a developer checkout, and a future LLM scratch tree. Ambient pytest plugins are useful in their own projects, but they should not get to decide whether Micromax's focused checks hang. Likewise, after `scripts/bootstrap.sh` creates `.venv`, fallback format/lint and revision packaging should keep inspecting Micromax itself rather than third-party dependency trees.

Rev714 makes the boring path boring:

- focused tests use the repo's own runner
- doctor tests use the same isolated default
- local generated state is ignored by fallback hygiene tools
- revision zips stay small after bootstrap
- lint failures point at real Micromax text, not vendored or generated files

## Follow-up ideas

- Add a small chunked test runner for environments where the full suite exceeds one command window.
- Teach `tools/mxdoctor.py` to report the isolated pytest setting explicitly before running tests.
- Consider sharing one generated-path skip helper across `mxlint`, `mxformat`, and `mkrevzip` once the archive wants another tooling cleanup pass.
