Rev1000 note: the repository now makes release-evidence state explicit and corrects stale first-contact language that still called a working editor a future prototype. The accompanying mission audit identifies the central risk: Micromax has built a stronger trust laboratory than product-adoption loop.

Latest substantive landing (rev1000): `mxaudit` separates release-lane presence from current, internally consistent, complete, and passed evidence; the CLI, package metadata, core docstrings, and tutorial now describe the editor that exists. The next sequence is sustained dogfood, first-run/help clarity, executed publication evidence, and only then coordinator extraction under net deletion. See `docs/958-mission-product-reality-and-evidence-honesty-audit.md` and `REV1000_AUDIT.md`.

# Micromax

Micromax is a small concatenative language, replayable reference VM, and
headless-plus-curses editor host for capability-scoped end-user automation. The
language is the editor's configuration, macro, and plugin substrate; the editor
is the first proving ground for a reusable least-authority host.

## Heart of the mission

Build a calm editor people can trust and inhabit, with a scripting system they
can understand rather than merely enable. Tiny and inspectable are means, not
the finish line. The product order is:

1. **Trust:** boring startup, safe saves and discards, predictable plugins,
   bounded host work, useful failures, and complete journey tests.
2. **Taste:** clean defaults, disciplined highlights, clear hierarchy, and
   restrained polish.
3. **Flow:** quick project movement and low-friction search, edit, selection,
   multicursor, macro, and command loops.

The VM stays host-neutral. Filesystem, process, clipboard, persistence, network,
and UI effects belong to explicit host policy and capability checks. Micromax's
capability model is an in-process application boundary, not an operating-system
sandbox for hostile Python/native code, process compromise, or unbounded memory.

## Start here

Install the checkout into the active Python environment, then run the
reference curses editor with an optional file:

```bash
python -m pip install -e .
micromax-editor --tui
micromax-editor --tui path/to/file.txt
```

Use `Ctrl-G` for searchable help, `Ctrl-O` for the bounded project-file picker,
`Ctrl-B` to switch buffers, `Ctrl-F` to search, `Ctrl-S` to save, `Ctrl-Space`
for the command/action palette, and `Ctrl-E` for the command bar. The
line-oriented reference UI and compact headless contract remain available for
non-curses and machine consumers:

```bash
micromax-editor
micromax-editor --help-doc docs/70-tutorial.md --dump-screen 24 80
```

## Current product loop

- Startup always leaves a live active buffer. A failed requested open remains a
  visible failure; machine screen dumps return nonzero while still emitting
  inspectable fallback JSON.
- `new [NAME]` creates an empty untitled buffer. Repeated names become
  `*scratch-2*` or `name<2>`; creation never replaces a live buffer.
- `Ctrl-B`, `recentpick`, and `recentdirpick` select the most-recent useful
  other file on an empty query instead of defaulting to the active file.
- `Ctrl-O` opens one bounded project-file snapshot. Fresh-interpreter process
  construction and target readiness have separate finite leases; the configured
  scan timeout begins only after the worker target is ready to traverse. With no query it selects the
  most-recent other open project file first, then other readable open/recent
  members; `Ctrl-O`, `Enter` therefore toggles the last two files. Typing still
  searches the complete snapshot. A failed navigation accept leaves that picker
  open for correction. `Ctrl-E`, then `open PATH`, remains the deliberate
  arbitrary-path route.
- `Ctrl-S` saves, `Ctrl-Z`/`Ctrl-Y` undo/redo, `Ctrl-F` finds, `Ctrl-B` switches
  buffers, and `Ctrl-Space` opens the command/action palette.
- `find`, `findnext`, and `findprev` use one ordered set of non-empty,
  non-overlapping whole-buffer matches. Boundary crossing wraps explicitly to
  top or bottom; a sole match reports no movement. Literal work stays local.
  Every caller-authored regex is compiled and matched in a killable, bounded
  one-shot child. Literal and regex paths both retain one exact buffer-version
  snapshot, so navigation, `i/n` status, and visible projection do not rescan
  unchanged text.
- Interactive query-replace obtains one immutable source-generation match and
  capture-expansion plan before capture mode begins. Literal planning scans
  bounded overlapping windows over a shallow shared line tuple plus packed line
  starts; regex planning stages the same canonical windows once into a private
  exact-text file and sends only a validated path/byte/character descriptor to
  the existing killable worker. The editor process creates no complete joined
  regex source or full-source JSON body. The delayed match plan retains packed
  start/end cells and the narrowest replacement owner rather than one Python row
  graph per match. Later answers validate the exact buffer generation
  and local old text, advance through monotonic source coordinates, never rematch
  replacement-created text, and retain only accepted old/new slices for one
  atomic Undo row.
- Micromax syntax, primary and secondary selected text, and selected logical
  newlines are visible in both the compact headless screen contract and the
  reference TUI through one tested precedence.
