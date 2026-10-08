# Decisions log

This is the running list of decisions we’ve made (and why).

## rev2 (2026-02-25)

### D001 — Forth is the plugin system
**Decision**: micromax plugins/config/macros are all micromax.

**Why**: it’s the core differentiator (Emacs-like power) while micro-like UX stays the baseline.

**Risk**: plugins can crash / hang / poison global state.

**Mitigation (planned)**:
- wordlists + search order for namespace hygiene
- explicit hostcall allowlist (capability style)
- structured errors + trace
- later: time/step limits per evaluation + per-plugin VM instances

### D002 — Namespacing starts with wordlists + search order
**Decision**: implement minimal Search-Order-like mechanism early, not as a later add-on.

**Why**: editor/plugin ecosystems die without namespace hygiene.

**Implemented in rev2**:
- `wordlist`, `set-current`, `set-order`, `only/also/previous/definitions`, `order` helper.

### D003 — Quotations are core (not optional)
**Decision**: quotations `[ ... ]` are first-class values executed by `call`.

**Why**: keybindings/macros/callbacks want “code as a value”. It’s the ergonomic bridge to editor scripting.

### D004 — Variables/constants are in v0
**Decision**: include `constant`, `variable`, `@`, `!` in v0.

**Why**: real editor scripting needs some persistent state; this is the smallest useful surface.

### D005 — Host bridge is allowlisted
**Decision**: no ambient power; host calls must be explicitly registered.

**Implemented in rev2**:
- `hostcall ( "name" -- ... )` calls only registered host functions.

## rev3 (2026-02-25)

### D006 — Build tools live *inside the archive*
**Decision**: ship formatting/lint/test tooling in-repo so a future LLM (or human) can continue work immediately.

**Implemented in rev3**:
- `ruff` lint+format, `mypy` typechecks, `pytest` tests
- `Makefile` + `scripts/` helpers
- optional `pre-commit` config

### D007 — Add a hard execution budget as a safety floor
**Decision**: every evaluation can run with a **step budget** to prevent untrusted code (plugins) from freezing the host.

**Why**: editor scripting must be safe by default.

**Implemented in rev3**:
- `set-budget ( n -- )` and `with-budget ( n q -- )`
- budget exhaustion raises a structured error

### D008 — micromax is *Forth-inspired*, not standards-bound
**Decision**: we will happily diverge from traditional Forth where it improves ergonomics/safety.

**Why**: the target is an editor scripting ecosystem, not Forth conformance.

**Near-term implications**:
- keep wordlists/search-order (solves real editor/plugin problems)
- keep quotations + combinators as a core ergonomic pillar
- be suspicious of invisible global state (e.g., implicit `STATE`) unless we can make it explicit and debuggable

### D009 — Concurrency will be cooperative-first
**Decision**: plan for concurrency, but default to **cooperative tasks** with explicit yield points.

**Why**: cooperative scheduling is easier to reason about for editor state, avoids many data races, and composes with budgets.

**Planned**:
- `yield`/`pause` primitive and a tiny task scheduler (later)
- isolate editor mutations to the UI task; background tasks communicate via message queue


## rev4 (2026-02-25)

### D010 — “micromax” is the language name
**Decision**: micromax names the **language** (and VM). The editor is a later target and can be named later.

**Why**: we want a crisp identity for the language as the plugin system.

### D011 — Execution tokens + deferred words are ground-floor features
**Decision**: include:
- `'` + `execute` (xts)
- `defer` + `is` + `defer@`/`defer!` (hooks)

**Why**: editor scripting needs first-class callbacks/hook points and keymap-friendly “code handles”.

**Guardrail**: all callbacks still run under `catch` + budgets in the host.


## rev5 (2026-02-25)

### D012 — Preserve paren comments as documentation
**Decision**: Forth-style paren comments `( ... )` are preserved during parsing and used as docstrings
for colon definitions when they appear at the start of a definition.

**Why**: we want a low-friction path to:
- readable code
- `help`/`where` tooling
- eventual stack-effect checking (Factor-style inspiration)

**Implemented in rev5**:
- `help name` prints docs
- `where name` shows the defining wordlist

### D013 — Add a minimal container type: lists
**Decision**: introduce host-value lists as the first container type.

**Why**: editor scripting needs small collections (handlers, selections, search results) and this is
the least complex useful structure.


## rev7 (2026-02-25)

### D014 — Start a testable editor *core* now (headless)
**Decision**: begin the `micro`-esque editor as a **headless core** first.

**Why**: we can make rapid progress with unit tests in this container, and delay
terminal UI decisions (curses vs. tcell-like wrapper vs. something else).

**Implemented in rev7**:
- `micromax_editor.Buffer` (line-based for now)
- multi-cursor *model* support (list of cursors)
- undo/redo stack
- a minimal command/action registry

### D015 — Adopt micro-style action chains in keybindings
**Decision**: support action chaining separators inspired by micro:

- `,` always continue
- `|` abort if previous action succeeded
- `&` abort if previous action failed

**Why**: this is a tiny feature with outsized UX payoff for keymaps.

**Implemented in rev7**:
- `micromax_editor.keymap.parse_action_chain`
- `Editor.run_action_chain`

### D016 — Plugins are micromax directories with lifecycle words
**Decision**: ship a minimal plugin manager now:

- each plugin has its own wordlist/namespace
- optional `plugin.json`
- `init.mx` entrypoint
- optional lifecycle words: `preinit`, `init`, `postinit`, `deinit`

**Why**: we need a real embedding story early so the language design stays
grounded in the editor use-case.

**Implemented in rev7**:
- `micromax_editor.plugins.PluginManager`
- sample `plugins/core/` plugin

### D017 — Add a tiny `see` word to the language
**Decision**: add `see name` to print a readable representation of a word.

**Why**: debuggability is pedagogy.

**Implemented in rev7**:
- `see` for primitives/colon words/deferred words/hooks

**Implemented in rev5**: `list push pop len nth set-nth clone`

### D018 — Hooks are first-class multi-handler words
**Decision**: add hook words that run an ordered list of callbacks (xts).

**Why**: matches common editor extensibility patterns (Emacs hooks) and keeps extension points cheap.

**Implemented in rev5**: `hook hook-add hook-rm hook-clear hook@ hooks`

### D019 — Modules are friendly named wordlists
**Decision**: layer a small module API on top of wordlists/search order.

**Why**: plugin ecosystems need namespaces. Wordlists solve the core problem; modules make it easy.

**Implemented in rev5**: `module ... endmodule`, `use`, `in`, `modules`

### D020 — Add `require` as load-once include
**Decision**: add `require` which loads a file at most once per VM instance.

**Why**: plugin/config layering wants idempotent loading.



## rev6 (2026-02-25)

### D021 — Prioritize pedagogy and offline hackability
**Decision**: add tutorial/cookbook/hacking docs and keep the VM readable with minimal dependencies.

**Why**: micromax should be maintainable by hand, without internet or LLM support.

**Implemented in rev6**:
- `docs/70-tutorial.md`
- `docs/71-cookbook.md`
- `docs/72-hacking-by-hand.md`

### D022 — Add runtime locals sugar (`->name` / `name`)
**Decision**: support a simple locals mechanism to reduce stack-shuffle noise:
- `->name` stores into a local (popping a value)
- `name` loads the local value
- locals are **per colon call** (frames), plus a persistent session frame

**Why**: editor scripting benefits from readability; locals are a pragmatic concession.
See Gforth locals for precedent in Forth ecosystems:
https://gforth.org/manual/Local-Variables-Tutorial.html

**Guardrail**: locals shadow words; `' name` still quotes the dictionary word.

### D023 — Add postfix message-send sugar (`.word`) + dynamic `send`
**Decision**: support `.word` as sugar for `"word" send`, and define `send` to execute a word by string name.

**Why**: improves ergonomics for “object-ish” pipelines while staying fundamentally word-based.

### D024 — Add hot-reload building blocks (`reload`, `unrequire`)
**Decision**: add `reload` to force re-evaluation of a file and `unrequire` to forget a required path.

**Why**: hot reload is essential for plugin iteration and editor scripting.

### D025 — Make “host owns the world” an explicit contract
**Decision**: treat the host boundary as a first-class design surface.
Add `host.api-version`, `host.feature?`, and `host.features`.

**Why**: embedded language ecosystems need stable host API versioning and feature discovery.


## rev8 (2026-02-25)

### D026 — Separate “actions” from “command-bar commands”
**Decision**: the editor core has two dispatch surfaces:
- **actions**: keybind targets that return success/failure (for chaining)
- **commands**: command-bar strings parsed with shell-like quoting

**Why**: micro’s UX splits these concepts cleanly (actions in keybindings; commands in Ctrl-e bar), and it keeps the editor core testable.

**Implemented in rev8**:
- `ActionRegistry` (`src/micromax_editor/commands.py`)
- `CommandDispatcher` (`src/micromax_editor/command_dispatcher.py`)

### D027 — Implement command bar + `command:` / `command-edit:` keybindings
**Decision**: support micro-style bindings that run command-bar commands (`command:`) and open the command bar prefilled (`command-edit:`).

**Why**: huge leverage for discoverability + macro-like workflows without inventing a macro DSL.

**Implemented in rev8**:
- `Editor.enter_prompt(kind='command')`
- `micromax_editor.cmdline.parse_cmdline` (shlex)
- `Editor._run_action_spec` handling `command:` and `command-edit:`

### D028 — Add a minimal options system + incremental search substrate
**Decision**: implement an options registry with global and buffer-local values, and a search subsystem that respects options.

**Why**: micro’s `incsearch` and `ignorecase` are low-hanging editor features that immediately improve UX and guide the embedding API.

**Implemented in rev8**:
- `Options` (`src/micromax_editor/options.py`)
- `SearchState` (`src/micromax_editor/search.py`)
- default options: `ignorecase=true`, `incsearch=true`, `hlsearch=false`

### D029 — Keybinding chain parsing must respect quotes and escaping
**Decision**: parse action chains so separators can appear inside quoted args or be escaped with `\\`.

**Why**: micro explicitly supports this, and it is necessary for `command:` bindings with quoted args.

**Implemented in rev8**:
- upgraded `parse_action_chain` in `src/micromax_editor/keymap.py`


## rev9 (2026-02-25)

### D030 — Add selection + internal clipboard as core editor substrate
**Decision**: implement a simple, testable selection model (anchor + primary cursor) and an internal clipboard.

**Why**: micro’s headline value is “desktop-default” text operations in the terminal (Shift+arrows select; Ctrl-c/x/v copy/cut/paste). This unlocks real editing workflows immediately.

**Implemented in rev9**:
- selection helpers in `Editor` (`selection_text`, `delete_selection`, etc.)
- actions: `SelectLeft/Right/Up/Down`, `SelectAll`, `Copy`, `Cut`, `Paste`, `CutLine`, `DuplicateLine`
- core plugin binds micro-esque defaults (`plugins/core/init.mx`)

### D031 — Add indentation actions + micro Tab chain
**Decision**: implement `IndentSelection` / `UnindentSelection`, and keep micro’s default Tab chain (`Autocomplete|IndentSelection|InsertTab`).

**Why**: indentation is a common “selection-level” operation and the Tab chain is an elegant low-tech macro.

**Implemented in rev9**:
- options: `indent` (default four spaces)
- actions: `IndentSelection`, `UnindentSelection`, `Autocomplete`, `InsertTab`

### D032 — Add `replace` / `replaceall` command-bar commands (regex by default)
**Decision**: implement micro-like `replace` / `replaceall` commands with `-a` (all) and `-l` (literal) flags.

**Why**: search without replace is half a tool; replace is also a good test of shell parsing + command dispatcher + undo.

**Implemented in rev9**:
- commands: `replace`, `replaceall` in `src/micromax_editor/command_dispatcher.py`
- undo recording for command-driven text edits

### D033 — Best-effort micromax action hooks (`ed.pre-action`, `ed.on-action`)
**Decision**: create micromax hook words for action notifications and fire them from `Editor.run_action`.

**Why**: gives plugins a clean, language-native “event surface” without hardcoding a Python callback registry.

**Implemented in rev9**:
- `hook ed.pre-action` and `hook ed.on-action` created in editor init
- `Editor._emit_mx_hook` + hook notifications around action calls



