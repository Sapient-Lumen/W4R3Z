# Entrypoint and source-contract refactor — rev0072

## Problem 1: source identity was operationally tied to upload aliases

Hundreds of historical files contain a numbered source filename from the session in which they were created. The bytes were stable, but command examples could fail when the same bundle was uploaded under a different suffix.

rev0072 adds `tools/source_bundle_locator.py`. Current workflows now select a bundle using:

```text
SHA-256: feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b
required lanes: github-tag-3.3.10, github-branch-3.3.x, github-branch-master
```

Selection priority is explicit path, `NICOTINE_SOURCE_ZIP`, then common upload locations. A malformed ZIP, wrong digest, or incomplete lane set fails closed.

Historical references remain untouched because they are evidence about earlier sessions, not active configuration.

## Problem 2: navigation had become append-only

Before rev0072:

```text
README.md              324 lines
START-HERE.md           613 lines
```

They mixed current decisions with many superseded revision sections. That is a cognitive failure mode: the file named “start here” required reading an archive.

rev0072 moves the full prior files without deleting them:

```text
docs/archive/README-through-rev0071.md
docs/archive/START-HERE-through-rev0071.md
```

New current entrypoints are bounded and point to canonical ledgers rather than repeating every historical gate.

## Refactor invariants

- No historical evidence table or manifest is rewritten.
- No embedded upstream source is added.
- Current entrypoints contain no required numbered upload alias.
- The locator has fail-closed negative controls.
- The closure probe checks entrypoint line budgets and archive presence.

## Why this matters

The cube's previous waste audit measured disk duplication, but the more damaging waste was decision latency. A maintainer should be able to answer three questions immediately:

```text
Which upstream commit was tested?
Did the behavior fail before and pass after?
What should be reviewed next?
```

rev0072 makes those answers first-class and machine-readable.

## Problem 3: exploratory test composition was order-dependent

A combined exploratory workflow let a stateful historical witness runner precede the broader upstream unit suite. The later run stalled rather than producing a trustworthy result. rev0072 split these purposes and added a second probe with fresh source and HOME/XDG/TMP/cwd namespaces for each state. Both isolated unit states now produce the same `58 passed, 1 skipped` outcome. See `docs/TEST-LANE-ISOLATION-REFACTOR-REV0072.md`.
