# Rev480 — command-palette path-completion rows now keep open/recent context

## Why

Micromax already treated file-opening through the command palette as a first-class
flow: selecting a palette file row reported the landed target explicitly, and
rev479 made visible `Recent Files` rows reuse exact `recent_detail_row(PATH)`
metadata instead of flattening back to basename + parent.

But one adjacent seam still lagged behind that same trust model. When a query
looked like a filesystem path, the palette still rendered `openpath` completion
rows as generic `file` / `dir` items with a blank info slot, even when one
visible target was already recent, already open, dirty, or at least clearly in
a particular parent directory.

## What changed

- add one tiny `_command_palette_open_path_row(...)` helper that formats palette
  filesystem rows in one place
- exact file targets now reuse `recent_detail_row(PATH)` state when the path is
  already in the recent-file MRU
- non-recent but currently open file targets keep best-effort open/dirty/readonly
  cursor state instead of going blank
- ordinary filesystem completion rows now keep a small parent-directory cue when
  Micromax has no richer exact state to reuse
- focused tests pin both the live `command_palette_apropos_rows()` contract and
  the hostcall `ed.command-palette-rows QUERY` contract for visible `openpath` rows

## Result

Filesystem completion stays tiny and capability-gated, but the palette stops
throwing away context it already knows about the visible file target. If one
row already points at a recent or open file, Micromax keeps that tiny honest
state visible before selection; if not, it still preserves enough parent-path
context to keep neighboring file rows legible.
