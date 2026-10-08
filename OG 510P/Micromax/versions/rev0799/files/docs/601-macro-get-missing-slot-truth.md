# Rev660 - raw macro fetches stop fabricating missing slots

## Why

Micromax already had truthful macro *execution* behavior around missing names:
`macro play NAME` failed explicitly as `no such macro: NAME`, and the richer
inventory/status surfaces (`macro list`, `macro status`, `ed.macro-inventory-rows`,
`ed.macro-status-rows`) made it easy to inspect real saved state before running
automation.

But one narrow headless seam still lingered under the raw storage surface.
`Editor.get_macro(name)` used `self.macros.get(name, self.macro)`, which meant
*any* missing name quietly fell back to the current `last` macro steps. The
portable `ed.macro-get` hostcall inherited that behavior automatically.

That made missing-slot reads unsafe in exactly the wrong way: a script asking
for `ghost` could receive a perfectly real macro, just not the one it asked for.

## What changed

Rev660 keeps the fix deliberately tiny:

- `get_macro("last")` still returns the current default `last` macro steps
- any other missing name now returns `[]`
- `ed.macro-get` inherits that behavior automatically
- focused tests pin both the editor method and the hostcall contract

## Result

Raw macro fetches now tell the truth about missing names. Future scripts, tests,
and LLMs can ask for one exact macro slot without accidentally inspecting or
replaying whatever happens to be in `last`.
