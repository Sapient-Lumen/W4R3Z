# Makefile currentness refactor — rev0031

The Makefile is now a currentness surface. It should not contain stale `REV####` artifact defaults from older revisions.

## Why this matters

Future sessions often start with convenience commands. If those commands write old artifact names, the cube can appear inconsistent even when the manifest-driven harness is correct.

## Rule

Convenience commands should derive artifact prefixes from `src/browserrt.mjs` or use manifest-driven commands.

## Audit guard

`tools/check_cube.py` now fails when `Makefile` contains stale explicit artifact prefixes for older current revisions.
