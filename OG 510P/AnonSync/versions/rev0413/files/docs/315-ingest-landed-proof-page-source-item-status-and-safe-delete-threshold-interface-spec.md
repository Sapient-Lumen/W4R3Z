# Ingest landed proof page: source item status and safe-delete threshold interface spec

## Purpose

This page answers one ordinary question:

> for this source item or cohort, has the data merely been noticed, is it still in flight, or has it landed on enough approved sinks that source-side cleanup is now honest under policy?

The page exists because `seen`, `queued`, `uploading`, `present on one sink`, and `safe to delete from source` are not synonyms.

## Core decision

Every capture-only ingest relationship must render one first-class **Ingest landed proof** page.
That page owns:

- source item identity or cohort identity
- per-sink status
- winning durability threshold
- safe-delete verdict under current policy
- counterfactuals that would change the verdict

The workbench must not let the operator infer cleanup safety from a generic progress number.

## Primary layout

The page always renders the same regions in the same order:

1. item strip
2. source-to-sink status matrix
3. policy threshold card
4. safe-delete verdict card
5. landed receipts

### 1) Item strip

Show:

- source item or cohort label
- discovered time
- current global verdict: `not-seen`, `queued`, `in-flight`, `landed-below-threshold`, `landed-safe-under-policy`, `indeterminate`
- strongest next honest action

### 2) Source-to-sink status matrix

Each row shows one sink and one of these states:

- `not-admitted`
- `not-yet-seen`
- `queued`
- `in-flight`
- `written-not-verified`
- `landed`
- `landed-but-not-counting`
- `failed`
- `unknown-stale`

Each row must also show:

- last evidence time
- durability class of the sink
- whether this row currently counts toward safe-delete threshold

The operator must be able to answer: **where exactly has this item really landed?**

### 3) Policy threshold card

This card publishes:

- winning threshold rule, for example `one durable desktop sink`, `all primary sinks`, or `one durable sink plus one encrypted custody sink`
- how many counted sinks are satisfied now
- what single counterfactual would flip the verdict if it is not yet safe
- whether stale evidence downgrades certainty

The operator must be able to answer: **what bar must be met before source cleanup becomes honest?**

### 4) Safe-delete verdict card

This card publishes:

- `safe now`, `not yet safe`, `safe with caution`, or `indeterminate`
- exact reason
- whether delete guidance applies to source only, source plus local previews, or broader cleanup
- strongest recommended alternative if not safe yet

The operator must be able to answer: **can I delete from the source now without pretending the landing threshold was met?**

### 5) Landed receipts

Receipts show:

- item discovered
- sink landed
- threshold satisfied
- safe-delete guidance granted or revoked
- evidence downgraded stale
- sink later fell out of threshold

## Non-negotiable rules

### Rule 1 — progress is not landing

A byte count or queue bar is never enough to imply safe cleanup.
The page must state which sinks reached `landed` and which did not.

### Rule 2 — landed is not automatically safe-delete

Landing on one sink may still be below policy threshold.
The page must keep `landed` and `safe under policy` separate.

### Rule 3 — stale evidence must downgrade certainty

If the product cannot refresh the sink evidence, the verdict must become cautious or indeterminate rather than stale optimism.

## Honest outputs

The page may conclude:

- `Seen locally, queued to NAS-pine, not yet landed anywhere; do not delete from source.`
- `Landed on laptop-ash but policy requires one desktop sink and one encrypted sink; safe-delete still blocked.`
- `Landed on NAS-pine and desktop-ash; threshold met; source cleanup safe under current policy.`
- `Earlier safe verdict downgraded because the only counting sink is now stale and unverified.`

It may not collapse those outcomes into one generic `backed up` badge.