## rev10 (2026-02-25)

### D034 — Upgrade selection model to per-cursor anchors
**Decision**: selections are per cursor (each cursor can have its own anchor), matching modern multi-cursor editors.

**Why**: multi-cursor editing without per-cursor selections quickly becomes confusing; this also keeps clipboard and insert/delete semantics consistent.

**Implemented in rev10**:
- `EditorBuffer.sel_anchors: list[Cursor|None]` aligned with `cursors`
- selection helpers updated to take an optional cursor index
- multi-cursor-safe editing: apply multi-cursor edits bottom-to-top

### D035 — Implement micro-esque macros (action-level)
**Decision**: macros record executed actions/commands (not raw keypresses) and store a snapshot of `editor.input` for replay.

**Why**: the headless core doesn't have a full key-event model yet; action-level macros are stable across UI implementations.

**Implemented in rev10**:
- actions: `ToggleMacro`, `PlayMacro`
- core plugin binds micro defaults: Ctrl-u / Ctrl-j

### D036 — Implement micro-esque multi-cursor primitives
**Decision**: implement the core micro multi-cursor actions that are easy to test and unlock real workflows.

**Implemented in rev10**:
- `SpawnMultiCursorSelect`, `SpawnMultiCursorUp/Down`, `RemoveMultiCursor`, `RemoveAllMultiCursors`, `SkipMultiCursor`, `SpawnMultiCursor`
- core plugin binds micro defaults (Alt-n / Alt-Shift-Up/Down / Alt-p / Alt-c / Alt-x / Alt-m)

### D037 — Implement CutLine accumulation until paste
**Decision**: `CutLine` appends cut lines to the clipboard until the next paste.

**Why**: micro documents this behavior and it makes repetitive line-cut workflows much nicer.

**Implemented in rev10**:
- clipboard stores either `items` (selection chunks) or `lines` (cut-line blocks)
- paste resets cut-line accumulation

### D038 — Add prompt history navigation with context-aware bindings
**Decision**: keep per-prompt history and bind Up/Down as `PromptHistoryPrev|CursorUp` and `PromptHistoryNext|CursorDown`.

**Why**: micro-style action chains let one binding behave differently in prompt vs buffer without a complex mode system.

**Implemented in rev10**:
- prompt history state in `Prompt` + `Editor.history`
- actions: `PromptHistoryPrev`, `PromptHistoryNext`



## rev11 (2026-02-25)

### D039 — Add a small set of stack ergonomics words (`nip`, `tuck`, `pick`, ...)
**Decision**: implement a small handful of high-leverage stack words used in practice.

**Why**: micromax wants to be ergonomic *without* requiring a huge standard library.
These words also make scripts and tests shorter and clearer.

**Implemented in rev11**:
- `nip`, `tuck`, `2dup`, `2drop`, `depth`, `clear`, `pick`, `roll`

### D040 — Expose a return stack (`>r`, `r>`, `r@`, `rdrop`, `rdepth`)
**Decision**: expose return-stack manipulation primitives.

**Why**: return-stack words are a minimal, well-known extension point in Forth culture.
They also enable certain stack arrangements without adding a long list of primitives.

**Implemented in rev11**:
- `>r`, `r>`, `r@`, `rdrop`, `rdepth`

### D041 — Add tiny quotation combinators (`dip`, `keep`)
**Decision**: add the "two smallest" useful combinators for quotation ergonomics.

**Why**: `dip` and `keep` appear repeatedly across Joy/Factor/Forth-adjacent code.
They reduce noisy stack juggling, which is especially important in editor scripting.

**Implemented in rev11**:
- `dip`, `keep`

### D042 — Improve error formatting with source excerpts
**Decision**: keep evaluated sources in the VM and include a one-line excerpt + caret
in formatted errors.

**Why**: micromax is meant to be hacked by hand and debugged offline; error messages
should point directly at the problem.

**Implemented in rev11**:
- `VM.sources` cache
- `VM.format_error()` includes a best-effort excerpt

## rev13 (2026-02-25)

### D043 — Tier-2 is late-bound and minimal
**Decision**: the first compiled tier uses only `PUSH` and `EXEC_NAME`, where `EXEC_NAME` applies the *same* runtime name rules as tier-1 (locals shadowing, `.name` send sugar), and resolves names at execution time.

**Why**: this preserves dynamic redefinition/reload semantics and keeps the compiler tiny and portable.

**Risk**: fewer speed wins than early-binding or richer bytecode.

**Mitigation**: add optional caching/ids later without changing semantics.

### D044 — Token-parsing words remain tier-1 for now
**Decision**: compiled code rejects words that require reading the token stream at runtime (e.g. `module`, `constant`, `local@`).

**Why**: it keeps tier-2 small and avoids re-creating an interpreter inside the compiler.

**Risk**: some advanced metaprogramming cannot run compiled.

**Mitigation**: expand the compiler story later (compile-time expansion or non-parsing runtime alternatives).

### D045 — Prefer non-parsing runtime lookup
**Decision**: add `find` (`"name" -- xt|0`) so runtime code can look up words without `'` (token parsing).

**Why**: improves portability and makes tier-2 compilation easier.

### D046 — Add orthogonal editor range primitives
**Decision**: expose `ed.range-text`, `ed.replace-range`, `ed.delete-range` as undoable, orthogonal hostcalls (primary buffer).

**Why**: gives scripts real editing power without exploding the hostcall surface with one-off commands.

## rev14 (2026-02-25)

### D047 — Multi-cursor lists are in document order with an explicit primary index
**Decision**: store cursors in document order and track the primary cursor via an explicit `primary` index.

**Why**: this matches how selection-oriented editors describe the world (primary vs document-order selections) and makes scripting deterministic.

**Consequence**: internal editor code must not assume cursor 0 is the primary.

### D048 — Normalize multi-cursor invariants after every action
**Decision**: after each action, normalize cursor lists: clamp positions, align anchor lists, remove duplicates, sort, and fix up `primary`.

**Why**: multi-cursor bugs are "state leaks". Normalization makes the editor resilient and keeps unit tests honest.

### D049 — Expose a minimal multi-cursor host surface
**Decision**: add hostcalls `ed.cursors`, `ed.set-cursors`, `ed.primary`, `ed.set-primary`, `ed.selections`, and `ed.replace-selections`.

**Why**: these few calls let micromax scripts inspect/edit multi-cursor state without committing to a large object model or adding maps/dicts.

## rev15 (2026-02-25)

### D050 — Transactional undo grouping for scripts
**Decision**: add `ed.with-undo` hostcall that runs a quotation while suppressing internal undo recording, then records a single undo snapshot (or rolls back on error).

**Why**: plugin actions frequently need multiple hostcalls but should appear as one user-visible undo step (similar in spirit to grouped changes in modal editors).

### D051 — Expose clipboard as orthogonal host primitives
**Decision**: add clipboard hostcalls `ed.clipboard`, `ed.set-clipboard`, `ed.clipboard-items`, and `ed.set-clipboard-items`.

**Why**: scripts need to cooperate with editor copy/cut/paste semantics (including multi-item clipboards) without reaching into Python internals.

### D052 — Add a per-buffer selection recovery stack (not undo)
**Decision**: add `ed.push-selections`/`ed.pop-selections` and keep the saved state out of undo history.

**Why**: multi-cursor workflows make it easy to accidentally clear/merge selections; a tiny recovery stack is a cheap, testable escape hatch.

## rev16 (2026-02-25)

### D053 — Expose directionless range helpers for the primary selection
**Decision**: add `ed.selection-range` and `ed.set-selection-range` hostcalls.

**Why**: many editor operations (replace, delete, extract) are naturally described as ranges; a directionless, normalized view is convenient and portable.

**Note**: directed endpoints remain available via `ed.selections`.

### D054 — Allow scripts to set directed selections via lists
**Decision**: add `ed.set-selections` hostcall that accepts `[]` or `[aL aC cL cC]` per cursor.

**Why**: this makes cursor/selection state manipulable without introducing maps/dicts or opaque objects.

### D055 — Add selection direction actions
**Decision**: add editor actions `FlipSelections` and `EnsureSelectionsForward`.

**Why**: selection-oriented editors commonly expose anchor/cursor control; having these as core actions keeps behavior testable and scriptable.

## rev17 (2026-02-25)

### D056 — Add a portable cursor/selection snapshot format
**Decision**: expose `ed.cursorstate` and `ed.set-cursorstate` using a lists+ints wire format: `[primary [[id line col aL aC] ...]]` with `-1 -1` for missing anchors.

**Why**: scripts and plugins often need to stash/restore cursor state (e.g. preview helpers, temporary navigation) without coupling to editor internals. Keeping it "portable on the wire" supports a future Rust/WASM host.

### D057 — Add save-excursion style cursor restoration
**Decision**: add `ed.with-cursorstate` that runs a quotation and then restores cursor/selection state in a `finally` block.

