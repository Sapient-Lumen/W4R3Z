# Repo map (rev1000)

Rev1000 changes project direction and evidence presentation rather than adding a runtime subsystem. The normal structural audit now distinguishes release-manifest presence from current source/test inventory, internal consistency, completeness, and pass state. First-contact surfaces describe the current editor product. The next sequence is sustained dogfood and first-run/help clarity, then executed publication evidence and only then coordinator extraction under a second-consumer plus net-deletion rule. See `docs/958-mission-product-reality-and-evidence-honesty-audit.md` and `REV1000_AUDIT.md`.

This is the compact executable map. Use `docs/revision-index.json` for the full
per-revision ledger and `docs/history/02-repo-map-through-rev0951.md` for the
previous chronology-heavy map.

## Product layers

- `src/micromax/` — parser/compiler/VM, dictionary, core words, bundled stdlib,
  resource limits, regex containment, REPL, and portability oracle.
- `src/micromax_editor/` — headless editor model, actions, commands, prompts,
  keymaps, persistence/recovery, compact screen contract, capabilities, plugin
  lifecycle, startup, and curses view. `selection.py` and `highlight.py` own the
  pure visible span projection consumed by `editor.py`, `screen_contract.py`,
  and `tui.py`.
- `plugins/` — bundled Micromax packages and manifests. `core` is a readable
  mirror/extension package, not a trusted-name hook.
- `portability/kernel_cases.json` — observable cross-implementation behavior.
- `tests/` — VM, editor, authority, plugin, package, CLI, and evidence contracts.
- `tools/` — context, audit, effect-contract, lint, doctor, timely, portability,
  release, aggregate-test, revision-archive, constructor-stall, and hot-path
  allocation evidence CLIs.
- `docs/` — living design/security/help contracts plus revision notes; compacted
  living-doc bodies are preserved under `docs/history/`.

## Current finite/sparse owners

- `src/micromax/subprocess_start.py` — one absolute synchronous-constructor lease, one unresolved gate, completion-time classification, and late cleanup handoff.
- `src/micromax/worker_process.py` and `src/micromax_editor/project_files.py` — one-shot framed result ownership plus an optional caller-bounded post-start seam; project scans alone use a one-byte target-ready gate before their traversal deadline.
- `src/micromax_editor/host_process.py` and `src/micromax/regex_runtime.py` — process-tree/capture and readiness consumers of that lease.
- `src/micromax_editor/viewport_math.py` — compact Fenwick line-prefix index plus sparse true-wordwrap line layouts.
- `src/micromax_editor/search.py`, `replace_plan.py`, `textpos.py`, and `simultaneous_edits.py` — packed/reused source coordinates and compact edit plans.
- `src/micromax_editor/buffer.py`, `simultaneous_edits.py`, `query_replace.py`, `undo.py`, `editor.py`, `actions_default.py`, and `micromax_bridge.py` — direct one-range splices with one shared same-line constructor, generation-local exact signatures, live-growth fast-dirty promotion, local sidecar rebasing, bounded typing rows, atomic sparse immediate/delayed groups, retained-text budgets, shared first-write aggregate line-vector generations for `ed.with-undo` and immediate macros, nested restore observation, and guarded replay.
- `tools/reproduce_subprocess_start_stall.py`, `tools/measure_hotpath_allocations.py`, `tools/measure_undo_retention.py`, `tools/measure_history_retention.py`, `tools/measure_simultaneous_history.py`, `tools/measure_first_write_transactions.py`, `tools/measure_macro_first_write.py`, `tools/measure_typing_history.py`, `tools/measure_qreplace_history.py`, `tools/measure_qreplace_source.py`, `tools/measure_qreplace_dense_plan.py`, `tools/measure_line_vector_replay.py`, `tools/measure_multirange_planning.py`, `tools/measure_dynamic_fastdirty_longline.py`, `tools/measure_single_payload_save.py`, `tools/measure_framed_recovery.py`, and `tools/measure_qreplace_regex_transport.py` — reproducible evidence, not runtime registries.

## Startup, exit, and default-key authority

`src/micromax_editor/startup.py:create_editor_runtime()` is the shared headless
CLI/TUI runtime bootstrap:

1. resolve trusted versus restricted workspace policy;
2. construct `Editor`;
3. install the complete product keymap as trusted host policy;
4. install editor hostcalls;
5. load plugins or scan them without evaluation;
6. load trusted user init when policy allows it;
7. refresh capabilities and optional persistence.

`startup.py:open_initial_buffer()` is the second shared boundary. It opens the
requested path/help target, returns a typed `InitialBufferResult`, and guarantees
a live active buffer after recoverable failure. CLI screen dumps can therefore
emit valid fallback JSON while still returning nonzero; TUI startup surfaces the
same failure in editor messages.

`__main__.py:run_headless_repl()` routes `:q`, `:q!`, and EOF through editor quit
policy rather than leaving the loop directly. Dirty non-interactive EOF is an
explicit status-2 failure; terminal EOF returns to the prompt without counting
as confirmation.

Key files:

- `default_keybindings.py` — immutable host-owned global, prompt,
  query-replace, and internal-confirmation defaults;
- `discard_guard.py` — one weak-identity/version/path/dirty witness shared by
  `quit`, `close`, `closeall`, and `only`;
- `editor.py` — minimal embed bootstrap, key resolution, delayed authority,
  discard-scope capture, and runtime reload;
