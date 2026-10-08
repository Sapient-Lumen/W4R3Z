# Rev445: tiny shared option-family summary rows

## What changed

- Added `option_section_summary_rows(QUERY)` in the editor core.
- Added hostcall `ed.option-section-summary-rows`.
- Added plain `showoptiongroups [QUERY]`.
- Added focused coverage for the new command/hostcall/capability surface.

## Why this matters

Micromax already had the right two ends of option inspection:

- plain `show` for the full active canonical inventory
- plain `showoption NAME` for one exact value/default/doc row

But one small gap still remained between those two scales. If a human, script, or
future UI wanted the first broad question answered honestly — *what option
families exist right now, and roughly what lives in each family?* — the repo
still forced them to walk the full canonical `show` inventory and infer family
structure from dotted names by hand.

That was workable, but it was noisier than the recent topic/docs/plugin/hook/
binding summary surfaces. Rev445 keeps the follow-up deliberately small and
aligned with those newer discovery helpers.

## New shared row shape

`option_section_summary_rows(QUERY)` returns rows shaped like:

- `[label count sample_name sample_detail]`

Current labels stay deliberately human and tiny:

- `Editor` for unprefixed options like `readonly` or `autosave`
- dotted-family labels like `Capabilities`, `Prompt`, `Help`, `History`,
  `Recent`, `Save Cursor`, `Viewport`, `TUI`, etc.

`sample_name` and `sample_detail` reuse the first visible canonical option row in
that family, so the summary stays count-aware without inventing a second richer
schema.

## Human-facing command

`showoptiongroups [QUERY]` now prints the same shared family summary.

Examples:

- `showoptiongroups`
- `showoptiongroups disallow edits`
- `showoptiongroups cap.persist`

This gives humans the same side-effect-free first-stop family view that scripts
and future UIs get through `ed.option-section-summary-rows`.

## Design notes

- This does **not** replace `show`.
- This does **not** create a second option registry.
- This does **not** widen config semantics.
- It only adds one tiny grouped summary register on top of the existing
  canonical option inventory.

That keeps the archive aligned with the broader Micromax direction:

- tiny inspectable surfaces
- one shared truth per human/host boundary
- broad browse state that stays easy for future LLMs to ask about directly
