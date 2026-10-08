# Rev821 — cloudtainer deep-read audit

This revision is both an audit handoff and a small runtime/CLI repair.  The
session inspected the rev0820 datacube as a source archive, an installed package,
a documentation corpus, a test/evidence machine, and an editor/runtime design.

## What changed in this revision

- Fixed the headless CLI `--help-doc <absolute-or-outside-docs-root.md>` path.
  The editor and script hostcalls still keep docs-root containment by default,
  but the trusted CLI entry point may now open an explicit markdown path supplied
  by the user.  This restores the markdown cue dump tests without widening script
  authority.
- Added this audit note and moved the current TODO/worklist/revision index to
  rev821.

## Local source snapshot

The filtered source tree contains 1,056 tracked-ish files after this audit note:
747 markdown files, 272 Python files, 8 manifests, 7 shell scripts, 5 JSON files,
3 `.mx` files, and 2 TOML files.  The big weight is intentional project history,
but the current landing surfaces are carrying too much of that history inline.

Large surfaces observed:

- `docs/` — about 5.37 MB across 746 files.
- `src/` — about 6.12 MB across 169 files after transient build caches are
  excluded from packaging.
- `tests/` — about 5.91 MB across 366 files.
- `src/micromax_editor/editor.py` — 1.23 MB, 29,196 lines, 1,129 function
  definitions, and an `Editor` class spanning about 26,607 lines.
- `README.md` — 844 KB with 574 `Rev... note` preambles and 465 `Latest tiny
  landing` preambles before a conventional landing page can do its job.
- `TODO.md` — 940 KB with 491 revision notes and 473 tiny landings.
- `docs/43-worklist.md` — 837 KB with 446 revision notes and 409 worklist
  landings.
- `docs/01-llm-start-here.md` — 704 KB; it starts as old TODO material before
  the durable “start here” material appears.
- `docs/02-repo-map.md` — 414 KB; it also starts as old TODO material before the
  durable map appears.

The largest code seams are now obvious extraction targets:

- `Editor._docs_cues_model_from_parts` — about 2,081 lines.
- `Editor._prompt_commandish_suggestion_rows` — about 602 lines.
- `Editor.submit_prompt` — about 527 lines.
- `Editor._prompt_command_token_candidates` — about 517 lines.
- `install_default_commands` — about 3,494 lines.
- `install_editor_hostcalls` — about 2,963 lines.
- `install_core_words` — about 1,885 lines.

## Validation evidence from this session

- `python tools/mxcontext.py --check` passed on the incoming rev0820 tree.
- The focused prompt-completion hostcall file passed: 258 tests in 12.82 seconds
  of pytest time, about 16 seconds wall-clock in this cloudtainer.
- A complete chunked aggregate run was attempted with file isolation and JSON
  evidence capture.  It found a real failure in `tests/test_editor_main_cli.py`:
  17 CLI markdown cue tests failed because the CLI could no longer open explicit
  temp markdown paths outside `docs_root()`.  The failure was not just output
  truncation.
- After the rev821 fix, `tests/test_editor_main_cli.py` passes: 20 tests in
  15.11 seconds.
- The security boundary regression lane also passes after the fix:
  `tests/test_editor_help_docs_boundary.py tests/test_editor_main_cli.py` passes
  23 tests in 14.53 seconds.

The full suite is still too chatty and long-running for a turn-by-turn cloudtainer
handoff unless it is captured to `.artifacts/` and summarized.  The failed
aggregate attempt reached 2,128 collected tests and continued past chunk 6/8
before being stopped after the actionable CLI failure was reproduced and fixed.

## What is missing

1. **Installed-package docs/plugins story.**  An install probe showed the package
   installs the Python packages and `micromax/stdlib/core.mx`, but not the root
   `docs/` or `plugins/` trees.  From outside the source checkout,
   `python -m micromax_editor --help-doc 00-vision --dump-screen 10 80` cannot
   open `00-vision`.  Either package the docs/plugin resources intentionally or
   declare source-checkout-only behavior and make the CLI error explicit.
