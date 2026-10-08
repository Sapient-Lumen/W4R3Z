# Rematch worlds should budget compact repeat-sidecar rewrites by transition count

## Claim
When the real archive constraint is how many sidecar rewrites the inheritor can tolerate, compact repeat-sidecar planning should use an explicit transition-count budget rather than an implicit per-switch byte penalty.

## Why
The measured 0.18-repeat frontier over the next 256 novel appends shows that the rewrite-count ladder is highly uneven. The first allowed sidecar rewrite is worth 5679.676082 bytes against fixed route blocks. The third allowed rewrite is still structural and buys 2920.473524 bytes beyond the two-transition plan because it preserves the first big cliff fallback. But after four allowed rewrites, almost all of the reachable value is already captured.

On the current frontier, the first four rewrites capture 0.968419 of the full dynamic savings against fixed route blocks. The fifth rewrite buys only 134.276182 bytes, and the sixth only 1.979428 bytes. That means the inheritor should treat rewrite count as a scarce budget to spend on the biggest regime changes first, not as a reason to replay every small oscillation.

## Implementor rule
- With zero allowed rewrites, keep route blocks from the start.
- With one allowed rewrite, stay on bare pages through append 55 and then jump into route blocks.
- With three allowed rewrites, also keep the first cliff fallback to filters.
- With four allowed rewrites, also keep the final landing back to filters after append 238.
- Treat four rewrites as the practical ceiling on the current frontier unless the archive truly cares about the last few hundred bytes.
- Do not spend additional rewrite budget on the single-step cliff fallbacks unless those last bytes matter more than operational simplicity.

## Minimal takeaway
If rewrite count is the real bottleneck, buy the first four compact repeat-sidecar transitions and stop.
