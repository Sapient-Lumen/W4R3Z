*rev198 follow-up:* the JSON corpus now also pins down that deleting a missing map key leaves existing entries intact, so future hosts do not need to infer that small mutation/no-op contract only from Python tests.


# Portability ledger (Rust/WASM)

*rev197 follow-up:* the JSON corpus now also pins down another already-promised map behavior: `m@` returns `0` for a missing key, so future hosts do not need to infer that contract from Python tests alone.


This file is the *contract* that keeps the Python reference VM from drifting away from the eventual Rust/WASM VM.

Anything in the **portable kernel** must have an obvious Rust/WASM implementation.
Anything outside it must be explicitly marked as **reference-only** or **host-provided**.

## 1) Portable kernel (rev14)

These categories should remain small and stable.

### Stack + return stack
- `dup drop swap over rot`
- `>r r> r@ rdepth`

### Control / execution
- quotations: `[ ... ]`
- `call` (execute a quotation)
- `execute` (execute an XT)
- `'` (push XT)
- `if when while`

### Arithmetic / comparison (int-only)
- `+ - * / mod`
- `= < >`
- `0=` (may become stdlib later)

### Memory / state
- `cell` via `variable/constant` (Cells)
- `@ !`

### Collections (lists)
- `list push pop len nth set-nth clone`

### Type predicates + conversions
- `int? str? list? map? quote? xt?`
- `to-int to-str`
- `s= s<` (typed string comparisons)

### Collections (maps)
- `map map? m@ m! m? m-del m-keys m-items m-merge`
  - policy: keys are strings in portable mode

### Dictionary + compilation
- `find` (string name -> xt|0)
- `dict-version` (global dictionary/search-order version; used for tier-2 cache invalidation; lookup-only operations like successful `find`, `get-order`, `get-current`, `host.api-version`, `host.feature?`, or `host.features` should not bump it)
- `compile` / `compiled?` (tier-2 tooling; optional but portable)

### Namespaces + module hygiene
- `wordlist set-current get-current set-order get-order`
- `only also previous definitions`
- `module endmodule use in modules` (portable, but can be stubbed in tiny embeddings)

### Errors + safety
- `catch throw`
- `last-error last-error.`
- `set-budget budget with-budget` (step budget; portable)

### Host boundary
- `hostcall`
- `host.api-version host.feature? host.features`
- `host.capabilities` (optional registry; hostcall)

### Locals sugar (portable but optional)
- `locals local@ local? local! unlocal locals-clear`

## 2) Stdlib words (loaded at boot)

These are defined in `src/micromax/stdlib/core.mx` and are intentionally *not* VM primitives.

- `nip tuck 2dup 2drop`
- `rdrop`
- `dip keep 2dip 2keep bi tri`

Rule: new convenience words should land in stdlib first unless there is a strong reason.

## 3) Reference-only (allowed to diverge)

These are useful for hacking and debugging, but are not required in a minimal embedded VM:

- printing/debug: `. cr emit .s words see help where order disasm`
- introspection helpers: `words-list words-rows wid-words wid-word-rows wid-name` (useful for tooling; optional in tiny embeddings)
- xt introspection: `xt-kind xt-effect xt-doc xt-src xt-src-rows xt-span here-span` (optional; helpful for tooling and docs)
- hook inspection: `hook-rows`, `hook-detail`, `hook-groups`, and best-effort hook spans are tooling-oriented (optional)
- hook grouping: `hook-group! hook-group@ hook-rm-group` are optional portability-friendly cleanup helpers
- tier-2 inline caching is keyed by `dict-version` (implementation detail; portable to Rust/WASM)
- tier-2 bytecode uses a constant pool (instruction operands are indexes into `consts`)
- tier-2 bytecode supports tiny control flow (`JMP`/`JZ`) and direct quotation calls (`CALL_Q`); jump operands are signed relative instruction offsets
- bytecode JSON serialization (`bytecode-json` / `bytecode-load-json`) is tooling-oriented (optional)
- convenience stack ops: `pick roll clear` (may move in/out depending on needs)
- any direct filesystem access baked into the VM (prefer hostcalls)

## 3b) Editor host surface (host-provided; must stay "portable on the wire")

The editor's hostcalls are not VM primitives, but their *data representations*
must stay portable (ints/strings/lists only).

- cursors are `[[line col] ...]` in document order
- primary cursor is an integer index into the cursor list
- selections are `[[aL aC cL cC] ...]` (directed anchor/cursor) or `[]` for none
- cursorstate snapshots are `[primary [[id line col aL aC] ...]]` with `aL/aC = -1/-1` for none
- messages are `["...", ...]` (list of strings); exposed via `ed.messages` / `ed.pop-message` / `ed.clear-messages` / `ed.with-messages` / `ed.capture-messages`
- statusline/infobar state is a string-keyed map returned by `ed.status` (see `docs/69-editor-statusline-model.md`)
- viewport state is a string-keyed map returned by `ed.viewport` and set by `ed.viewport!` (top/left/height/width)
- macros are a list of tagged steps: `["a", ACTION, [[key val] ...]]` for actions and `["c", CMDLINE]` for commands (see `docs/58-editor-macros.md`)
- clipboard text is a string (may include trailing newline when linewise)
- clipboard items are `["...", ...]` plus a kind string: "items"|"lines"
- selection recovery stack is host-local (no wire format; exposed only via push/pop hostcalls)
- jumplist is host-local (cursor/selection snapshots); exposed via push/jump hostcalls and `ed.jump-info` returning `[index size]`
- editor command metadata can be exposed as `[[name doc group|0 [file line col]|0] ...]` (tooling-oriented)
- editor binding metadata can be exposed as `[[key action-spec group|0 [file line col]|0] ...]` (tooling-oriented)
- binding descriptions are plain strings and can be exposed as `desc|0` fields in keymap rows
- keymode rows can be exposed as `[[mode once?] ...]` with `once?` as `0|1`; `ed.press-key` is a host convenience wrapper around key dispatch
- keymap discovery can be exposed as `ed.binding-rows-for`, `ed.available-bindings`, `ed.resolve-key`, plus description-rich siblings (`ed.binding-info-for`, `ed.available-binding-info`, `ed.resolve-key-info`), using only strings / ints / lists
- editor registration grouping via `ed.group!` / `ed.group@` is an optional cleanup/debugging helper

