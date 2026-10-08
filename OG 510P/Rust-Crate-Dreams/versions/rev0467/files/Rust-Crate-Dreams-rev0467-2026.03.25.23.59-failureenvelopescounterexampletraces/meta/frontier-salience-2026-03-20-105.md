# Frontier salience snapshot — 2026-03-20 (105)

This pass did **not** add another warning family, another export gate, or another summary register.
It deepened **P-0514 Crate Upgrade Pack Kit** by making one more receiver-facing truth explicit:

- **baseline-state truth** — upgrade packs can now say whether the checked subject was a pinned published release, a reconstructible package extract, a git checkout, or a mutable local workspace, and whether that subject was pristine, dirty, partially migrated, or generated.

## Main judgment

After lane-selection, config-basis, capture-context, session-honesty, replay-bridge, export, and public-trace surfaces became explicit, one ordinary lie still remained:

1. a lane could still sound like a clean release-to-release contract when the checked subject was already a mutable or partially migrated local workspace,
2. and exact command/config metadata could still launder a dirty tree into fake release-pair confidence.

Those are not small metadata details.
They change what kind of contract the pack is honestly allowed to export.

## Why this beat nearby work again

The archive already had enough to say:

- what command/config/session produced the evidence,
- how public readers could trace exported claims,
- and how a reviewer could replay or reconstruct the evidence.

What it still lacked was one compact way to say:

- “this lane was checked from a published crate baseline,”
- “this result came from a reconstructible package extract,”
- “this workspace was already partially migrated,”
- or “do not summarize this as a clean release-pair contract yet.”

That is a real product refinement, not another naming flourish.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better freezeable choice compounds later support work.
2. **P-0514 Crate Upgrade Pack Kit** — stronger again because exact command/config truth can no longer piggyback into fake pristine-baseline confidence.
3. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown and drain truth remain widely under-served.
4. **P-0522 Crate Persistence Surface Pack Kit** — still strong because durable-state promises remain under-specified.
5. **P-0521 Crate Resource Surface Pack Kit** — still strong because admission and backlog truth stay receiver-facing and testable.
