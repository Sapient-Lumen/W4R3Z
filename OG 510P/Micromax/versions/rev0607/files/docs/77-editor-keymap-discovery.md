Rev580 note: plain `showbindings` and `whichkey` command-bar completion keep one visible active-keymode witness even when the reachable binding inventory is empty — safe-startup/default-global state can preview `default=active bindings=0 · global bindings=0` and `active bindings=0 · global bindings=0` instead of trailing off into generic `show bindings`, so the active-binding entry points stay concrete before any custom bindings are installed; `docs/522-active-binding-empty-witness.md` records why that tiny trust/taste follow-up matters.

Latest tiny landing (rev580): this is a small trust/taste follow-up to rev572/rev573/rev579's keymap-discovery and command-bar honesty pass. Micromax already had the important nearby pieces: plain `showbindings` and `whichkey` already previewed the live reachable-binding inventory before Enter whenever any binding existed, `showbindings active` already reused that same reachable register after Enter, and rev579 had just taught the adjacent keymode inventory surfaces to keep the visible `global` witness concrete in the all-empty startup case. But one tiny adjacent seam still lingered in the shared empty active-binding path: `_prompt_showbindings_mode_row(...)` still ended both no-arg previews with generic `show bindings` whenever the reachable inventory was empty, even though Micromax already knew the active keymode stack and the same leading visible mode. Rev580 keeps the fix deliberately small and compatible: new `_active_keymode_binding_witness()` reuses `keymode_inventory_rows()` plus `keymode_detail_row(NAME)`, empty active-inventory previews for plain `showbindings` and `whichkey` now preserve the leading visible mode as `MODE bindings=0`, focused tests pin both commands' populated and empty previews, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/43-worklist.md` / `docs/55-editor-command-bar.md` / `docs/64-editor-prompt-completion.md` / `docs/66-editor-micromax-commands.md` / `docs/77-editor-keymap-discovery.md` plus `docs/514-showbindings-command-preview.md` / `docs/515-whichkey-command-preview.md` / `docs/522-active-binding-empty-witness.md` record the intent. The goal is simple: if Micromax already knows which active keymode anchors an empty reachable-binding inventory, the broad `showbindings` and `whichkey` entry points should keep that witness before Enter instead of ending with generic prose.

Rev579 note: plain `showkeymodes` command-bar completion keeps one visible keymode sample even when every visible mode has zero bindings — safe-startup/default-global state can preview `active global · known=1 · global bindings=0` instead of collapsing back to counts-only, so the broad keymode entry point stays concrete before any custom maps are installed; `docs/521-showkeymodes-empty-sample-preview.md` records why that tiny trust/taste follow-up matters.

Latest tiny landing (rev579): this is a small trust/taste follow-up to rev442/rev459/rev559/rev578's keymode and command-bar honesty pass. Micromax already had the important nearby pieces: `showkeymodes` already exposed the visible active/known inventory after Enter, `keymode_inventory_rows()` / `ed.keymode-inventory-rows` already exposed that same register headlessly, exact `keymode_detail_row(NAME)` / `showkeymode NAME` inspection already kept one mode concrete, and rev559 had already taught the no-arg command row to reuse one leading exact mode sample when bindings existed. But one tiny adjacent seam still lingered in the all-empty keymode case: `_prompt_showkeymodes_command_row(...)` only appended detail when the leading visible mode had at least one binding, so a fresh editor still collapsed back to counts-only `active global · known=1` exactly when the calmest startup state most needed one concrete witness. Rev579 keeps the fix deliberately small and compatible: plain `showkeymodes` now falls back to the first visible exact keymode row even when its binding count is `0`, its no-arg command row can preview `active global · known=1 · global bindings=0` instead of only the counts, focused tests pin both populated and default-global previews, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/43-worklist.md` / `docs/55-editor-command-bar.md` / `docs/64-editor-prompt-completion.md` / `docs/66-editor-micromax-commands.md` / `docs/77-editor-keymap-discovery.md` plus `docs/521-showkeymodes-empty-sample-preview.md` record the intent. The goal is simple: if Micromax already knows the first visible keymode in the live inventory, the broad no-arg preview should keep that witness even when every visible mode is empty.

Rev573 note: plain `whichkey` command-bar completion previews the live active binding inventory now too — the exact command row can show `active bindings=N · ...` or `active bindings=0 · show bindings` instead of falling back to generic exact-command metadata even though Micromax already knows the same reachable keymap before Enter; `docs/515-whichkey-command-preview.md` records why that tiny trust/flow follow-up matters.

