# Rev334: picker-driven navigation should not be silent

This is a tiny **flow/trust** follow-up to rev331–rev333.

Those recent revisions already tightened the ordinary command paths:
- `open` tells you what file/cursor it landed on
- `save` tells you what it wrote and whether save-time cleanup happened
- `buffer` / `prevbuf` / `close` / `only` / `closeall` tell you which buffer became active
- `goto` / `jump` / `helpjump` / `markjump` tell you where the cursor actually landed

But one small inconsistency remained: the editor's **searchable picker surfaces** still often behaved like the older, quieter editor.
The move worked, but the user had to infer the landing from the screen.

That was especially visible in:
- `jumppick`
- `helpoutlinepick`
- the heading side of `helpnavpick`
- internal-link selections from `helpnavpick` / `helplinkpick`

## Goal

Keep the rule simple:

> If a navigation surface moves the user somewhere meaningful, it should say where it landed.

That keeps typed commands and picker-driven navigation in the same UX dialect.
The point is not extra chatter; the point is to remove one last category of “I think it moved, but where exactly?” moments.

## What rev334 changes

Successful picker-driven navigation now reports the real landed target:
- `jumppick` → `jump: name @ line:col`
- `helpoutlinepick` → `helpjump: name @ line:col`
- heading-side `helpnavpick` → `helpjump: name @ line:col`
- internal-link `helpnavpick` / `helplinkpick` selections now also report the landed docs target

External-link flows keep their existing explicit capability/confirmation messages.

## Why this matters

This is small, but it strengthens all three current editor goals:

- **Trust**: success messages now match the real result even in picker-driven flows.
- **Taste**: navigation surfaces feel more internally consistent.
- **Flow**: the user does not need to stop and re-orient after a successful search selection.

## Scope discipline

This is intentionally not a large redesign of pickers or docs navigation.
It does not add previews, diffs, richer breadcrumbs, or new picker models.
It only makes already-correct navigation more explicit.

That keeps the change easy to test, easy to reason about, and easy for future contributors or LLMs to continue.