- Repeated occurrence selection advances from live active-buffer selections.
  Typing, paste, newline, deletion, indentation, range hostcalls, and accepted
  query replacements apply all ranges against one pre-edit document and rebase
  every cursor. Ambiguous overlap fails before text, sidecars, undo, clipboard,
  or VM operands change. Ordinary one-cursor edits retain one direct splice;
  consecutive top-level one-character typing, Backspace, or Delete actions may
  replace the newest row with one exact bounded burst while time, geometry,
  versions, sidecars, authority, and action chronology remain continuous. The
  burst ends at 500 ms or 256 code points and at every command, movement,
  nesting, selection, multicursor, structural, or authority boundary. Immediate
  simultaneous edits plan directly against one canonical line-vector generation,
  reuse complete untouched line strings, publish one detached vector once, and
  retain one sparse old/new-slice group without complete source/result planning
  strings. Grouped replay validates every changed target before one commit, and stale replay keeps its
  history row. `ed.with-undo` and immediate macro replay capture
  text-free state shells and retain one detached tuple of canonical line strings
  only immediately before a pre-existing buffer's first actual mutation.
  Changed after generations share complete untouched string objects; success,
  rollback, Undo, and Redo need no complete document join under the measured
  fast-dirty path. Trusted aggregate history restore also announces itself to an
  enclosing first-write observer, so a macro beginning with Undo retains the
  true outer entry generation. Pure navigation replay owns no content vector and
  remains outside history. Delayed query-replace keeps one shallow immutable line
  generation plus packed line starts and one packed match-span plan, scans
  literal plans through bounded windows, and finalizes accepted work as one sparse
  source/final-coordinate witness; answers materialize only exact match slices and
  never the live complete document under fast-dirty operation. Sparse grouped Undo/Redo validates directly against the
  canonical line vector, reuses complete untouched line strings, and publishes
  one detached vector without complete history-owned current/result strings.
  History rows account logical retained UTF-8 content per buffer; `undobytes`
  applies a visible local soft limit at complete oldest-row boundaries, and
  `undostatus` reports current-buffer and total usage. Aggregate accounting does
  not claim to include pointer-vector, object, sidecar, native, or RSS overhead.
- `MoveLinesUp`/`MoveLinesDown`, `DuplicateLine`, and `CutLine` now use
  immutable source-line plans. Whole-line selection endpoints retain boundary
  meaning, ordinary cursors follow their source text, duplicate-line preserves
  columns, and cut-line removes every fully or partially selected row—or unique
  cursor rows when unselected—with one buffer witness and one undo/redo step.
- A failed explicit save retains a private durable checkpoint. An ordinary
  Unix/UTF-8 save shares one exact immutable payload across recovery, commit,
  writing, and clean-baseline hashing; DOS, other codecs, and normalization keep
  distinct representations. No-cleanup save takes no undo or full buffer-state
  snapshot, while cleanup rollback begins before its first mutation. On restart,
  `recoveries` lists bounded candidates, `recover` opens exact text in a dirty
  review buffer without touching disk, and `recoverdismiss` discards a record.
  Unresolved records remain visible as cached `[recovery:N]` status truth;
  repaint never scans the journal. Recovery-open into an existing clean buffer
  is one Undo/Redo decision over text, its generation signature, codec metadata,
  dirty provenance, and journal authority. A later save establishes the current
  clean baseline; `fastdirty` replay compares against that live baseline without
  joining the document, and history cannot resurrect a retired record. Changed targets still require
  `save!` or an explicit `saveas FILE` choice.
- In `--trust restricted`, plugin metadata is visible but code is inert.
  `plugin load NAME` approves an exact bounded package snapshot and activates it
  when unloaded. For a loaded plugin it approves a replacement without changing
  the live generation; `plugin reload NAME` is the explicit commit. Running
  callbacks use committed snapshot bytes even if disk changes. `plugin unload`
  is graceful and may run `deinit`; `plugin revoke` skips plugin lifecycle code
  and removes managed runtime before marking the grant revoked.
- Plugin source, lifecycle, graceful unload, commands, keys, timers, hooks,
  prompt-origin work, and macro replay enter one fresh host-owned VM step
  budget. Guest `set-budget` cannot clear it, and failed callbacks retain
  rollback/recovery behavior. When rollback removes a plugin's transient message,
  the command boundary supplies one generic failure instead of leaving an older
  success message visible; specific surviving failures are never duplicated.
- Capability-approved `ed.open-url` no longer calls the platform browser
  controller on the editor/plugin thread. One isolated Python child owns
  browser discovery and any text-mode wait under a finite deadline and bounded
  diagnostics. Shared argv/shell completion also releases descendants retaining
  Micromax capture pipes; fully stdio-detached external effects survive.
