# Frontier salience snapshot — 2026-03-20 (89)

This pass did **not** add another codemod, another release bot, or another analyzer.
It deepened **P-0514 Crate Upgrade Pack Kit** by making two more receiver-facing truths explicit:

- **native import truth** — which upgrade facts came from machine-native tool/report surfaces, how they were consumed, and whether the lane was stable, unstable, external, or mixed;
- **fixup posture truth** — whether an observed fix is manual-only, suggestion-only, approval-required, or bounded-autonomous.

## Main judgment

The sharper missing layer is still the **joined upgrade-support contract** above today’s substrate.
But after the authority / scope / lineage / arbitration passes, the next false merge risk sat in two places:

1. native tool import and later summary still looked interchangeable,
2. fix capability and allowed execution posture still looked interchangeable.

Those are not pedantic differences.
They are ordinary ways upgrade support becomes misleading.

## Why this beat nearby work again

The archive already had enough to say:

- what hazard classes exist,
- where the hazard claims came from,
- which package/workspace lanes were really checked,
- and which follow-through work is still active.

What it still lacked was a compact way to say:

- “this fact came from a native tool import rather than a later summary,”
- “this native lane is stable versus unstable versus merely external,”
- and “this fix exists, but the lane still only permits an approval-gated or manual execution posture.”

That is a real product refinement, not just another naming pass.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better freezeable choice compounds later support work.
2. **P-0514 Crate Upgrade Pack Kit** — now stronger again because it distinguishes native import truth and fixup posture above source lineage, authority, scope, and follow-through.
3. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown and drain truth remain widely under-served.
4. **P-0522 Crate Persistence Surface Pack Kit** — still strong because durable-state promises remain under-specified.
5. **P-0521 Crate Resource Surface Pack Kit** — still strong because admission and backlog truth stay receiver-facing and testable.
