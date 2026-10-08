# Revision 0972 audit

## Priority judgment

Rev0971 explicitly left plugin imports and host models as the highest-risk unfinished boundary. The important defect was not the lack of a process or WebAssembly runtime. It was that the live in-process contract had no executable meaning: `plugin.json requires` controlled scheduling while source and callbacks inherited ambient wordlists; read visibility could become dictionary or deferred-behavior mutation; and exact renderer snapshots looked like extension API. Isolating that accidental surface would have made it harder to remove later.

Rev0972 therefore narrows authority where names are resolved and words are mutated, applies one rule to source, lifecycle, and retained callbacks, and makes a small host-surface classification enforceable. It does not add a registry mirror, worker, compatibility layer, or sandbox claim.

## Severe or wasteful findings

| Finding | Consequence | Correction |
|---|---|---|
| Plugin execution inherited the editor's ambient search order | An undeclared loaded sibling could satisfy source, lifecycle, command, key, timer, or hook lookup | Install one exact order for every plugin generation: self, declared dependency closure, then Forth |
| `requires` meant load order but not runtime imports | Metadata, review, and executable authority disagreed | Treat the loaded `requires` closure as the readable namespace contract |
| A plugin could name another module and use `use`, `in`, raw `set-current`, or `set-order` | Undeclared reads and cross-plugin definitions bypassed the apparent dependency boundary | Preflight namespace operations and keep only the executing plugin wordlist writable |
| Definition safety depended on every defining primitive remembering a check | A future primitive could change `CURRENT` and write through the boundary | Enforce writes again at `VM._add_word()`, the shared dictionary mutation point |
| A readable dependency's `defer` could be rebound through `is` or `defer!` | Importing behavior silently granted authority to replace it | Stamp every inserted word with its owning wordlist and require owner-write authority for deferred mutation |
| Plugins could create modules or anonymous wordlists | Namespace topology could become ambient state consumed by later code | Refuse the reachable module/wordlist creation words during explicit plugin execution |
| `hooks` enumerated hooks from all dictionaries | Undeclared sibling names leaked despite lookup restrictions | Filter hook inventory to the active readable closure |
| Source, lifecycle, and delayed callback paths each assembled execution state separately | One repaired path could leave another ambient or writable | Centralize dependency-order planning and pass one explicit identity/read/write scope through all paths |
| Exact prompt, statusline, screen, gutter, display, and viewport projections were advertised to plugin code | Extensions could couple to renderer internals and receive state an eventual narrow component host should not import | Hide those exact models from plugin feature probes and deny plugin-originated calls before stack consumption |
| Namespace context accepted identity and authority independently | A caller could appear scoped while omitting its real read/write sets | Reject partial scopes and unknown wordlist identifiers before mutating VM context |
| A first draft let dependency visibility imply deferred reassignment | The nominal read/write split still had a behavior-mutation hole | Audit mutation primitives separately from definition paths and cover both name-based and token-based rebinding |
| A first draft changed empty `previous` from a no-op into a dictionary-version touch | Unrelated standalone VM behavior would drift for no security value | Preserve the historical no-op while retaining scoped checks when an order exists |

## Trust review

The scope is installed only when the editor has an explicit plugin identity, immutable package root/generation, readable wordlist set, and writable wordlist set. Validation occurs before context mutation. On every success or failure, prior plugin identity, source authority, package snapshot, namespace scope, search order, current wordlist, and runtime group state are restored by the existing transaction owners.

Read order is deterministic breadth-first closure: the plugin itself, direct `requires` entries in manifest order, transitive dependencies level by level, then Forth. Direct imports therefore outrank implementation details of those imports. The transitive closure remains available because Micromax colon words resolve names dynamically; a dependency executing for a consumer must still resolve its own declared imports.

Dictionary visibility is not dictionary ownership. Namespace words reject undeclared reads and dependency writes before consuming stack operands where practical. `VM._add_word()` remains the final definition guard. Word ownership extends that rule to `is` and `defer!`, including execution tokens already passed on the stack. Failures leave those operands intact.

Internal presentation hostcalls remain registered for the trusted headless consumer and TUI. The denial is conditioned on explicit plugin execution identity, so normal host rendering and diagnostics retain the existing bridge. Plugin `host.feature?` and `host.features` report the reduced world, and exact calls fail before the call name or model arguments are removed.

This is not deep object isolation. A dependency may deliberately return a mutable cell, list, map, or other value; possession is an explicit object capability. Shared hook registration is also intentional and remains governed by provenance, generation, authority, and cleanup rules rather than dictionary ownership.

## Refactor and waste removed

