# Research notes (selected inspirations)


Rev60 note: Helix explicitly exposes a **jumplist picker** UI (`Space-j`) in addition to back/forward navigation, which is a strong argument for making our navigation targets row-shaped and searchable from day one. Kakoune discussions around marks storing full selections also suggest a future extension where marks can capture multi-cursor state, not just a single cursor.

This is a curated set of ideas we’re borrowing from / reacting to.

## micro editor (target UX baseline)

micro’s philosophy is “modern terminal editor with sane defaults” and includes
common keybindings, a menu, multi-cursor, and a plugin system (Lua + plugin manager).

**Takeaway for micromax**: keep a “nano-like” discoverability layer, but make the
extension language our core differentiator.

References:
- micro repo / feature list: https://github.com/micro-editor/micro
- micro website (plugin system): https://micro-editor.github.io/

## “Forth as the plugin language” has precedent

Forth has been used as an interactive *embedded control language* in real systems:

- **Open Firmware (IEEE 1275)** exposes a Forth CLI, and even supports a compact
  bytecode form (FCode) used for device drivers.
  - https://en.wikipedia.org/wiki/Open_Firmware
  - https://www.devicetree.org/open-firmware/home.html

- **FreeBSD boot loader** historically embeds a Forth interpreter (via FICL) as one
  of its built-in configuration/script interpreters.
  - https://man.freebsd.org/loader
  - FICL overview: https://ficl.sourceforge.net/ficl.html

**Takeaway**: “Forth as a plugin/config language” is *not* an eccentric idea; it
has proven value where interactive debugging + extensibility matter.

## Forth standard (scope boundary)

Forth-2012 defines a small required “Core” word set and organizes everything else into
optional word sets. This “word-set modularity” matches our goal: small kernel, add-ons.

References:
- Core wordset glossary: https://forth-standard.org/standard/core
- Search-Order word set (wordlists + search order): https://forth-standard.org/standard/search

## “Hacker-level Forth”: metaprogrammable control flow

Classical Forth’s deeper magic is that control flow is “just words” cooperating during
compilation. Implementations that keep a linked dictionary and a threaded code model make
it easier to reach this “hacker level”.

Reference:
- Eli Bendersky, *Implementing Forth in Go and C* (user vs hacker-level distinction):
  https://eli.thegreenplace.net/2025/implementing-forth-in-go-and-c/

## Namespacing: wordlists + search order

Modern Forth systems use wordlists and a search order (a stack/list of wordlists) to
control name resolution and keep domains from colliding.

References:
- Forth-2012 Search-Order word set: https://forth-standard.org/standard/search
- Gforth manual: wordlists overview: https://gforth.org/manual/Word-Lists.html

## colorForth: reducing hidden state

Chuck Moore experimented with removing the traditional `STATE` mechanism by attaching
attributes to words so parsing/compilation is less context-sensitive.

Reference:
- Discussion of colorForth removing `STATE` and word-tied attributes:
  https://langdev.stackexchange.com/questions/1170/is-colorforths-unique-syntactic-approach-helpful-to-the-programmer

## Factor: quotations + combinators for ergonomics

Factor formalizes quotations (`[ ... ]`) as anonymous functions and relies heavily on
combinators to reduce stack shuffling. We want *some* of this ergonomics while staying
smaller and closer to Forth.

References:
- Slava Pestov, *Factor: a dynamic stack-based programming language* (DLS paper):
  https://factorcode.org/littledan/dls.pdf
- Factor docs on stack shuffling pain point: https://docs.factorcode.org/content/article-tour-stack-shuffling.html

## “Why Lua in Neovim?” (contrast case)

Neovim makes Lua a first-class scripting/config language.

References:
- Neovim docs: Lua overview: https://neovim.io/doc/user/lua.html
- Neovim Lua guide: https://neovim.io/doc/user/lua-guide.html

**Takeaway**: embedded languages win when they’re:
- always available (no external runtime installation)
- fast enough for interactive use
- tightly integrated with the host API

We should aim for the same, but with micromax.

## RetroForth: “modern, pragmatic Forth”

Retro positions itself as tiny, elegant, and adaptable—a useful datapoint for “modern Forth”
taste and packaging.

Reference:
- https://retroforth.org/

## Additional landscape / adjacencies (rev3)

### Namespaces via Search-Order / wordlists
- Forth 2012 Search-Order word set: https://forth-standard.org/standard/search
- `SET-ORDER`: https://forth-standard.org/standard/search/SET-ORDER

### Quotations + combinators (Factor/Joy/Retro)
- Factor paper (quotations, combinators, tooling): https://factorcode.org/littledan/dls.pdf
- Factor: words vs quotations metadata: https://concatenative.org/wiki/view/Factor/FAQ/What%27s%20Factor%20like%3F
- Joy overview: https://hypercubed.github.io/joy/html/forth-joy.html
- Joy FAQ: https://hypercubed.github.io/joy/html/faq.html
- RetroForth overview (prefix-guided compiler, quotations/combinators, vocabularies): https://retroforth.org/

### Forth interpreter/compile state (why we may diverge)
- Revisiting Forth (describes interpreter states): https://blog.jacobvosmaer.nl/0049-revisiting-forth/
- Starting Forth: compiling words / dual behavior: https://www.forth.com/starting-forth/11-forth-compiler-defining-words/

### Concurrency in Forth systems
- Gforth multitasker (cooperative + pthread): https://gforth.org/manual/Multitasker.html
- Gforth pthread notes (real concurrency implies conflict avoidance): https://gforth.org/manual/Pthreads.html



## New sources (rev4)

- Factor stack checker constraints around combinators (useful model for “stack effects later”):
  https://docs.factorcode.org/content/article-inference-combinators.html
- RetroForth overview + handbook:
  https://retroforth.org/
  https://www.retroforth.com/Handbook-Latest.epub
- FreeBSD loader(8) notes it embeds multiple interpreters including a Forth based on FICL:
  https://man.freebsd.org/loader
- FICL paper (embedding / portability perspective):
  https://dl.acm.org/doi/10.1145/606666.606672
- colorForth discussion (syntactic experiments to reduce hidden interpreter state):
  https://langdev.stackexchange.com/questions/1170/is-colorforths-unique-syntactic-approach-helpful-to-the-programmer


## New sources (rev5)

- Forth-2012 `DEFER` (standardized deferred words):
  https://forth-standard.org/standard/core/DEFER
- Wren embedding docs (embedding API is first-class):
  https://wren.io/embedding/
- Janet embedding docs (stable embedding story):
  https://janet-lang.org/capi/embedding.html
- Emacs hooks/advice docs (cheap extensibility patterns):
  https://www.gnu.org/s/emacs/manual/html_node/elisp/Hooks.html
  https://www.gnu.org/s/emacs/manual/html_node/elisp/Advising-Functions.html

## New sources (rev24)

### Micro editor plugin lifecycle + keybinding philosophy

Micro’s runtime help documents a simple plugin lifecycle (`preinit`, `init`, `postinit`, `deinit`) and a JSON-based keybinding/config surface, with plugins typically written in Lua.

References:
- micro help: plugins: https://github.com/zyedidia/micro/blob/master/runtime/help/plugins.md
- micro help: keybindings: https://github.com/zyedidia/micro/blob/master/runtime/help/keybindings.md
- micro tutorial (mentions `init.lua` + config system): https://github.com/zyedidia/micro/blob/master/runtime/help/tutorial.md

**Takeaway**: a tiny set of predictable lifecycle entrypoints + explicit keybinding/config files scales surprisingly far.
Micromax’s wordlists/modules map cleanly onto “one namespace per plugin”, and editor hostcalls can mirror micro-style lifecycle calls.

