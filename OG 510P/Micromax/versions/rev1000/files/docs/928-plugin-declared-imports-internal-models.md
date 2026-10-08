# Declared plugin imports and internal host models (rev0972)

## Why this was the risky next step

Micromax already had strong package-byte, grant, reload, rollback, unload,
revocation, and delayed-callback work, but its executable extension boundary was
still wider than its metadata implied. `plugin.json requires` influenced load
order without defining the names a plugin could actually resolve. Source,
lifecycle words, and delayed callbacks inherited ambient VM search order, and a
plugin that knew another module name could switch into that wordlist and define
there. The trusted Python bridge also advertised exact renderer snapshots to
plugin code even though only the host, headless consumer, and TUI need them.

Building a process or WebAssembly host on top of that surface would have frozen
accidental authority. Rev0972 therefore reduces the live in-process interface
first. It does not add an isolation process and does not claim malicious-code
containment.

## Findings and corrections

| Finding | Consequence | Correction |
|---|---|---|
| Plugin execution inherited ambient search order | An undeclared sibling could satisfy a source, lifecycle, or delayed callback lookup | Every plugin generation now gets one exact order: self, declared dependency closure, then Forth |
| `requires` described scheduling but not imports | Metadata and execution authority disagreed | The loaded dependency closure is now the readable namespace contract |
| `use`, `in`, `set-current`, `set-order`, and raw dictionary mutation were separate bypasses | A plugin could inspect or write an undeclared wordlist, or a future primitive could forget a preflight | Core words preflight access and `VM._add_word()` enforces writes at the mutation point |
| A visible dependency `defer` could be rebound with `is` or `defer!` | Read authority silently became behavior-replacement authority | Every word is stamped with its owning wordlist; deferred mutation requires write authority for that owner |
| Plugin code could create modules/wordlists | One plugin could grow ambient namespace topology that later plugins accidentally consumed | Wordlist/module creation is internal during explicit plugin execution |
| `hooks` listed event words from every wordlist | Undeclared sibling names leaked even when execution lookup was constrained | Hook inventory is filtered to the active readable closure |
| Exact statusline, prompt, screen, viewport-row, gutter, and display models were advertised to plugins | Extensions could couple to renderer internals and receive more state than an eventual component import needs | Exact presentation models are hidden from feature probes and denied for plugin-originated execution; trusted host use is unchanged |
| Namespace context parameters could be partially supplied | A caller could appear scoped while omitting the actual readable/writable sets | Plugin identity now requires explicit readable and writable wordlist sets before any context mutation |

## Executable namespace contract

For a loaded plugin `P`, source evaluation, `preinit`, `init`, `postinit`,
`deinit`, commands, keybindings, timers, hooks, and other retained callbacks use
the same rules:

1. `CURRENT` is `P`'s wordlist.
2. Read order is `P`, all direct `requires` entries in manifest order, then their
   transitive dependencies breadth-first, then Forth.
3. Direct dependencies precede transitive implementation words. This prevents a
   dependency-of-a-dependency from shadowing an explicitly imported package.
4. Only `P`'s wordlist is writable.
5. Ambient loaded siblings are neither readable nor enumerable.
6. New wordlists/modules are refused.
7. The previous trusted VM order, current wordlist, plugin identity, and scope
   are restored after success or failure.

The transitive closure is necessary because Micromax word references are late
bound. When code defined by dependency `A` calls one of `A`'s own declared
imports, that import must remain resolvable while `A` is executing on behalf of
`P`.

The write guard is deliberately duplicated at two levels. User-facing namespace
words fail before consuming their operands where practical, producing useful
errors. `VM._add_word()` remains the authoritative final check so a later
primitive cannot bypass the boundary merely by changing `CURRENT` directly.
Word ownership extends that rule to mutable deferred behavior. Wordlist
allocation follows the same mutation-point rule: `VM.new_wordlist()` checks
creation authority before changing the allocator counter, dictionaries, or
names, even when a future primitive calls it without a source-level preflight.

## Host surface classification

Rev0972 adds a deliberately small executable classification, not a second copy
of the full hostcall registry:

- **stable** — lifecycle names and the product-proven calls used for messages,
  command/key registration, timers, package-local source, options, recent rows,
  line/cursor/selection/range mutation, and grouped undo;
- **experimental** — every other editor hostcall by default; usable today but not
  promised as a future process/component ABI;
