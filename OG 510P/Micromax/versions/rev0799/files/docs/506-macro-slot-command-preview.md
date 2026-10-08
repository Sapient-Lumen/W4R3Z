# Rev564 — truthful `macro play NAME` / `macro record NAME` slot previews

## Why

Micromax already had the right tiny state underneath named macro slots:

- `macro_inventory_rows()` already exposed saved slot names and step counts headlessly
- `macro play NAME` already depended on that same saved-slot inventory
- `macro record NAME` already knew whether a typed slot name would overwrite an existing macro or create a new one

But command-bar completion for `macro play NAME` / `macro record NAME` still collapsed every visible slot row back to a generic `macro slot` placeholder, and `macro play` still suggested the empty default `last` slot even when playback would immediately fail.

## What changed

- added shared `_prompt_macro_slot_row(...)`
- `macro play NAME` completion now reuses saved slot counts for exact slot rows
- `macro record NAME` / `macro rec NAME` / `macro start NAME` completion now reuses the same slot counts and distinguishes overwrite-vs-new-slot intent
- `macro play` candidates now come from `macro_inventory_rows()` instead of raw `self.macros.keys()`, so the empty default `last` slot stops appearing as a playable suggestion
- focused tests pin empty-play, missing-slot, saved-slot, overwrite, and default-record-slot cases

## Examples

- `macro play demo` rows can now show `demo (1 step) · play macro`
- `macro record demo` rows can now show `demo (1 step) · overwrite on save`
- exact new targets can now say `new macro slot · record new macro`
- exact `last` recording rows can now say `last [default] · record default slot`
- empty `macro play` now shows no fake `last` candidate

## Why this shape

This keeps macro-slot discovery aligned with the same tiny headless inventory Micromax already trusts after Enter. The change stays deliberately narrow: no macro semantics changed, only the pre-Enter rows stopped pretending that every slot looked the same.

Future humans and LLMs can now tell whether a macro slot is playable, overwritable, missing, or just the default recording slot before they submit the command.

## Checks

Focused coverage now pins:

- empty `macro play` omitting the empty `last` slot
- missing exact `macro play NAME` rows reporting `no such macro`
- saved `macro play NAME` rows showing exact step counts
- exact new/default `macro record NAME` rows showing `record new macro` / `record default slot`
- saved `macro record NAME` rows showing `overwrite on save`