### Maps / hashtables in concatenative languages

Factor treats hashtables as a first-class collection and provides a dedicated vocabulary with predictable predicates and constructors.

Reference:
- Factor docs: hashtables vocabulary: https://docs.factorcode.org/content/word-hashtable%2Chashtables.html

In traditional Forth systems, “map” structures tend to be library-level (no standard core wordset), reinforcing the idea that a *small* primitive surface can still be enough if the embedding story is clear.

References:
- Discussion thread on Forth hash tables: https://comp.lang.forth.narkive.com/bcnGy5Uo/hash-tables-in-forth
- Gforth manual: wordlists/search order (namespace model that we already lean on): https://gforth.org/manual/Word-Lists.html

## New sources (rev25)

### Prompt / command bar completion conventions

Many editors converge on the same ergonomic pattern:

- **micro**: command bar (`Ctrl-e`) with `Tab` completing when possible.
  - quick reference cheat sheet: https://cheatography.com/mynocksonmyfalcon/cheat-sheets/micro-text-editor/
- **Kakoune**: prompt completion uses `Tab` / `Shift-Tab` to cycle.
  - discussion + doc pointer: https://discuss.kakoune.com/t/select-from-autocomplete-options/1835
- **Helix**: completion menus use `Tab`/`Shift-Tab` (and `Ctrl-n`/`Ctrl-p`) for next/prev.
  - keymap docs: https://docs.helix-editor.com/keymap.html

**Takeaway**: “Tab = next, Shift-Tab = prev” is a strong default for any completion list, whether it’s LSP, prompt completion, or command palette. If we model completion state as data (candidate list + index + replacement range), the same behavior can be reused across UI layers.

## New sources (rev27)

### File/path completion in command prompts

Micro’s command bar is heavily used for file/workspace operations (e.g., opening files and changing directories). In practice, users rely on `Tab` completion to avoid retyping long paths.

A recurring pain point in some implementations is “Tab completes to the first match” without a clear, predictable way to *cycle* other matches — which shows up as UX friction in real-world `open` workflows.

References:
- Micro command bar overview + `Tab` completion behavior (walkthrough): https://forum.garudalinux.org/t/mastering-the-micro-text-editor/32889
- Micro issue reporting `open`+Tab completing to the first match instead of cycling cleanly: https://github.com/micro-editor/micro/issues/2977

**Takeaway**: if we model prompt completion as a *session* (candidate list + index + replacement range), we can make cycling explicit (`Tab`/`Shift-Tab`) and avoid the “first match trap,” while still keeping a tiny, UI-agnostic core.

## New sources (rev28)

### Quoting and spaces in paths

Micro’s own help text is explicit: arguments containing spaces should be quoted, and the command bar parser follows `/bin/sh`-style quoting and escaping rules.

Separately, there are real-world bug reports where path handling breaks specifically when a completed path contains spaces, even though completion itself can find/cycle the candidate.

References:
- micro help: command bar parsing and quoting rules: https://github.com/micro-editor/micro/blob/master/runtime/help/commands.md
- micro issue: opening via file switcher fails when the path contains spaces: https://github.com/micro-editor/micro/issues/3970

**Takeaway**: path completion needs a quoting/escaping story, not just a directory listing story. Our headless completion model can stay tiny while still auto-quoting paths with spaces (and escaping embedded `"`) so the command parser sees correct arguments.

## 2026-02-26 — Command/arg completion as a first-class extension surface

- micro’s plugin API exposes `MakeCommand(name, fn, completion)` and explicitly passes a completion strategy (e.g. `config.NoComplete`). This reinforces that “command definition” and “how its args complete” should be configurable as separate concerns.
- Kakoune’s shift toward `complete-command` (separate from `define-command`) is a strong design signal: completion wants to be **reconfigurable in hooks** and composable without exploding flag sets.

Links (for later deep reading):
- https://terokarvinen.com/2022/micro-editor-plugin-hello-world/ (shows `config.MakeCommand(..., config.NoComplete)`)
- https://discuss.kakoune.com/t/designing-the-new-complete-command-command/2008 (motivation and tradeoffs for `complete-command`)

## New sources (rev30)

### Keybinding discoverability and removal

Micro already treats “what is this key bound to?” as an explicit command-bar workflow via `showkey`, and its keybinding docs describe disabling bindings by assigning the `None` action. Helix’s remapping docs similarly frame keybindings as a table of commands/macros and explicitly allow disabling keys with `no_op`. Kakoune’s mode docs emphasize attaching docstrings to mappings so discoverability information can be surfaced in the automatic info box.

References:
- micro commands help (`showkey`): https://github.com/micro-editor/micro/blob/master/runtime/help/commands.md
- micro keybindings help (`None` action disables bindings): https://github.com/micro-editor/micro/blob/master/runtime/help/keybindings.md
- Helix remapping docs (`no_op`, command/macros in keymaps): https://docs.helix-editor.com/remapping.html
- Kakoune modes docs (mapping docstrings shown in info box): https://github.com/mawww/kakoune/blob/master/doc/pages/modes.asciidoc

**Takeaway**: bindings should be treated as inspectable data, not only executable shortcuts. Even before we have layered keymaps or a rich UI, a small provenance-bearing binding record gives us better debugging, help, and reloadability.

## rev31 — hooks should be inspectable, not just runnable

- micro’s plugin help explicitly treats lifecycle/event callbacks as first-class plugin surface: `preinit`, `init`, `postinit`, `deinit`, `onAction`, `preAction`, `onBufferOpen`, etc. That reinforces the idea that editor hooks are not incidental internals — they are part of the public scripting model and deserve tooling.
- Kakoune’s hooks model emphasizes *named hook groups* and explicit removal via `remove-hooks`, which is a strong design signal that hook installations are configuration data that users need to manage after the fact.
- Emacs documents hooks as variables holding a list of functions to run on an occasion, which maps very closely to Micromax’s ordered multi-handler hook words. The useful lesson is not copying Lisp variables; it is preserving the “hook = inspectable list of callbacks” mental model.
- There is also explicit user demand for seeing currently active hooks in Kakoune discussions, which validates spending a small amount of surface area on hook introspection instead of treating it as a luxury.

Design takeaway for Micromax: keep hook *execution* tiny and portable, but add best-effort provenance and a stable row-oriented inspection word (`hook-rows`) so the live system remains debuggable.

## rev32 — statusline semantics should be shared, rendering should stay flexible

- Helix explicitly models the statusline as configurable **left / center / right** element lists, with defaults including file name, modification indicator, selections, and cursor position. This is a strong design signal that the *semantic pieces* of status belong in a stable model even if rendering/layout changes later.
- Micro treats the statusline as real editor surface rather than pure decoration. Its options/help mention the statusline directly (including how it behaves as a split divider), and user feedback around reclaiming the last line reinforces that this strip of UI matters in a terminal editor where space is precious.

References:
- Helix editor docs, `editor.statusline`: https://docs.helix-editor.com/master/editor.html
- micro options/help (statusline option/divider behavior): https://github.com/micro-editor/micro/blob/master/runtime/help/options.md
- micro issue about reclaiming the last line when statusline is disabled: https://github.com/zyedidia/micro/issues/3630

**Takeaway**: Micromax-editor should keep a tiny, shared **status model** in the headless core, then let future UIs decide how to lay it out (single line, split infobar, transient message strip, etc.).


## rev33 — hook groups are cheap cleanup power

