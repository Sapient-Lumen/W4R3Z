# Partner choice can reward observable reciprocity while eroding hidden care

A new source adds an important caution to Concord's leave/rematch program.

- `RS-GR-134` studies partner choice when some helping is **observable** to third parties and some helping is **unobserved** but still keeps a partner in good enough condition to reciprocate later.
- The result is not simply “partner choice increases cooperation.”
- Instead, partner choice can increase **observable reciprocity/signalling-based help** while decreasing **unobserved stake-based help**.
- The paper also reports when the pro-cooperation effect is stronger: when interactions are shorter, when observers judge based on visible helping, and when multiple cooperative partners can be held simultaneously.

## Why this matters for Concord

This archive is already moving from fixed dyads toward partner choice and reputation.
`RS-GR-134` says the next implementor should not treat those as automatically Golden-Rule-like.
A world that rewards agents for being chosen can select for **being seen to help**, not necessarily for **quietly maintaining the other agent's welfare when nobody is watching**.

That is exactly the kind of failure mode a Golden-Rule program should surface rather than average away.

## Minimal implementor handoff

Any leave/rematch + reputation lane should publish at least two distinct help surfaces:

1. **observable help** that can influence reputation, partner choice, or third-party evaluation;
2. **unobserved partner-maintenance help** that affects the partner's condition or future ability to reciprocate even when no one else sees it.

If a candidate improves only on the first surface, treat that as **performative reciprocity** until stronger evidence appears.
