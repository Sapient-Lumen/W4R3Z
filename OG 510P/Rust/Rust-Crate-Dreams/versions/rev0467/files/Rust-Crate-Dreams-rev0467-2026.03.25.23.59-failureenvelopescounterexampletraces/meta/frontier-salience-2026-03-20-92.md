# Frontier salience snapshot — 2026-03-20 (92)

This pass did **not** add another release renderer or push the pack toward generic publication tooling.
It deepened **P-0514 Crate Upgrade Pack Kit** by making two more receiver-facing truths explicit:

- **export-posture truth** — whether the lane stays private/internal, needs redaction, or is actually fit for public downstream export;
- **publication-surface truth** — the exact public entry points and off-surface omissions that make up the stable contract.

## Main judgment

The sharper missing layer is still the **joined upgrade-support contract** above today’s substrate.
But after source heads, readiness, review queue, and consistency all became explicit, the next ordinary lie sat at the export boundary:

1. internal maturity still got mistaken for public-shareable posture,
2. and the whole working tree could still get mistaken for the stable public contract.

Those are not process-only concerns.
They are ordinary ways a careful migration bundle still turns into a misleading downstream surface.

## Why this beat nearby work again

The archive already had enough to say:

- where hazards came from,
- which imports were native versus summarized,
- which source heads were operational versus citation-ready,
- which scope and follow-through truths were still partial,
- and whether the pack stayed `hold`, reached `candidate`, or looked `freeze_ready`.

What it still lacked was a compact way to say:

- “this lane is still private because redaction blockers remain,”
- “this frozen public contract exports only these exact files/receipts,”
- and “these floating or private working materials stay off-surface even though maintainers still use them.”

That is a real product refinement, not just more release ceremony.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better freezeable choice compounds later support work.
2. **P-0514 Crate Upgrade Pack Kit** — stronger again because it now distinguishes internal maturity from export posture and makes the public contract surface exact.
3. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown and drain truth remain widely under-served.
4. **P-0522 Crate Persistence Surface Pack Kit** — still strong because durable-state promises remain under-specified.
5. **P-0521 Crate Resource Surface Pack Kit** — still strong because admission and backlog truth stay receiver-facing and testable.
