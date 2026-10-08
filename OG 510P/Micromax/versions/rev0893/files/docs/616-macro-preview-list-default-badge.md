# Rev675 - badge preview-side `last` inventory samples too

## What changed

Micromax now keeps the `[default]` badge on prompt-side macro inventory samples when `last` is the sampled saved slot.

- `macro list` preview rows can now show `last (N step[s]) [default]`
- `macro status` preview rows can now show `... e.g. last (N step[s]) [default]`
- runtime inventory strings were already using the same badge from rev674

## Why it matters

Rev674 fixed the runtime inventory strings, but the command-bar sample path could still flatten `last` back into a plain saved macro. That was tiny, but it made the preview lane slightly less trustworthy than the runtime lane immediately behind it.

This rev keeps the badge consistent across both sides of the same inventory story.

## Verification

Focused prompt tests pin `macro list` and `macro status` preview rows when `last` is the only obvious saved sample.