**Why**: many editor ecosystems have a common pattern (e.g. Emacs' `save-excursion`) where helper commands can move around without disturbing the user's cursor.

## rev18 (2026-02-25)

### D058 — Add a per-buffer jumplist (navigation history)
**Decision**: implement a per-buffer jumplist with actions `PushJump` / `JumpBack` / `JumpForward` and hostcalls `ed.push-jump`, `ed.jump-back`, `ed.jump-forward`, `ed.jump-info`, `ed.clear-jumps`.

**Why**: navigation history is a ubiquitous editor primitive (Vim/Helix). Keeping it per-buffer and storing full cursor/selection state makes it deterministic and scriptable, while staying separate from undo.

### D059 — Add data-returning XT introspection helpers
**Decision**: add `xt-kind`, `xt-doc`, and `xt-src` words.

**Why**: tooling (including future LLM-assisted refactors) benefits from structured access to documentation and definitions without scraping printed output.

## rev19 (2026-02-25)

### D060 — Add a global dict-version for tier-2 cache invalidation
**Decision**: maintain `VM.dict_version` and expose it as `dict-version`.

**Why**: tier-2 bytecode needs a cheap invalidation mechanism so per-call-site caches stay correct under word redefinition and search-order changes.

### D061 — Use per-call-site inline caches for `EXEC_NAME`
**Decision**: compiled `EXEC_NAME` instructions carry a `WordRef` that caches name resolution keyed by `dict-version`.

**Why**: this preserves tier-1 late-binding semantics while avoiding repeated dictionary lookups when the dictionary/search order is stable.

### D062 — Centralize search-order mutation through `set_search_order`
**Decision**: replace direct writes to `search_order` in core/module/plugin code with `VM.set_search_order(...)`.

**Why**: search order changes affect name resolution; routing all mutations through a single helper ensures `dict-version` is bumped consistently.

## rev20 (2026-02-25)

### D063 — Add a constant pool to tier-2 bytecode
**Decision**: represent bytecode as a constant pool (`consts`) plus a linear instruction stream whose operands are indices.

**Why**: it keeps the instruction stream compact, makes a future binary encoding straightforward for Rust/WASM, and matches common VM practice.

**Note**: this is a representation change only; semantics remain identical.

### D064 — Expose editor message log to scripts
**Decision**: add hostcalls `ed.messages`, `ed.last-message`, `ed.pop-message`, and `ed.clear-messages`.

**Why**: headless-first workflows (and plugin debugging) benefit from being able to inspect and clear the editor message log from micromax without reaching into Python internals.

### D065 — Keep repo context output up to date for future LLMs
**Decision**: update `tools/mxcontext.py` to include bytecode + caching docs and the cursorstate/jumplist docs.

**Why**: future automated refactors work best when the key docs are enumerated in one stable place.

## rev21 (2026-02-25)

### D066 — Add JSON serialization for tier-2 bytecode
**Decision**: add a simple, tagged JSON encoding for tier-2 bytecode and expose it via `bytecode-json` and `bytecode-load-json`.

**Why**: this enables offline caching and provides a straightforward cross-language validation path for the eventual Rust/WASM VM (generate JSON in Python, load/execute in Rust, compare behavior).

### D067 — Add message-log save/capture helpers for scripts
**Decision**: add hostcalls `ed.with-messages` and `ed.capture-messages`.

**Why**: headless-first workflows and tests often want to run an action/command and assert what it *said* without polluting the persistent message log.

### D068 — Document the bytecode serialization shape explicitly
**Decision**: add `docs/27-bytecode-serialization.md` and update the bytecode-format doc to reference it.

**Why**: keeping the archive self-describing makes future refactors and ports (including LLM-assisted ones) significantly easier.

## rev22 (2026-02-25)

### D069 — Add tiny tier-2 control flow ops and compile `if/when/while`
**Decision**: extend tier-2 bytecode with `CALL_Q`, `JZ`, and `JMP`, and add a semantics-preserving peephole compile for:

- `flag [t] when`
- `flag [t] [f] if`
- `[cond] [body] while`

**Why**: these patterns dominate real runtime scripting hot paths (keybindings/actions). Compiling them avoids pushing quotation values and calling the runtime control words, while preserving late binding inside quotations.

### D070 — Auto-record jumplist entries for `goto` and `jump`
**Decision**: add editor option `jumplist.auto` (default true). When enabled, `goto`/`jump` record both the "from" and "to" cursor states.

**Why**: this matches the common “jump list” ergonomics in editors (e.g. Vim/Helix): after a big jump, users expect a single back-step to return.


## rev23 (2026-02-25)

### D071 — Named macro slots + cancel macro
**Decision**: extend macro recording/playback beyond a single "last macro" to support named macro slots, and add `CancelMacro` to discard a recording without overwriting the previous macro.

**Why**: micro's single last-macro is great for quick repetition, but a small library of named macros (like Vim/Emacs) makes early automation dramatically more usable without needing a full plugin ecosystem.

### D072 — Make macros script-visible with a portable encoding
**Decision**: add macro hostcalls (`ed.macro-*`) and define a portable macro representation using only lists/ints/strings:

- `["a", ACTION, [[key val] ...]]` for action steps (with `editor.input` snapshot)
- `["c", CMDLINE]` for command steps

**Why**: this lets scripts inspect/persist/edit macros without needing a map/dict type in the VM, and keeps a clean Rust/WASM port path.

### D073 — Expose `editor.input` for tooling and fix command history duplication
**Decision**: add hostcalls to read/list/clear `editor.input` and ensure command history is recorded exactly once for command prompt submissions.

**Why**: parameterized actions need a stable, scriptable way to set and inspect inputs, and prompt history should not double-record entries.

## rev24 (2026-02-25)

### D074 — Add portable, string-keyed maps to the VM
**Decision**: promote **Map** (mutable, string-keyed dictionaries) to a core value type and add a tiny primitive surface:

- `map map?`
- `m@ m? m! m-del`
- `m-keys m-items m-merge`

**Why**: editor scripting and plugin configuration quickly want structured state that is more readable than “lists of pairs”, and the Rust/WASM port story for a string-keyed hash map is straightforward.

**Policy**: in portable mode, map keys are **strings**; primitives enforce this by parsing keys as strings.

## rev25 (2026-02-25)

### D075 — Prompt completion modeled as a suggestion session
**Decision**: implement command-bar completion as a small, headless *suggestion session* stored on `Prompt`:

- `suggestions`, `suggest_index`
- `suggest_start/suggest_end`
- `suggest_base`

Bind `Tab` to cycle forward (existing `Autocomplete`) and `Shift-Tab` to cycle backward (`PromptCompletePrev`), matching common editor conventions.

Expose minimal hostcalls for UI/scripting experimentation:
- `ed.prompt-suggestions`
- `ed.prompt-suggest-index`
- `ed.prompt-complete`
- `ed.prompt-clear-suggestions`

**Why**: this makes the command bar feel immediately “real editor” (discoverable + fast), while keeping the editor core headless and testable.

### D076 — Add `xt-span` and store spans on colon words
**Decision**: store a definition span on `ColonWord` (the `:` token span) and add `xt-span`:

- `xt-span` ( xt -- [file line col] | 0 )

**Why**: spans are cheap, portable metadata that dramatically improve debugging, tooling, and reloadability, especially when the editor’s commands and keybindings are *data* (quotations) created dynamically.

## rev26 (2026-02-26)

### D077 — Add contract tests for spans and prompt completion hostcalls
**Decision**: add direct unit tests for:

- `xt-span` on colon words + quotations (and `0` on primitives)
- command-bar completion via hostcalls (`ed.prompt-*`)

**Why**: these features are small but foundational for debugging and headless UX. A dedicated test keeps the contract stable across refactors and prevents subtle regressions.

### D078 — Document source-span debugging as a first-class workflow
**Decision**: add `docs/65-debugging-spans.md` describing the span model and how `format_error` and `xt-span` fit together.

**Why**: micromax is meant to be evolved offline by humans and future LLMs; spans are one of the highest leverage “make debugging pleasant” affordances, so the repo should explain them explicitly.

## rev27 (2026-02-26)

### D079 — Add filesystem path completion for `open` / `save` / `cd`
**Decision**: extend command-bar completion to support micro-style file/workspace commands:

- `open PATH`
- `save PATH`
- `cd PATH`

Rules (portable, predictable):
- hidden files are only suggested when the typed name starts with `.`
- directories get a trailing path separator so you can continue completing into them
- files at end-of-line get a trailing space (dirs do not)
- cap suggestion list size to avoid pathological directories

**Why**: path completion is one of the fastest ways to make the command bar feel “real” in daily use, and the suggestion-session model means we can *cycle* candidates instead of committing to the first match.

**Tests**: add a headless test that creates a temp directory and validates unique-dir, unique-file, and multi-candidate cycling behavior.

## rev28 (2026-02-26)

### D080 — Quote-aware path completion for `open` / `save` / `cd`

**Decision**: extend filesystem path completion to handle paths that require quoting.

- If the user started a quoted token (single or double quotes), completion happens *inside* that quote style.
- If the user did not start a quote token, but a completion contains whitespace or a double quote, completion auto-wraps it in **double quotes** and escapes internal `\\` and `"`.
- For directory completions when quoting is active, we keep the closing quote **open** so users can keep tabbing into the directory.
- If the user already typed a closing quote, we preserve it (even for directories).

**Why**: micro’s command bar follows `/bin/sh`-style quoting rules, and real-world usage frequently involves paths with spaces. Quote-aware completion prevents “completion works, execution fails” footguns.

**Tests**: add headless tests for auto-quoting a space-containing file, auto-quoting a space-containing directory (and continuing completion), preserving an explicit closing quote for directories, and escaping embedded double quotes.

## rev29 (2026-02-26)

### D081 — Micromax-defined command-bar commands (`ed.cmd-add`)

**Decision**: expose a minimal hostcall that lets micromax scripts define command-bar commands.

- Hostcall: `ed.cmd-add` with stack effect `( xt name doc -- ok )`.
- The command xt is executed as `( args -- ... )` where `args` is a list of strings.
- If the xt leaves an int/bool on top of the stack, it is treated as an ok flag; otherwise ok defaults to 1.
- Commands are replaceable/reloadable: registering the same name overwrites the previous definition.
- Best-effort provenance: attach a `Span` (via `vm.last_span`) so `help <cmd>` can show where a command was registered.

**Why**: micro’s plugin API has an explicit “make a command” call (`MakeCommand`) and it’s a key bridge from scripting to real UX. We need the same bridge to make micromax the *native* config/plugin system rather than a sidecar macro language.

**Tests**: add headless tests for add/exec/help/provenance/remove.

### D082 — Prompt completion hook (`ed.complete.*`) with additive/replace modes

**Decision**: allow micromax scripts to supply prompt completion candidates without UI entanglement.

- Lookup order: `ed.complete.<cmd>` then `ed.complete`.
- Contract: `( cmd tok_i prefix toks -- cands mode )`
  - `cands` is a list of insertion strings
  - `mode`: 0 none, 1 add, 2 replace
- The editor merges these candidates into the existing suggestion-session machinery.

**Why**: Kakoune’s shift toward a dedicated completion configuration command (`complete-command`) demonstrates that completion wants to be *customizable* separately from command definition. Providing a tiny, scriptable hook now keeps us compatible with that “completion is its own thing” philosophy.

**Tests**: add a headless test exercising command-specific completion and Tab/Shift-Tab cycling.

### D083 — `here-span` + `vm.last_span` as provenance substrate

**Decision**: track the VM’s most recent executed span (`vm.last_span`) and expose it as a primitive `here-span`.

**Why**: embeddings often need to attach “where did this come from?” to dynamic registrations (commands, hooks, bindings). A tiny, best-effort span signal helps debugging and keeps the archive friendly to future tooling.

**Tests**: add a unit test that `here-span` returns `[file line col]`.

## rev30 (2026-02-26)

### D084 — Keybindings carry best-effort provenance and are removable

**Decision**: treat editor keybindings as small records instead of bare strings.

- `Keymap` now stores `key`, `action_spec`, and optional `span`.
- `ed.bind` attaches `vm.last_span` as best-effort provenance.
- Add `ed.unbind` and `ed.bindings` hostcalls.
- Improve `showkey` so it reports provenance when available.
- Add a user-facing `unbind KEY` command.

**Why**: the editor roadmap explicitly wants transparent keybinding introspection: users and plugins should be able to answer “what does this key do right now?” and “where did that binding come from?” without a UI-specific debugger.

**Tests**: add headless tests covering script-defined bindings, `showkey` provenance, `ed.bindings`, and `unbind`.

## rev31 (2026-02-26)

### D085 — Hook definitions and handler registrations carry best-effort provenance

**Decision**: extend hook words with tiny debugging metadata while keeping execution semantics unchanged.

- `HookWord` now records the definition span.
- `hook-add` stores handler entries as `{xt, span}` internally.
- `hook@` stays backward-compatible and returns a plain xt list.
- Add `hook-rows NAME` returning `[[handler-name [file line col]|0] ...]`.
- Extend `xt-span` so hook words participate in the same provenance story as colon words and quotations.
- Add an editor command-bar command `showhook NAME` for headless inspection of installed handlers.

**Why**: once commands and keybindings gained provenance, hooks became the obvious remaining blind spot. Editor/plugin systems only stay pleasant if users can answer “what is attached here right now, and where did it come from?” without reverse-engineering the whole config.

**Tests**: add unit tests for `hook-rows`, `xt-span` on hook words, backward-compatible `hook@`, and editor `showhook`.

## rev32 (2026-02-26)

### D086 — Statusline/infobar state is a shared headless model, not a UI-specific string

**Decision**: expose editor status as portable data first.

- Add `Editor.status_model()` returning a small map of shared editor state.
- Add hostcalls:
  - `ed.status` → portable map
  - `ed.status-summary` → deterministic debug/headless summary string
- Add a user-facing command-bar command `showstatus`.

The model currently includes:

- file/buffer identity (`buffer_name`, `file_name`, `path`, `cwd`)
- dirty/read-only state
- cursor/selection state
- prompt state
- macro recording/playback flags
- last message

**Why**: we want future UIs to render shared semantics instead of each one inventing its own notion of “current status”. Helix’s explicit left/center/right statusline element model is a good reminder that render layout should be configurable, while micro’s statusline-as-real-editor-surface reminds us that even a tiny terminal editor should treat that line as meaningful state, not an afterthought.

**Tests**: add headless tests for `ed.status`, `ed.status-summary`, and `showstatus`.


## rev33 (2026-02-26)

### D087 — Hook handlers may carry a group tag; plugin reload cleans grouped handlers automatically

**Decision**: extend hook registrations with an optional string **group** while keeping plain `hook-add` source compatible.

- `HookHandler` now carries `{xt, span, group}` internally.
- `hook-add` uses `vm.current_hook_group` as a best-effort default group.
- Add:
  - `hook-group!` / `hook-group@` — set/query the default group
  - `hook-groups NAME` — list unique groups on a hook
  - `hook-rm-group NAME` — remove only matching grouped handlers from one hook
  - `hook-detail NAME` — `[[handler-name group|0 span|0] ...]`
- `showhook NAME` now shows `handler#group@file:line:col` when available.
- `PluginManager` evaluates plugin code/lifecycle words with `current_hook_group = "plugin:<name>"` and removes that group on unload/reload.

**Why**: Kakoune's `remove-hooks` group model is a good proof that dynamic hook ecosystems need cheap grouped cleanup. micro's reload-friendly lifecycle makes the same pressure visible from the plugin side: repeated load/unload cycles should not leave stale callbacks behind.

**Tests**: add unit tests for `hook-detail`, `hook-rm-group`, current group state, and plugin reload/unload cleanup of grouped hook handlers.

## rev34 (2026-02-26)

### D088 — Editor commands and keybindings get registration groups

**Decision**: mirror the successful hook-group pattern for the editor bridge.

- `Command` now stores optional `group` metadata.
- `Binding` now stores optional `group` metadata.
- New editor hostcalls:
  - `ed.group!` / `ed.group@` — set/query the default editor registration group
  - `ed.cmd-rows` — `[[name doc group|0 [file line col]|0] ...]`
  - `ed.binding-detail` — `[[key action-spec group|0 [file line col]|0] ...]`
- `ed.cmd-add` and `ed.bind` attach `vm.current_editor_group` as a best-effort group tag.
- `help <cmd>`, `showcmd`, and `showkey` now include group metadata when present.

**Why**:
- plugin reload/unload needs a cheap way to tear down dynamic registrations
- commands and bindings are part of the live editor environment, so they should be inspectable data
- this keeps future mode/layered-keymap work compatible with today’s metadata shape

### D089 — PluginManager cleans grouped editor registrations on unload/reload

**Decision**: the reference `PluginManager` now sets `vm.current_editor_group = "plugin:<name>"` while evaluating plugin source and lifecycle words, and removes grouped commands/bindings on unload.

- `install_editor_hostcalls()` sets `vm.editor_owner = ed` as a best-effort cleanup backpointer.
- `PluginManager.unload()` now removes:
  - grouped hook handlers (`remove_hook_group`)
  - grouped command-bar commands (`command_dispatcher.remove_group`)
  - grouped keybindings (`keymap.remove_group`)

**Consequence**: reloads can safely replace commands/bindings without stale registrations surviving from old plugin revisions, even though the prototype loader still does not garbage-collect plugin wordlists.

**Tests**: add focused tests for group query/detail rows and plugin reload cleanup across commands + keybindings.



### D090 — keybindings gain a small mode/layer system with global fallback

**Decision**: add named keymap modes to the editor core, but keep the model deliberately
small: bindings now carry a `mode` string, the editor keeps an active key mode stack, and
lookup resolves **topmost active mode first, then global**.

New surface:
- command-bar: `bindmode`, `unbindmode`, `keymode`, `pushkeymode`, `popkeymode`, `showkeymodes`
- hostcalls: `ed.bind-mode`, `ed.unbind-mode`, `ed.binding-modes`, `ed.keymode!`, `ed.keymode@`, `ed.keymode-push`, `ed.keymode-pop`, `ed.keymodes`
- status model: `keymode` field

**Why**:
- real editors layer keymaps by context
- this unlocks transient/plugin-owned maps without committing to a full modal UI
- `showkey` can now answer "what does this key do *right now*?" more honestly
- grouped plugin cleanup continues to work because mode bindings use the same metadata path

**Non-goal**: this is not yet a full Helix/Kakoune/Emacs mode architecture. It is a compact, portable substrate that future minor/transient modes can build on.

## rev36 (2026-02-26)

### D091 — Add one-shot keymodes and centralize key dispatch

**Decision**: keep the existing named keymode stack, but allow entries to be either
persistent or **one-shot**.

New surface:
- editor core:
  - `Editor.dispatch_key(key)` — resolve + execute a key through active keymodes
  - active keymode rows now include a one-shot flag
- command-bar:
  - `pushkeymode-once MODE`
  - `showkeymodes` marks one-shot modes with `!`
- hostcalls:
  - `ed.keymode-push-once`
  - `ed.keymode-rows` — `[[mode once?] ...]`
  - `ed.press-key`
- status model:
  - `keymode_once`

**Semantics**:
- the topmost one-shot mode gets first crack at the next key
- if it has a binding for that key, the binding runs and the mode pops
- if it does not, the mode pops and lookup falls through to remaining modes/global
- persistent modes behave as before

**Why**:
- Helix minor modes and Kakoune next-key contexts both show the value of short-lived
  layered keymaps
- Emacs `set-transient-map` is the classic proof that “one (or more) subsequent keys”
  is a useful editor primitive
- centralizing key dispatch keeps future UIs and tests from open-coding
  `resolve_key_binding()` + `run_action_chain()` and accidentally bypassing keymode
  semantics

**Non-goal**: this is not yet a full multi-key parser or timeout-based prefix-map system.
It is a compact, deterministic substrate for future transient maps.


## rev37 (2026-02-26)

### D092 — Add keymap discovery / whichkey-style inspection surfaces

**Decision**: keep bindings as simple records, but add a tiny discovery surface that can answer both:

- what bindings exist in one mode?
- what bindings are currently reachable after active keymode precedence is applied?

New surface:
- hostcalls:
  - `ed.binding-rows-for` — exact bindings for one mode
  - `ed.available-bindings` — precedence-resolved current keymap
  - `ed.resolve-key` — machine-readable sibling of `showkey`
- command-bar:
  - `showbindings [MODE|active]`
  - `whichkey` (alias for active binding discovery)

**Why**:
- once transient keymodes exist, users/scripts need a cheap answer to “what can I press right now?”
- discovery should live in the headless core as data, not as a popup/UI commitment
- this keeps future Rust/WASM or alternate UIs free to render the same semantics differently

**Non-goal**: this is not yet a timeout-driven prefix parser or popup contract. It is a small, deterministic inspection layer over the existing keymap model.


## rev38 (2026-02-26)

### D093 — Add binding descriptions / docstrings as data, not UI chrome

**Decision**: keep keybindings as simple records, but let them carry an optional
**human description** (`desc`) in addition to the exact action spec.

New surface:
- keymap/editor core:
  - bindings now optionally carry `desc`
  - `Editor.binding_desc(binding)` derives a fallback label from command/action docs
- hostcalls:
  - `ed.bind-doc` / `ed.bind-mode-doc`
  - `ed.binding-info-for`
  - `ed.available-binding-info`
  - `ed.resolve-key-info`
- command-bar:
  - `binddoc KEY DOC...`
  - `bindmodedoc MODE KEY DOC...`
  - `whichkey` now prefers human descriptions over raw action specs
  - `showkey` now includes `[desc ...]` when available

**Why**:
- raw action chains are truthful but noisy; discovery surfaces should be able to show
  short human labels
- Kakoune mapping docstrings and Emacs `which-key` descriptions both point toward
  “binding help text belongs with the binding”, not in a UI-only lookup table
- derived fallback labels from command/action docs keep the feature immediately useful
  even before scripts start attaching custom descriptions

**Non-goal**: this is not a popup contract or a full prefix-menu system. It is a
small metadata layer that keeps discovery surfaces portable and testable.


### D094 — Add tiny first-class prefix-map helpers on top of one-shot keymodes

**Why**
- One-shot keymodes already made prefix-style maps *possible*.
- In practice, scripts had to hand-write `command:pushkeymode-once MODE,command:whichkey`, which was correct but noisy.
- A tiny named helper makes the feature much easier to discover without introducing a new binding class or UI commitment.

**Decision**
- Add command-bar `prefixmode MODE` to push a one-shot mode and immediately show reachable bindings.
- Add command-bar `bindprefix KEY MODE [DOC...]` for the common “global prefix key” case.
- Add hostcalls:
  - `ed.prefix-mode`
  - `ed.bind-prefix`
- Keep prefix bindings represented as ordinary bindings whose action-spec is `command:prefixmode MODE`.

**Why this shape**
- Preserves portability: prefix maps remain keymap data, not a special runtime object.
- Preserves discoverability: `showkey`, `ed.resolve-key-info`, and `whichkey` all keep working unchanged.
- Preserves reload hygiene: prefix bindings still use the normal grouping/provenance machinery.

**Tests**
- Add focused tests for `ed.bind-prefix`, `prefixmode`, `bindprefix`, dispatch through a prefix key, and one-shot pop behavior after the next matching key.


## rev40 (2026-02-26)

### D095 — Add mode-local prefix-map helpers on top of one-shot keymodes

**Why**
- Global prefix helpers (`bindprefix`, `ed.bind-prefix`) made leader-style menus easy,
  but configs still had to hand-write mode-local prefix bindings.
- Helix/Kakoune-style nested minor modes strongly suggest that “prefix inside one
  mode enters another short-lived key layer” is a normal editor pattern, not a
  special UI feature.
- Keeping this as sugar over ordinary bindings preserves all the introspection and
  cleanup work already in the repo.

**Decision**
- Add command-bar `bindmodeprefix OWNERMODE KEY MODE [DOC...]`.
- Add hostcall `ed.bind-mode-prefix`.
- Keep the resulting binding as an ordinary mode-local keymap row whose action-spec
  is `command:prefixmode MODE`.

**Why this shape**
- Preserves portability: still just strings / ints / lists on the wire.
- Preserves discoverability: `showkey`, `ed.resolve-key-info`, and `whichkey` keep
  working unchanged.
- Preserves reload hygiene: grouped/provenance-aware binding cleanup still applies.

**Tests**
- Add focused tests for hostcall creation, command-bar creation, resolution only in
  the owner mode, and dispatch into a one-shot target mode.


## rev41 (2026-02-26)

### D096 — Add deterministic fuzzy fallback to command-bar completion for command-ish tokens

**Why**
- micro’s command prompt establishes the baseline expectation that `Tab` should complete commands/options/paths.
- Helix’s picker model shows that fuzzy matching is an ergonomic default when users are searching named editor surfaces rather than spelling exact prefixes.
- The repo roadmap already called out “fuzzy + argument completion” as low-hanging fruit, but full fuzzy-open/path search would be a bigger UX commitment.

**Decision**
- Keep the existing completion contract and suggestion-session model.
- For built-in **command-ish** completion sources (`command`, `help`, `set/show/toggle`, `plugin`, `macro`):
  - try **exact prefix** matches first
  - if that yields nothing, fall back to a tiny **subsequence fuzzy matcher**
  - rank fuzzy hits deterministically: contiguous substring hits first, then earlier/tighter/boundary-friendlier matches, then shorter names
- Keep filesystem path completion for `open` / `save` / `cd` explicitly **prefix-based** for now.
- When fuzzy fallback is active, headless messages say `fuzzy:` / `fuzzy matches:` so tests and future UIs can tell what happened.

**Why this shape**
- Preserves the current mental model for users who already rely on exact-prefix `Tab`.
- Makes command discovery more forgiving without silently turning path completion into a file picker.
- Keeps the implementation tiny, inspectable, portable, and easy to reproduce in future Rust/WASM ports.

**Tests**
- Add focused tests for:
  - unique fuzzy command completion
  - multiple fuzzy command matches + cycling
  - help-topic fuzzy ranking that prefers camel-boundary-style matches


## rev42 (2026-02-26)

### D097 — Extend prompt completion to a few high-value argument surfaces before inventing previews

**Why**
- The fuzzy fallback added in rev41 made command discovery more forgiving, but the next obvious friction point was after the command name: users still had to remember option values, keymode names, and inspection topics.
- Neovim’s command-line completion docs are explicit that completion is useful across **different categories** (command names, files, option names, etc.), which reinforces that argument completion should be treated as a normal command-line concern rather than a special UI feature.
- Kakoune’s `complete-command` model is a good reminder that completion policy should stay tied to commands / argument slots, not hidden in a popup implementation.

**Decision**
- Keep the existing prompt suggestion-session contract unchanged.
- Add small built-in completion for a few argument slots that are already stable and inspectable:
  - `set` / `setlocal OPTION VALUE` → built-in bool/enum values
  - `keymode` / `pushkeymode` / `pushkeymode-once` / `prefixmode` → known keymode names
  - `showbindings` → `active` plus known keymode names
  - `bindmode` / `bindmodedoc` / `unbindmode` / `bindmodeprefix` mode slots → known keymode names
  - `showcmd` → command names
  - `showhook` → hook names visible in the current VM
- Reuse the same exact-prefix-first + tiny fuzzy fallback policy for these command-ish argument surfaces.
- Do **not** add a preview/metadata channel yet; keep completion output as plain candidate strings until we need richer UI contracts.

**Why this shape**
- Captures a lot of ergonomic value without widening the prompt/session data model.
- Keeps path completion, option/value semantics, and mode discovery all explicit and testable in the headless core.
- Makes future previews easier to add later because the candidate-source boundaries are now clearer.

**Tests**
- Add focused tests for enum/bool option value completion.
- Add focused tests for keymode-name completion and `showbindings active|MODE` completion.
- Add focused tests for `showhook` topic completion.



## rev43 (2026-02-26)

### D098 — Extend prompt completion into `bind` / `bindmode` action specs

**Why**
- After rev42, the next obvious command-bar friction point was keybinding authoring: `bind` and `bindmode` still required users to remember action names and `command:` / `command-edit:` syntax from memory.
- micro’s keybindings docs make those right-hand-side action specs a first-class user surface, not an implementation detail.
- Reusing the existing command completion logic inside `command:` bindings keeps the model smaller and more portable than inventing a separate “binding RHS” completion engine.

**Decision**
- Keep the existing prompt suggestion-session contract unchanged.
- Add built-in action-spec completion for:
  - `bind KEY ACTIONSPEC`
  - `bindmode MODE KEY ACTIONSPEC`
- Complete plain editor action names in those slots.
- Treat `command:` and `command-edit:` as first-class completion prefixes.
- If the current binding action-spec starts with `command:` / `command-edit:`, reuse the ordinary command-ish completion rules for the embedded command line.

**Why this shape**
- Makes keybinding authoring much more discoverable without widening the prompt/session data model.
- Keeps bindings inspectable as ordinary action-spec strings.
- Reuses the existing slot-aware command completion logic instead of forking a second completion policy.

**Tests**
- Add focused tests for:
  - `bind` action-name completion
  - `bind` `command:NAME` completion
  - nested command-argument completion inside a binding (`command:showbindings a`)
  - `bindmode` `command-edit:NAME` completion


## rev44 (2026-02-26)

### D099 — Add prompt suggestion metadata rows without changing the completion/session contract

**Why**
- After rev43, the next obvious improvement was not “more candidates” but “better context”: future UIs and micromax-side tools need to know *what* a suggestion is (command, option, action, file, keymode) and often want a tiny annotation (doc/current value/etc.).
- Neovim’s completion APIs are a useful precedent: completion items carry fields like `word`, `menu`, `kind`, and `info`, and UI rendering is treated as a separate concern.
- Kakoune’s `complete-command` docs reinforce that completion policy is attached to command argument structure, while menu presentation stays downstream.

**Decision**
- Keep `Prompt.suggestions` and the existing suggestion-session/cycling semantics unchanged.
- Add a parallel best-effort metadata surface for active suggestion sessions:
  - `Prompt.suggestion_rows`
  - row shape: `[insert, kind, menu, info]`
- Expose the rows to micromax via a new hostcall:
  - `ed.prompt-suggestion-rows`
- Populate rows for the current built-in completion surfaces where we already have useful context:
  - commands / actions / hooks / keymodes / plugins / macro slots
  - option names with kind/current/default/doc summaries
  - option values with small “current value” hints
  - binding RHS prefixes / embedded `command:` suggestions
  - path suggestions as `file` / `dir`
- Keep plugin-provided completion candidates string-only for now; if they do not supply richer metadata, rows fall back to blank annotations.

**Why this shape**
- Future terminal or GUI layers can show a richer completion list without forcing a UI decision into the headless core.
- Existing tests, keybindings, and prompt behavior remain stable because insertion/cycling still runs on plain strings.
- The row format is tiny, portable, and easy to mirror in future Rust/WASM ports.

**Tests**
- Add focused tests for command suggestion docs, option suggestion metadata, binding-RHS command docs, and file/dir suggestion kinds.



## rev45 (2026-02-26)

### D100 — Add a tiny second layer of quotation combinators in stdlib, not as VM primitives

**Why**
- The current stdlib already proved the pattern with `dip` and `keep`: small quotation combinators can buy a lot of ergonomics without widening the primitive VM surface.
- Factor’s docs are a strong precedent that `2dip` / `2keep` belong in the same “preserving combinators” family, and that `bi` / `tri` can be defined compositionally in terms of simpler words.
- Joy and Retro both reinforce the same broader lesson: a concatenative language becomes much nicer to script once there are a few standard quotation combinators that reduce stack gymnastics.
- This is especially relevant for Micromax because the editor is meant to become the first serious target; config/plugin scripts will benefit from these patterns quickly.

**Decision**
- Extend `src/micromax/stdlib/core.mx` with:
  - `2dip`
  - `2keep`
  - `bi`
  - `tri`
- Keep them as ordinary stdlib definitions rather than VM primitives.
- Record them in the portability ledger as part of the portable stdlib surface.
- Update tutorial/cookbook/examples so future humans/LLMs see these as intended building blocks, not obscure trivia.

**Why this shape**
- Keeps the VM tiny and inspectable.
- Makes the new words easy to port because their behavior is visible in ordinary Micromax source.
- Avoids prematurely committing to a much larger combinator zoo before real editor scripts demonstrate the need.
- Preserves the project rule that convenience words land in stdlib first whenever possible.

**Tests**
- Add focused tests for `2dip` / `2keep` stack behavior.
- Add focused tests for `bi` / `tri` cleave behavior.


## rev46 (2026-02-26)

### D101 — Add doc-first stack-effect introspection instead of a checker

**Why**
- Earlier research already suggested the right ordering: declarations/comments first, interactive inspection second, optional validation last.
- Gforth’s tutorials reinforce that stack-effect comments are baseline readability, not exotic machinery.
- Factor’s reflective tools (`stack-effect`, `infer`, `effect>string`) are a strong precedent for making stack effects available to users and tools even before committing to a heavyweight checking subsystem.
- Micromax now has enough word introspection (`xt-kind`, `xt-src`, `xt-span`, `help`, `see`) that stack effects were the obvious missing piece.

**Decision**
- Add `xt-effect ( xt -- s )` returning a canonical effect string or `""`.
- Tighten `xt-doc` so it returns the descriptive doc text *without* duplicating a leading stack effect.
- Add row-based dictionary inspection:
  - `words-rows ( -- rows )`
  - `wid-word-rows ( wid -- rows )`
  - row shape: `[name kind effect doc wid wl]`
- Teach colon-definition doc capture to split leading stack-effect comments from descriptive comments while keeping ordinary docs simple.
- Update `help` / `see` to show effect + summary separately.

**Why this shape**
- Gives future UIs, scripts, and LLMs a stable inspection surface without forcing checker semantics into the runtime.
- Keeps the VM tiny: effects remain strings, not a new runtime type.
- Makes stdlib words and colon definitions participate in the same tooling story as primitives.
- Preserves the project’s portability story because the row/data surfaces are plain lists/strings.

**Tests**
- Extend introspection tests for `xt-effect` and cleaned-up `xt-doc`.
- Add tests for `words-rows` and `help` output with separated effect/doc text.
- Verify stdlib combinators expose their effect metadata through the same surface.

### D119 — Editor help falls back to visible Micromax words; add `showword`

**Problem**: rev46 added good VM-side metadata (`xt-effect`, `xt-doc`, `words-rows`), but the editor command bar still treated help as if only editor commands/actions were real topics. That made the live environment feel split: language introspection lived in the REPL, editor discovery lived in the prompt.

**Why now**:
- micro’s command-bar docs treat `help` and prompt completion as real discovery surfaces, not just a string parser.
- Gforth’s word index shows the usefulness of presenting words as *rows with metadata* (name, effect, wordset) rather than raw dumps.
- Factor’s help system / `apropos` reinforces that named words should be searchable topics in the live environment.

**Decision**:
- Keep editor `help` behavior stable for editor commands/actions first.
- If no editor command/action matches, fall back to the **currently visible Micromax word** from the active search order.
- Add `showword NAME` as the explicit editor-side inspection command for VM words.
- Extend command-bar completion so:
  - `help` includes visible Micromax word names
  - `showword` completes visible Micromax word names
  - prompt suggestion rows for those topics include best-effort word metadata (`kind`, `wordlist`, `effect`, doc summary)

**Implementation notes**:
- Reuse the VM’s current search order via `find_word_with_wid()` / `all_words_view()` rather than inventing a parallel editor registry.
- Keep the output intentionally small: `word NAME [kind] ( effect ) [wl NAME]: summary (defined at file:line:col)` when data is available.
- Do not attempt a full help browser or word picker yet. This is reflective plumbing and command-bar ergonomics, not UI commitment.

**Tests**:
- `help NAME` falls back to a visible Micromax word and includes effect/doc/provenance.
- `showword NAME` reports the visible word with wordlist/effect/doc/provenance.
- prompt completion for `showword` returns word candidates and suggestion-row metadata.

**Consequence**: the editor now feels more like the actual Micromax environment. Word metadata is available from both the REPL and the command bar, and the next obvious step (if needed) is a small picker/browser on top of the same row data rather than more bespoke plumbing.



### D120 — Add `apropos QUERY` and row-first editor topic discovery

**Context**: rev47 made visible Micromax words first-class help topics (`help NAME` fallback, `showword NAME`), but discovery still assumed you mostly knew the exact topic name already. The roadmap’s next obvious step was “a tiny searchable word/help picker”, but a real picker would have been a UI commitment rather than a headless-core improvement.

**Decision**:

- Add `Editor.help_topic_rows()` returning shared `[[name kind menu info] ...]` rows for command-bar commands, actions, and visible Micromax words.
- Add `Editor.apropos_rows(query)` using the existing tiny deterministic subsequence ranking used by prompt completion.
- Add command-bar command `apropos QUERY` that prints a ranked preview of matching topics.
- Add hostcalls:
  - `ed.topic-rows` — all searchable topics as rows
  - `ed.apropos-rows` — ranked rows for a query
- Let prompt completion treat `apropos` arguments like `help` topics, so exact-prefix and small fuzzy completion still work there too.

**Why**:

- Factor’s `apropos` is the clean precedent: searchable help/word discovery by subsequence before any heavyweight browser.
- Neovim shows that searchable help/index surfaces (`:help`, `:helpgrep`, command indexes) remain useful even without a unified picker abstraction.
- Helix’s fuzzy pickers are a reminder that search-first discovery is ergonomic, but a picker is a *separate* UX layer that should sit on top of stable row data rather than be the first implementation step.

**Consequence**: Micromax-editor now has a search-first discovery surface that stays completely headless and scriptable. Future UIs/LLMs can build a picker/browser on top of `ed.topic-rows` / `ed.apropos-rows` without inventing another metadata path, while ordinary users immediately get `apropos QUERY` in the command bar.


### D121 — Let Micromax completion hooks return suggestion rows

**Context**: rev44 introduced prompt suggestion metadata rows (`[insert kind menu info]`) for built-in completion surfaces, and rev48 added row-first topic discovery. But Micromax-defined completion hooks (`ed.complete.<cmd>` / `ed.complete`) still only returned plain candidate strings, which meant plugin commands looked second-class in any future UI/tooling that wanted docs/kinds/current-value hints.

**Decision**:

- Keep the original completion-hook contract working:
  - `( cmd tok_i prefix toks -- cands mode )`
- Add an optional richer contract:
  - `( cmd tok_i prefix toks -- cands rows mode )`
- `rows` uses the same aligned row shape already used elsewhere in the editor prompt:
  - `[insert kind menu info]`
- When plugin rows are present, overlay them onto the editor's best-effort inferred rows by insertion string.
- When rows are omitted, keep the current fallback behavior: infer what we can from the final candidate list and leave the rest blank.

**Why**:

- Neovim is a clean precedent for structured completion items (`word`, `kind`, `menu`, `info`) that are separate from the popup UI itself.
- Helix's picker/completion docs reinforce that the UI layer should sit on top of stable item metadata rather than be the first implementation step.
- Micromax already had the right row contract internally; the missing piece was simply letting plugin-provided candidates participate in it.

**Implementation notes**:

- `_mx_prompt_completion_candidates()` now accepts both 2-result and 3-result contracts and normalizes rows to at most four strings per candidate.
- `prompt_complete()` still computes its usual built-in/path metadata rows, then overlays plugin rows on top so plugins can either replace blank metadata or deliberately override built-in hints.
- Replace-mode plugin completion clears `path_mode`; path-specific metadata should only come from actual path completion, not be guessed for arbitrary plugin candidates.

**Tests**:

- A plugin completion word can return `cands rows mode` and those rows appear through `ed.prompt-suggestion-rows`.
- Plugin rows can overlay an existing built-in candidate's metadata without duplicating the candidate.
- Existing `cands mode` tests remain green, preserving backward compatibility.

**Consequence**: custom Micromax commands now participate in the same completion metadata surface as built-ins. That makes future picker/tooltip UIs, REPL helpers, and LLM-facing tooling simpler because they can consume one row language instead of special-casing plugin completions.


### D122 — Make `apropos` summary-aware and use it for failed `help` lookups

**Context**: rev48 added `apropos QUERY` and row-first topic discovery, but matching still looked only at the topic name. That meant the command bar had search-first discovery in principle, yet obvious descriptive queries like “visible micromax” or typo recovery from `help shwrd` still underperformed unless the user already knew the right name.

**Decision**:

- Keep `apropos` **name-first** using the existing tiny deterministic subsequence matcher.
- If the topic name does not match, fall back to the row's summary/doc text (`menu` + `info`) before giving up.
- Reuse the same `apropos` ranking path when `help NAME` fails to find an exact command/action/word, and show a short “Try: ...” suggestion list.
- Do not add a picker/browser yet; keep this improvement entirely in the headless command/row layer.

**Why**:

- Neovim's `:help` / `:helpgrep` split is a strong reminder that “look up this exact topic” and “search the help corpus” are distinct needs, and both matter.
- Helix's command palette/picker model reinforces that search-first discovery is useful, but the picker should sit on top of stable search data rather than be the first implementation step.
- Micromax already had the row model (`[name kind menu info]`); broadening the search policy was cheaper and more composable than inventing a new UI surface.

**Implementation notes**:

- `Editor.apropos_rows()` now uses `_apropos_row_sort_key()`:
  - exact/fuzzy name matches rank first
  - summary/doc substring matches rank after that
  - summary/doc fuzzy matches rank after that
- `c_help` now calls `ed.apropos_rows(topic, limit=4)` on an exact-lookup miss and shows a short preview of likely topics.

**Tests**:

- `apropos visible micromax` now finds `showword` by its summary text.
- `ed.apropos-rows` exposes the same behavior through the hostcall surface.
- `help shwrd` now returns a short suggestion list instead of only `No help for: shwrd`.

**Consequence**: command-bar discovery is noticeably more forgiving without adding UI weight. Future pickers/LLM tools still consume the same row-first topic surface, but ordinary users now get better help search and typo recovery immediately.


### D123 — Add a dedicated searchable topic prompt on top of topic rows

**Context**: rev48-50 established the right substrate for discovery (`help_topic_rows`, `apropos_rows`, summary-aware search, and prompt suggestion rows), but there was still no *single headless interaction model* that felt like a command palette/help picker. Future UIs or scripts had to assemble that lifecycle themselves.

**Decision**:
- Add a new prompt kind: `topic`.
- Add `Editor.enter_topic_prompt(query="")` which preloads ranked topic rows into the ordinary prompt suggestion-session model.
- Add command-bar command `topicpick [QUERY]`, action `TopicPrompt`, and hostcall `ed.topic-prompt`.
- Let `Tab` / `Shift-Tab` cycle ranked topic candidates inside the topic prompt using the existing prompt machinery.
- On submit, open help for the selected topic (or the best-ranked topic for the current query).

**Why**:
- Helix treats pickers as a distinct UI with its own keymap, which suggests Micromax should first define the *state machine* cleanly before worrying about terminal rendering.
- VS Code’s Command Palette and Quick Pick guidance reinforce that one searchable surface for commands/topics is valuable, and that each item should carry small contextual metadata (`description`, `detail`) rather than be a bare string.
- Micromax already had the row shape (`[insert kind menu info]`) and ranking path; the smallest useful step was to reuse them in a dedicated prompt kind instead of inventing a separate browser abstraction.

**Implementation notes**:
- `Editor.prompt_complete()` now supports `prompt.kind == "topic"` in addition to ordinary command prompts.
- Topic prompts use `help_topic_rows()` / `apropos_rows()` directly and keep the query text as `suggest_base`, so the first Tab reveals/caches ranked rows and later Tab/Shift-Tab cycles them predictably.
- Topic-prompt submission records topic history under prompt kind `topic`, which means history recalls the submitted selection/query rather than trying to preserve a pre-selection partial query.

**Consequence**: the editor now has a tiny, genuinely usable, search-first discovery prompt without committing to a heavyweight browser UI. Future UIs/LLMs can still consume `ed.topic-rows` / `ed.apropos-rows` directly, but there is now also a canonical headless interaction flow for “open a topic/help picker and choose something.”


## rev52 (2026-02-26)

### D124 — Make the topic prompt live-updating and expose the active suggestion row

**Context**: rev51 added a dedicated `topic` prompt on top of topic rows, but it still behaved too much like ordinary command-line completion: once the query text changed, the suggestion session was cleared and external tooling had no canonical way to ask “what item is currently selected?” That was enough for tests, but not yet a great substrate for a future command palette/help browser.

**Decision**:
- Centralize prompt text mutation through `Editor.set_prompt_text()` so prompt-specific side effects are explicit.
- Preserve existing `find` behavior (`incsearch` still re-runs on text changes).
- Make `topic` prompts re-run ranking automatically whenever the query text changes.
- Add `Editor.prompt_current_row()` and hostcall `ed.prompt-current-row` returning the selected `[insert kind menu info]` row (or `[]`).
- Keep the ordinary `Prompt` data model tiny; do not add a separate preview/browser object yet.

**Why**:
- Helix pickers are interactive filtered lists with their own keymaps, which suggests the core should expose “query changes update the ranked rows” before worrying about terminal rendering.
- VS Code Quick Pick guidance is a strong reminder that items usually want lightweight metadata (`description`/`detail`) and a notion of the *currently active item* even when the picker UI is otherwise simple.
- Vim's completion docs (`completeopt` preview / popup) reinforce that previewing extra information is a downstream UI concern that depends on the current item; that makes “what is the active row?” the right headless primitive, not a hard-coded preview widget.

**Consequence**: the topic prompt now behaves more like a genuine search picker while staying fully headless. Future TUIs/LLMs can render a side preview or statusline detail from `ed.prompt-current-row` without having to duplicate topic ranking or selection logic.


### D125 — Add grouped topic sections and compact current-item previews

**Context**: rev52 made the topic prompt live-updating and exposed the active row, but two obvious follow-ups remained for future UIs/LLMs: (1) many picker UIs want coarse grouping such as commands vs actions vs words, and (2) statuslines/preview panes want a small “current item” summary string without every downstream consumer reassembling one by hand.

**Decision**:
- Add grouped topic-section helpers:
  - `Editor.help_topic_section_rows()`
  - `Editor.apropos_section_rows(query)`
- Expose them as hostcalls:
  - `ed.topic-section-rows`
  - `ed.apropos-section-rows`
- Add compact current-item helpers:
  - `Editor.prompt_current_section()`
  - `Editor.prompt_current_preview()`
- Expose those as hostcalls too:
  - `ed.prompt-current-section`
  - `ed.prompt-current-preview`
- Mirror the same prompt-current fields into the portable status model so future statuslines/infobars do not need bespoke picker plumbing.

**Why**:
- VS Code Quick Pick explicitly supports separators for “multiple obvious groups of selections”, which is a good precedent for exposing coarse sections before building a richer UI.
- VS Code’s command presentation docs also reinforce that command/category grouping is a meaningful discovery aid, not just decoration.
- Helix pickers keep preview behavior as a separate concern (`Ctrl-t` toggles preview), which supports Micromax exposing the *data needed for previews* rather than baking in a preview widget.
- Neovim’s completion model similarly distinguishes short menu text from longer info text and exposes the currently selected completion item structurally.

**Consequence**: the topic/help picker substrate is now noticeably friendlier to inherit. Future TUIs/LLMs can render grouped sections and preview/status text directly from stable host surfaces instead of reverse-engineering ranking output or inventing a parallel grouping model.


## rev54 (2026-02-26)

### D126 — Add a searchable current-binding prompt on top of resolved binding rows

**Context**: rev51-53 established a solid headless substrate for searchable topic discovery (`topicpick`, row metadata, current-item previews, grouped sections). A nearby discovery problem remained on the keybinding side: the editor already had `whichkey`, `showbindings`, and machine-readable binding rows, but there was still no canonical *search-first* flow for inspecting the currently reachable keymap.

**Decision**:
- Add a new prompt kind: `binding`.
- Add command-bar command `bindingpick [QUERY]`, action `BindingPrompt`, and hostcall `ed.binding-prompt`.
- Add `Editor.binding_prompt_rows()` / `Editor.binding_apropos_rows(query)` plus hostcall `ed.binding-prompt-rows`.
- Keep the row shape aligned with the rest of the prompt system: `[insert kind menu info]`, where `insert` is the key, `menu` contains the winning mode + action-spec, and `info` carries the resolved human description.
- Make binding prompts live-refresh on query changes using the same `Editor.set_prompt_text()` path as topic prompts.
- Submitting a binding prompt runs `showkey KEY` for the selected/best-ranked binding.
- Reuse the existing prompt preview/status machinery (`ed.prompt-current-row`, `ed.prompt-current-preview`, status model fields) instead of inventing binding-specific display plumbing.

**Why**:
- which-key-style tools exist because users often need help *discovering current bindings*, not just learning command names once.
- VS Code’s split between Command Palette and Keyboard Shortcuts is a nice reminder that command discovery and binding discovery are distinct searchable surfaces.
- Helix continues to suggest the same implementation order Micromax has been following: item rows + query/selection state first, picker/popup rendering later.

**Consequence**: Micromax-editor now has a genuinely usable search-first binding discovery surface that stays entirely inside the existing headless prompt/session model. Future TUIs/LLMs can render it like a picker or which-key menu later, but the core already exposes the important semantics today.


## rev55 (2026-02-26)

### D127 — Let topic/help and binding discovery handle small multi-term queries across row fields

**Context**: rev48-54 established solid searchable row surfaces for topics and current bindings (`apropos`, `topicpick`, `bindingpick`), but matching still mostly assumed the query was one ordered string. That meant obvious command-palette searches like `word show` or binding searches like `quit Ctrl` underperformed even though the right metadata was already present in the row model.

**Decision**:
- Keep existing single-string matching/ranking as the first path for topic and binding discovery.
- Add a tiny term-splitting fallback for queries with multiple whitespace-separated words.
- For topics, let terms match across the topic name plus summary/doc text.
- For bindings, let terms match across the key, resolved description, and action-spec/menu text.
- Reuse the same ranking path everywhere that already depends on these rows: `apropos`, failed `help`, `topicpick`, `bindingpick`, and the hostcall row APIs.
- Make `help ...` use the full joined query for fallback suggestions rather than only the first token.

**Why**:
- Helix's picker docs point to `fzf`-style filtering, which is a useful reminder that once a surface becomes “picker-like,” users expect multi-term search to work.
- fzf's default extended search mode explicitly supports multiple space-delimited terms.
- The which-key.nvim command-palette request is a nice concrete signal that key discovery becomes much more useful when search can combine description text and keystrokes.
- VS Code Quick Pick continues to reinforce the “label + description/detail” model, which naturally pushes search beyond a single primary string.

**Consequence**: Micromax's search-first help/topic/binding surfaces now feel much closer to a real command palette while staying completely headless and deterministic. Future UIs/LLMs still consume the same row-first APIs; they just get better multi-term ranking out of the box.


## rev56 (2026-02-26)

### D128 — Add a searchable command/action palette on top of the existing prompt row substrate

**Context**: rev48-55 built a solid search-first discovery substrate (`apropos`, `topicpick`, `bindingpick`, row metadata, current-item previews, multi-term matching), but there was still no canonical “find a command/action and do it” flow. Users could discover topics and bindings, yet had to drop back to the ordinary command bar or raw keybindings to actually *invoke* most things.

**Decision**:
- Add a new prompt kind: `palette`.
- Add command-bar command `commandpick [QUERY]`, action `CommandPalette`, and hostcall `ed.command-palette`.
- Add `Editor.command_palette_rows()` / `Editor.command_palette_apropos_rows(query)` plus hostcall `ed.command-palette-rows`.
- Reuse the same `[insert kind menu info]` row shape as topic/binding prompts, but restrict the palette surface to **commands + actions** (no Micromax words).
- Selecting an **action** executes it immediately.
- Selecting a **command** does **not** eagerly execute it; instead it opens the ordinary command prompt prefilled with `name ` so the user can supply arguments deliberately.
- Reuse existing prompt live-refresh, preview, history, and status-model plumbing instead of inventing palette-specific UI state.

**Why**:
- VS Code’s Command Palette is the canonical precedent for “all commands are found here,” and its UX guidance stresses clear command naming/grouping.
- VS Code’s capabilities docs also reinforce that commands are a primary integration surface for editor features and extensions.
- legendary.nvim is a nice Neovim-side reminder that the *semantic registry* of commands/keymaps can be separate from the eventual picker UI.
- micro’s command bar remains the closest ergonomic family member for Micromax, so a good design is one where the palette can still hand off to the ordinary command bar when arguments matter.

**Consequence**: Micromax-editor now has a genuinely useful execution-oriented search surface without abandoning the small headless design. Future TUIs/LLMs can render it like a command palette, but the core semantics are already present: searchable rows, live query updates, current-item previews, action execution, and command staging through the ordinary command prompt.


### D129 — Add MRU-aware command palette sections instead of a heavier picker

**Context**: rev56 added a small searchable command/action palette on top of the prompt row substrate, but it still treated every command/action as equally fresh. Real command palettes become materially more useful once they remember what the user actually picked recently, and future UIs/LLMs also benefit from knowing when an item belongs to a `Recent` bucket rather than a plain command/action group.

**Decision**:
- Keep the existing `command_palette_rows()` data model as the canonical alphabetical command/action registry.
- Add a tiny palette-local MRU of **successful palette selections** (not all editor actions globally).
- Make empty palette queries show MRU items first without duplicating them in the rest of the list.
- Use MRU as a tiebreaker for equivalent palette matches.
- Expose grouped palette sections through `Editor.command_palette_section_rows(query)` and hostcall `ed.command-palette-section-rows`, with labels such as `Recent`, `Commands`, and `Actions`.
- Let `prompt_current_section` / preview / status surfaces report `Recent` when the active palette item comes from that MRU bucket.

**Why**:
- GitHub's Command Palette docs explicitly mention suggestions based on current context and recently used resources.
- Positron's docs say recently used commands appear first, which is exactly the low-friction behavior a tiny headless palette should steal.
- VS Code's command-palette guidance still stresses naming/grouping, which supports surfacing recency as explicit grouped data rather than hiding it in a UI-only sort order.

**Consequence**: the command palette now behaves more like a real daily-driver surface while staying fully headless. Future TUIs/LLMs can render a `Recent` section directly from stable row data, and the core avoids a broader “track every action forever” commitment by scoping recency to actual palette selections.

## rev58 (2026-02-27)

### D130 — Treat `xt-src` as a first-class inspection surface (definition + provenance + compilation)

**Context**: we already have spans (`xt-span`), doc/effect metadata (`xt-doc`, `xt-effect`), and row-based dictionary views. But the “show me what this thing *is*” workflow still often requires jumping between multiple tools (`showword`, `see`, `disasm`) and losing context in headless message streams.

**Decision**:
- Extend `xt-src` so it returns a **multi-line** source-ish rendering:
  - first line is a compact definition-ish form (stable for tooling/tests)
  - following `\\` comment lines optionally include: `effect`, `doc`, `defined at …`, and tier-2 `compiled …` stats
- Teach the editor’s `showword` command to append `xt-src` output so a single inspection message includes both documentation and a decompiled definition.

**Why**:
- micro’s upstream “help topics” lean heavily on deterministic text output; a headless editor needs strong textual inspection primitives before any UI layer exists.
- Debugging and reloadability in a plugin ecosystem improve dramatically when “what is this binding/command/word” is one copy/paste away.

**Consequence**: inspection flows become more ergonomic without adding any heavier UI machinery. Future TUIs/LLMs can treat `xt-src` as the canonical “printable definition” surface and layer richer views on top when needed.

## rev59 (2026-02-27)

### D131 — Prefer row-shaped inspection APIs when we expect UIs (or LLMs) to consume them

**Context**: `xt-src` became a compact, multi-line “source surface”, but any UI wanting syntax-ish treatment (definition vs metadata) would have to parse free-form text. Meanwhile, editor navigation features (like marks) are only truly useful if scripts and headless UIs can enumerate them deterministically.

**Decision**:
- Add `xt-src-rows` to expose `xt-src` as stable `[[text kind span|0] ...]` rows.
- Add editor **named marks** (`mark`/`markjump`/`marks`) and basic multi-buffer navigation (`buffers`/`buffer`) early, and expose them via hostcalls (`ed.marks`, `ed.mark-set`, `ed.mark-jump`, `ed.buffers`, `ed.active-buffer`, `ed.set-active-buffer`).

**Why**:
- Row APIs are the simplest “contract” between a tiny VM and multiple future UIs (TUI/GUI/LLM tooling) without committing to a heavy renderer.
- Marks are a navigation primitive that keeps headless tests meaningful while we delay UI commitments.

**Tradeoffs**:
- Adds a little surface area.
- Some “metadata kinds” are conventions rather than a full schema.

**Mitigation**:
- Keep kinds minimal and obvious (`def/effect/doc/span/compiled/meta`).
- Keep everything best-effort and non-authoritative (tooling surfaces, not compilation semantics).


## rev60 (2026-02-27)

### D132 — Ship searchable pickers for navigation targets early (buffers + marks)

**Context**: We already had a headless command palette (`commandpick`) and row-shaped prompt suggestion surfaces, plus named marks and multi-buffer primitives. But actually using marks/buffers efficiently without a UI meant either memorizing names or typing them perfectly.

**Decision**:
- Add `bufferpick [QUERY]` and `markpick [QUERY]` prompts that reuse the same suggestion-row model as other pickers.
- Teach command-bar completion to suggest buffer names for `buffer` and mark names for `markjump`/`mark`.
- Extend prompt section naming so `buffer` and `mark` rows render with sensible labels (not defaulting to `Word`).

**Why**:
- micro’s ecosystem relies on small plugins (like bookmark/next/prev) for day-to-day navigation, which implies that "searchable navigation targets" are a high-leverage primitive.
- Helix treats the jumplist as a first-class picker surface in addition to back/forward, suggesting that list+picker is a stable UX pattern worth modeling headlessly.

**Consequence**: Navigation workflows (switch buffer, jump to mark) become discoverable and testable via pure data/rows, without any commitment to a terminal UI widget.


## rev61 (2026-02-27)

### D133 — Keep a living worklist and land Tier-0 “real editor” basics

**Context**: The repo had a long roadmap and many good ideas, but it was becoming hard to tell what was *actually missing* for day-to-day editor use versus what was long-term (syntax highlighting, mouse, async tasks, WASM). At the same time, a few “obvious editor keys” (Delete, word jumps, page/document navigation) were missing, and `quit` didn’t warn on unsaved buffers.

**Decision**:
- Add a living priority entry point: `TODO.md` + a detailed tiered list `docs/43-worklist.md`.
- Implement Tier-0 movement/editing basics:
  - forward delete (`Delete`)
  - word jump + word select (Ctrl-Left/Right, Shift-Ctrl)
  - page/document navigation (PageUp/Down using `page.height`, Ctrl-Home/End)
  - `quit` now warns/arms when any buffers are dirty; `quit -f` / `quit!` force
  - add a default `Ctrl-l` binding to prefill `goto` in the command bar
- Add tests that exercise open/save, quit warning semantics, delete, word/page/document navigation.

**Why**:
- A tiny, inspectable project still needs a **minimum viable editing loop** (otherwise all higher-level features are hard to validate).
- A living worklist reduces repeated audits and makes it easier for future humans/LLMs to pick “the next useful thing” confidently.

**Tradeoffs**:
- Adds more default actions/bindings.

**Mitigation**:
- Keep the semantics conservative and UI-agnostic.
- Keep command/binding doc strings stable (tests + discoverability depend on them).


## rev62 (2026-02-27)

### D134 — Unblock real scripting: string hostcalls + lifecycle hooks + filetypes

**Context**: Plugin authors need basic string operations, type checks, and stable event hooks long before we have a full TUI. Also, “hook handlers accidentally depending on prior handlers’ stack effects” is an easy footgun in a concatenative language.

**Decision**:
- Add a reference string hostcall set (`mx.strings`) and install it by default in the editor embedding:
  - hostcalls: `s+ s-len s-slice s-index s-contains? s-split s-join s-replace s-trim s-upper s-lower`
  - editor bridge also defines convenience words with those names in the default wordlist.
- Add typed predicates/conversions as portable primitives: `int? str? list? quote? xt? to-int to-str` and typed string compares `s=`/`s<`.
- Add editor lifecycle hooks: `ed.on-open`, `ed.on-save`, `ed.on-change` (buffer mutation detector).
- Add a minimal filetype detector (extension + shebang) exposed via `ed.filetype` and `status_model()['filetype']`.
- Change hook execution semantics so **each handler runs with the same baseline stack** and stack effects are discarded between handlers.

**Why**:
- Strings are the “glue” type for editor scripting: status messages, prompts, parsing, filetype checks.
- Lifecycle hooks are the smallest useful step toward an ecosystem (formatters, autosave, lint hooks) without over-committing to a complex event system.
- Per-handler stack isolation prevents subtle ordering bugs and makes plugin reload/unload behavior easier to reason about.

**Tradeoffs**:
- Adds surface area (hostcalls + a few core words).
- Hook isolation prevents intentionally pipeline-like hooks.

**Mitigation**:
- Treat hooks as notifications; pipeline composition belongs in explicit combinators or dedicated words.
- Keep the string hostcall set small and well-tested; add richer formatting (`s-format`) later.


## rev63 (2026-02-27)

### D135 — Make it tactile: viewport model + unbound typing + minimal TUI + `s-format`

**Context**: Until you can type into the editor and see the cursor move in something like a real loop, it’s too easy to over-design headless surfaces and under-specify scrolling/movement semantics. Also, plugin authors need a tiny formatting helper to produce usable messages/status text.

**Decision**:
- Store a simple headless viewport model on `Editor`: `(top_line, left_col, height, width)`.
  - Expose it via hostcalls `ed.viewport` and `ed.viewport!` and include it in `ed.status`.
  - After each action, auto-adjust the viewport so the primary cursor remains visible.
- Treat **unbound printable keys** as text input:
  - when a prompt is active, they edit the prompt
  - otherwise, they insert into the buffer
- Add prompt editing actions (`PromptInsertText`, `PromptBackspace`, …) and a reserved `prompt` keymap mode to override arrows/backspace/delete while a prompt is open.
- Add `s-format` hostcall (plus `format` alias word) as a minimal printf-ish formatter (`%s`, `%d`, `%%`).
- Add a minimal curses TUI (`python -m micromax_editor --tui`) implementing input → dispatch → render.

**Why**:
- Viewport + cursor-visibility is the smallest shared scrolling semantics that keeps future TUIs honest.
- Unbound typing is the difference between a “test harness” and something you can actually edit with.
- Prompt editing belongs in the core: it must behave consistently across UIs.
- `s-format` drastically reduces friction for status/messages without bloating the portable kernel.

**Tradeoffs**:
- The `prompt` keymap mode name is now effectively reserved.
- The fallback typing behavior means tests/UIs should use non-printable key names for synthetic inputs when they don’t intend to insert text.

**Mitigation**:
- Keymap lookup still prefers explicit bindings; fallback only applies when a key is truly unbound.
- Document the reserved mode name and keep the TUI explicitly “minimal MVP” until the rendering/span model matures.


## rev64 (2026-02-27)

### D136 — Make it configurable and navigable: `jumppick`, rc/init, and load-path conventions

**Context**: We now have a minimal TUI loop and a viewport model, so navigation history and config become immediately useful. Also, plugin distribution needs a predictable way to locate supporting files without hardcoding absolute paths.

**Decision**:
- Add a searchable **jumplist picker**: `jumppick [QUERY]`.
  - prompt kind: `jump`
  - newest-first rows with position + line preview
  - restore an explicit jumplist entry via `Editor.jump_to_index()`
- Add **user init/rc loading** at editor startup:
  - default: `~/.config/micromax/init.mx`
  - override: `$MICROMAX_INIT`
  - loaded after plugins so user config can override
- Define a small **`include`/`require` search convention** in the VM:
  - relative-to-caller source directory (best-effort via `vm.last_span`)
  - current working directory
  - host-provided `vm.load_paths`
  - `$MICROMAX_PATH` (os.pathsep-separated)
- Make plugin loading more robust:
  - plugin init failures do **not** abort `load_tree`
  - errors are recorded (`PluginManager.load_errors`)
  - best-effort cleanup removes leaked hooks/commands/bindings for failed plugins
- Improve minimal TUI usability for pickers by showing the current picker selection preview inline on the prompt line.

**Why**:
- `jumppick` turns an internal navigation structure into a usable tool.
- A user init file is foundational for a “live environment” editor.
- A load-path convention enables plugin/library sharing without baking in absolute paths.
- Non-fatal plugin loading prevents “one bad plugin bricks startup.”
- The TUI preview is the smallest UI affordance that makes pickers workable without building a full dropdown renderer yet.

**Tradeoffs**:
- `require`/`include` semantics are slightly more complex than “open a path.”
- The caller-relative resolution is best-effort (depends on spans).

**Mitigation**:
- Keep the resolution order short and deterministic; document it (`docs/88-require-and-paths.md`).
- Preserve the ability for hosts to override policy via `vm.load_paths`.


## rev65 (2026-02-27)

### D137 — Micro-esque indentation + tab insertion semantics

**Context**: Enter/Tab are the two highest-frequency editing keys. If they feel wrong, the whole editor feels wrong.

**Decision**:
- Implement auto-indent on newline by copying the current line’s leading whitespace onto the new line.
  - Avoid *double indentation* when splitting before/inside an indent prefix by only copying the portion of the indent that lies to the left of the cursor.
- Add micro-style tab options:
  - `tabsize` (int, default 4)
  - `tabstospaces` (bool, default true)
  - `InsertTab` inserts a literal `\t` when `tabstospaces=false`, otherwise inserts spaces to the next tab stop.
  - Space insertion aligns by **visual column**, accounting for existing tabs on the line.

**Why**:
- Copy-indent-on-newline is the smallest, predictable autoindent that works across languages.
- `tabsize`/`tabstospaces` are common editor muscle memory and match micro naming.
- Visual-column-aware tab alignment avoids “mystery off-by-some-spaces” behavior when a file already contains tabs.

**Tradeoffs**:
- This is not language-aware indentation (no “indent after :” yet).
- The headless model is character-based; tab rendering is a UI concern, so visual column is best-effort.

**Mitigation**:
- Keep the policy extremely small and deterministic; grow to language-aware indent only once we have a syntax-span model.
- Unit tests cover split-at-BOL, inside-indent, and tab alignment edge cases.


## rev66 (2026-02-27)

### D138 — Syntax highlighting as a portable span model

**Context**: We want syntax highlighting without locking the core to a terminal/color library.

**Decision**:
- Define syntax highlighting as *per-line spans*: `[[start_col end_col tag] ...]`.
- Expose it through editor hostcalls:
  - `"ed.highlight" hostcall` → spans for a line range
  - `"ed.highlight-tags" hostcall` → the tag vocabulary
- Ship a tiny default highlighter for `filetype=micromax` that handles strings, comments, numbers, and def names.

**Why**:
- The UI can map tags to colors later (curses, tui, wasm, etc.) without changing plugins.
- Spans are easy to test and reason about, and they compose naturally with later features (pair highlights, search matches, trailing ws, etc.).

**Tradeoffs**:
- The first highlighter is intentionally line-local (no multi-line state).

**Mitigation**:
- Keep the tag vocabulary small and stable; allow richer highlighters later.


### D139 — Timers as a deterministic, thread-free queue

**Context**: Plugins need debouncing/autosave without spawning threads or relying on real time in tests.

**Decision**:
- Add a tiny timer queue owned by the editor and driven by the host event loop.
- Expose three hostcalls:
  - `"ed.after"` schedules a quotation to run after N ms
  - `"ed.cancel-timer"` cancels a timer id
  - `"ed.pump-timers"` runs due timers and returns how many executed
- Timer callbacks run like hooks: stack-isolated and best-effort (errors become messages).
- Plugin unload cancels timers belonging to that plugin’s registration group.

**Why**:
- Deterministic in tests (injectable clock), simple in the TUI loop, and keeps the VM substrate tiny.

**Tradeoffs**:
- Timers are cooperative: nothing runs unless the host pumps.

**Mitigation**:
- Pump timers in every UI tick (curses loop already does this).


## rev71 (2026-02-28)

### D151 — Softwrap is a visual-row world

**Decision**: When `softwrap=true`, vertical movement and scrolling should operate on *visual rows*
(wrapped fragments), not logical lines. This matches what many editors do when wrap is enabled
(e.g. micro's cursor movement within a wrapped line).

**Implementation shape**:
- Add `viewport_top_subline` and treat the viewport start as `(top_line, top_subline)`.
- Keep `view_rows` / `cursor_view_pos` as the shared headless rendering contract.
- Preserve a per-cursor "goal x" for vertical motions so movement feels stable across short wrap rows.

### D152 — Plugin manager should be scriptable + errors should surface

**Decision**: Plugin management isn't just a UI concern; scripts should be able to query/reload plugins and inspect
load/dependency errors.

**Implementation shape**:
- Hostcalls: `plugin.list`, `plugin.reload`, `plugin.errors`.
- CLI command `plugin list` prints recent captured load errors.
- `PluginManager.reload()` must respect `plugin.json`'s `entry` field.


## rev72 (2026-02-28)

### D153 — Statusline format strings should be micro-compatible

**Decision**: implement `statusformatl`/`statusformatr` as micro-esque `$()` directive templates.

**Why**:
- imports configuration muscle-memory from micro (and keeps the split left/right model)
- keeps the default TUI deterministic while still allowing customization

**Shape**:
- a tiny renderer (`src/micromax_editor/statusformat.py`) with compatibility directives (`filename`, `modified`, `line`, `col`, `lines`, `percentage`, `opt`, `bind`, `overwrite`) plus a few editor-specific helpers (`readonly`, `sel`, `cur`, `keymode`, `macro`).

### D154 — Cleanup belongs in stdlib (`ensure`/`finally`)

**Decision**: add an always-run cleanup combinator in the stdlib rather than adding VM primitives.

**Why**:
- keeps the VM kernel small and portable
- `catch`/`throw` already provide the needed semantics (stack restoration + error propagation)

**Semantics**:
- `cleanup` runs regardless of success/failure
- on failure, `cleanup` runs with the pre-body stack (because `catch` restores)
- if `cleanup` fails, it overrides the body error

## rev70 (2026-02-28)

### D00X — Keep exception ergonomics in stdlib, not primitives
**Decision**: add `try?`, `try`, and `recover` as stdlib combinators built on `catch` + `last-error`, rather than adding new VM primitives.

**Why**: keeps the core VM small/portable (Rust/WASM), while still making the common “recover” pattern pleasant.

**Notes**: this matches the spirit of Forth’s minimal exception core (`CATCH`/`THROW`) plus library-level sugar.

### D00Y — Provide a reference statusline formatter
**Decision**: add `Editor.statusline_text(width)` as a deterministic baseline formatter, and have the minimal TUI use it.

**Why**: UI layers should use `status_model()` for structure, but a shared formatter reduces drift and gives tests a single, stable target.



### rev74 — Safe buffer lifecycle + recent files MRU

- **Problem:** `open` previously clobbered an already-open buffer with the same name, which could silently drop unsaved edits.
- **Decision:** Treat `open` as *switch-if-open* (dedupe by normalized `Buffer.path`). A separate explicit `reload`/refresh path can exist later.
- **Additions:**
  - `close` / `close!` to close buffers with a dirty-buffer double-tap guard (mirrors `quit`).
  - Recent-files MRU tracked headlessly (`recent` / `recentpick`) plus hostcalls `ed.recent` / `ed.recent-clear`.
  - Resource helper `ed.with-viewport` (save/restore viewport around a quotation).
- **Why:** This matches common editor expectations (buffers are durable; open should not discard changes) and makes plugin/UX flows (switching files, picker-based navigation) easy to validate headlessly.



## rev75

- Added a tiny buffer MRU to make `close` and `prevbuf` feel predictable (MRU wins over dict order).
- `commandpick` now also surfaces `Recent Files` and can open them directly, while keeping commands staged and actions immediate.
- Recent files can be optionally persisted to `~/.config/micromax/recent.json` when `recent.persist=true` (loaded after user init).
- Added `plugins/capdemo` as a living example of `host.feature?` capability checks.


## rev76

- **Docs-backed help buffers:** `help TOPIC` now falls back to opening a matching `docs/*.md` page into a protected read-only buffer (plus a dedicated docs picker: `helppick`).
- **Protected buffers:** added a small "protected" flag (`local_options['readonly']`) used to reject mutating editor actions/commands for internal buffers.
- **TUI picker list:** the curses TUI now renders a small suggestion list under the prompt line, including section headers when they can be inferred.


## rev77

- **Docs navigation helpers:** help buffers gained `helpfollow` (follow a markdown link under the cursor) and `helpback` (return to the previous docs page), backed by a tiny in-editor stack.
- **Picker UX polish:** the curses TUI suggestion list gained scroll windowing with "more" markers, and uses basic terminal attributes (reverse for selection, bold for headers).


## rev78

- **Docs browser polish:** help/docs buffers now get lightweight link highlighting in the TUI (underline link labels; bold-underline when the cursor is on a link).
- **Link list / picker:** added `helplinkpick` to pick from links on the current docs page.
- **Capability registry:** added a tiny capability registry (`host.capabilities`) and editor options `cap.*` to gate unsafe host surfaces.
- **Unsafe surfaces (gated):** external docs links can open via `cap.open-url`; a minimal `ed.shell` hostcall exists behind `cap.shell`.


## rev79

- **Docs outline / headings picker:** added `helpoutlinepick` to navigate a docs page by headings, plus hostcalls `ed.help-outline-rows` and `ed.help-link-rows` for plugins and tooling.
- **Markdown affordances in TUI:** headings in docs buffers are now rendered in bold (links still underline as before).


## rev80

- **Docs-as-browser keybindings:** in help/docs buffers, `Enter` follows the link under the cursor and `Backspace` goes back (browser-style convenience).


## rev81

- **Capability-gated file reads:** added `ed.fs-read` behind `cap.fs-read` (UTF-8, size-limited) to support safe plugin tooling without implicit host access.
- **Docs quick-jump:** added `helpjump` as a direct heading jump command (and outline picker shortcut), making docs navigation faster than always picking.
- **Picker grouping polish:** buffer and plugin picker rows are now grouped into contiguous sections (help/scratch/dirs; errors/loaded/available), and the TUI indents outline items by heading level for readability.


## rev82

- **Docs browser polish:** `helplinkpick` suggestions are now grouped into Docs/Files/External sections, and this grouping is also exposed headlessly via `ed.helplink-section-rows`.
- **TUI debugging affordance:** added `rawkeys` to show raw terminal key events for binding/debugging.


## rev83

- **Markdown link support:** docs navigation recognizes reference-style links (`[text][id]` + `[id]: target`) and autolinks (`<https://...>`), both for `helpfollow` and the link picker.


## rev84

- **Docs page navigator:** added `helpnavpick`, a combined headings+links picker for the current docs page.
- **Headless nav surface:** added `ed.helpnav-section-rows` (grouped headings + grouped link sections) so future UIs/scripts can reuse the same navigator substrate.


## rev97

- **Docs link picker sections by heading (optional):** `helplinkpick` (and `ed.helplink-section-rows`) can now group links by the nearest markdown heading via `help.linksections heading` (default remains Docs/Files/External).
- **Filesystem metadata helper (gated):** added `ed.fs-stat` behind `cap.fs-stat` to support safe file-picking scripts without giving write access.
- **Archive packaging helper:** added `tools/mkrevzip.py` so offline checkouts can generate standard-named `Micromax-rev####-YYYY.MM.DD.HH.MM-<tag>.zip` archives reproducibly.