Latest tiny landing (rev573): this is a small trust/flow follow-up to rev367/rev423/rev429/rev459/rev571/rev572's keymap-discovery and command-bar honesty pass. Micromax already had the important nearby pieces: `whichkey` already reused the same live reachable-binding inventory as `showbindings active` after Enter, plain `showbindings` now previewed its default active binding inventory before Enter, and exact `showbindings MODE|active` rows already surfaced truthful active/mode-level keymap state in completion. But one tiny adjacent seam still lingered at the no-arg `whichkey` entry point: typing plain `whichkey` in the command bar still showed only generic command metadata even though Micromax already knew the active reachable-binding count and one sample winner. Rev573 keeps the fix deliberately small and compatible: new `_prompt_whichkey_command_row(...)` reuses `_prompt_showbindings_mode_row('active ')`, exact command completion for plain `whichkey` now previews active binding inventory before Enter, focused tests pin both populated and empty command rows, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/43-worklist.md` / `docs/55-editor-command-bar.md` / `docs/64-editor-prompt-completion.md` / `docs/66-editor-micromax-commands.md` plus `docs/77-editor-keymap-discovery.md` and `docs/515-whichkey-command-preview.md` record the intent. The goal is simple: if Micromax already knows the reachable keymap behind plain `whichkey`, the command bar should show that truth before Enter instead of hiding behind one more generic exact-command hint.

Rev572 note: plain `showbindings` command-bar completion previews the default active binding inventory now too — the exact command row can show `default=active bindings=N · ...` or `default=active bindings=0 · show bindings` instead of falling back to generic exact-command metadata; `docs/514-showbindings-command-preview.md` records why that tiny trust/flow follow-up matters.

Latest tiny landing (rev572): this is a small trust/flow follow-up to rev367/rev423/rev429/rev459/rev571's keymap-discovery and command-bar honesty pass. Micromax already had the important nearby pieces: plain `showbindings` already defaulted to `active` after Enter, `showbindings active` / `whichkey` already reused the shared reachable-binding inventory, exact `showbindings MODE|active` rows now preview truthful mode-level state before Enter, and the command path already answered empty active maps as `0 binding(s)`. But one small adjacent seam still lingered at the exact no-arg entry point: typing plain `showbindings` in the command bar still showed only generic command metadata even though Micromax already knew the default active binding count and one sample reachable winner. Rev572 keeps the fix deliberately small and compatible: new `_prompt_showbindings_command_row(...)` reuses `_prompt_showbindings_mode_row('')`, exact command completion for plain `showbindings` now previews `default=active` binding inventory before Enter, focused tests pin both populated and empty command rows, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/43-worklist.md` / `docs/55-editor-command-bar.md` / `docs/64-editor-prompt-completion.md` / `docs/66-editor-micromax-commands.md` plus `docs/77-editor-keymap-discovery.md` and `docs/514-showbindings-command-preview.md` record the intent. The goal is simple: if Micromax already knows the default active binding inventory behind plain `showbindings`, the command bar should show that truth before Enter instead of hiding behind one more generic exact-command hint.

# Editor keymap discovery (rev38)

Rev35/36 added named keymodes plus one-shot / transient keymodes.
The obvious next pressure point is **discoverability**:

- after pushing a transient mode, what keys are available *right now*?
- how can a headless UI or script inspect the current reachable keymap without scraping messages?
- how do we keep this small enough that future Rust/WASM ports can mirror it directly?

This revision adds a tiny **keymap discovery** surface.

## Design goals

- keep the core representation as plain binding records
- expose *resolved* bindings after keymode precedence is applied
- keep command-bar output deterministic and compact
- stay portable: only strings / ints / lists on the wire

## New hostcalls

```text
ed.binding-rows-for   ( mode|0 -- rows )
ed.available-bindings              ( -- rows )
ed.available-binding-inventory-rows ( -- rows )
ed.binding-section-summary-rows   ( query -- rows )
ed.keymode-inventory-rows          ( -- rows )
ed.keymode-detail-row              ( name -- row|0 )
ed.binding-detail-row              ( key -- row|0 )
ed.resolve-key                      ( key -- row|0 )
ed.resolve-key-info                 ( key -- row|0 )
```

### `ed.binding-rows-for`

Returns exact bindings for one mode.

```text
[[key action-spec group|0 [file line col]|0] ...]
```

Passing `0` means the global map.

### `ed.available-bindings`

Returns the bindings that are currently reachable *after* active keymode
precedence is applied.

```text
[[mode key action-spec group|0 [file line col]|0] ...]
```

Rules:
### `ed.available-binding-inventory-rows`