- `plugins/core/init.mx` — exact public Micromax mirror; exact repeats are
  idempotent and do not take ownership;
- `binding_policy.py` / `runtime_policy.py` — protected read/replay/mutation
  decisions;
- `tests/test_editor_default_keybindings_core.py` — parity and physical product
  journeys;
- `tests/test_editor_startup_discard_trust.py` — fallback, process-status,
  state-bound discard, EOF, trusted, and restricted journeys.

A bare `Editor()` intentionally keeps only the small internal modal bootstrap.
Embedders opt into the full product map before loading plugins.

## Restricted plugin source authority

`PluginManager.scan_tree()` exposes contained metadata without evaluating plugin
source. Interactive `plugin load` asks `plugin_package.py` to capture one bounded
immutable `PluginPackageSnapshot`. `plugin_meta.parse_plugin_meta()` validates
metadata and entry existence against those bytes, and initial evaluation receives
the same object.

A loaded `Plugin` record is the committed generation: object identity, root,
generation, digest, file count, and snapshot travel with deferred registrations.
`vm_load_policy.read_policy()` resolves package-local `include`/`require` from the
snapshot. Ordinary callbacks therefore perform no live plugin-tree traversal,
hashing, or worker creation. The source authorizer is an in-memory check over the
currently advertised plugin object, active grant state, and approved snapshot.

For an already loaded plugin, `plugin load` creates a pending replacement
approval without changing the live generation. `plugin reload` explicitly checks
live disk against that approval and stages/commits the retained snapshot.
`plugin unload` is graceful and may run `deinit`; `plugin revoke` skips lifecycle
code, transactionally removes managed runtime, and then revokes the grant.

Focused owners:

- `src/micromax_editor/plugin_package.py` — bounded exact package bytes and worker result;
- `src/micromax_editor/plugin_meta.py` — pure metadata validation;
- `src/micromax_editor/plugins.py` — grants, generations, reload, cleanup, retention;
- `src/micromax_editor/vm_load_policy.py` — snapshot source reads;
- `src/micromax_editor/editor.py` / `plugin_commands.py` — visible transitions;
- `tests/test_restricted_plugin_journey.py`;
- `tests/test_plugin_package_snapshots.py`;
- `tests/test_editor_plugin_manual_load_grants.py`.

## Plugin namespace and host-surface contract

`PluginManager.plugin_execution_search_order()` plans one deterministic readable
world: the plugin, direct dependencies in manifest order, breadth-first
transitive dependencies, then Forth. `plugin_load_root_context()` installs that
world for source, lifecycle, and delayed callbacks. `WordlistAccessScope` in the
host-neutral VM allows reads from the world, writes only to the plugin wordlist,
and denies wordlist/module creation. Core namespace words preflight useful
errors; `VM._add_word()` and owned deferred mutation are the final fail-closed
checks.

`plugin_contract.py` keeps the compatibility promise deliberately smaller than
the trusted Python bridge. Product-proven lifecycle/hostcalls are stable, the
rest are experimental by default, and exact statusline/prompt/screen models are
internal: plugin feature probes omit them and plugin calls are denied, while the
headless/TUI host continues to use them.

Focused owners and evidence:

- `src/micromax/vm.py` / `core.py` — wordlist scope, dictionary ownership, and namespace primitives;
- `src/micromax_editor/plugins.py` — dependency closure and source/lifecycle order;
- `src/micromax_editor/editor.py` — retained callback restoration;
- `src/micromax_editor/plugin_contract.py` — stable/experimental/internal policy;
- `tests/test_plugin_surface_contract.py` — import, write, disclosure, model, rollback, and callback regressions.

## Plugin execution fuel

`src/micromax/vm.py` separates script-visible budget state from embedding-owned
host frames. `VM.eval(step_budget=...)` enters `host_step_budget()`; guest
`set-budget` and `with-budget` cannot clear or enlarge that frame, and nested host
frames all consume the caller's remaining steps. `set-budget` now owns only a
persistent script base, so it no longer destroys an enclosing `with-budget`.

`src/micromax_editor/plugin_execution_budget.py` selects the finite embedding
default and restores script-budget state after every plugin turn.
`PluginManager._plugin_execution_context()` covers source and lifecycle;
`Editor.plugin_callback_context()` covers recognized live retained callbacks.
Commands, keys, timers, hooks, prompt-origin operations, and macro replay already
funnel through the latter via `run_script_origin_callback()`.

Primary evidence is `tests/test_plugin_execution_budget.py`, plus existing plugin
surface, reload, containment, runtime-group, prompt, macro, timer, hook, feature,
and smoke suites. This owner limits VM dispatch only. Known blocking filesystem,
process, and regex operations keep their separate deadline/worker owners; Python
hostcalls, native code, memory, and process faults remain outside fuel.

## String allocation and value-text boundary

`src/micromax/host_limits.py` owns fail-safe byte/cell normalization, shared
prospective/postcondition messages, and nonallocating UTF-8 accounting.
`host_strings.py` computes exact geometry for concatenate/split/join/replace
before allocation; join uses a bounded alias-size cache and no parts-list copy.
`value_text.py` incrementally renders the stable nested representation used by
`core.py` (`to-str`, `.`, `.s`) and `s-format %s`. `VM.value_text_max_bytes` is
the non-hostcall ceiling; ordinary hostcall results retain their existing
byte/cell ceiling and postcondition. `host_regex.py`, source loading, and editor
query preflight reuse the shared UTF-8 counter.

