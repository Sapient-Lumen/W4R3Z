# Tiny visible brace matching (`matchbrace`, `matchbraceleft`)

Rev182 adds a deliberately small, renderer-local brace cue to the curses TUI.

## What it does

- `matchbrace=true` bold-underlines visible brace pairs
- `matchbraceleft=true` also checks the character immediately left of the cursor
- supported pairs are only `()`, `[]`, and `{}`
- matching is textual and nest-aware across the whole buffer
- ordinary buffers and docs/help buffers both use the same tiny cue

## What it does **not** do

- no syntax awareness yet
- no persistent brace spans in headless editor state
- no jump-to-match action yet
- `matchbracestyle` now provides one tiny style choice (`underline` or `highlight`), but still no broader theme contract

## Why this size

Micromax already has several tiny renderer overlays (`hlsearch`, `cursorline`,
`hltrailingws`, `hltaberrors`, `colorcolumn`, `scrollbar`), so visible brace
matching no longer needs to wait for a full span/theme subsystem. The goal here
is simply to make bracket-heavy text a little easier to scan while keeping the
archive small, explicit, and easy to port.
