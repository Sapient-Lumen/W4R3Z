# Rev677 - let fresh `macro record last` use the `[default]` badge too

## What changed

Micromax now uses the same default-slot badge style for unsaved exact record targets.

- fresh `macro record last` / `macro rec last` / `macro start last` rows now say `last [default]`
- saved `macro record last` rows still say `last (N step[s]) [default]`
- the action text remains `record default slot` for fresh `last`

## Why it matters

The saved record path already used the newer badge dialect, but the empty default-slot path still used the older parenthetical wording. That was tiny, but it made one exact record flow speak two slightly different visual languages.

## Verification

Focused prompt tests pin both the fresh `last [default]` row and the blocked exact `start last` row wording.
