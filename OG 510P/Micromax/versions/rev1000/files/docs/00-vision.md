# Vision

Rev1000 makes a project-level correction rather than adding another runtime subsystem. Release evidence is now reported as presence, currency, consistency, completeness, and pass state instead of letting “the lane exists” stand in for a receipt. First-contact surfaces describe the current editor rather than a future prototype. The accompanying mission audit finds that Micromax's trust engineering is unusually strong while product adoption, taste, flow, public identity, and executed release evidence remain underproved. The next sequence is sustained dogfood and first-run clarity, then executed publication evidence and only then coordinator extraction under a second-consumer plus net-deletion rule.

## Mission

Micromax is a tiny, inspectable, Forth-inspired language and replayable virtual
machine in service of a calm, serious, scriptable editor.

Its native configuration, macro, and plugin system should make end-user
programmability powerful without quietly granting ambient host authority. The
editor is the proving ground: language semantics, host boundaries, provenance,
recovery, and resource limits matter because they must support daily work.

The shortest useful mission phrase is:

> a calm editor with explicit effects, visible provenance, recoverable failure,
> bounded host work, and headless truth

Tiny, portable, and clever are not sufficient outcomes. The editor must become
an instrument people choose to live in.

## Product order

1. **Trust.** Startup is boring; defaults work; open, save, undo, replace,
   recovery, and plugin failure are predictable; denials explain themselves;
   tests exercise complete user journeys.
2. **Taste.** Defaults show restraint and hierarchy. Syntax, selection, prompt,
   status, diagnostics, help, and inactive information share a coherent visual
   vocabulary rather than accumulated decoration.
3. **Flow.** Project movement is fast; repeated edit/search/replace/multicursor/
   macro loops have low friction; prompts and keymaps remove sharp edges.

Security machinery that breaks ordinary editing has failed the product. Polish
that hides unsafe behavior has failed trust. Features that expand surface area
without improving a lived loop are not progress.

## Language and VM commitments

Micromax keeps the compositional strengths of Forth without claiming Forth
standard conformance:

- a small vocabulary of named words and direct interaction;
- data-stack composition, wordlists, and explicit search order;
- deterministic reference semantics and a portability corpus;
- source spans, structured errors, quotations/combinators, and execution budgets
  suited to embedding;
- a tiny host-neutral core rather than ambient filesystem, process, network,
  clipboard, persistence, or UI access.

The Python VM is the semantic oracle for future ports. Another implementation
succeeds by preserving observable language and host-boundary contracts, not by
copying Python internals.

## Editor commitments

The editor grows headless-first. Buffer, cursor, selections, undo, actions,
keymaps, command bar, search, replace, multicursor, macros, project movement,
plugin lifecycle, and persistence must remain inspectable without curses.

The view consumes stable models rather than owning behavior. A feature is not
finished merely because it appears in the TUI; its headless journey, failure
messages, authority, rollback, and resource limits are part of the product.

Current trust examples show the desired shape:

- startup failure leaves a live buffer and an honest nonzero machine result;
- creation never replaces a live same-name buffer;
- dirty discard consent is bound to exact object/version/path/scope state;
- empty navigation pickers avoid the active-file no-op; project picking uses one finite immutable inventory with captured authority-filtered context, gives process construction, target readiness, and traversal/result separate finite boundaries, and retains the exact prompt after failed targets while every retry revalidates authority and filesystem truth;
- save recovery checkpoints exact editor text and atomic final-mode intent before
  commit, reopens changed work for review, and retains matching-byte witnesses
  until the permission transaction is synchronized or explicitly refused;
- new recovery checkpoints publish one versioned compact JSON authority header
  plus a raw payload tail; explicit load materializes exactly the bytes it must
  return, while listing, inspection, residue discovery, permission continuation,
  and restart commit stream integrity verification under bounded work;
- restricted plugin approval captures exact bytes, and approval, activation,
  graceful unload, and revoke are distinct visible transitions;
