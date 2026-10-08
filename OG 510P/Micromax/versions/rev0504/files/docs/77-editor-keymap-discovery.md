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

- no argument means `active`
- `showbindings active` shows the precedence-resolved current keymap
- `showbindings MODE` shows exact bindings for that mode
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
Rev459 extends that same exact row into command-bar completion too: `showkeymode NAME`, `showbindings MODE`, `keymode`, `pushkeymode`, `pushkeymode-once`, and `prefixmode` now all reuse the exact keymode row for their prompt metadata, so mode selection keeps active/once/known-or-internal state plus one sample binding visible instead of degrading back to a generic `keymode` label.

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