Primary evidence is `tests/test_string_preallocation_budget.py`,
`tests/test_value_text_budget.py`, `tests/test_string_hostcalls.py`,
`tests/test_hostcall_result_budget.py`, and the plugin amplification journey in
`tests/test_plugin_execution_budget.py`. The Linux address-space probe establishes
ordering only. Total heap retention, arbitrary native-call wall time, child
memory, crashes, and syscalls remain separate owners.

## Buffer creation and identity

`src/micromax_editor/buffer_names.py` is the pure naming owner:

- `BufferNameCollisionError` names exact-creation failure;
- `unique_buffer_name()` chooses the first bounded deterministic `name<N>` or
  `*name-N*` label without touching editor state.

`Editor.new_buffer()` is the strict insertion primitive. It rejects empty/live
names before cursor allocation, dictionary insertion, authority sidecars, MRU,
activation, or disk-signature work. `new_buffer_unique()` is the explicit
convenience lane used by file/help opens and human untitled creation.

`buffer_commands.py:c_new` and `actions_default.py:NewBuffer` route through
`Editor.create_untitled_buffer()`. Script context is denied until a finite
buffer-count/text/lifecycle capability exists. No shipped key is displaced.

`tests/test_editor_buffer_creation.py` pins no-clobber state, deterministic
naming, path-based file/help reuse, public feedback, authority, and registry
identity across abort/undo/redo. `mxaudit.buffer_creation` parses the `Editor`
AST. It inventories three single-key insertion owners, three direct deletion
owners, the guarded rename `pop()`, and one in-place bulk transaction restore.
Runtime replacement of public `buffers` or `marks` mappings is rejected; only
`__init__` may assign either registry object, and all mark restore paths must
clear/update in place.

## Query replace, whole-buffer search, and regex containment

`src/micromax_editor/query_replace.py` owns `QueryReplaceBufferWitness`, a weak
reference to the exact target `EditorBuffer` plus the monotonic `Buffer.version`
that authorized delayed coordinates. It also owns `QueryReplaceSourceSnapshot`:
one detached tuple that shares the exact immutable source line strings, one
read-only packed line-start vector, canonical cursor/offset projection, and
bounded exact range materialization. Names remain diagnostic; dead, replaced, or
generation-stale witnesses never authorize an edit.

`src/micromax_editor/replace_plan.py` owns side-effect-free bounded planning and
`ReplacementEdits`, the read-only delayed-plan owner. Literal query-replace scans
fixed canonical offset windows with at most `len(search) - 1` overlap, preserving
flat-source Unicode, case-folding, non-overlap, start-offset, and match-budget
semantics without retaining or constructing a complete joined source. Match
start/end coordinates are published in one interleaved `array('Q')`; literal and
uniform regex plans retain one shared replacement value, while varying capture
expansions retain only their exact value references. Indexing projects the same
concrete `ReplacementEdit` rows existing consumers expect. Every non-literal plan
still asks the isolated worker for concrete rows once. Canonical bounded source
chunks stage in one private exact-text file, the request carries only a strict
descriptor, and the child validates and decodes that file before applying the
existing regex ceilings. Interactive query-replace
walks the immutable source-generation plan monotonically with one mapped
cursor/offset boundary and validates identity, generation, source/final
coordinates, and exact local old text before every accepted edit. The completed
plan shares across plugin/runtime deep-copy snapshots; mutable session and
rollback state remain separately owned. Exceptional stale history authenticates
ownership by replaying and comparing line vectors, not joined documents.
Accepted rows retain exact old/new slices and finalize as one sparse atomic
`SimultaneousEditWitness`.

`src/micromax_editor/search.py` owns one ordered non-empty, non-overlapping span
set in original source offsets, exact buffer/version/query/policy snapshots,
forward/backward wrap resolution, `i/n` lookup, and bisected viewport projection.
Its public `PackedOffsets` coordinate sequence is implemented once in
`src/micromax_editor/textpos.py` and shared with query-replace.
Literal work remains local. Every caller-authored regex scan routes through
`src/micromax/regex_runtime.py`, which owns flat-string and file-backed request
construction, shared execution policy, the bounded ready handshake, separate
startup/request deadlines, the central memory-headroom default, result decoding,
and teardown. Query-replace uses the file-backed line-vector path; VM/search
callers that already own a flat string keep the ordinary API.
`src/micromax/regex_worker_child.py` is a directly executed `python -I -S`
stdlib-only child that validates the regular file and exact descriptor counts, materializes
the one `str` required by Python `re`, installs Linux post-source `RLIMIT_AS`,
and owns pattern compilation, match/replacement execution, and allocation-free
substitution preflight. Deep parser recursion and memory exhaustion return stable
operation failures instead of escaping the foreground.

`Editor.find()` scans a candidate before committing active-search authority. A
failed candidate leaves prior query/provenance/cursor/replay truth unchanged.
Literal and worker-routed regex results now share one exact active
`SearchSnapshot` lease keyed by buffer identity/version, query, literal/case
policy, timeout, and match budget. Navigation, status, highlight, and screen
projection reuse that immutable set until any witness changes; this is not a
persistent/background index. The historical `search_match_spans()` rendering
helper remains best-effort and non-throwing, while command/navigation paths
expose exact worker errors through `SearchSnapshot`.

