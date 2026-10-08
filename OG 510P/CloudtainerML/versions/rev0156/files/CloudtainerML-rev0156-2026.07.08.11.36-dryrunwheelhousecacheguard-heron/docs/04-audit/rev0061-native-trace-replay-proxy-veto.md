# rev0061 — native trace replay proxy veto

## Why this revision exists

rev0060 produced a replayable learned trace packet and found a score-storage-allowed sparse opportunity under proxy work units. That was useful, but risky: proxy arithmetic can silently promote a sparse path before native loops have actually consumed the same scores and values.

rev0061 converts that proxy opportunity into a native C++ materialized-score replay. The input is the rev0060 local tiny-trained trace packet. Scores are already materialized, so this is not a QK computation benchmark and not a fused-kernel claim.

## What was measured

The native replay compares two score-consumption/value-accumulation paths over the same 256 rows:

- dense materialized-score attention over all 64 tokens;
- mass-histogram sparse attention with a 0.95 score-only mass target.

Both use native C++ loops. The sparse path still needs global score storage as input.

## Result

The mass-histogram path preserves output quality on this packet but is slower than dense in the measured score-consumption replay:

- native speedup vs dense score-consumption: `0.810951219572`
- quality rate: `1.0`
- mean selected fraction: `0.45166015625`
- rev0060 proxy speedup: `1.2770849410104002`

That converts a proxy opportunity into a measured non-win on this CPU path.

## Claim boundary

This revision does **not** close the public/pretrained trace blocker, QK score-computation blocker, or GPU/fused-kernel blocker. It only says that the learned trace packet now has a native materialized-score replay, and that proxy-only promotion is vetoed.