Returns the tiny shared current-binding inventory reused by plain `showbindings active` and `whichkey`.

```text
[[mode key action-spec label once?] ...]
```

Where:
- `label` is the human-facing `whichkey` text (resolved description when present, otherwise the action-spec)
- `once?` is `1` when the winning mode is currently one-shot / transient

This deliberately complements `ed.available-bindings` / `ed.available-binding-info` instead of replacing them: the lower-level rows still expose provenance/group detail, while this tiny register preserves the already-curated human discovery surface for scripts and future UIs.

### `ed.binding-section-summary-rows`

Returns the tiny shared winning-mode binding summaries reused by plain `showbindingmodes [QUERY]` and now by command-bar completion for the same query slot.

```text
[[label count sample_name sample_detail] ...]
```

Where:
- `label` is the visible winning-mode section label (`Prompt`, active mode names like `nav`, `Global`)
- `count` is the number of currently reachable bindings in that bucket
- `sample_name` reuses the first visible key in that bucket
- `sample_detail` reuses that key's first visible human label

This deliberately complements `ed.binding-section-rows` instead of replacing it: grouped rows still answer the full picker-browsing question, while this tiny register answers the smaller first-stop question of what reachable binding buckets exist right now.

### `ed.keymode-inventory-rows`

Returns the tiny shared active/known keymode inventory reused by plain `showkeymodes`.

```text
[[section mode once?] ...]
```

Where:
- `section` is `"active"` or `"known"`
- `mode` is the visible keymode name for that section
- `once?` is `1` when the active mode is currently one-shot / transient

This deliberately complements `ed.keymode-rows` instead of replacing it: the lower-level hostcall still exposes the raw active stack plus the unfiltered known binding-mode list, while this tiny register preserves the exact human-facing active/known snapshot that `showkeymodes` already presents.

### `ed.keymode-detail-row`

Returns the tiny shared exact keymode row reused by plain `showkeymode NAME`.

```text
[mode active? known? once? binding_count sample_key|0 sample_action|0 sample_desc|0] | 0
```

Where:
- `active?` is `1` when the mode is currently on the active stack
- `known?` is `1` when the mode is part of the visible durable keymode inventory shown by `showkeymodes`
- `once?` is `1` when the currently active mode is one-shot / transient
- `binding_count` is the current number of exact bindings registered for that mode
- `sample_*` expose one stable first binding when available, otherwise `0`

This deliberately complements `ed.keymode-inventory-rows` instead of replacing it: the broader hostcall still answers the active-vs-known register question, while this tiny row answers the adjacent exact question without forcing callers to rejoin that register with lower-level mode-local binding rows.

- active modes are considered from top of stack to bottom
- global bindings are used as fallback
- if two modes bind the same key, the higher-precedence mode wins
- rows are sorted by key for deterministic tests and tooling

This is intentionally close to the question:

> what can I press right now?

### `ed.binding-detail-row`

Returns the tiny shared resolved-binding row reused by plain `showkey KEY`.

```text
[mode key action-spec desc|0 group|0 [file line col]|0] | 0
```

This deliberately complements `ed.resolve-key` / `ed.resolve-key-info` instead of replacing them: those lower-level helpers still expose direct resolver results, while this named row makes the human-facing `showkey` surface explicit and reusable for scripts and future UIs. Rev460 extends that same exact row into command-bar completion too, so `showkey KEY` can complete directly against currently reachable bindings without dropping back to a generic or empty prompt row.

### `ed.resolve-key`

Resolve one key through the active keymode stack.
Returns:

```text
[mode key action-spec group|0 [file line col]|0] | 0
```

This is the low-level machine-readable sibling of `showkey KEY`; rev429 adds `ed.binding-detail-row` as the named shared row for that exact human-facing surface.

## New command-bar surface

```text
showbindings [MODE|active]
showbindingmodes [QUERY]
showkeymode NAME
showkeymodes
whichkey
```

### `showbindings`

- no argument means `active` (and rev572 lets the plain command-bar row preview that default active inventory before Enter)
- `showbindings active` shows the precedence-resolved current keymap
- `showbindings MODE` shows exact bindings for that mode (and rev571 keeps unmatched typed mode names visible in command-bar completion long enough to preview `0 bindings`)
- `showbindings global` shows the global map
- empty and non-empty results both stay count-aware (`0 binding(s)` vs `N binding(s), ...`)

Example:

```text
bindings active: 3 binding(s), Ctrl-g@goto!->command:showkeymodes, Ctrl-x@nav->command:quit, Ctrl-z@global->command:help
```

The `!` suffix means the winning mode is currently one-shot / transient.

### `showbindingmodes`

