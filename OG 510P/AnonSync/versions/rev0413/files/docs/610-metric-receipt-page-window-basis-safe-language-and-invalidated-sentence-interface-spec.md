# Metric receipt page — window basis, safe language, and invalidated sentence interface spec

## Purpose

The archive already treats serious mutations and reviews as receipted.
What it still lacked was one small durable artifact for the interpretive event:

> we decided this row only earned a narrower sentence, and we want later readers to inherit that exact interpretation instead of re-overreading it.

## Core decision

AnonSync must issue one **Metric receipt** whenever a status-bearing row, counter, or timestamp is reviewed for action-bearing interpretation.

## Receipt contents

The receipt must preserve:

- metric identity and rendered value at review time
- metric family and window class
- freshness basis at review time
- strongest safe sentence adopted
- stronger invalidated sentence explicitly rejected
- residue or missing proof that blocked the upgrade
- next proof page, if any
- reviewer and timestamp

## Public object

### Metric receipt page

Fields:

- `metric_receipt_id`
- `metric_ref`
- `rendered_value_snapshot`
- `metric_family`
- `window_class`
- `freshness_basis_ref` nullable
- `safe_sentence`
- `invalidated_sentence`
- `blocking_residue_rows[]`
- `next_page_refs[]`
- `reviewed_at`
- `reviewed_by`

## Compact row contract

A compact receipt row should preserve this order:

1. metric label
2. value snapshot
3. window class
4. safe sentence
5. rejected stronger sentence

Example:

```text
Peers     2 of 5     connected-now + ever-known     two peers online now; five historically known     all five peers currently participating
```
