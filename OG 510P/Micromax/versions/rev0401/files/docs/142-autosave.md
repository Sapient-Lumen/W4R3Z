# Autosave (`autosave`) (rev201)

Micromax now treats `autosave` as a real ordinary editor option instead of leaving timed saves to future plugins or future UIs.

## Option

- `autosave` (int, default `0`)

Interpretation:
- `0` disables autosave
- `N > 0` means: best-effort save dirty path-backed buffers every `N` seconds

## Current rule

Autosave is intentionally conservative and shared-core:

- only buffers that already have a real path participate
- the existing host-driven timer pump is still the clock; there are no threads
- autosave reuses the same save path as manual `save`, so save-time options still apply:
  - `rmtrailingws`
  - `eofnewline`
  - `mkparents`
  - `fileformat`
  - `encoding`
- read-only buffers are skipped
- save failures become ordinary editor messages (`autosave error: ...`)
- `quit` first tries immediate autosave for eligible dirty buffers, then falls back to the usual unsaved-changes warning for anything still dirty

## Why this shape

Current upstream micro docs still frame `autosave` as a normal editor option rather than plugin sugar. Micromax already had the smallest honest substrate for that behavior:

- a deterministic timer pump
- one shared save path
- a deliberately simple dirty bit

So the right move was to reuse those pieces, not invent crash-recovery backups, background daemons, or undo persistence.

## Non-goals (for now)

Rev201 does **not** try to implement:

- backup-file rotation / crash recovery
- undo persistence (`saveundo`)
- autosaving unnamed scratch buffers
- “save only when content hash changed” logic beyond the current ordinary dirty bit

## Pointers

- editor core: `src/micromax_editor/editor.py`
- quit command: `src/micromax_editor/command_dispatcher.py`
- related timer model: `docs/90-timers.md`