- One-shot filesystem, save, plugin-package, docs, project, and compatibility-regex workers defer Process construction/start to one finite owner, then publish exactly one bounded frame over a private socket. At most one unresolved start can survive a caller deadline; the late starter owns child/channel cleanup. Header and body reads retain their separate absolute result deadline.
- Softwrap cursor, viewport, and inverse movement share one compact per-buffer visual-row index. Exact line-preserving edits refresh only changed rows, while fixed-width rendering computes boundaries arithmetically and materializes only visible fragments.
- Importable isolated workers prefer `spawn` over `forkserver`; this avoids forking from a server whose startup libraries created native threads. Spawn remains slower, but its Process constructor/start is now caller-finite through a separate startup deadline. Synchronous `subprocess.Popen` creation is a distinct residual boundary.
- Buffers with saved baselines of at least 1 MiB, or exact live generations that grow across 1 MiB, receive a visible local `fastdirty=true` policy: the crossing edit remains exact and later edits use a sticky dirty flag until save instead of hashing the whole document. `setlocal fastdirty false` restores exact undo-to-clean tracking. Exact current-generation signatures are reused at save only while their mutation witness remains valid.
- Micromax `Int` is now exactly a non-boolean signed-64-bit value at source, conversion, bytecode import/export/dispatch, predicates, and typed integer consumers. Arithmetic inspects operands first, commits only after overflow or zero checks, and preserves Micromax floor-division/remainder semantics for future Rust/Wasm ports.
- String hostcalls now preflight exact result geometry before allocation. A 300 MB replacement projection fails with a finite policy error and unchanged operands; join avoids an input-list copy and stops after a proven alias overrun. `to-str`, `.`, `.s`, and `s-format %s` share one bounded incremental renderer. These are result-amplification boundaries, not total heap or arbitrary native-call containment.
- Dirty `quit`, `close`, `closeall`, and `only` require an unchanged second
  request. Any edit or relevant target/context change refreshes the warning;
  force forms remain explicit.

## Try it

```bash
micromax
micromax-editor
micromax-editor path/to/file.txt
micromax-editor --tui path/to/file.txt
micromax-editor --trust restricted path/to/file.txt
micromax-editor --help-doc 00-vision --dump-screen 24 80
micromax-editor --help-doc 00-vision --dump-screen 24 80 --dump-screen-detail diagnostic
micromax-editor --dump-screen 24 80 | micromax-screen --check
```

The headless REPL uses `:q` for safe quit and `:q!` for explicit discard. Dirty
EOF does not silently count as confirmation: an interactive terminal returns to
the prompt, while exhausted non-interactive input exits with status 2.

## Development and evidence

```bash
make bootstrap
make timely
make timely-tests
make release-suite
make release-verify
make repro-release
make test
make doctor
make audit-metrics
make effect-contracts
python tools/mxcontext.py --check
```

`make test` delegates to the process-group-aware `tools/mxtest.py` runner.
The Makefile, shell entrypoint, mxtest, and doctor default common numerical
runtime pools to one native thread while preserving explicit overrides. A test
child is complete only after its confirmed process group is gone, so successful
leaders cannot leave forkservers, resource trackers, or grandchildren holding
command pipes open. Narrow runs can use
`make test PYTEST_ARGS='tests/test_name.py -q' TEST_TIMEOUT=300`.

`make timely` is bounded health evidence, not a complete full-suite claim.
Runtime or tooling changes invalidate prior release evidence. Only a complete,
current `make release-verify` manifest supports a full-suite statement.

`make repro-release` is the smaller publication lane: a hash-locked builder
acquires exact wheels, independently verifies them, bootstraps verified pip,
installs with package-index resolution disabled, captures one source, runs focused
trust checks, builds two identical wheels, probes the installed wheel, and builds
two receipt-bound archives. Tag/manual GitHub runs are configured to attest and
retain those exact outputs. The workflow has not been executed in this
cloudtainer, and the lane does not prove an OS sandbox, public release, consumer
verification, cross-platform equality, or universal reproducibility.

`tools/mxcontext.py` emits a curated working set rather than the whole datacube.
Historical living-doc bodies are preserved under `docs/history/`; exact
per-revision surfaces and guarantees live in `docs/revision-index.json`.

## Read in this order

1. `docs/00-vision.md` — mission, product order, and non-goals.
2. `docs/958-mission-product-reality-and-evidence-honesty-audit.md` — rev1000 diagnosis, online research, speculation, and staged correction.
3. `docs/01-llm-start-here.md` — compact current handoff and judgment rules.
4. `docs/70-tutorial.md` — start with the editor, then learn its automation language.
5. `docs/02-repo-map.md` — executable architecture and validation lanes.
6. `docs/security-boundaries.md` — actors, authority, mitigations, and residual risk.
7. `docs/40-roadmap.md` and `docs/41-decisions-log.md` — current outcomes and durable decisions.
8. `docs/43-worklist.md` and `TODO.md` — current executable work.
9. `docs/revision-index.json` — exact per-revision surfaces, guarantees, risks, and historical audit paths.
10. `docs/history/` — preserved superseded living guidance; use it as archaeology, not current direction.

Recent deep technical evidence remains indexed rather than duplicated here. Start
from the current mission and follow only the revision entries relevant to the
owner you are changing.

## Handoff archives

```bash
make revzip TAG=foobarnamesummaryhighlightcodename
make revzip-verify ZIP=Micromax-rev####-stamp-tag.zip
```

Each linked session artifact preserves:

```text
Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip
```
