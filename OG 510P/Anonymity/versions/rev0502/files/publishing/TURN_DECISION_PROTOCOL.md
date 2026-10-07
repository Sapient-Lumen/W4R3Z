# Turn-by-Turn Decision Protocol

This protocol is designed for many-turn operation by an LLM-in-charge.

## Core rule

A turn does **not** need to release anything.
A good turn may simply record one of the following:

- no change,
- hold,
- nominate one candidate,
- demote one candidate back to hold,
- promote one candidate into the published-ready queue,
- or publish one already queued paper.

## Strong bias

The bias is toward the smallest safe action.

## Recommended maximum irreversible action per turn

At most **one** paper may be moved into `published/` in a single turn.
In many turns, zero papers should be published.

## Before reviewing any paper

1. Read `published/LEGACY_PUBLISHED_LINKS.md`.
2. Read `release_queue/STATUS.md`.
3. Read the newest decision note if one exists.

## Decision order for each review turn

1. Identify one paper under review.
2. Check whether its source `.tex` path is stable.
3. Check whether the title/scope/dependency boundary is still moving.
4. Apply the conservative release policy.
5. Record one written decision.
6. Only then consider promotion.

## Publication gating rule

A paper should normally spend at least one explicit recorded step in the Published-ready queue before being copied into `published/`.
This gives the repo a visible freeze stage.

## Successful long-horizon behavior

If another 100 turns occur, the desired behavior is not "release something every turn."
The desired behavior is:

- preserve the integrity of the archive,
- keep the queue gentle and small,
- and release only when the repo itself contains a written reason to trust the freeze.
