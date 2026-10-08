# Size metric page: visible counts, exclusions, and drift explanation interface spec

## Purpose

The archive already had list rows, policy precedence, exclusion rules, and availability language.
What it still lacked was one precise interface contract for a deceptively ordinary surface:

> when the product shows `size`, `items`, `bytes present`, or `storage used`, what exactly is that metric counting, and why might it differ from what the operator sees on disk or on another seat?

Current Resilio docs make this seam load-bearing.
They still say ignored files are not counted in the `Size` column, placeholders are 0-byte files, folder views can expose optional columns like `size` and `date synced`, and hidden `.sync` / Archive / StreamsList / `.!sync` material can coexist with user files.
That is a usable product.
It is still too easy to misread.

## Core decision

AnonSync should give every visible size/count metric its own inspectable **metric card**.
A metric card answers four questions:

1. **scope** — which object does this metric talk about?
2. **membership** — which entries qualify?
3. **count rule** — which bytes/counts are included or excluded?
4. **freshness** — how current is the computation?

## Fixed review order

Every metric page or popover should render sections in this order:

1. **Metric identity**
2. **Inclusions**
3. **Exclusions**
4. **Known drift causes**
5. **Seat variance**
6. **Repair / reverify actions**

## 1) Metric identity

State clearly:

- metric name
- unit (`bytes`, `entries`, `materialized bytes`, `subject bytes`, etc.)
- surface where it appears
- whether it is a per-seat, per-subject, or cross-seat metric

No row or column should display a number whose type cannot be named.

## 2) Inclusions

List the included families explicitly, for example:

- fully materialized payload bytes
- directories as entries but not as bytes
- fetched metadata that is part of the current contract
- history bytes only if the metric says it is a `resident footprint` metric rather than `live subject size`

## 3) Exclusions

List the excluded families explicitly, for example:

- ignored/excluded paths
- placeholder names without payload bytes
- hidden managed material
- temp or in-flight bytes
- off-seat content known only by announcement or structure

Every exclusion row should say whether the excluded family still exists locally, exists remotely only, or is outside the subject entirely.

## 4) Known drift causes

This section must explain why the visible metric may disagree with the operator's expectations:

- policy changes applied after indexing
- provisional scans or deferred hashing
- weak watchers / delayed rescans
- sparse files or placeholders
- hidden service/history/temp material
- peer-wise differences in excluded sets or materialized subsets

The point is not to apologize for drift.
The point is to name it.

## 5) Seat variance

A metric page should state whether another seat may legitimately show a different value because of:

- different materialization level
- different exclusion policy
- different history retention
- different temporary/in-flight state
- different storage class or metadata capability

A different number should not automatically look like corruption.

## 6) Repair / reverify actions

Good actions include:

- `recompute metric now`
- `show byte-family breakdown`
- `show excluded families`
- `show hidden managed bytes`
- `compare with another seat`

These actions should explain rather than overwrite.

## Compact row behavior

In list views, the number itself can stay compact.
But every compact metric must have an inspectable explanation surface with:

- metric label
- freshness state
- top exclusions
- link to footprint page

## Receipt

A metric receipt should prove:

- metric name and scope
- exact inclusion / exclusion contract
- timestamp of computation
- confidence state
- top drift causes that were active at the time

## What must never happen automatically

The product must never:

- let `size` silently switch meaning between surfaces
- call placeholder-only entries `present bytes`
- silently hide excluded bytes while implying absence
- let hidden service/history bytes distort a `live subject` metric without explanation
- show stale numbers as if freshly computed

## Resulting product doctrine

A metric is a contract, not a decoration.
If the product cannot say what a number counts, it should not show the number as authoritative.
