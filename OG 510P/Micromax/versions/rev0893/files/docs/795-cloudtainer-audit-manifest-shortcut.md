# Rev0836 — cloudtainer audit and manifest shortcut alignment

This revision is a deep-read audit pass plus one small workflow repair.  The
incoming rev0835 archive had made the aggregate evidence manifest travel in the
handoff zip, but the advertised Makefile shortcut still wrote a different
manifest path.  In practice, a future operator could type `make test-all-chunks`
and silently start `.artifacts/mxtest-all.json` instead of resuming the archive-
carried `.artifacts/mxtest-all-64.json`.

## What changed

- Added `TEST_MANIFEST ?= .artifacts/mxtest-all-64.json` to `Makefile`.
- Routed `test-all-chunks`, manifest summary, manifest verification, current
  source/environment/current checks, and chunk recommendation through
  `$(TEST_MANIFEST)`.
- Kept the manifest path overridable, so an operator can still run
  `make test-all-chunks TEST_MANIFEST=.artifacts/mxtest-all.json` when they want
  the older canonical name.
- Added a tiny Makefile regression test to keep the default aligned with the
  archive-carried 64-chunk evidence lane.
- Added this audit note and refreshed the living handoff docs for rev0836.

## Deep-read findings

### Missing or still underbuilt

1. **A complete aggregate suite manifest.**  The carried evidence path is much
   better than it was before rev0835, but it is still partial evidence, not a full
   pass.  After resuming the incoming manifest in this cloudtainer, the old-source
   `.artifacts/mxtest-all-64.json` reached 281 selected tests passed with no
   failures.  After rev0836 source edits, the current-source manifest is regenerated before
   packaging so the handoff carries source/environment-current evidence.
2. **Partitioned source attestation.**  The source digest covers docs, tests,
   tools, project config, examples, plugins, portability data, and runtime code.
   This is safe, but it means a docs-only handoff note invalidates every partial
   test manifest.  That is now one of the largest avoidable costs in the
   cloudtainer loop.
3. **A curated installed help manifest.**  The wheel currently carries all 760
   root `docs/*.md` files, about 3.23 MB uncompressed, as installed help data.
   That preserves discoverability but mixes product help, design notes, and
   revision archaeology in the runtime surface.
4. **An explicit plugin/public API contract.**  Capability and authority tests
   are strong, but the stable plugin author surface is still less obvious than
   the internal hostcall/test surface.
5. **A smaller editor coordination object.**  `src/micromax_editor/editor.py` is
   still about 24k lines and the `Editor` class spans nearly the whole module.
   Recent extractions helped, but prompt, help, session, and screen ownership are
   still too easy to couple accidentally.
6. **A doctor/preflight timeout policy.**  The default doctor is intended to be a
   bounded preflight, but it still shells through multiple pytest children without
   an explicit child timeout.  In this cloudtainer, repeated doctor attempts were
   fragile enough that focused tests were more trustworthy than a long doctor
   scrollback.

### What should change next

1. **Keep one evidence lane per archive.**  Use `.artifacts/mxtest-all-64.json`
   as the default handoff manifest while this 64-chunk runway is active.  Keep
   `.artifacts/mxtest-all.json` only as an explicit override or a later full-pass
   canonical lane.
2. **Split source attestation into dependency classes.**  At minimum, record
   separate digests for runtime code, tests, docs/help, toolchain files, and
   packaging metadata.  Resume should stay conservative, but manifest summaries
   should be able to say “only docs changed” rather than throwing away all prior
   test progress silently.
3. **Create `docs/help-manifest.json` or similar.**  Installed help should be a
   curated subset plus a generated index.  Revision notes can remain in the
   datacube zip without becoming runtime help topics.
4. **Add performance budgets around docs/help startup and prompt completion.**
   A local smoke showed `python -m micromax_editor --help-doc 00-vision
   --dump-screen 24 80` taking about 2 seconds in this cloudtainer.  The exact
   number is host-sensitive, but it is enough to justify a budget test around
   cold docs scanning and first Tab/help completion.
5. **Give `mxdoctor` child subprocesses explicit timeouts.**  The mxtest runway
   has timeout and checkpoint semantics; doctor should not be the command that
   can hang indefinitely in a handoff preflight.
6. **Continue prompt seam purification before adding more prompt features.**
   The extracted `prompt_suggestions.py` still takes a broad editor object.  The
   safest next slice is inventory providers first, row/detail formatting second,
   then a protocol once tests pin the boundary.

### Places where something went wrong or wasteful

- **The Makefile shortcut drifted from the carried artifact.**  This is fixed in
  rev0836.  The old behavior did not corrupt evidence, but it wasted cloudtainer
  time by creating a second aggregate manifest path.
- **Repo-wide source digesting is too coarse for a docs-heavy datacube.**  It is
  safe, but every revision note invalidates partial test evidence.  This is the
  biggest remaining structural waste in the current loop.
- **Installed help is probably overinclusive.**  Shipping every root Markdown
  note as runtime help keeps history searchable, but it also makes the wheel and
  help index carry many revision-specific notes that are not user help.
- **Default doctor is still less controlled than mxtest.**  The project invested
  heavily in checkpoint/runtime behavior for the aggregate suite, but the human
  “is this archive healthy?” command does not yet inherit the same timeout
  discipline.
- **The monolith is smaller but still central.**  After rev0824-rev0828, the worst
  dispatcher seams are better, yet `Editor` remains the place where unrelated
  concepts meet.  Future changes should be seam extractions, not new behavior in
  the class body.

## Online research notes used for this audit

- CPython's official version-status page shows Python 3.10 in security mode with
  end of life scheduled for 2026-10, while 3.13 and 3.14 are active bugfix
  branches.  That means `requires-python >=3.10` is fine for now but should have
  a planned 3.11/3.12+ floor transition before 3.10 EOL.
- Setuptools' data-file guidance says the common package-runtime-data case is to
  include data inside packages rather than arbitrary platform-specific data
  locations.  Micromax's current `data-files` install works, but a future package
  resource layout would likely be cleaner for docs/plugins.
- Pytest 9.0 made `PytestRemovedIn9Warning` errors by default, and 9.1 is
  expected to remove the affected features.  The current environment is already
  running pytest 9.0.2, so warning-clean tests matter.
- pytest-xdist supports `loadfile` and `loadscope` distribution modes that keep
  file/class groups together.  Micromax's custom mxtest runner provides stronger
  manifest/checkpoint semantics, but xdist remains a useful reference for future
  parallel execution or scheduling ideas.

## Validation evidence

- `python tools/mxcontext.py --check` passed on the incoming rev0835 tree.
- `python tools/mxlint.py` passed on the incoming tree.
- Focused pre-change tests passed: `tests/test_mxtest.py`,
  `tests/test_docs_living_hygiene.py`, and `tests/test_revision_index.py` passed
  110 tests.
- The incoming `.artifacts/mxtest-all-64.json` verified as source/environment
  current when run with the expected isolated environment variables.
- A bounded resume advanced the old-source manifest from 160 passed selected
  tests to 281 passed selected tests with no failures before this revision's
  source edits invalidated the old source digest.
- After rev0836 source/doc changes, the current `.artifacts/mxtest-all-64.json`
  is regenerated/resumed before packaging and `--verify-current` is expected to
  report manifest/source/environment ok with `resume-safe: true` while the
  aggregate remains partial.
- Rev0836 adds `tests/test_makefile_handoff_manifest.py` to cover the Makefile
  shortcut alignment.