The VM hostcalls in `src/micromax/host_regex.py` preflight stack shape and byte
budgets locally. With a finite positive timeout, compilation and execution both
occur in the child; only an explicit finite nonpositive timeout selects the
legacy local-engine embedding escape hatch. `src/micromax/worker_process.py`
owns shared multiprocessing terminate/join/kill cleanup used by regex adapters
and editor filesystem workers.

Primary evidence is `tests/test_rev0999_file_backed_regex_transport.py`,
`tests/test_rev0998_packed_qreplace_plan.py`,
`tests/test_rev0997_qreplace_source_snapshot.py`, `tests/test_regex_containment.py`,
and the search-navigation, interaction, history, editor-core, and query-replace
suites. The current transport witness is
`.artifacts/rev0999-regex-transport.json`; the packed-plan and shallow-source
witnesses remain `.artifacts/rev0998-qreplace-dense-plan.json` and
`.artifacts/rev0997-qreplace-source.json`. Design, measurement, primary-source
research, rejected abstraction, and residuals are in
`docs/957-file-backed-regex-query-replace-transport-audit.md`,
`docs/956-packed-query-replace-plan-audit.md`, and
`docs/955-segmented-query-replace-shallow-source-audit.md`. The installed
lifecycle contract remains `docs/100-query-replace.md`; prior timeout/search and
worker-memory analysis remains in
`docs/926-regex-fastchild-search-replace-containment.md` and
`docs/932-regex-worker-address-space-headroom.md`.

## Multi-location editing and macro transaction

`src/micromax_editor/simultaneous_edits.py` is the pure geometry and line-vector construction owner. Both planners index one immutable source generation, coalesce exact duplicates, reject ambiguous overlap, derive source/result offsets, and map original positions with explicit affinity. The product planner builds a detached canonical line vector; the flat planner remains the differential oracle.

`Editor._apply_simultaneous_buffer_edits()` owns pure editor application: it validates cursor owners, uses one witnessed local replacement for every one-range operation, maps those sidecars through local line/column geometry, and sends genuine multi-range operations through `plan_simultaneous_edits_lines()`. The multi-range path snapshots source strings by reference, retains compact source/result line starts, publishes one `Buffer.replace_lines()` mutation, and never needs a complete source or result document string.
`Editor._apply_undoable_simultaneous_buffer_edits()` owns history selection: one
direct `BufferSplice`, one sparse `SimultaneousEditWitness`, or a delayed
query-replace owner that emits the same sparse witness shape at finalization.
`actions_default.py` and `micromax_bridge.py` construct intent and share this
seam rather than owning competing coordinate or snapshot algorithms.

`Buffer.replace_range()` is a one-touch line-vector splice. Buffer input normalizes CRLF/CR to LF while preserving other Unicode separators as data. `LineVectorSimultaneousEditPlan` compares ranges in place, captures exact old text only for changed ranges when history needs it, and reuses complete untouched source strings. Equal replacements remain sidecar-only and suppressed aggregate steps do not allocate per-action old slices they will discard. `SimultaneousEditWitness` replay validates every target before one text commit, including adjacent deletes whose inverse insertions share an offset.
Query-replace keeps one shallow immutable line tuple plus packed starts as its
planning oracle; literal scans materialize bounded windows, delayed navigation
materializes only exact match slices, and exceptional stale authentication
replays line vectors. Accepted history retains only sparse source/final slices
plus sidecars. The shared first-write aggregate owner instead captures a text-free
editor shell and installs transaction-local pre-mutation observers that retain
one shallow canonical line-vector tuple only for touched pre-existing buffers.
The observers continue only to distinguish one mutation boundary from several,
with a saturated count that guards exact `BufferChange` accounting. Finalization
retains changed after tuples; trusted rollback/Undo/Redo restoration announces
itself to any enclosing observer before replacing the live vector. `ed.with-undo`
and immediate macro replay use that owner with separate change predicates and
user-visible policy.

`src/micromax_editor/line_edits.py` owns specialized source-line transforms that
cannot be expressed as ordinary character-range replacements without losing
line identity. Immutable move, duplicate, and delete plans produce both the
output line vector and coordinate projection from one pre-edit snapshot.
`actions_default.py` supplies the one semantic bit absent from raw `(line, col)`:
whether `(end + 1, 0)` is a half-open trailing whole-line selection boundary or
the first character of a displaced neighboring line. It then installs text through
`Buffer.replace_lines()` before projecting cursors and anchors. `CutLine` deletes every
fully or partially selected row (or unique cursor rows when unselected) and
therefore scales by planned rows rather than repeated whole-document dirty hashes. Primary
evidence is `tests/test_line_edit_geometry.py` and the existing editor-core,
clipboard, selection, undo, transaction, and visible-selection suites.

Immediate macro replay uses the same first-write line-vector journal as
`ed.with-undo`: one detached before tuple is retained immediately before each
touched pre-existing buffer's first write, changed after tuples share untouched
string objects, and navigation-only playback retains no content vector or undo
row. Failure/finalization restore exact multi-buffer content, sidecars/registers,
history, input, and macro runtime flags. A macro beginning with Undo now crosses
the same mutation seam before trusted line-vector restore, so the outer aggregate
captures its true entry generation. The eager joined-text path remains executable
only as a differential oracle in tests and the two measurement tools. Built-in
action-only macros may suppress nested recording, but rollback waits until the
local suppression guard unwinds. Commands, extension actions, and Undo/Redo
macros retain exact-history execution. Live query-replace keeps its delayed owner
and sparse accepted history. External effects remain outside both rollback
contracts.