- Kakoune’s hook docs make hook *groups* explicit: a hook registered with `-group` can later be removed with `remove-hooks <scope> <group>`. That is a strong signal that real editor/plugin ecosystems need *grouped cleanup*, not only per-handler removal.
- Emacs’s hook docs emphasize `add-hook` / `remove-hook` as the modular way to manipulate hook lists without trampling unrelated handlers. Even without copying Lisp variables, the lesson is the same: hook installation should preserve other participants and make selective removal easy.
- micro’s plugin lifecycle (`preinit` / `init` / `postinit` / `deinit`) reinforces the value of having a cheap “tear down everything this plugin added” mechanism when reloads happen repeatedly during development.

References:
- Kakoune hooks docs / `remove-hooks`: https://github.com/mawww/kakoune/blob/master/doc/pages/hooks.asciidoc
- Kakoune community hook docs summary: https://discuss.kakoune.com/t/hooks/544
- Emacs Lisp manual, setting hooks (`add-hook` / `remove-hook`): https://www.gnu.org/s/emacs/manual/html_node/elisp/Setting-Hooks.html
- micro plugin lifecycle help: https://github.com/zyedidia/micro/blob/master/runtime/help/plugins.md

**Takeaway**: keep Micromax hook execution tiny, but add a *group tag* to registrations plus a group-removal path so plugin reload/unload can clean up callbacks without full VM resets or fragile per-handler bookkeeping.

## rev34 — dynamic editor registrations should be treated as cleanup-friendly data

- micro’s command and keybinding docs reinforce that commands and bindings are *live editor configuration*, not hardwired code paths: the command bar exposes `bind`, `showkey`, and `reload`, while plugin docs describe `deinit()` followed by `preinit()` / `init()` / `postinit()` on reload. That strongly suggests repeated development reloads need a cheap way to tear down dynamic registrations cleanly.
- micro’s plugin API also exposes `MakeCommand(...)` and `TryBindKey(...)`, which is a nice confirmation that “commands” and “bindings” belong in the plugin/config layer, not buried inside the editor core.
- Kakoune’s mapping docs are explicit that mappings are created and removed with `map` / `unmap`, scoped by mode/context, and can carry docstrings for discoverability. That is another signal that key registrations should be treated as inspectable data structures rather than anonymous callbacks.
- Helix’s remapping docs distinguish static commands, typable commands, and macros, and support disabling keys with `no_op`. Even though Helix is less dynamic at runtime, it still treats the keymap as declarative data with stable command names behind it.
- Emacs’s minor-mode docs are the classic reminder that separate keymaps compose by activation context. We are not copying the whole model yet, but it supports the direction of keeping Micromax-editor registrations explicit, inspectable, and mode-ready.

References:
- micro command bar / reload / showkey: https://raw.githubusercontent.com/zyedidia/micro/master/runtime/help/commands.md
- micro plugin API + lifecycle (`MakeCommand`, `TryBindKey`, `deinit`): https://raw.githubusercontent.com/zyedidia/micro/master/runtime/help/plugins.md
- micro keybindings / `command:` bindings / `None` unbinds: https://raw.githubusercontent.com/zyedidia/micro/master/runtime/help/keybindings.md
- Kakoune mapping / unmap / docstrings: https://raw.githubusercontent.com/mawww/kakoune/master/doc/pages/mapping.asciidoc
- Helix remapping / minor modes / `no_op`: https://docs.helix-editor.com/remapping.html
- Emacs keymaps and minor modes: https://www.gnu.org/software/emacs/manual/html_node/elisp/Keymaps-and-Minor-Modes.html

**Takeaway**: a tiny editor bridge should still treat dynamic commands and bindings as *registrations with metadata*. Group tags are a cheap addition that make plugin reload/unload safer now, while leaving room for future mode/layered keymaps.



## rev35 — keymaps want context, but the first useful step is tiny

- Helix's remapping docs distinguish normal/insert/select maps and explicitly support **minor modes** by nesting definitions under keys like `g` or `z`. That is a strong signal that context-sensitive keymaps are worth modeling as data, not hardcoded UI behavior.
- Helix's keymap docs also enumerate these minor modes as explicit subcontexts reachable from normal mode, reinforcing the idea that a small editor can have layered keymaps without going "full Vim."
- Kakoune's mapping docs make *mode* part of the mapping contract itself: `map`/`unmap` are parameterized by contexts like `normal`, `insert`, `prompt`, `user`, `goto`, and `view`, and mappings can carry docstrings for discoverability.
- Emacs's minor-mode docs are the classic proof that independent keymaps compose by activation state: each enabled minor mode can contribute its own keymap.
- micro is less mode-heavy, but its command/keybinding docs still reinforce that dynamic bindings are live configuration and should be inspectable (`bind`, `showkey`, `reload`).

References:
- Helix remapping / minor modes: https://docs.helix-editor.com/remapping.html
- Helix keymap docs / minor modes: https://docs.helix-editor.com/keymap.html
- Kakoune mapping modes and `map`/`unmap`: https://raw.githubusercontent.com/mawww/kakoune/master/doc/pages/mapping.asciidoc
- Emacs keymaps and minor modes: https://www.gnu.org/software/emacs/manual/html_node/elisp/Keymaps-and-Minor-Modes.html
- micro command bar / `showkey` / reload: https://raw.githubusercontent.com/zyedidia/micro/master/runtime/help/commands.md
- micro keybindings / chaining / `command:` bindings: https://raw.githubusercontent.com/zyedidia/micro/master/runtime/help/keybindings.md

**Takeaway**: Micromax-editor does not need a huge modal architecture yet. A small contract gets most of the value: bindings carry a `mode`, the editor keeps an active mode stack, lookup falls back to global, and the result stays introspectable + reload-safe.

## rev36 — transient keymodes are a small feature with big editor leverage

- Emacs’s `set-transient-map` is the most explicit statement of the pattern: a transient keymap takes precedence over other active keymaps for one or more subsequent keys, and the default behavior is “use it once”.
- Helix’s keymap and remapping docs show the same family of idea from a more editor-facing angle: `g`, `z`, and other minor modes are short-lived dedicated binding layers that you enter from a normal map.
- Kakoune’s docs mention `next-key[...]` style mode pushes, which is further confirmation that temporary binding layers are a natural primitive in modal-ish editors.

References:
- Emacs Lisp manual, `set-transient-map`: https://www.gnu.org/software/emacs/manual/html_node/elisp/Controlling-Active-Maps.html
- Helix keymap docs / minor modes: https://docs.helix-editor.com/keymap.html
- Helix remapping / nested minor modes: https://docs.helix-editor.com/remapping.html
- Kakoune hooks docs mentioning `next-key[...]` modes: https://github.com/mawww/kakoune/blob/master/doc/pages/hooks.asciidoc

**Takeaway**: Micromax-editor should keep key dispatch centralized and make short-lived keymap layers explicit data. A tiny “one-shot keymode” mechanism gets most of the value of prefix/transient maps without dragging in a full modal architecture or a complex event parser.


## rev37 — transient maps get much more useful once users can inspect them

- Emacs `which-key` exists for a reason: once prefixes / transient maps are part of the workflow, users need a quick “what keys follow this?” reminder. The important lesson for Micromax-editor is not copying the popup UI; it is keeping **available bindings** as data that a UI can render.
- Helix’s keymap docs make minor modes very explicit (`g`, `z`, `Space`, etc.) and many of those modes are effectively “discovery menus” for grouped commands. That reinforces the value of a headless `available-bindings` surface once Micromax-editor has named keymodes.
- micro is less modal, but its command-bar docs and keybinding help still reinforce that bindings should be inspectable and user-facing.
- Kakoune’s mode/mapping story points in the same direction: mappings are data attached to contexts, so surfacing the reachable ones is natural.