Reports one tiny broad summary of the currently reachable binding surface grouped by winning mode.

Example:

```text
showbindingmodes: 3 section(s), 3 binding(s)
goto: 1 (e.g. Ctrl-g — show portable statusline summary)
nav: 1 (e.g. Ctrl-x — request editor quit)
Global: 1 (e.g. Ctrl-z — show help for commands/actions)
```

This is the tiny broad sibling of `showbindings active` / `whichkey` and the lighter machine-facing sibling of `ed.binding-section-rows`. Rev443 adds the matching hostcall too: `ed.binding-section-summary-rows` exposes the same shared `[label/count/sample_*]` rows so scripts and future UIs can ask what binding buckets are reachable right now without reopening picker state or walking every grouped row. Rev468 extends that same tiny row into command-bar completion too, so `showbindingmodes [QUERY]` can complete directly to visible winning-mode labels without dropping back to opaque raw text.

### `showkeymode`

Reports one visible or currently active keymode directly.

Example:

```text
keymode goto [active once known] bindings=1 sample=g->command:showstatus (show portable statusline summary)
```

This is the tiny exact sibling of the broader `showkeymodes` register. Rev442 adds a matching machine-facing sibling too: `ed.keymode-detail-row` exposes the same exact `[mode active?/known?/once?/binding_count/sample_*]` row so scripts and future UIs can inspect one mode directly without rejoining inventory state with lower-level binding rows.
Rev459 extends that same exact row into command-bar completion too: `showkeymode NAME`, `showbindings MODE`, `keymode`, `pushkeymode`, `pushkeymode-once`, and `prefixmode` now all reuse the exact keymode row for their prompt metadata, so mode selection keeps active/once/known-or-internal state plus one sample binding visible instead of degrading back to a generic `keymode` label. Rev571 tightens the special `showbindings active` / unmatched-mode cases too: the `active` prompt row now previews the live reachable-binding count plus one sample winner, and unmatched typed mode names stay visible long enough to preview `0 bindings` instead of disappearing.

### `showkeymodes`

Reports the current keymode stack as two tiny inventories:

- `active keymodes: ...` keeps the currently effective stack in precedence order, defaulting to `global` when no mode is active
- `known keymodes: ...` keeps the durable visible binding-mode list while hiding tiny internal housekeeping/capture modes from that second line

Rev426 adds a tiny machine-facing sibling for that exact human surface too: `ed.keymode-inventory-rows` exposes the same ordered `[section/mode/once]` rows that `showkeymodes` already renders, so scripts stop reconstructing the register from split `ed.keymode-rows` results and local filtering policy.

### `whichkey`

Originally this was just a tiny alias for `showbindings active`. In rev38 it now
prefers **human descriptions** when available (custom binding docstrings first,
then derived labels from command/action docs).

Example:

```text
whichkey: 2 binding(s), Ctrl-x@nav->request editor quit, Ctrl-z@global->show help for commands/actions
```

This is deliberately *not* a popup system or timeout-driven UI feature.
It is a headless discovery command that future UIs can render however they want. Rev423 adds a tiny shared machine-facing sibling for that exact curated surface too: `ed.available-binding-inventory-rows` exposes the same ordered `mode/key/action/label/once` rows that `showbindings active` / `whichkey` already present to humans, so scripts stop re-deriving one-shot state and display labels by hand.

## Why this shape

The goal is to separate:

- **semantic discovery data** (available bindings, resolved keys)
- **rendering policy** (popup, infobar, command-line text, etc.)

That keeps the editor core testable and portable while still learning from the
"show me what keys are available after a prefix" workflows found in other editors.

## Non-goals

- no timeout-based multi-key parser yet
- no popup/window UI contract yet

Binding descriptions now exist as data (see `docs/78-editor-binding-descriptions.md`).
The discovery wire format stays stable because the description-rich rows live in sibling hostcalls rather than replacing the exact rows introduced here.


## Search-first sibling

Later revisions added a separate **search-first** sibling to these exact discovery rows:

- `bindingpick [QUERY]`
- `BindingPrompt`
- `ed.binding-prompt` / `ed.binding-prompt-rows` / `ed.binding-section-rows`

That surface reuses the same resolved-binding substrate but adds ranked search over key, action-spec, and human description text. Recent revisions also let multi-term queries match across those fields out of order, so searches like `quit Ctrl` or `editor quit` can still find the right binding without requiring exact phrasing. The same visible winning-mode labels now also group the prompt into sections (`Prompt`, active mode names like `nav`, `Global`) so future UIs and scripts do not need to reverse-engineer picker headers from flat row text.