## Language and host boundary

- `src/micromax/vm.py` — executable language semantics and step accounting.
- `core.py` / `core_registry.py` — core vocabulary installation.
- `stdlib_resource.py` — bounded package-resource stdlib loading.
- `host_limits.py` / `host_regex.py` — shared result/input budgets and VM
  regex preflight/routing; `regex_runtime.py` and `regex_worker_child.py` own the
  one-shot compile/match/expansion containment boundary.
- `micromax_bridge.py` — VM/editor hostcall installation; important but still
  large.
- `capabilities.py` — advertised host features and option gates.
- `hostcall_boundary.py`, `hostcall_transactions.py`, `file_access.py`,
  `fs_hostcalls.py`, and `host_process.py` — argument-preserving denials,
  contained files, receive-before-reap worker IPC, finite timeout normalization,
  exact Linux capture-pipe cleanup, process-tree teardown, and effect helpers.
- `open_url_process.py` / `open_url_child.py` — the product-default bounded
  browser-controller child; `Editor._open_url_fn` remains only an explicit
  test/embedder override.
- `effect_contracts.py` — generated high-risk effect/resource rows rendered into
  installed help at `docs/33-effect-resource-contract.md`.

The VM does not own ambient filesystem, process, clipboard, persistence, network,
or UI authority. The host explicitly supplies those effects.

## Project roots and project-file picker

`src/micromax_editor/project_files.py` is the read-only project/filesystem owner:

- `ProjectRootLocator` batches marker stats, bounds parent depth and marker rows,
  and keeps a short-lived cache used by recent-file grouping and the picker;
- `ProjectFileScanLimits` defines finite file, directory, depth, observed-entry,
  relative-path-byte, and wall-clock budgets;
- `scan_project_files()` creates one immutable deterministic snapshot, never
  intentionally follows symlinks, and returns typed timeout/error/truncation
  state;
- new recursive workers use `isolated_filesystem_worker_context()` and receive
  one complete bounded private frame before reap/teardown.

`src/micromax_editor/project_picker.py` is the pure presentation planner: it intersects bounded open/recent context with snapshot membership, caps promotion, removes duplicates, preserves complete-inventory query ranking, and supplies the shared section labels used by headless status, section jumps, and the TUI.

`Editor` remains the interaction and authority coordinator:

1. choose the nearest marker root, active-buffer parent, cwd, or script
   `cap.fs-root`;
2. require `cap.fs-list` for script-owned creation;
3. capture one snapshot plus readable active/MRU/recent decorations into `Prompt`;
4. map only candidate working-set paths lexically and intersect exact inventory
   members without canonicalizing the whole snapshot;
5. filter/group that immutable generation in memory while the user types;
6. require `cap.fs-open` for script-owned submission; and
7. re-resolve, contain, reject symlink/type changes, stat, and open.

`Ctrl-O` invokes `FilePicker`; `filepick [QUERY]` invokes the same path. The
empty picker selects the previous readable project file. A failed accept retains
the same prompt generation while every retry reruns step 6/7 checks. Arbitrary
path opening remains explicit through `open PATH` in the command bar.

## Headless editor core

- `editor.py` — current coordinator and most mutable editor state; treat audit
  metrics as the source of truth for size/method counts.
- `buffer.py` — text, cursors, selections, monotonic versions, exact
  `BufferChange` line-splice witnesses, one shared same-line splice constructor,
  generation-local exact signatures, and live-growth automatic fast-dirty; the
  pre-text-mutation observer invalidates signature truth before raw compatibility
  writes, while `touch_external()` remains required for unsupported unobserved
  mutation and conservative derived-state rebuild.
- `viewport_math.py` — reference wrapping plus compact `VisualRowIndex` prefix/
  inverse geometry; fixed-width counts and starts are arithmetic while true
  wordwrap remains sequential for the current logical line.
- `buffer_names.py` — strict collision error and bounded pure display-name
  disambiguation.
- `commands.py`, `command_dispatcher.py`, `binding_commands.py` — dynamic action
  and command surfaces.
- `keymap.py` — binding storage, modes, action-chain parsing, and provenance.
- `commandbar.py` — prompt state, cursor/history/suggestion mechanics, and
  snapshot fields.
- `prompt_suggestions.py` / `prompt_refresh.py` — reusable picker models plus
  preferred/avoided initial selection that does not rewrite provider ranking.
- `docs_cues.py` — headless markdown/help cue model; still a large extraction
  candidate.
- `options.py` / `option_policy.py` — global and buffer-local configuration plus
  script read/write policy.

The product discipline is headless-first: behavior and failure truth must be
testable without curses.

## Plugin trust and lifecycle

- `workspace_trust.py` — trusted/restricted automatic evaluation policy.
- `resource_roots.py` — installed-resource versus caller/cwd plugin roots.
- `plugins.py` — discovery, load, staged reload, unload, grants, cleanup, and
  diagnostics.
- `plugin_grants.py` — session grants, package fingerprints, freshness, and
  revocation.
- `plugin_runtime.py` — broad registration snapshots plus narrower group and
  generation rollback/cleanup seams.
- `runtime_policy.py` — same-origin mutation rules for delayed registrations.