References:
- which-key README / prefix discovery popup: https://github.com/justbur/emacs-which-key
- Helix keymap docs / minor modes and `Space` mode: https://docs.helix-editor.com/keymap.html
- Kakoune mapping docs: https://github.com/mawww/kakoune/blob/master/doc/pages/mapping.asciidoc
- micro command docs / command-bar binding workflows: https://github.com/zyedidia/micro/blob/master/runtime/help/commands.md

**Takeaway**: now that Micromax-editor has named + transient keymodes, the next small win is a **headless keymap discovery layer**. `showbindings` / `whichkey` are just thin renderers over portable data (`ed.available-bindings`, `ed.resolve-key`), which keeps the core honest and future UIs flexible.


## rev38 — once a keymap is discoverable, labels become part of the data model

- Kakoune’s mode docs explicitly say mapping docstrings are shown in the automatic info box. That is the cleanest statement of the idea that “human label for a binding” belongs with the mapping, not in an after-the-fact UI lookup table.
- Emacs `which-key` is not just about listing raw commands; it includes description replacement/customization features, and real user configs attach `:which-key` labels like “files”, “open file”, and “save file”. That is a strong signal that raw command names are often too noisy for discovery surfaces.
- Helix’s remapping docs keep bindings declarative and nested by mode, which reinforces that labels/descriptions can ride alongside the same binding data rather than living in a separate subsystem.
- micro is less elaborate here, but its `showkey`/command-bar story still supports the broader lesson that bindings are live, inspectable configuration — so adding a short human description is a natural extension, not a UI gimmick.

References:
- Kakoune modes docs / mapping docstrings surfaced in the info box: https://github.com/mawww/kakoune/blob/master/doc/pages/modes.asciidoc
- Emacs which-key README / description replacement support: https://github.com/justbur/emacs-which-key
- Emacs which-key issue showing `:which-key` labels in real configs: https://github.com/justbur/emacs-which-key/issues/267
- Helix remapping / minor modes as data: https://docs.helix-editor.com/remapping.html
- micro command-bar binding workflows: https://github.com/micro-editor/micro/blob/master/runtime/help/commands.md

**Takeaway**: once Micromax-editor has keymap discovery, the next small win is letting bindings carry a **human label**. `showbindings` can keep showing exact action specs, while `whichkey` and future UIs prefer descriptions. The label should live on the binding record (with derived fallbacks) so it survives reloads, tests, and future ports.


## rev39: prefix maps as a tiny first-class helper

Fresh outside references all pointed toward the same lesson: **temporary key layers are more usable when the editor treats them as a named primitive instead of expecting every config to hand-roll them**.

- The Emacs Transient manual describes a transient prefix command as activating a transient keymap that temporarily binds suffix/infix commands. That is almost exactly the conceptual model Micromax-editor already has with one-shot keymodes.
- The `which-key` README frames its job as showing the bindings that follow an incomplete/prefix key sequence. That validates pairing prefix-mode entry with immediate discovery output instead of making the user ask separately.
- Helix’s docs present `g`, `z`, and `Space` as minor-mode style key layers, which reinforces that prefix maps should be modeled as stateful keymap data, not hidden UI behavior.

References:
- Emacs Transient manual: https://www.gnu.org/software/emacs/manual/html_mono/transient.html
- which-key README / prefix discovery popup: https://github.com/justbur/emacs-which-key
- Helix keymap docs / minor modes (`g`, `z`, `Space`): https://docs.helix-editor.com/keymap.html

**Takeaway**: Micromax-editor did not need a new “special” prefix-map subsystem. The right low-hanging-fruit move was a tiny helper (`prefixmode`, `ed.bind-prefix`) built directly on top of the existing one-shot keymode + `whichkey` discovery substrate.



## rev40: mode-local prefix helpers are the smallest useful “local leader”

Fresh references all pointed toward the same lesson: once an editor has named
keymodes and one-shot maps, the next useful thing is **nesting them locally**
without inventing a new kind of object.

- Helix’s remapping docs explicitly describe minor modes accessed by pressing a
  key, and show nested definitions like `[keys.normal.g]` and `[keys.normal.z]`.
  That is a clean model for “a binding in one mode opens another small key layer”.
- general.el’s docs describe named prefix keymaps via `:prefix-command` /
  `:prefix-map`, which reinforces the broader idea that prefix maps should be
  named data, not ad-hoc action chains.
- Kakoune’s mode docs keep emphasizing that modes are how keys are grouped and
  discovered, which supports treating a mode-local prefix as “just another binding
  in the current mode that enters a short-lived submode”.

References:
- Helix remapping / minor modes and nested bindings: https://docs.helix-editor.com/remapping.html
- general.el / named prefix keymaps: https://github.com/noctuid/general.el
- Kakoune modes / mappings as grouped discoverable behavior: https://github.com/mawww/kakoune/blob/master/doc/pages/modes.asciidoc

**Takeaway**: Micromax-editor did not need a separate “local leader” subsystem.
The right low-hanging-fruit move was a tiny mode-local helper (`bindmodeprefix`,
`ed.bind-mode-prefix`) built directly on top of the existing one-shot `prefixmode`
and keymode stack.


## rev41: fuzzy command completion should help discovery without making paths spooky

Fresh references kept pointing at the same split:

- **micro** sets the baseline expectation that `Tab` in the command prompt should complete commands and filenames.
- **Helix** leans on fuzzy matching in pickers, which is a strong reminder that named editor surfaces are often easier to *search* than to spell exactly.
- **Kakoune** keeps completion as a distinct configurable subsystem, which reinforces that completion policy should stay explicit and inspectable rather than hidden inside a UI widget.

That suggests a very small, low-risk move for Micromax-editor:

- keep exact-prefix completion as the first rule
- add fuzzy fallback only for **command-ish names** (commands, actions, options, macro/plugin subcommands)
- keep filesystem paths prefix-based until we intentionally design a fuzzy-open/file-picker surface

References:
- micro help / `Tab` autocompletes in the command prompt: https://github.com/zyedidia/micro/blob/master/runtime/help/help.md
- micro default keys / command prompt autocomplete: https://github.com/zyedidia/micro/blob/master/runtime/help/defaultkeys.md
- Helix pickers / fuzzy matching: https://docs.helix-editor.com/pickers.html
- Helix completion menu / `Tab` and `Shift-Tab`: https://docs.helix-editor.com/keymap.html
- Kakoune prompt/completion direction: https://github.com/mawww/kakoune/blob/master/README.asciidoc

**Takeaway**: Micromax-editor did not need a heavyweight fuzzy engine or a new popup contract. The right low-hanging-fruit move was a tiny deterministic fuzzy fallback layered under the existing suggestion-session model, while keeping path completion conservative and explicit.

## rev41 (language follow-up): if Micromax grows stack-effect checking, keep it optional and tool-first

Factor’s docs remain a very good warning against over-designing this too early:

- stack-effect declarations are useful as lightweight executable documentation
- stack-effect tools can infer/report effects interactively
- stack checking catches real errors, but it is also a substantial subsystem with escape hatches and combinator-specific rules

References:
- Factor stack effect checking overview: https://docs.factorcode.org/content/article-inference.html
- Factor stack effect tools (`infer`, `stack-effect`, `effect>string`): https://docs.factorcode.org/content/article-tools.inference.html
- Factor stack effect declarations: https://docs.factorcode.org/content/article-effects.html

**Takeaway**: Micromax should likely grow any stack-effect support in this order: doc syntax first, interactive inspection next, optional dev-mode validation last. That keeps the language pleasant to script in before we commit to a full checker.

