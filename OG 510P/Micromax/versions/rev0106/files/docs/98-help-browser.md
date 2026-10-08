# Help browser

This page exists mostly as **test data** for Micromax’s docs-backed help system.
It also acts as a tiny “index” you can navigate *inside* the editor.

In a docs buffer:
- `Enter` follows the link under the cursor
- `Backspace` goes back
- `y` copies the link target under the cursor

## Links

- [Vision](00-vision.md)
- [Softwrap](94-softwrap.md)
- [Host API](31-host-api.md)
- [Open URL under cursor](101-open-url-under-cursor.md)

## External links

External links are shown as a message by default.

If you enable the capability gate, they can be opened via the host:

```text
set cap.open-url true
```

Even when enabled, Micromax confirms by default before opening external links.
You can turn the confirmation off:

```text
set open-url.confirm false
```

- [micro editor](https://micro-editor.github.io/)



## Reference-style links

Micromax's docs browser also understands common markdown reference links:

- [Vision ref][visionref]
- [Vision shortcut]

[visionref]: 00-vision.md
[Vision shortcut]: 00-vision.md

## Autolinks

Autolinks are also recognized:

- <https://micro-editor.github.io/>

## Link picker

While in a docs buffer, you can also pick links directly:

- `helplinkpick` (or `helplinkpick QUERY`)

In the TUI, link suggestions are grouped into sections.

- Default: **Docs**, **Files**, and **External** (option: `help.linksections kind`)
- Optional: grouped by the nearest markdown heading (option: `help.linksections heading`)

Picker UX:
- `Up` / `Down` moves the highlighted selection
- `PageUp` / `PageDown` jumps selection by a small window (option: `prompt.page`, default 8)
- `Alt-Up` / `Alt-Down` jumps between section headers
- `Ctrl-y` copies the selected row (for links: copies the target URL/path)
- `Ctrl-Home` / `Ctrl-End` jumps to first/last selection
- Option: `prompt.wrap` controls wrap vs clamp when moving past ends (default: wrap)
- In the minimal TUI, the active section header is repeated as a sticky header when paging through long sections


## Navigator picker

If you just want a single “go to something on this page” picker, use:

- `helpnavpick` (or `helpnavpick QUERY`)

This combines **Headings** and the same link sections used by `helplinkpick`.


## Outline picker

Docs pages can also be navigated by headings:

- `helpoutlinepick` (or `helpoutlinepick QUERY`)
- `helpjump` (or `helpjump QUERY`) — jump directly to the best-matching heading