Plugins run in-process. Restricted mode controls automatic evaluation and grants;
rev0972 also constrains executable namespace imports and internal host models,
but neither contains malicious loaded Python/native behavior. Delayed objects
preserve origin so a later user action does not launder plugin authority.

Continue lifecycle/owner work only for demonstrated stale authority, retained
disclosure, rollback failure, or resource exhaustion—not registry completeness.

## Trust, persistence, and file safety

- `docs/security-boundaries.md` is the installed living threat model.
- `docs/32-capabilities.md` is the host capability contract.
- `startup.py` and `discard_guard.py` own live first-buffer recovery and exact
  destructive-confirmation evidence.
- `recovery_journal.py` owns private durable records, v1 compatibility, v2
  framed raw-tail publication, bounded full-payload and authority-only readers,
  inode-bound immediate commit authority, record/temp inventories, target
  classification, exact permission repair, selectors, cleanup, and retirement.
- `save_residue.py` owns v3 save leases and conservative boot/PID-namespace/PID/
  start-time creator classification; unavailable proof remains unknown.
- `recovery_commands.py` exposes interactive-only list/open/dismiss, `recovermode`,
  `recovertemps`, and one-row `recoverclean` behavior; payload inventory never
  opens private temp bytes.
- `editor.py:_save_buffer` owns atomic plan → checkpoint → durable document commit
  → exact verification → cleanup order and preserves concrete symlink authority.
  Ordinary Unix/UTF-8 no-cleanup save uses one immutable payload for recovery,
  commit, writing, and clean-baseline hashing; normalization, DOS, and other
  codecs remain distinct. Undo/full-state snapshots exist only around a real
  cleanup mutation, whose rollback authority starts before `set_text()`.
- `buffer.py:canonical_utf8_signature()` hashes an already-owned strict canonical
  payload without another join/encode; callers without that exact proof retain
  the normal live-text signature path.
- `file_write.py` remains the one document writer, creates private payload temps,
  consumes pinned mode plans, and returns authority/durability witnesses; recovery
  continues only the narrow post-commit permission transaction.
- `file_access.py`, open/save paths, project scans, and persistence helpers carry
  containment, byte/row/time budgets, atomic-write policy, freshness checks, and
  visible failure behavior.
- Recent files, prompt history, saved cursors, cleanup diagnostics, recovery
  records, and related durable state require explicit persistence policy.

## Headless contract and bounded workers

- `screen_budget.py` owns public geometry, JSON byte/depth, cue/tag/token, and interoperable-integer limits.
- `screen_contract.py` projects the internal diagnostic graph into closed versioned `micromax.screen.v1`, normalizes public tokens/text, and refuses self-invalid source coordinates.
- `screen_consumer.py` is the independent stdlib receiving side and `micromax-screen` CLI; it owns strict JSON decoding, dynamic cursor/row/source/cue invariants, and terminal-safe escaped human text/error projections.
- `schemas/micromax-screen-v1.schema.json` is the packaged Draft 2020-12 structural schema; `tests/fixtures/screen-v1/blank-4x16.json` is the exact golden.
- `__main__.py --dump-screen` emits compact output by default and preflights dimensions before startup; `--dump-screen-detail diagnostic` exposes the full graph explicitly under the same public geometry budget.
- `micromax.worker_process` owns per-operation multiprocessing context choice,
  finite timeout normalization, and one-shot result framing. Importable workers
  prefer `spawn` after the cloudtainer exposed a forkserver with native startup
  threads; `forkserver` remains fallback, not a claimed safe persistent server. Its private
  `socketpair` channel incrementally receives one magic/length/pickle frame under
  an absolute deadline, checks serialized size before payload growth, closes the
  parent writer after start, and owns reap/terminate/kill/endpoint cleanup.
- Filesystem observation, file-write control, plugin package capture, docs/project
  scans, and compatibility regex workers all route through that owner; no affected
  product module directly calls `Queue.get()` or `Pipe.recv()` for terminal results.
- `micromax_editor.worker_process` is a compatibility re-export; worker users
  must not fork their own transport or lifecycle policy copy.
- `buffer.py` owns exact LF/unicode dirty signatures, bounded UTF-8 hashing,
  versions, and line-splice witnesses; `Editor.new_buffer()` installs the existing
  local `fastdirty` option at the 1 MiB saved-baseline threshold so the
  performance/accuracy choice is visible.
- `editor.py` retains one exact active search snapshot and one per-buffer compact
  visual-row index. Unchanged repaint/movement reuse witnessed facts; ordinary
  small same-line-count edits refresh affected row counts; structural, missed,
  large, or unknown edits rebuild safely.

## Context and documentation

`tools/mxcontext.py` emits a curated working set, not a file manifest. It combines
stable entrypoints with docs from the newest revision-index entries and reports
full source/docs/test counts.

`src/micromax_editor/docs_index.py` owns bounded docs catalog extraction. Leading
revision-banner paragraphs are provenance and are skipped when choosing picker,
completion, and help summaries; the first durable subject line remains visible.