- **internal** — exact host-owned presentation snapshots such as
  `ed.screen-model`, `ed.screen-rows`, `ed.display-rows`,
  `ed.statusline-model`, `ed.statusline-text`, `ed.prompt-panel`,
  `ed.prompt-window`, `ed.prompt-display`, gutter/edit-window/viewport rows,
  bottom-row models, and `ed.docs-cues`.

Internal calls remain registered because the trusted headless and TUI host use
the same Python bridge. During explicit plugin execution, however,
`host.feature?` returns false, `host.features` omits them, and an exact call fails
before consuming the call name or model arguments. This is a real authority
reduction rather than a documentation label.

## Deliberate capability exceptions

This is a namespace boundary, not deep object freezing. A dependency may
intentionally return a mutable `Cell`, list, map, or other portable value; that
returned object is an explicit object capability and remains mutable by the
recipient. Shared hook events are also intentional extension points: plugins may
append their own provenance-stamped handlers to visible hooks, while existing
handler read/fire/remove/clear rules still protect other origins and unload
cleanup.

A deferred word is different: merely resolving or executing it should not imply
permission to replace its behavior. `is` and `defer!` therefore require write
access to the word's owning dictionary even when the execution token is already
on the stack.

## Research checked 2026-07-18

Current extension systems separate a public import contract from host internals
before or alongside isolation:

- Visual Studio Code distinguishes stable API from proposed API; proposed APIs
  may change and are not available to ordinary published extensions. Its
  extension-host architecture also isolates extension impact from the main UI
  process and supports lazy activation.
  <https://code.visualstudio.com/api/advanced-topics/using-proposed-api>
  <https://code.visualstudio.com/api/advanced-topics/extension-host>
- The WebAssembly Component Model's WIT `world` explicitly names the exact
  imports a component may use and exports it provides. That is the useful future
  shape for Micromax: define the world before choosing the process boundary.
  <https://component-model.bytecodealliance.org/design/worlds.html>
  <https://component-model.bytecodealliance.org/design/wit.html>
- Zed compiles procedural Rust extensions to WebAssembly and instructs extension
  packages to include only necessary resources and stay inside the designated
  environment.
  <https://zed.dev/docs/extensions/developing-extensions>
- Wasmtime stores can add fuel, resource limiters, and call hooks. Those are
  valuable later resource controls, but they do not decide which editor models
  or namespace imports should exist in the first place.
  <https://docs.wasmtime.dev/api/wasmtime/struct.Store.html>

Micromax adopts the interface lesson, not another project's architecture. The
current implementation stays in-process so the reduced contract is exercised by
real product journeys before an isolation mechanism fossilizes it.

## Refactor and evidence

The change centralizes only three small ownership points:

- `WordlistAccessScope` in the host-neutral VM;
- plugin dependency/order planning in `PluginManager`; and
- plugin host-surface policy in `plugin_contract.py`.

Source, lifecycle, and delayed callback paths all consume those owners. Focused
regressions cover undeclared imports, dependency write attempts, deferred-word
mutation, raw `set-current`, mutation-point fail-closed behavior, transitive
late binding, direct-over-transitive precedence, hook-name disclosure, internal
model probes/calls, partial-context rejection, ambient-order contamination,
rollback, reload, revoke/unload cleanup, package-local includes, stale callback
generations, and hostcall stack preservation.

## Boundaries and next risk

- All plugin code still executes in the editor's Python process. It can consume
  CPU or memory and can exploit defects in any reachable primitive/hostcall.
- `experimental` is not a denial. The next interface reduction should follow an
  actual consumer or authority problem, not a drive to label every row.
- Mutable values deliberately exported by a dependency remain capabilities; no
  recursive freeze or object membrane exists.
- Hook registration is intentionally shared and remains governed by provenance,
  generation, and cleanup policy rather than dictionary ownership.
- There is no durable third-party compatibility promise, per-plugin Wasm world,
  syscall sandbox, or hostile-code containment claim.

The specialized line-edit geometry failure found immediately after this audit is
repaired in `docs/929-line-edit-source-plan-selection-boundary.md`. The next
plugin-boundary decision should begin with a measured CPU, memory, crash,
native-call, or fault-containment failure. A process/Wasm extension host should
import this reduced contract rather than the trusted Python bridge wholesale.