## rev42: argument completion should grow by command/slot, not by generic popup cleverness

Fresh references all pointed toward the same lesson: once a command bar exists,
**argument completion is part of the command model**, not just a UI flourish.

- Neovim’s command-line docs are explicit that completion applies to several
  categories such as command names, file names, and option names. That is a
  useful reminder that command bars become much more learnable once users can
  complete *what comes after the verb*, not only the verb itself.
- Kakoune’s `complete-command` docs go further and make completion a property of
  a command’s arguments / slots (`file`, `command`, shell-script-backed
  candidates, etc.). That reinforces Micromax-editor’s direction: keep
  completion policy attached to specific commands and argument positions.
- micro’s options help/docs keep exposing concrete option values (for example,
  enum-like settings such as clipboard backends), which is a practical reminder
  that users often need help recalling the *value vocabulary* as much as the
  command name.

References:
- Neovim command-line completion overview: https://neovim.io/doc/user/cmdline.html
- Kakoune `complete-command` / command completion configuration: https://igor-ramazanov.github.io/doc/pages/commands.html
- micro options help: https://github.com/micro-editor/micro/blob/master/runtime/help/options.md
- micro command-bar docs: https://github.com/micro-editor/micro/blob/master/runtime/help/commands.md

**Takeaway**: Micromax-editor did not need a generic preview popup or a separate
completion engine yet. The right low-hanging-fruit move was to grow completion
*by command and argument slot*: option values, keymode names, and inspection
subjects first; richer previews/metadata later.


## rev43: keybinding prompts should complete the thing you are about to bind, not just the command that edits bindings

Fresh references pointed at the same ergonomic lesson: once an editor exposes
**keybindings as commandable data**, users should not have to memorize the whole
right-hand side grammar by hand.

- micro’s keybindings docs are explicit that bindings can target ordinary editor
  actions, *chained* actions, and micro-style `command:` / `command-edit:`
  command-bar strings. That means the thing after `bind KEY ...` is a real user
  surface, not an opaque blob.
- Neovim’s command-line completion docs are a useful reminder that completion is
  often categorized by syntactic position: command names at the start, options
  after `:set`, mappings after `:map`, etc. That supports treating Micromax
  binding specs as another slot-aware completion surface.
- Kakoune’s mapping docs reinforce that mappings are first-class, documented
  objects with modes and docstrings; mapping ergonomics are part of the editor’s
  language, not an afterthought.

That suggests a compact move for Micromax-editor:

- let `bind` / `bindmode` complete editor action names
- treat `command:` / `command-edit:` as first-class action-spec prefixes
- when those prefixes are present, reuse the ordinary **command-ish**
  command-bar completion logic for the embedded command line instead of inventing
  a second mini-parser

References:
- micro keybindings / chaining / `command:` / `command-edit:`: https://raw.githubusercontent.com/micro-editor/micro/master/runtime/help/keybindings.md
- Neovim command-line completion categories (`:set`, `:map`, etc.): https://raw.githubusercontent.com/neovim/neovim/master/runtime/doc/cmdline.txt
- Kakoune mapping docs / docstrings / modes: https://raw.githubusercontent.com/mawww/kakoune/master/doc/pages/mapping.asciidoc

**Takeaway**: Micromax-editor did not need a new “binding wizard” UI. The right
low-hanging-fruit move was to extend the existing suggestion-session model into
`bind` / `bindmode`, and to treat `command:` / `command-edit:` bindings as
embedded command lines that can reuse the completion work already done.


## New sources (rev44)

### Completion metadata and UI separation

Neovim’s completion docs are a strong precedent for separating *candidate data* from *presentation*: `complete_info()` exposes per-item fields such as `word`, `menu`, `kind`, and `info`, while command-line completion state is available separately via `cmdcomplete_info()`.

Kakoune’s command completion docs reinforce that completion should be configured around command argument structure, with menu behavior treated as an option layered on top.

References:
- Neovim builtin docs: `complete_info()` / `cmdcomplete_info()`: https://neovim.io/doc/user/builtin.html
- Neovim UI docs: popupmenu / wildmenu are UI concerns: https://neovim.io/doc/user/api-ui-events.html
- Kakoune `complete-command`: https://igor-ramazanov.github.io/doc/pages/commands.html

**Takeaway**: Micromax should keep prompt completion headless and string-driven at its core, but attach a tiny, optional metadata channel (`kind/menu/info`) so future UIs do not have to reverse-engineer what each candidate means.


## rev45: tiny combinators buy a lot of ergonomics if they stay ordinary library code

A fresh pass over primary concatenative references pointed at the same lesson:
**quotation ergonomics matter early**, but the first wins do not require a large
optimizer-aware combinator tower.

- Factor’s docs explicitly group `dip` / `2dip` and `keep` / `2keep` as
  “preserving combinators,” which is a helpful mental bucket for Micromax: hide
  some values, run a quotation, restore them.
- Factor’s `bi` and `tri` docs are also useful because they show the words as
  *definitions in terms of simpler combinators* (`keep`/`dip`), not as magical
  VM-only behavior.
- Joy’s rationale keeps reinforcing why `dip` matters in the first place: it is
  the small abstraction that lets a stack language affect values *under* the top
  of stack without dropping into endless shuffle code.
- Retro’s docs are a good reminder that a tiny practical concatenative system can
  still lean heavily on quotes and combinators without becoming huge.

References:
- Factor preserving combinators: https://docs.factorcode.org/content/article-dip-keep-combinators.html
- Factor `bi`: https://docs.factorcode.org/content/word-bi%2Ckernel.html
- Factor `tri`: https://docs.factorcode.org/content/word-tri%2Ckernel.html
- Joy rationale (`dip` discussion): https://hypercubed.github.io/joy/html/j00rat.html
- RetroForth quotes and combinators: https://retroforth.org/nga/docs/QuotesAndCombinators.md

**Takeaway**: Micromax should keep stealing the *smallest useful* combinators first,
preferably as ordinary stdlib code. `2dip`, `2keep`, `bi`, and `tri` are the right size:
they noticeably reduce stack gymnastics in editor/config/plugin scripts while keeping the
VM tiny, inspectable, and easy to port.


## rev46: stack effects should be exposed as cheap metadata before they are validated

Fresh references pointed in the same direction:

- Gforth treats stack-effect comments as baseline readability hygiene and explicitly says you should write one for every definition when possible.
- Factor goes further and exposes stack effects as a reflective/tooling surface (`stack-effect`, `effect>string`, `infer`) instead of making the syntax useful only to the compiler.
- That combination is a good fit for Micromax: store/extract effect strings, expose them to tools and future UIs, and postpone any real checker until editor/plugin code proves it is worth the weight.

References:
- Gforth stack-effect comments tutorial: https://gforth.org/manual/Stack_002dEffect-Comments-Tutorial.html
- Gforth colon definitions tutorial: https://gforth.org/manual/Colon-Definitions-Tutorial.html
- Factor stack effect declarations: https://docs.factorcode.org/content/article-effects.html
- Factor stack effect tools: https://docs.factorcode.org/content/article-tools.inference.html
- Factor `stack-effect`: https://docs.factorcode.org/content/word-stack-effect%2Ceffects.html

**Takeaway**: the right rev46 move is small reflective plumbing (`xt-effect`, row-based word metadata, cleaner `help`) rather than a checker. That improves learnability immediately and keeps the VM/tier-2 story simple.

## rev47: in-editor word inspection should feel like part of the live environment