- `docs/revision-index.json` — authoritative structured revision history.
- `docs/installed-help-manifest.txt` — runtime help membership.
- `docs/33-effect-resource-contract.md` — generated installed effect facts.
- `docs/957-file-backed-regex-query-replace-transport-audit.md`, `REV0999_AUDIT.md`, and `.artifacts/rev0999-regex-transport.json` — current file-backed regex query-replace source transport, strict descriptor validation, parent/process-tree measurement, research, audit, and residuals.
- `docs/956-packed-query-replace-plan-audit.md`, `REV0998_AUDIT.md`, and `.artifacts/rev0998-qreplace-dense-plan.json` — packed dense plan, uniform-value sharing, immutable snapshot sharing, research, measurement, audit, and residuals.
- `docs/955-segmented-query-replace-shallow-source-audit.md`, `REV0997_AUDIT.md`, and `.artifacts/rev0997-qreplace-source.json` — shallow delayed source, segmented literal planning, shared packed line starts, line-vector stale authentication, research, measurement, and residuals.
- `docs/953-framed-raw-tail-recovery-audit.md`, `REV0996_AUDIT.md`, and `.artifacts/rev0996-framed-recovery-record.json` — current recovery frame, bounded authority reads, publication-race repair, research, measurement, and residuals.
- `docs/954-byte-locked-release-builder-hosted-provenance-audit.md` — exact builder-wheel authority, bounded verifier/bootstrap, source-bound receipt, hosted privilege split, retained attested subjects, research, and residuals.
- `docs/952-single-payload-save-clean-baseline-audit.md`, `REV0995_AUDIT.md`, and `.artifacts/rev0995-single-payload-save.json` — current one-payload save, cleanup rollback, complete huge-line journey, research, measurement, and residuals.
- `docs/951-dynamic-fastdirty-growth-single-pass-longline-audit.md` and `REV0994_AUDIT.md` — live-generation dirty policy, signature-cache ownership, one-line construction, and residuals.
- `docs/950-sustained-use-recovery-attention-command-failure-audit.md` and `REV0993_AUDIT.md` — sustained-loop recovery visibility, atomic authority history, command-failure truth, research, evidence, and residuals.
- `docs/949-aggregate-line-vector-transactions-audit.md` plus the two rev0992 artifacts — aggregate content-generation foundation, nested history repair, measurement, research, and residuals.
- `docs/944-macro-first-write-replay-transaction.md` and `docs/943-first-write-with-undo-transaction-journal.md` — preceding first-write owner designs and eager-reference evidence.
- `.artifacts/rev0987-macro-first-write.json` and `.artifacts/rev0986-first-write-transactions.json` — preceding joined-text first-write witnesses.
- `docs/942-atomic-sparse-simultaneous-history.md` and `.artifacts/rev0985-simultaneous-history.json` — preceding compact simultaneous-history design and measurement.
- `docs/history/` — preserved bodies removed from living contracts.

The living handoff is `README.md`, `TODO.md`, `docs/00-vision.md`,
`docs/01-llm-start-here.md`, this map, `docs/43-worklist.md`, and
`docs/security-boundaries.md`.

## Reproducible release lane

`release/requirements-builder.txt` is the single deliberately narrow builder lock:
seven exact Python 3.13.14 wheel projects, each authorized by SHA-256.
`tools/mxrelease.py` rejects alternate lock grammar, markers, URLs, extras,
editable/VCS rows, missing or duplicate hashes/projects, extra lock files,
undeclared runtime dependencies, and disagreement with the declared release
policy. The lock, builder, workflow, and package-policy files are themselves
source-digested release inputs.

`tools/mxbuilder.py` lets ambient pip perform acquisition only with exact hashes,
binary-only rows, and no dependency resolution. It then independently reopens
every wheel from a stable regular inode and verifies exact filename set, digest,
project/version metadata, safe member paths, duplicate case-fold aliases,
encryption, compression, regular-file kinds, member counts, member sizes, total
expanded size, and bounded `METADATA`. One verified pip wheel is safely extracted
into a pip-less virtual environment; the remaining verified wheelhouse is
installed with `--no-index`, `--find-links`, `--require-hashes`,
`--only-binary=:all:`, and `--no-deps`. The wheelhouse is rehashed afterward and
the exact installed set must equal the lock.

A self-digested builder receipt records the source lock, interpreter, exact wheel
names/sizes/hashes/projects/versions, installed versions, verifier ceilings, and
the implemented acquisition/bootstrap/install boundary. The release child gets
the receipt path and digest through a sanitized environment. `tools/mxrepro.py`
validates that binding before it captures the declared archive-member bytes once,
generates/checks context once, runs the focused release gates, materializes
separate wheel-A/wheel-B and archive-A/archive-B trees, verifies byte equality,
installs the selected wheel outside the source tree, probes imports/resources,
and seals the source and builder receipts. `tools/mkrevzip.py` owns deterministic
archive metadata, safe member policy, source/receipt schemas, and exact archive
verification. `tools/mxtoolrun.py` remains the finite child/process-tree owner.

```bash
make repro-release
```

The Make target uses a fresh private builder work tree so a completed or failed
attempt does not poison a retry; final output publication still refuses overwrite.
Package-index resolution is disabled after acquisition, but no OS network,
process, filesystem, or same-UID adversary sandbox is claimed.

`.github/workflows/reproducible-release.yml` separates authority by event. Pull
requests and ordinary non-tag pushes run the same reproducible target with only
`contents: read`. Tag pushes and manual dispatch alone receive `id-token: write`,
`attestations: write`, and `artifact-metadata: write`; they attest the exact two
wheel outputs, release receipt, run receipt, and revision ZIP, then upload those
same explicit files as a 30-day artifact with hidden-path opt-in and
failure-on-missing. Checkout credentials are not persisted. Checkout,
setup-python, attest, and upload-artifact are pinned to reviewed full commits.