- query-replace answers apply only to the exact buffer generation and local
  source slice shown; accepted work becomes one sparse atomic history row, and an
  unrelated edit clears the interaction before using its transient selection;
- syntax and primary/secondary selections are visible through the same bounded
  viewport facts in both the compact contract and reference TUI;
- repeated find-next/find-previous wraps with explicit boundary feedback, while
  navigation, search count, visible highlighting, and screen projection share
  one exact buffer/version/query/policy match snapshot until source truth changes;
- softwrap movement and rendering share one compact versioned visual-row index;
  fixed wrapping is arithmetic, true wordwrap retains bounded sparse checkpoints
  with exact changed-line eviction, and only visible fragments are materialized;
- caller-authored regex compilation and matching run outside the editor thread
  under separate startup/request deadlines, and failed candidate searches leave
  prior query authority, cursor, and replay truth untouched;
- capability-approved browser launch runs outside the editor/plugin thread in a
  bounded one-shot child; lingering descendants that retain Micromax capture
  pipes are released on the proved Linux path, while fully detached work survives;
- bounded multiprocessing workers and synchronous Popen owners begin their
  timeout before process construction, permit one unresolved start per owner
  family, share absolute leases with readiness/execution, and keep late child,
  channel/pipe, and operation cleanup with the starter;
- plugin-callable string replacement, split, join, and concatenation reject exact
  oversized projections before allocation, while formatter/core value rendering
  stops incrementally and preserves denied operands;
- query-replace capture expansion is planned once against witnessed source text;
  later answers consume one packed immutable plan, validate old text, and never
  rematch accepted replacement output;
- repeated occurrence selection derives continuation from live active-buffer
  selections, while multi-location actions and hostcalls interpret all ranges in
  one immutable pre-edit document and fail before ambiguous overlap mutates state;
- ordinary one-cursor insert/delete/newline/tab/paste stores one exact inverse
  splice, while immediate simultaneous typing/deletion/paste/cut/range edits
  store one sparse old/new-slice group plus exact sidecars; all changed targets
  validate before one replay commit and stale failure preserves stack membership;
- `ed.with-undo` and immediate macro replay group visible work while retaining
  one detached canonical line-vector generation only at a touched buffer's first
  mutation; after generations share untouched immutable strings, navigation-only
  replay retains no content vector, and nested Undo/Redo announces its restore to
  the outer first-write observer. Delayed query-replace retains one shallow
  shared line generation, packed line starts, and packed match spans, while
  accepted history stays sparse
  and external effects remain outside rollback;
- release builder authority begins with exact locked wheel bytes that are
  independently checked before and after no-index installation; release tests,
  two wheel builds, the installed candidate, receipt, and two archives derive
  from one captured source generation and fail on drift; tag/manual hosted runs
  may attest and retain those exact subjects without granting signing authority
  to pull-request verification.

## Trust model

The VM has no ambient outside world. The editor host owns effects and exposes
only explicit hostcalls, options, actions, commands, and delayed registrations.
Capabilities are least-authority application policy. Provenance survives from
registration through later execution so a physical keypress cannot launder
plugin authority.

Trusted product defaults still make a usable editor. Restricted startup controls
automatic source evaluation and explicit approval; it is not a hostile-code
sandbox after arbitrary native or Python code is loaded.

Rollback claims stay narrow. Plugin transactions can restore managed editor
state, but they do not make arbitrary edits, durable writes, external effects,
memory use, or wall-clock work atomic unless a smaller contract proves it.

## Resource model

Every host-facing collection should answer four questions:

1. What input or root is authoritative?
2. What bounds traversal and materialization before a VM result budget applies?
3. What happens on timeout, partial observation, or malformed state?
4. Which authority owns creation, delayed use, and cleanup?

Project discovery, recovery inventory, regex workers, plugin snapshots,
string-result construction, typed integer execution, and external browser launch
now have concrete finite answers. New features should follow those examples
rather than rely on a generic result-size limit or instruction counter after
expensive host work has already begun.