- one dependency-closure/search-order planner instead of ambient-order surgery in source, lifecycle, and callback callers;
- one VM wordlist scope with a shared dictionary mutation guard instead of per-definition policy duplication;
- one small plugin host-surface policy instead of copying all 251 editor hostcall rows into a second registry;
- no process, Wasm runtime, IPC protocol, version-negotiation framework, capability manifest rewrite, background service, or new user option;
- no broad declaration that every current hostcall is stable;
- no recursive object freezer or membrane pretending to make in-process code hostile-safe;
- no loss of package-local include, immutable generation, rollback, reload, unload/revoke, delayed callback, runtime-group, or trusted renderer behavior.

## Research judgment

Official current documentation supports defining a narrow interface before choosing isolation machinery. Visual Studio Code separates stable and proposed APIs and runs extensions in extension hosts; the WebAssembly Component Model uses WIT worlds to name imports and exports; Zed packages Rust extensions into Wasm with constrained resources; and Wasmtime offers fuel, resource limiters, and call hooks. Those mechanisms are useful only after the imported world is intentional. Micromax adopts that interface lesson while keeping the present in-process trust claim explicit. Source links and interpretation are recorded in `docs/928-plugin-declared-imports-internal-models.md` and `docs/10-research-notes.md`.

## Remaining risk

Plugin code still runs in the editor process and can consume CPU or memory or exploit defects in any reachable primitive or hostcall. The 209 hostcalls currently classified experimental remain callable; experimental means no compatibility promise, not denial. The internal-model list is exact and must be extended when new equivalent renderer projections are introduced. `requires` provides names and ordering, not semantic versions or conflict resolution. Mutable returned values and shared hooks remain explicit cross-plugin capabilities. No operating-system, syscall, native-code, crash, or hostile-code containment is claimed, and no complete repository-suite claim is made.


## Specialized line-edit audit and correction

The next roadmap item produced two ordinary edit failures before implementation. Moving a half-open whole-line selection changed the selected text even when the bytes moved correctly. Duplicating a line reset the primary column and left secondary cursors attached to whichever text inherited their old numeric row. Undo/redo preserved the wrong geometry, proving that the defect lived in the edit contract rather than rendering.

The root cause was duplicated post-mutation row arithmetic. A raw `(line, col)` cannot distinguish a half-open trailing selection boundary `(end + 1, 0)` from the first character of the neighboring line. `src/micromax_editor/line_edits.py` now owns immutable move, duplicate, and delete plans built from one source vector. Each plan returns output text and coordinate projection; `actions_default.py` pairs endpoints with selection sidecars to supply the boundary role, then installs text/cursors/anchors with one mutation witness.

`CutLine` also exposed an incomplete selection contract and severe avoidable work: it ignored fully or partially selected spans, and deleting 1,000 cursor rows caused 1,000 full-document exact-dirty hashes and version increments. It now cuts the selected line span when present, otherwise unique cursor rows. Five fresh-process runs against the rev0971 archive and final rev0972 source measured medians of 0.642 seconds and 0.050 seconds respectively (about 12.8x in this environment), with the new path advancing `Buffer.version` once while retaining one undo row. This is scoped local evidence, not a portable throughput claim.

A follow-on namespace audit found that source-level `wordlist`/`module` preflight was not sufficient as an invariant: a future primitive could call `VM.new_wordlist()` directly. The allocator now calls `require_wordlist_creation()` before mutating `_next_wid`, dictionaries, or names, and a plugin-context regression proves failure leaves all three unchanged.

No universal edit algebra, rope, source-line registry, mark/diagnostic/fold migration framework, process host, or Wasm ABI was added. Line plans currently project editor cursors and selection anchors only. Equal adjacent line text can still produce a meaningful move because source identity changes. Duplicate-without-selection retains established primary-line semantics rather than multiplying every secondary cursor line.

Current Micro source and a live move-lines issue were reviewed as external checks. Micro independently treats cut/duplicate as selection-aware and contains special column-zero selection compensation in line movement. The issue concerns viewport continuation rather than Micromax's exact defect, but supports the broader requirement that text, directed selection, cursor identity, undo, and view continuation agree. Detailed links, transcript, benchmark, limits, and speculation are in `docs/929-line-edit-source-plan-selection-boundary.md`.


## Context-budget correction

Adding the line-edit evidence exposed that the recent-revision document union had reached the 64-document handoff ceiling. The correction does not raise the ceiling or drop evidence: the oldest recent root triplet, rev0963 audit/changelog/tests, moved intact into the existing `docs/history/` lane and the rev0963 index paths now point there. The curated context therefore remains bounded while exact historical bodies remain packaged and discoverable.
