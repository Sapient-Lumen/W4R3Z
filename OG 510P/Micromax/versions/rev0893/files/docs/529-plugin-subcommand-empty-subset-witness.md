# Rev587: keep a live inventory witness when an exact plugin subcommand has an empty subset

## Why

Micromax already made the broad plugin entry points truthful before Enter:
`showplugins`, `plugin`, `pluginpick`, and `showplugin` all distinguish an
unavailable plugin manager from a real empty manager and from a populated
inventory. But the narrower exact subcommands still had one tiny trust gap.

When the plugin manager was live and the overall inventory was non-empty,
`plugin reload` and `plugin errors` still collapsed an empty target subset back
to bare counts like `0 loaded plugins` or `0 plugins with errors`. That was not
wrong, but it looked too much like a totally empty plugin manager and threw away
concrete state Micromax already knew.

## What changed

The exact no-arg command-bar rows for `plugin reload` and `plugin errors` now
keep one broad inventory witness when their own target subset is empty but the
manager still has plugins.

Examples:

- `plugin reload` with only broken plugins now previews
  `0 loaded plugins · 1 plugin total · e.g. beta [error, deps:missingdep]`
- `plugin errors` with only healthy loaded plugins now previews
  `0 plugins with errors · 1 plugin total · e.g. alpha [loaded]`

A truly empty configured plugin manager still keeps the simpler old rows:

- `plugin reload` → `0 loaded plugins`
- `plugin errors` → `0 plugins with errors`

An unavailable subsystem still stays explicit:

- `plugin reload` / `plugin errors` → `plugin manager not available`

## Why this shape

This keeps the change tiny and local. The subcommands still lead with the exact
subset count they care about, but they no longer make a live plugin subsystem
look empty just because one narrower target bucket currently has no matches.
That makes the command bar a little more truthful and more legible in headless
startup, plugin debugging, and future LLM-driven inspection loops.
