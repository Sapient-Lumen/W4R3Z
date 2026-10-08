# Rev603: runtime `plugin info NAME` keeps the loaded-state witness

## What changed

Filtered runtime `plugin info NAME` no longer flattens a healthy loaded no-description target back to bare `errors: 0`.
When Micromax already knows the plugin is loaded and there is no richer detail to show, the final error line now says `errors: 0 · loaded plugin`.

## Why it matters

This is the same tiny state witness exact command-bar completion and runtime `showplugin NAME` already preserve. Keeping `plugin info NAME` aligned makes the narrow exact plugin-inspection loop more coherent before and after Enter.