The new VM-level metadata (`xt-effect`, `xt-doc`, `words-rows`) made one next step feel obvious: the editor command bar should be able to inspect *visible Micromax words* directly instead of forcing users to drop into the REPL or write one-off scripts.

A few outside references lined up neatly here:

- **micro** keeps a built-in command-bar help workflow centered on `Ctrl-e`, `help`, and discoverability via command prompt completion. That is a strong reminder that the editor prompt itself should be a first-class discovery surface, not merely a thin parser.
- **Gforth**’s manual includes a **Word Index** where each entry is listed with stack effect and wordset, which is a nice precedent for surfacing word metadata as rows rather than just raw text dumps.
- **Factor** goes even further with a searchable help system and `apropos`, where named words/help topics are discoverable by fuzzy-ish subsequence search and then rendered with structured metadata.

**Takeaway**: the right rev47 move is *not* a full browser or picker yet. It is smaller: let editor `help` fall back to the currently visible Micromax word, add an explicit `showword NAME`, and wire prompt completion/metadata rows to the same live dictionary. That keeps the system inspectable and headless while making the editor feel much more like Micromax’s native environment.

References:
- micro command bar / help topics / Tab discovery: https://raw.githubusercontent.com/zyedidia/micro/master/runtime/help/help.md
- micro command list / command-bar parsing: https://raw.githubusercontent.com/zyedidia/micro/master/runtime/help/commands.md
- Gforth Word Index (stack effect + wordset): https://gforth.org/manual/Word-Index.html
- Gforth stack-effect comments tutorial: https://gforth.org/manual/Stack_002dEffect-Comments-Tutorial.html
- Factor help vocabulary: https://docs.factorcode.org/content/vocab-help.html
- Factor `apropos`: https://docs.factorcode.org/content/word-apropos%2Chelp.apropos.html



## rev48: searchable topic rows beat a premature picker

Fresh references pointed in the same direction:

- **Factor** already has `apropos`, which searches words/vocabularies/help articles by subsequence and ranks the results with a simple distance algorithm.
- **Neovim** still leans heavily on searchable help/index surfaces such as `:helpgrep` and the command index rather than requiring one monolithic help browser first.
- **micro** keeps the command bar and built-in help system as the main discovery path, which is a reminder that Micromax should strengthen the prompt before inventing a larger UI.
- **Helix** shows that fuzzy search belongs naturally on named editor surfaces, but also that a full picker is a separate UX commitment with its own keymap and lifecycle.

Useful references:

- Factor `apropos`: https://docs.factorcode.org/content/word-apropos%2Chelp.apropos.html
- Neovim `:helpgrep` / help search: https://neovim.io/doc/user/usr_02.html
- Neovim help index: https://neovim.io/doc/user/vimindex.html
- micro command-bar help: https://github.com/zyedidia/micro/blob/master/runtime/help/help.md
- micro prompt autocomplete note: https://github.com/zyedidia/micro/blob/master/runtime/help/defaultkeys.md
- Helix pickers: https://docs.helix-editor.com/pickers.html

**Takeaway**: the right rev48 move is still *not* a heavyweight picker. It is smaller and more composable: expose a shared topic-row model for commands/actions/words, add a tiny `apropos QUERY` command using the existing deterministic fuzzy ranking, and surface the same rows to scripts via hostcalls so future UIs/LLMs can reuse exactly the same discovery substrate.


## rev49: plugin completion should speak the same row language as built-ins

- **Neovim**'s completion/UI surface is a strong precedent for exposing completion items as structured rows rather than plain strings: `complete_info()` returns items with fields such as `word`, `menu`, `kind`, and `info`, and the UI popupmenu event uses an array form `[word, kind, menu, info]`.
- **Helix** treats pickers and completion menus as their own UI layer with separate navigation semantics, which is a good reminder that the headless core should expose *item metadata*, not commit to a specific popup implementation.
- Micromax already had exactly the right row shape on the editor side (`[insert kind menu info]`) for built-in prompt completion. The awkward gap was that plugin-provided completions could only return strings, so custom commands looked second-class in future UIs/tooling.

Sources:
- Neovim `complete_info()` / complete items: https://neovim.io/doc/user/builtin.html
- Neovim UI popupmenu items: https://neovim.io/doc/user/api-ui-events.html
- Helix pickers / completion navigation: https://docs.helix-editor.com/pickers.html and https://docs.helix-editor.com/keymap.html

**Takeaway**: the right rev49 move is not a picker yet. It is smaller and more composable: let `ed.complete.<cmd>` / `ed.complete` optionally return aligned completion rows in the same `[insert kind menu info]` shape already used by built-ins, and make the host merge/overlay those rows instead of inventing a plugin-only metadata path.


## rev50: let `apropos` search summaries/docs before building a picker

Fresh references still point to the same general lesson: **search-first help is valuable even before you commit to a picker UI**, and those searches should not be limited to exact names.

- **Neovim** keeps a strong split between direct help lookup (`:help`) and broader help search (`:helpgrep` / help indexes), which is a reminder that discovery often needs to search *descriptions*, not just tags.
- **Helix** has a command palette and fuzzy pickers, reinforcing that search-first discovery is ergonomic, but the picker itself is still a separate UX layer from the searchable data.
- **micro** keeps built-in help in the command bar, which supports the idea that Micromax should keep strengthening prompt-driven discovery rather than jumping straight to a browser UI.

Useful references:

- Neovim `:help` / `:helpgrep`: https://neovim.io/doc/user/helphelp.html and https://neovim.io/doc/user/usr_02.html
- Neovim help index: https://neovim.io/doc/user/vimindex.html
- Helix command palette / pickers: https://docs.helix-editor.com/keymap.html and https://docs.helix-editor.com/pickers.html
- micro help overview: https://github.com/zyedidia/micro

**Takeaway**: the right rev50 move is still *not* a full picker. It is smaller and more composable: keep `apropos QUERY` name-first, but let it fall back to topic summary/doc text, and make `help NAME` surface a few likely matches when exact lookup fails. That improves discovery and typo recovery immediately while preserving the same headless topic-row substrate for any future picker UI.


## rev51: a tiny topic/help prompt beats a premature browser

Fresh references still point in the same direction: **searchable pickers are useful, but the stable substrate should be item rows + prompt semantics before a heavyweight UI/browser lands.**

- **Helix** describes pickers as interactive windows with their own keymap and fuzzy filtering, which is a good reminder that a picker is a distinct UI layer rather than just “more completion.”
- **VS Code** separates the broader **Command Palette** idea (all commands are discoverable from one search surface) from **Quick Pick** item design guidance (`description` for current-item context, `detail` for extra context). That maps surprisingly well onto Micromax’s existing `[insert kind menu info]` rows.
- Micromax already had the hard part: `help_topic_rows()`, `apropos_rows()`, and prompt suggestion rows. The missing piece was a tiny *searchable prompt mode* that could reuse those rows directly instead of forcing future UIs/scripts to assemble a picker lifecycle themselves.

Sources:
- Helix pickers: https://docs.helix-editor.com/pickers.html
- VS Code Quick Picks: https://code.visualstudio.com/api/ux-guidelines/quick-picks
- VS Code Command Palette: https://code.visualstudio.com/api/ux-guidelines/command-palette

**Takeaway**: the right rev51 move is not a full browser, command palette UI, or popup menu system. It is smaller and more composable: add a `topic` prompt kind plus `topicpick [QUERY]`, `TopicPrompt`, and `ed.topic-prompt`, preload it with ranked topic rows, let `Tab` / `Shift-Tab` cycle within that prompt, and make `Enter` open help for the selected/best-ranked topic. That gives the editor a real search-first discovery surface while preserving the same headless prompt/session contract.