2. **A current documentation lane separate from the history lane.**  The current
   `README`, `TODO`, worklist, start-here doc, and repo map have become append-only
   revision ledgers.  That preserves archaeology but punishes every human/LLM
   entry point.
3. **A product/release landing.**  The source contains a language runtime, editor,
   plugin host, docs browser, and a safety model, but the top-level README does
   not quickly answer what to install, what is stable, what is experimental, and
   what a user should try first.
4. **A stable extension/API boundary document.**  Capabilities and hostcalls are
   heavily tested, but the public plugin contract versus internal hostcall/test
   scaffolding is not cleanly separated for plugin authors.
5. **A durable evidence mode.**  Raw full-suite output is expensive and confusing
   in this environment.  The project already has `tools/mxtest.py`; the missing
   part is making the default handoff say “manifest path, digest, slowest files,
   failed files” rather than streaming thousands of pytest lines.
6. **Syntax/language infrastructure decision.**  The editor currently hand-builds
   a lot of markdown and command-prompt structure.  If the goal is a general code
   editor, eventually choose whether Tree-sitter/LSP are optional integrations,
   hard dependencies, or deliberately out of scope.

## What has gone wrong or wasteful

- **Append-only preambles are drowning the living docs.**  This is the biggest
  waste because every later session must re-read old rev notes before reaching
  the current invariant.  Keep the history, but move it behind an index or a
  `docs/history/` stream.
- **The editor god object is now a coordination tax.**  The code works, and the
  tests show strong safety intent, but a 26k-line class makes every feature look
  adjacent to every other feature.  Extract pure models first; do not start with
  risky behavior rewrites.
- **The full-suite evidence path can look broken when only the reporting channel
  is overloaded.**  Early doctor runs looked like failures because output/time
  limits were hit.  Captured manifests fixed that enough to reveal a real CLI
  bug, which is the right direction.
- **Package behavior and source-checkout behavior diverge.**  The root docs and
  plugin defaults assume a source tree.  The packaging test only checks stdlib
  resources, so the installed editor can be missing its own help corpus without
  failing CI.
- **Duplicate numeric doc prefixes exist.**  Current duplicates are `32`, `735`,
  and `752`.  They may be harmless, but prompt/docs grouping treats numeric
  families as meaningful; duplicates should be intentional or renumbered.

## Recommended next cuts

1. Add an installed-package regression test for `--help-doc 00-vision` from a
   temp cwd after `pip install --target ... .`.  Decide whether to package docs
   as `micromax_editor` resources or make `MICROMAX_DOCS` mandatory outside a
   checkout.
2. Split current landing docs from history:
   - `README.md` becomes a short product/repo landing.
   - `TODO.md` keeps only rev821 current tasks plus a link to historical TODOs.
   - `docs/01-llm-start-here.md` starts with current invariants.
   - Revision notes move to generated/history docs indexed by
     `docs/revision-index.json`.
3. Extract `docs_cues_model`, prompt completion, command registration, hostcall
   registration, and core word registration into modules with behavior-preserving
   tests.  Treat this as a mechanical refactor lane, not a feature lane.
4. Make `tools/mxtest.py --run-chunks ... --json .artifacts/...` the default
   evidence path and surface `--manifest-summary` in the handoff.
5. Document the plugin contract as capabilities plus lifecycle plus allowed
   persistence.  Keep internal hostcalls separate from “stable plugin API”.
6. Defer Tree-sitter/LSP/Wasm until after the docs/package boundary is clean,
   but keep them as explicit roadmap choices rather than letting bespoke editor
   infrastructure grow forever by accident.

## Speculative positioning

Micromax’s distinctive value is not “another terminal editor”; it is a small
language/runtime with an editor host, capability-filtered extension surfaces, and
recoverable plugin lifecycle semantics.  That is a plausible niche: simpler than
Neovim’s ecosystem, safer than arbitrary embedded Python, and more programmable
than a plain nano-like editor.  The risk is that the project spends too much of
its cloudtainer budget maintaining append-only documentation and giant dispatcher
functions instead of clarifying the product boundary.
