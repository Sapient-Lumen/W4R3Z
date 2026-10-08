# Rev678 - centralize macro `[default]` badge formatting

## What changed

Micromax now uses one tiny helper to add the shared `[default]` badge across macro surfaces.

- runtime list/status strings reuse the helper
- prompt-side inventory samples reuse the helper
- exact play/record/count slot rows reuse the helper

## Why it matters

By rev677 the visible macro wording was in a much better place, but the badge policy itself was duplicated in several spots. That made future edits riskier than they needed to be.

This rev is intentionally small and structural: keep the visible behavior the same, but make it harder for future changes to drift across nearby surfaces.

## Verification

Focused tests pin representative list/status/prompt/default-slot rows while the new helper takes over the shared formatting work.