## Searchable prompts / command palette lessons

A few editor/UI systems converge on the same useful separation:

- keep a **filterable item model** with lightweight metadata (`label`/`kind`/`description`/`detail`)
- let the query update the ranked item list continuously
- treat any richer preview panel as a *downstream UI concern*, not the core completion/search contract

References:
- Helix pickers: https://docs.helix-editor.com/pickers.html
- VS Code Quick Pick UX guidelines: https://code.visualstudio.com/api/ux-guidelines/quick-picks
- Vim `completeopt` preview docs: https://vim-jp.org/vimdoc-en/options.html

**Takeaway for Micromax**: the headless core should expose stable rows + active selection state first. That gives future TUIs/LLMs enough substrate to render a command palette / topic browser / preview pane later without changing ranking or command-discovery semantics.


## rev53: grouped sections and current-item previews belong in the headless substrate

Fresh references point to a small but important next step: once Micromax already has ranked topic rows and an active selection, the next useful thing is **not** a full picker widget. It is exposing the two bits of structure downstream UIs repeatedly want:

- **coarse grouping** (commands vs actions vs words)
- a tiny **current-item preview summary**

- **VS Code Quick Pick** explicitly supports separators for “multiple obvious groups of selections”, which is a strong precedent for adding section/group surfaces before any richer UI work.
- **VS Code command/category presentation** is another reminder that grouping command-like items is part of discoverability, not just decoration.
- **Helix** keeps preview as a picker-level concern (`Ctrl-t` toggles preview), which reinforces the idea that Micromax should expose preview *data* first instead of baking in a preview widget.
- **Neovim** continues to support the same split in completion: short `menu` text, longer `info` text, and structural access to the currently selected item via `complete_info()`.

Sources:
- VS Code Quick Picks (`Using separators`): https://code.visualstudio.com/api/ux-guidelines/quick-picks
- VS Code command categories / grouping: https://code.visualstudio.com/api/references/contribution-points
- Helix pickers and preview toggle: https://docs.helix-editor.com/pickers.html and https://docs.helix-editor.com/keymap.html
- Neovim completion item fields / current selection: https://neovim.io/doc/user/insert/ and https://neovim.io/doc/user/builtin.html

**Takeaway**: the right rev53 move is to add grouped topic-section rows plus compact current-item preview helpers (`section`, `preview`, status-model fields). That makes the archive much friendlier for future TUIs/LLMs while keeping the actual UI commitment deferred.


## rev54: searchable binding discovery should reuse the same prompt/row substrate, not invent a popup contract

Fresh references point to a small but useful next step after `topicpick`: editors often need a way to **discover current keybindings** without forcing users to memorize prefix trees or commit the core to a popup UI too early.

- **which-key.nvim** states its core value very plainly: it helps users remember keymaps by showing available keybindings *as you type*. That is a strong reminder that Micromax should treat binding discovery as a first-class editor surface.
- **VS Code** keeps command discovery and keyboard-shortcut discovery as separate but related searchable surfaces: the Command Palette is the universal command finder, while the Keyboard Shortcuts editor is where bindings are inspected and searched.
- **Helix** continues to reinforce the architectural split: pickers are a real UI layer with their own keymap, so the headless core should first expose stable searchable rows + active selection semantics, not a hard-coded popup/browser.

Sources:
- which-key.nvim README: https://github.com/folke/which-key.nvim
- VS Code Keyboard Shortcuts: https://code.visualstudio.com/docs/configure/keybindings
- VS Code Command Palette: https://code.visualstudio.com/api/ux-guidelines/command-palette
- Helix pickers/keymap: https://docs.helix-editor.com/pickers.html and https://docs.helix-editor.com/keymap.html

**Takeaway**: the right rev54 move is not “build which-key as a popup.” It is smaller and more composable: add a searchable `binding` prompt (`bindingpick`, `BindingPrompt`, `ed.binding-prompt`) plus searchable current-binding rows (`ed.binding-prompt-rows`) that reuse the existing prompt/session/status substrate. That gives Micromax a `whichkey`-adjacent discovery path while keeping the renderer decision deferred.


## rev55: search prompts should handle multiple terms across names + metadata, not just one ordered string

Fresh references point to a small but meaningful refinement after `apropos`, `topicpick`, and `bindingpick`: once you have searchable rows, users very quickly expect **multiple terms** to work across both the primary label and the supporting metadata.

- **Helix** says most pickers use **fzf syntax** for filtering, which is a useful reminder that picker search is usually richer than “match one string in order.”
- **fzf** itself documents “extended-search mode” where users can type **multiple search terms delimited by spaces**. That is exactly the expectation Micromax was starting to brush up against.
- A **which-key.nvim** feature request makes the keybinding side explicit: a command-palette-style search should be able to search by both the **description** and the **keystrokes**, not just a single field.
- **VS Code Quick Picks** keep reinforcing the same architectural idea: items have a main label plus supporting description/detail text, so search/discovery surfaces naturally want to benefit from more than just the first label.

Sources:
- Helix pickers: https://docs.helix-editor.com/pickers.html
- fzf search syntax: https://github.com/junegunn/fzf
- which-key.nvim command-palette request: https://github.com/folke/which-key.nvim/issues/978
- VS Code Quick Picks: https://code.visualstudio.com/api/ux-guidelines/quick-picks

**Takeaway**: the right rev55 move is still *not* a heavier picker UI. It is smaller and more composable: keep the existing deterministic ranking, but let `apropos`, failed `help`, `topicpick`, and `bindingpick` treat whitespace-separated terms as a tiny bag-of-words query across the row fields they already expose. That brings Micromax much closer to real command-palette / key-discovery expectations while preserving the same headless row-first design.


## rev56: a real command palette should execute actions but stage commands for arguments

Fresh references point to a very natural next step after `topicpick` and `bindingpick`: once a small editor already has searchable rows for commands/actions and a live prompt substrate, the next useful thing is a **real command palette**.

- **VS Code** is explicit that the Command Palette is where all commands are found, and that clear naming/grouping matter for discoverability.
- **VS Code** also treats commands as central editor integration points, which is a good reminder that Micromax should make command/action discovery a first-class native surface rather than only a help search trick.
- **legendary.nvim** is a nice Neovim-side precedent because it builds a legend/command-palette surface over commands, keymaps, and autocommands while still delegating the finder UI to picker plugins.
- **micro** keeps the command bar as a central interaction surface (`Ctrl-e`), which suggests that Micromax should keep the palette tightly connected to the existing command prompt instead of inventing a separate execution model.

Sources:
- VS Code Command Palette UX guidelines: https://code.visualstudio.com/api/ux-guidelines/command-palette
- VS Code command capabilities: https://code.visualstudio.com/api/extension-capabilities/common-capabilities
- legendary.nvim README: https://github.com/mrjones2014/legendary.nvim
- micro command/help docs: https://github.com/zyedidia/micro/blob/master/runtime/help/help.md and https://github.com/zyedidia/micro/blob/master/runtime/help/commands.md

**Takeaway**: the right rev56 move is still *not* a heavyweight popup or browser. It is smaller and more composable: add a searchable command/action palette on top of the existing prompt/row/ranking substrate, let selecting an **action** execute it immediately, and let selecting a **command** open the ordinary command bar prefilled so the user can still supply arguments deliberately.


## rev57: command palettes get materially better when they remember what you actually picked

A small search-first palette already existed in Micromax by rev56, but outside precedents point to an obvious next ergonomic step: **recently used items belong near the top**.