## Architecture direction

Prefer small owners around coherent policy, not speculative subsystem rewrites.
`project_files.py` owns bounded discovery; `startup.py` owns first-buffer
recovery; `discard_guard.py` owns destructive confirmation evidence;
`recovery_journal.py` owns interrupted-save state; `plugin_package.py` owns exact
plugin package bytes; and `buffer_names.py` owns pure bounded name allocation.
`Editor` coordinates active-buffer context, prompts, messages, and effects.

Continue extraction only when it removes demonstrated coordinator gravity,
stale lifetime, retained authority, rollback risk, duplicated bounded-work logic,
or a real check/use gap. Generated contracts and compact living docs should
replace chronology where possible; history remains available through
`docs/revision-index.json` and `docs/history/`.

## What is still missing

- A declared supported-filesystem and sudden-power-loss matrix beyond the
  existing Linux/POSIX process-death evidence for the save/recovery protocol.
- Terminal-specific refinement of the now-complete small hierarchy: cursor
  shape/focus and palette quality still vary, but syntax, help, diagnostics,
  search, primary/secondary selection, prompt, and status have one executable
  80x24 contract.
- Terminal-cell and grapheme semantics for `micromax.screen.v1` row text, driven
  by a concrete cross-renderer consumer rather than speculative schema growth.
- An executed hosted builder receipt and artifact attestation, consumer-side
  verification, public release publication, and broader cross-platform wheel
  reproduction beyond the configured Ubuntu/Python lane. Exact wheel hashes and
  pip no-index installation do not lock the runner image or create an OS sandbox.
- Plugin instruction starvation, predictable string amplification, checked
  integer growth, opaque regex-native memory growth, browser-controller wait,
  and shared multiprocessing startup now have separate owners. Synchronous
  starter-thread creation, a permanently blocked constructor/late owner, cleanup
  callback liveness, and Windows process-tree ownership remain missing; any broader
  process/WebAssembly host should import the rev0972 reduced world rather than
  the trusted Python bridge.
- Navigation now has one repaired buffer/recent/project loop. Revisit it only
  from a new concrete transcript; do not add project search, result panes,
  watchers, or background symbols by anticipation.
- Caller-authored regex already runs in a one-shot child with Linux post-request
  address-space headroom. Its Popen constructor and readiness now share one
  startup deadline; a platform call that never returns can still retain the one
  daemon starter, and no ambient pool is implied.
- Repeated search, replacement geometry, simultaneous application/history, and
  true wordwrap now have exact sparse derived owners. Immediate multi-range
  planning/replay, aggregate content history, and delayed query-replace no longer
  retain complete parent document strings; dense plans no longer retain per-match
  Python row graphs, and regex worker requests no longer serialize the complete
  source. Measure O(lines) pointer/index generations, source-transfer failure, the
  broad non-text shell, and very-long-line behavior only from concrete journeys
  before considering a rope, piece table, or broader transport machinery.
- Query-replace content-version isolation only if a supported concurrent or
  out-of-band mutation path proves the exact-object witness insufficient.
- Stable immutable buffer identity only when persisted references, multi-view,
  rename, recovery, or plugin handles prove names carry too much weight.

## Non-goals for now

- hostile-code containment inside the Python process;
- a large language runtime, JIT, or ambient standard library;
- background indexing/watchers before bounded snapshots prove insufficient;
- broad theme/plugin APIs without a concrete renderer or journey that needs them;
- automatic public release publication before an executed, retained, and consumer-verified hosted run;
- owner registries or lifecycle abstractions added only for conceptual symmetry.

## Decision rule

Ask of each change:

> Does this make the editor more trustworthy, tasteful, or fluid without making
> the language, host boundary, or repository harder to inspect than the value it
> creates?

When the answer is unclear, prefer a complete headless journey and a smaller
reversible seam over a new doctrine layer.
