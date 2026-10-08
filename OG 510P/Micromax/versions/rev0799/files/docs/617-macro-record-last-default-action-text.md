# Rev676 - let saved `macro record last` say `overwrite default slot on save`

## What changed

Micromax now keeps the default-slot wording visible in the exact saved record row for `last`.

- saved `macro record last` / `macro rec last` / `macro start last` rows now say `overwrite default slot on save`
- other saved record rows like `demo` still say `overwrite on save`
- new/missing `last` still says `record default slot`

## Why it matters

The exact play path already spoke in explicit default-slot terms, but the exact saved record path still flattened `last` back to a generic overwrite action. That was tiny, but it made the default slot feel less intentional exactly where a user chose to overwrite it.

## Verification

Focused prompt tests pin the saved `last` record row wording while preserving the generic overwrite wording for non-default saved slots.