- **GitHub** describes its command palette as showing suggestions based on current context and resources used recently, which is a good reminder that search-first surfaces become more helpful when they remember what mattered to *this* user recently.
- **Positron**'s command-palette docs are explicit: recent commands appear first, making repeated actions faster.
- **VS Code**'s Command Palette UX guidance still reinforces the complementary structural lesson: clear names and grouping matter, which argues for exposing a grouped `Recent` / `Commands` / `Actions` view in the headless substrate rather than burying recency in a UI-only layer.

References:
- GitHub Command Palette: https://docs.github.com/en/get-started/accessibility/github-command-palette
- Positron Command Palette: https://positron.posit.co/command-palette.html
- VS Code Command Palette UX guidelines: https://code.visualstudio.com/api/ux-guidelines/command-palette

**Takeaway**: the right rev57 move is still not a heavier popup. It is smaller and more composable: keep the existing row-first command palette, but add a tiny MRU of successful palette selections, rank those recents first for empty queries (and as tie-breakers for equivalent matches), and expose grouped palette sections so future TUIs/LLMs can render `Recent` explicitly instead of reverse-engineering it.

## rev59: tooling-friendly “source surfaces” + introspection-first UX

While continuing to steal editor UX ideas from micro and Emacs, it’s worth noticing a very practical
pattern across “serious” programmable editors:

- **Discovery** surfaces (help/which-key/describe) are only as good as their underlying *data models*.
- A scripting language embedded in an editor needs not just an evaluator, but a set of stable
  introspection hooks: *what is this thing*, *where did it come from*, *what does it do*, and
  *show me its source-ish definition*.

New concrete “steals”:

- micro’s upstream help topics make heavy use of *simple textual inspection* as the primary UX.
  That argues for a small, deterministic `xt-src` surface that hosts can render without a full UI.
  - https://github.com/zyedidia/micro/blob/master/runtime/help/keybindings.md
  - https://github.com/zyedidia/micro/blob/master/runtime/help/plugins.md

- Emacs’ manual emphasizes the layered nature of keymaps (global maps, major-mode local maps, and
  even more local overrides). That is a great conceptual justification for keeping micromax’s
  mode-aware keymap resolution *inspectable* rather than “just a lookup”.
  - https://www.gnu.org/software/emacs/manual/html_node/emacs/Customization.html

- zForth is a reminder that “tiny, embeddable, engineer-friendly Forth” is a real and recurrent
  niche: prioritize integration ergonomics and a small surface area over language purity.
  - https://github.com/zevv/zForth

**Takeaway**: invest in *inspection-first* primitives (spans, rows, and source-ish renderers) early;
they pay back immediately for headless tests, future TUIs, and LLM-driven workflows.


## rev98: picker UX steals from fzf + capability discipline wants an explicit sandbox knob

Two small but useful "steals" from existing tools:

- fzf explicitly supports *sticky headers* / non-selectable header lines (`--header` and `--header-lines`).
  That aligns with Micromax's picker UX direction (sticky section headers + section jumps) and suggests
  that *structured list rendering* should remain a first-class headless concept, not UI glue.

- micro users have long asked for (and built plugins around) lightweight fuzzy file/buffer search via fzf.
  That reinforces that "command palette" and "open file" flows become dramatically more useful when
  they can safely consult the filesystem.

But a safety note: capability-based design literature keeps returning to "no ambient authority" and
least-privilege. For Micromax that translates into two pragmatic rules:

1) default capabilities off,
2) when a capability is enabled, provide a way to *reduce its blast radius*.

An optional `cap.fs-root` knob (a sandbox root for fs helpers) is a small, inspectable step in that direction.

References:
- fzf advanced options (`--header`, `--header-lines`): https://github.com/junegunn/fzf/blob/master/ADVANCED.md
- micro fuzzy finder request + fzf plugin note: https://github.com/zyedidia/micro/issues/477
- capability-based security overview: https://en.wikipedia.org/wiki/Capability-based_security


## rev103: clipboard backends — micro’s OSC 52 notes + “side effects as capabilities”

Micro’s docs have a very practical perspective on clipboard behavior:

- `clipboard=terminal` is a strong default for SSH workflows, because it can *export* clipboard
  content to your local system clipboard via OSC 52.
- terminal support is uneven: some emulators support writing but not reading; some require explicit
  opt-in settings.

For Micromax, this maps cleanly onto our capability story:

- an internal clipboard is harmless and always available
- exporting to the system clipboard is a **side effect**, and scripts should not get that power
  “for free” when a privileged backend is selected

So we implement:
- best-effort OSC 52 export in the curses TUI when `clipboard=terminal`
- a dedicated `cap.clipboard-write` gate for script-originated exports

References:
- micro `copypaste` help (OSC 52 support caveats): https://github.com/zyedidia/micro/blob/master/runtime/help/copypaste.md
- micro `options` help (`clipboard` backends): https://github.com/zyedidia/micro/blob/master/runtime/help/options.md



## rev104 — bracketed paste + external clipboard

- Bracketed paste wraps pasted text in `ESC[200~ ... ESC[201~` and is enabled via `CSI ? 2004 h` (and disabled with `CSI ? 2004 l`).
- micro recommends bracketed paste when available, and otherwise temporarily enabling its `paste` option to aggregate paste key bursts.
- For external clipboard integration, micro expects tools like `xclip`/`xsel` on Linux and `pbcopy` on macOS; Windows has `clip`.

Pointers:
- https://github.com/zyedidia/micro/blob/master/runtime/help/copypaste.md
- https://cirw.in/blog/bracketed-paste
- https://stackoverflow.com/questions/749544/pipe-to-from-the-clipboard-in-a-bash-script
- https://superuser.com/questions/97762/how-to-pipe-text-from-command-line-to-the-clipboard


## rev105 — external clipboard import: micro’s Ctrl-v behavior + wl-paste no-newline

Micro’s `copypaste` help notes that its default paste binding (`Ctrl-v`) reads the
*system* clipboard via platform tools like `pbpaste` on macOS and `xclip`/`xsel`
on Linux (and syscalls on Windows).

That’s a useful “micro-esque” target for Micromax when `clipboard=external`:
- copy/cut exports to system clipboard (already done)
- paste can best-effort **import** from system clipboard (new)

On Wayland, `wl-paste` has a `-n/--no-newline` flag to avoid appending a newline
after the pasted content, which is a nice default for editor pastes.

Pointers:
- micro `copypaste` help (Ctrl-v reads system clipboard): https://github.com/zyedidia/micro/blob/master/runtime/help/copypaste.md
- wl-paste man page (`-n/--no-newline`): https://man.archlinux.org/man/wl-paste.1.en


## rev106 — scanability polish: fzf-style kind cues + markdown inline code

Two small patterns from other tools are worth stealing:

1) **fzf uses separate “text elements” for coloring** (prompt, pointer, marker, header, info, hl, etc.), which is a good mental model for our pickers: style *kinds* and *roles* rather than repainting everything. We applied this lightly in the minimal TUI by giving hint styles to action rows, file-ish rows, and link-ish rows.

2) **Inline markdown code spans** (`` `code` ``) are a common docs affordance; dimming them (without going full syntax highlighting) makes docs pages easier to scan in a terminal UI.

Pointers:
- fzf advanced doc (color elements + themes): https://github.com/junegunn/fzf/blob/master/ADVANCED.md
- fzf man page (shows `--color` element names): https://man.archlinux.org/man/fzf.1.en
- markdown inline code spans (backticks; multiple delimiters for literal backticks): https://stackoverflow.com/questions/33224686/how-to-render-triple-backticks-as-inline-code-block-in-markdown
