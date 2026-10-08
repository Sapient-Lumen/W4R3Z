# Rev446 — command palette buckets get one tiny broad summary row

## What changed

Micromax already had strong search-first command-palette surfaces:

- `commandpick [QUERY]` / `CommandPalette` / `ed.command-palette` opened the live searchable palette
- `ed.command-palette-rows` exposed the flat ranked register for scripts and future UIs
- `ed.command-palette-section-rows` exposed grouped visible buckets like `Recent Files`, `Recent`, `Commands`, `Actions`, and path-like `Directories` / `Files` / `Open` sections

But one small inspectability seam still remained: the palette was stronger at full grouped browse state than at the simpler first question future humans/LLMs often ask before drilling in:

> what broad command-palette buckets are visible right now?

Rev446 keeps the fix deliberately small:

- add `command_palette_section_summary_rows(QUERY)` in the editor core
- expose it as `ed.command-palette-section-summary-rows`
- add plain `showpalettegroups [QUERY]` for humans

## Row shape

`command_palette_section_summary_rows(QUERY)` / `ed.command-palette-section-summary-rows` return:

```
[label count sample_name sample_detail]
```

Where:

- `label` is the visible palette bucket (`Recent Files`, `Recent`, `Commands`, `Actions`, or path-like `Directories` / `Files` / `Open`)
- `count` is the number of currently visible rows in that bucket
- `sample_name` reuses the first visible palette item in that bucket
- `sample_detail` reuses that first row's detail text

Examples:

- `['Recent', 1, 'showstatus', 'showstatus - show portable statusline summary']`
- `['Actions', 1, 'CommandMode', 'Open the command bar']`

The shape intentionally stays tiny. Full grouped browse state still belongs to `commandpick` / `ed.command-palette-section-rows`.

## Why this matters

This is a small trust/flow improvement for Micromax's search-first command surface.

Future humans, scripts, and LLMs can already open the palette and can already inspect its grouped rows, but there was still no official first-stop register for the smaller broad question of what buckets are visible right now. The new summary rows and plain `showpalettegroups [QUERY]` keep that answer inspectable without opening the live prompt, scraping picker headers, or walking every grouped row.

## Focused tests

- `tests/test_editor_mx_commands_and_completion.py`
- `tests/test_editor_capabilities_registry.py`

## Next tiny seams

- some other grouped picker families still only expose their full grouped row shapes and not a lighter summary sibling
- the command palette is now inspectable at flat, grouped, and broad-summary levels, but future work may still want similarly tiny exact rows for other search-first picker-only surfaces if they remain worth the surface area
