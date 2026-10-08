# Research — kitty remote control match builders and terminal adapters

## Current lesson

Kitty is a good example of why VHK needs app-native adapter lanes instead of forcing every terminal workflow through generic key replay.

Its remote-control surface already supports:

- sending arbitrary text into specific kitty windows
- matching target windows by title / cmdline / cwd and related window metadata
- talking to kitty over a socket when control happens from outside the target instance

That makes kitty a strong first terminal-native adapter seam.

## What changed in VHK

This revision adds `vhk gen-kitty-pack` as the first concrete export for the app-native protocol lane.

The pack intentionally stays narrow:

- it exports only kitty-targeted `TypeText` routes
- it requires explicit title/title-regex evidence to build a stable `--match`
- it records class/app_id-only kitty routes as skipped instead of pretending those can already be translated honestly