### 3c) Reference host helpers (host-provided)

These are not VM primitives. Editor embeddings install them as hostcalls and
also define convenience words that call them.

- string helpers: `s+ s-len s-slice s-index s-contains? s-split s-join s-replace s-trim s-upper s-lower s-format`

## 4) Policy for adding surface area

Before adding a primitive or hostcall, record:

- **category**: kernel / stdlib / host / reference-only
- **porting plan**: how it works in Rust/WASM
- **tests**: at least 2 targeted tests
- **docs**: stack effect + 1 example


- prefix maps are represented as ordinary key bindings whose action-spec enters a one-shot keymode (`command:prefixmode MODE`); `ed.bind-prefix` and `ed.bind-mode-prefix` are convenience sugar, not new binding classes.


## 5) Portability corpus

The repo now carries a tiny **JSON portability corpus** in `portability/kernel_cases.json`.

Purpose:
- capture a few stable, data-only expectations for the portable kernel + boot stdlib
- make it easy for future Rust/WASM ports to validate semantics without importing Python-specific pytest helpers
- keep the corpus small enough to evolve by hand when the language grows

Runner surfaces:
- library: `src/micromax/portability_suite.py`
- CLI: `tools/mxportable.py`
- tests: `tests/test_portability_suite.py`

Runner/CLI policy:
- corpora should fail fast on duplicate names, missing categories, or malformed expectations
- optional `tags` are allowed for coarse-grained grouping (for example `namespaces`, `recovery`, `combinators`)
- the CLI now supports targeted bring-up runs via `--category`, `--tag`, exact-name `--name`, `--name-contains`, `--list`, and `--inventory`
- the CLI also supports `--json` so selected cases/results or inventory views can be consumed mechanically during host bring-up

Policy:
- prefer corpus cases for behavior that is part of the **portable kernel** or boot stdlib
- corpus cases may also optionally include `host_features: ["..."]` to seed the VM feature inventory before evaluation, keeping positive host-boundary probes data-only instead of baking them into the runner
- current examples now include kernel arithmetic/control/modules plus `0=`, successful and failing `catch`, `while`, `when`, return-stack basics, `execute`, `constant`, `variable`, typed predicates, typed string ordering via `s<`, `find` success/missing behavior, `dict-version`, lookup-only `find` + `get-order` + `get-current` stability around `dict-version`, `compile`/`compiled?` positive + primitive-negative behavior, `host.api-version`, positive + missing `host.feature?`, `host.feature?` lookup-only `dict-version` stability for both present and absent probes, bare-VM and seeded `host.features` plus `host.features` lookup-only `dict-version` stability, list clone/pop isolation, `to-int`, `to-str`, map mutation/inspection (`m?`, `m!`, `m-del`, `m-merge`, `m-keys`, `m-items`), locals shadowing plus session-local query/removal, wordlist/search-order lookup, same-wordlist latest-definition precedence, `get-current`, `set-current`, the fact that `set-current` alone does not add a wordlist to the search order, `get-order`/`set-order` round-tripping, `definitions` including persistence across later `set-order` changes, `also`, `previous`, `only`, duplicate-name search-order precedence, `in`, and boot-stdlib combinators/recovery helpers (`bi`, `dip`, `2dip`, `2keep`, `tri`, `try?`, `try`, `recover`, `ensure`, `finally`) plus a budget-exhaustion case observed through `catch`
- prefer broad but simple tags (`memory`, `locals`, `combinators`, `namespaces`, `budget`, etc.) so corpus slices stay easy to inspect during Rust/WASM bring-up
- keep cases data-only (`source`, expected stack, or expected error substring)
- avoid host-specific side effects or non-portable runtime objects in corpus expectations

- rev199 follow-up: the JSON portability corpus now also pins down that `m-keys` returns an empty list for an empty map, keeping the map-inspection contract explicit for future hosts.


- `m-items` on an empty map returns `[]` (not `0`, null, or an omitted value).


- rev202 portability follow-up: the JSON corpus now also covers `m-merge` with an empty destination map adopting the source pairs (`map-merge-empty-destination-adopts-source`).


- The tiny JSON portability corpus now also covers the negative `m?` case (`map-has-missing-key-is-false`) so future hosts pin down that missing-key predicates return `0`.


- rev204 portability follow-up: the JSON corpus now also covers overwriting an existing map key updating its value (`map-store-overwrite-updates-value`).
