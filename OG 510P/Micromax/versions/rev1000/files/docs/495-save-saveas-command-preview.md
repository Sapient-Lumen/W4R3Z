# Save/saveas command previews (rev553)

Rev553 is a small trust-first follow-up to Micromax's existing save feedback.

The actual save path was already doing the careful work:

- `save` / `saveas` already reported the real written path after Enter
- pathless `save` already failed honestly as `save: buffer has no path`
- protected/read-only buffers already rejected writes
- `save FILE` already reused ordinary filesystem completion

But one small seam still lingered exactly where users decide whether a write feels safe: typing plain `save` or `saveas` in the command bar still showed a generic exact-command row instead of the current write target or blocker.

## What changed

The no-arg command rows for `save` and `saveas` now preview current buffer write state before Enter.

Examples:

- `save` → `target /tmp/demo.txt | dirty`
- `save` → `buffer has no path | dirty · use saveas FILE`
- `saveas` → `current path /tmp/demo.txt | dirty · expects FILE`
- `saveas` → `new file | dirty · expects FILE`

The preview also carries a small `readonly` cue when the current buffer is protected/read-only.

## Why this matters

This is intentionally tiny, but it tightens one important trust loop:

- users can see whether Micromax already has a write target
- pathless buffers stop looking deceptively ready to save
- protected buffers stop hiding behind generic command provenance
- future frontends/scripts/LLMs inherit the same small write-state summary the command bar already trusts

## What this does not solve yet

Rev553 stays deliberately small. It does not add:

- a save preview diff
- a richer overwrite/permission inspector
- project-wide write summaries
- atomic-save / backup / fsync policy work

Those are still good trust-first follow-ups.
