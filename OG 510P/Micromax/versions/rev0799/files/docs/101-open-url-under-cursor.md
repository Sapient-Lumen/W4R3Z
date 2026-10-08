# Open URL under cursor (rev89)

Rev638 note: plain `urlopen`, alias `openurl`, and `urlcopy` now keep the live under-cursor URL visible in exact command-bar completion before Enter. That tiny preview now mirrors the same trust boundary the runtime already knows: open can preview `disabled (cap.open-url) · URL` or `URL [confirm]`, copy can preview the exact `URL`, and both commands can say `no url under cursor` without falling back to generic command or alias metadata.

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

When confirmation is required, the prompt also names the request source
(`help`, `cursor`, or explicit `command`), and the editor enters a tiny
capture keymode:

- `y` / `Enter` → open
- `n` / `Esc` → cancel
- `c` → copy the URL

This keeps URL opening explicit and prevents accidental browser launches from stray keypresses.

## Feedback

- exact command-bar completion now previews the same live under-cursor URL/open-boundary truth before Enter: `disabled (cap.open-url) · URL`, `URL [confirm]`, `URL`, or `no url under cursor`
- successful open: `urlopen: URL`
- successful copy: `urlcopy: URL`
- missing under-cursor URL: `urlopen: no url under cursor` / `urlcopy: no url under cursor`
- confirmed opens/copies keep the same typed command prefixes too: accepting confirmation reports `urlopen: URL`, confirmation-copy reports `urlcopy: URL`, and docs-help links routed through the same confirmation surface report `helpfollow: URL` / `helplinkcopy: URL`
- capability denial keeps the same typed prefix: `urlopen: disabled (cap.open-url) ...`

## Tips

- URL detection trims common trailing punctuation (like commas or closing parentheses) as a best-effort heuristic.
- For docs buffers, `Enter`/`Backspace`/`y` remain dedicated to the help browser (follow/back/copy markdown link target).
