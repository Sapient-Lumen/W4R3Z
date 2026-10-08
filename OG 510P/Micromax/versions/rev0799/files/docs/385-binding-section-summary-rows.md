# Rev443 — reachable bindings get one tiny broad summary row

## What changed

Micromax already had good current-binding inspection surfaces:

- `showbindings active` exposed the flat reachable binding register for humans
- `whichkey` exposed the same register with friendlier labels
- `ed.available-binding-inventory-rows` exposed that same ordered register to scripts and future UIs
- `bindingpick` / `ed.binding-section-rows` exposed grouped reachable bindings by winning mode

But one small inspectability seam still remained: the reachable binding surface was stronger at full flat inventories and full grouped browse state than at the smaller first question future humans/LLMs often ask first:

> what broad winning-mode binding buckets are reachable right now?

Rev443 keeps the fix deliberately small:

- add `binding_section_summary_rows(QUERY)` in the editor core
- expose it as `ed.binding-section-summary-rows`
- add plain `showbindingmodes [QUERY]` for humans

## Row shape

`binding_section_summary_rows(QUERY)` / `ed.binding-section-summary-rows` return:

```
[label count sample_name sample_detail]
```

Where:

- `label` is the visible winning-mode bucket (`Prompt`, active mode names like `nav`, `Global`)
- `count` is the number of currently reachable bindings in that bucket
- `sample_name` reuses the first visible key in that bucket
- `sample_detail` reuses the first visible human-facing label for that key

Examples:

- `['goto', 1, 'Ctrl-g', 'show portable statusline summary']`
- `['Global', 1, 'Ctrl-z', 'show help for commands/actions']`

The shape intentionally stays tiny. Full grouped browse state still belongs to `bindingpick` / `ed.binding-section-rows`, while exact single-binding detail still belongs to `showkey KEY` / `ed.binding-detail-row`.

## Why this matters

This is a small trust/flow improvement for Micromax's live keymap surface.

Reachable bindings were already inspectable as a flat register and browseable as grouped rows, but there was still no official first-stop register for the smaller broad question of what winning-mode buckets currently exist. The new summary rows and plain `showbindingmodes [QUERY]` keep that answer inspectable without reopening picker state, scraping grouped headers, or walking every grouped row.

## Focused tests

- `tests/test_editor_keymap_discovery.py`
- `tests/test_editor_capabilities_registry.py`

## Next tiny seams

- some other picker-heavy navigation surfaces still expose only a flat inventory or a full grouped browse shape and not the lighter first-stop summary sibling
- the keymap loop is now inspectable at exact single-binding, flat reachable-register, grouped browse, exact keymode, and broad binding-summary levels, but future work may still want similarly tiny first-stop summaries for other active editor-state families
