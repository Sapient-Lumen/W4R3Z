# Open URL under cursor (rev89)

Micromax-editor supports a small, safe-by-default workflow for working with URLs in any buffer.

## Commands

- `urlopen` — open the URL under the cursor
- `urlopen URL` — open an explicit URL
- `openurl` — alias for `urlopen`

- `urlcopy` — copy the URL under the cursor
- `urlcopy URL` — copy an explicit URL

Recognized URL forms are intentionally conservative:

- `http://...`
- `https://...`
- `mailto:...`

## Default keybindings

The core plugin binds:

- `Alt-o` → `OpenUrlUnderCursor`
- `Alt-y` → `CopyUrlUnderCursor`

This matches common “open link under cursor” editor muscle memory (and mirrors a small micro plugin that uses `Alt-o`).

## Safety boundaries

Opening external URLs is **capability-gated**:

- `cap.open-url` (default: `false`)

Even when enabled, opening URLs is **confirmed by default**:

- `open-url.confirm` (default: `true`)

When confirmation is required, the editor enters a tiny capture keymode:

- `y` / `Enter` → open
- `n` / `Esc` → cancel
- `c` → copy the URL

This keeps URL opening explicit and prevents accidental browser launches from stray keypresses.

## Tips

- URL detection trims common trailing punctuation (like commas or closing parentheses) as a best-effort heuristic.
- For docs buffers, `Enter`/`Backspace`/`y` remain dedicated to the help browser (follow/back/copy markdown link target).
