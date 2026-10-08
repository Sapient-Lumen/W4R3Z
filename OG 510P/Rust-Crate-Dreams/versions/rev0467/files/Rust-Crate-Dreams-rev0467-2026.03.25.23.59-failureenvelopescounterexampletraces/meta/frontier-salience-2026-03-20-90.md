# Frontier salience snapshot — 2026-03-20 (90)

This pass did **not** add another release workflow, another docs scraper, or another codemod.
It deepened **P-0514 Crate Upgrade Pack Kit** by making two more receiver-facing truths explicit:

- **source-head truth** — which imported guidance head is current for operators and which source, if any, is actually citation-ready;
- **pack-readiness truth** — whether the whole pack honestly stays `hold`, advances to `candidate`, or is truly `freeze_ready`.

## Main judgment

The sharper missing layer is still the **joined upgrade-support contract** above today’s substrate.
But after the authority / lineage / arbitration / import / posture passes, the next false-merge risk sat in two places:

1. latest operational guidance still looked interchangeable with citation-ready guidance,
2. and overall pack maturity still had to be inferred by hand from many otherwise honest receipts.

Those are not process-only differences.
They are ordinary ways a half-ready migration story turns into an over-claimed public contract.

## Why this beat nearby work again

The archive already had enough to say:

- where hazard claims came from,
- which package/workspace lanes were really checked,
- what native imports and fixup posture existed,
- and which follow-through work stayed active.

What it still lacked was a compact way to say:

- “this import family has an operational head but no citation-ready head yet,”
- “this pack is informative but still belongs in `hold`, not `freeze_ready`,”
- and “here is the single safest next move before we freeze this release-pair contract.”

That is a real product refinement, not just more archive ceremony.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better freezeable choice compounds later support work.
2. **P-0514 Crate Upgrade Pack Kit** — now stronger again because it distinguishes source heads and pack readiness above source lineage, imports, authority, scope, and follow-through.
3. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown and drain truth remain widely under-served.
4. **P-0522 Crate Persistence Surface Pack Kit** — still strong because durable-state promises remain under-specified.
5. **P-0521 Crate Resource Surface Pack Kit** — still strong because admission and backlog truth stay receiver-facing and testable.
