# Open-target cursor parsing (`parsecursor`) (rev191, relanded in rev192)

Rev191/192 adds a tiny shared `parsecursor` option to the editor core.

## Option

- `parsecursor` (bool, default `false`)

When enabled, open targets like `file:line[:col]` are interpreted as:

- open `file`
- place the primary cursor at `line` / `col` immediately

Rules:

- line numbers are 1-based
- columns are 0-based (`file:42` means line 42, column 0)
- malformed suffixes stay literal paths
- if the literal path already exists, it wins over parsing (so existing colon-containing paths remain openable)
- explicit parsed targets override `savecursor` for that open

## Shared paths

The same policy now flows through:

- interactive `open` / direct `open_file(...)`
- capability-gated `ed.open`
- scripted `open ...` through `ed.command` / prompt submit
- path-style command-palette opens

That tradeoff is deliberate: the first pass mirrors micro's small `parsecursor`
idea without inventing a larger session/open-command subsystem.


Rev331 follow-up: explicit command-path `open ...` now also reports the post-open landed target as `opened: path @ line:col`, so parsecursor-driven opens stop being visually correct but verbally silent. The summary is taken from the real editor state after open, so it also covers savecursor-restored and already-open-buffer cases honestly.