This is a configured, hash-locked same-platform lane. The cloudtainer interpreter
is Python 3.13.5 rather than the required 3.13.14, and local package-index DNS was
unavailable, so no end-to-end builder receipt, hosted run, attestation, retained
artifact, public release, consumer verification, locked runner image, or
Windows/macOS receipt is claimed.

## Structural audit lane

`tools/mxaudit.py` measures repository/editor/plugin/evidence structure and
hard-checks installed-help consistency, current revision entrypoints,
generated-contract freshness, editor startup/discard/query-replace boundaries,
cleanup guards, owner routes, finite budgets, queue-drain policy, timely-summary
honesty, and package-verifier evidence. `editor_trust` keeps ordinary
startup/exit invariants separate from plugin lifecycle; `buffer_creation` proves
no-clobber ordering/direct map ownership; the query-replace witness check pins
identity plus cleanup-time undo rollback; and the release checks pin strict
revision lineage, source snapshotting, mixed-generation refusal, atomic
publication, and a descriptive state row for every carried full-suite manifest.
That row reports current source/test inventory, internal consistency,
completeness, pass state, batch/file/test counts, digest, and issues. Partial or
stale evidence remains inspectable without becoming a release claim.

```bash
make audit-metrics
python tools/mxaudit.py --json --check
```

Large files, absent CI, and dependency-lock observations remain measurements
unless an executable policy says otherwise.

## Timely cloudtainer lane

`make timely` runs context, audit, lint, quiet portability, and fast doctor
checks. `.artifacts/mxtimely-summary.json` is incremental and
completion-honest: a stopped prefix is partial, not passed.

```bash
make timely
make timely-tests
```

## Aggregate evidence lane

Makefile defaults are the handoff contract:

```text
CHUNKS=64
MAX_NEW_TESTS=60
MAX_NEW_FILES=4
TEST_BATCH_SIZE=10
FILE_TIMEOUT=45
MAX_RUNTIME_SECONDS=18
TEST_MANIFEST=.artifacts/mxtest-all-64.json
TIMELY_MANIFEST=.artifacts/mxtimely-mxtest.json
RELEASE_MANIFEST=.artifacts/mxrelease-full-suite.json
RELEASE_MAX_RUNTIME_SECONDS=8
RELEASE_BATCH_TIMEOUT=20
RELEASE_BATCH_SIZE=12
RELEASE_MAX_NEW_BATCHES=0
TIMELY_TIMEOUT_SCALE=1
TEST_TIMEOUT=1800
```

The ordinary entrypoint is also bounded: `make test` routes pytest through `tools/mxtest.py`, which owns the child process group and tears it down on timeout or interrupt. Use `PYTEST_ARGS` for a narrow selector and `TEST_TIMEOUT` for the chunk deadline.

Run bounded resumable aggregate progress:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxtest.py \
  --run-chunks 64 \
  --strategy segment \
  --isolate-files \
  --resume \
  --checkpoint-tests \
  --max-new-tests 60 \
  --max-new-files 4 \
  --test-batch-size 10 \
  --file-timeout 45 \
  --max-runtime-seconds 18 \
  --json .artifacts/mxtest-all-64.json \
  --durations 0
```

Verify current combined evidence:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python tools/mxtest.py \
  --verify-current .artifacts/mxtest-all-64.json
```

The aliases are `make test-all-chunks` and `make test-verify-current`. Do not
infer completeness unless verification passes against the current source digest.

## Short-window full-suite release lane

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make release-suite
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make release-next
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src make release-verify
python tools/mxrelease.py --manifest .artifacts/mxrelease-full-suite.json --summary
```

`release-suite` may leave a clean partial checkpoint. Only `release-verify`
asserts a complete, passed, untimed-out, current full-suite manifest.

## Current risks and safe next cuts

- Product proof is the largest gap. The repository has exhaustive local trust
  evidence but no compact sustained-use ledger showing clean-install adoption,
  repeated project work, restricted startup, recovery, and non-author success.
- `Editor` remains a 32,000-line coordinator with 1,382 direct methods. A valid
  extraction needs a second real consumer, narrower authority, preserved
  journeys, and net deletion; wrappers, moves, and registries do not count.
- Docs/tests/audit/release machinery can become a second product. Prefer one
  durable contract plus a machine ledger, and follow historical notes only from
  `docs/revision-index.json`.
- The hosted exact-byte lane is configured, not executed and consumer-verified
  for this source. The short-window full-suite checkpoint is intentionally
  partial; `mxaudit` and `mxrelease` must keep its state explicit.
- Grapheme-cluster editing, terminal-cell width, filesystem/power-loss support,
  Windows/macOS process/release receipts, async-save generation ownership, and a
  compact stable extension world remain open.
- “Micromax” is an internal codename until a distinct searchable public name is
  supported by naming and legal review.
- The rev0999 regex transport, rev0996 recovery framing, exact sparse history,
  bounded workers, one-payload save, and headless product models are current
  trust foundations. Do not reopen them without a concrete product transcript.

Safe sequence: run five sustained dogfood sessions and ship at most three
product corrections; execute and independently verify the hosted release
subjects; then choose one coordinator extraction or compact extension-contract
cut under net deletion. Add a Wasm/process host, new text representation,
watcher, background index, async save, generic owner/transport registry, or
platform claim only from reproduced need and a smaller public contract.
