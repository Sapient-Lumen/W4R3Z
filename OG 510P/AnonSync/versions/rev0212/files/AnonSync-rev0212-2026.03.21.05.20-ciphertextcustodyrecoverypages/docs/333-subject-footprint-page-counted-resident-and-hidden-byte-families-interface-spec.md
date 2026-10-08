# Subject footprint page: counted, resident, and hidden byte families interface spec

## Purpose

The archive already had availability, fetchability, history, metadata-fidelity, exclusion policy, and storage/cleanup work.
What it still lacked was one ordinary page that answers the everyday operator question:

> how much of this subject is really here on this seat, and what byte families are part of that answer?

Current Resilio docs make this seam concrete instead of hypothetical.
They still say ignored files are not counted in the main `Size` column, placeholders are 0-byte stand-ins, `.sync` contains service material including `Archive`, `IgnoreList`, `StreamsList`, and temporary `.!sync` files, and some byte families are intentionally sparse or hidden.
That is good raw honesty.
It is still not a good page contract.

## Core decision

AnonSync should represent subject footprint as a **stack of byte families**, not a single vague `size` number.

Every subject-footprint page must separate at least these families:

1. **counted live bytes** — bytes that belong to the subject's main, policy-counted content on this seat
2. **resident but not counted bytes** — bytes present locally but excluded from the current metric contract
3. **sparse names only** — placeholders, detached names, or other entries that do not currently carry the full payload
4. **managed hidden bytes** — service state, temp transfer residue, metadata sidecars, history stores, or other product-owned bytes
5. **off-seat only bytes** — content known to exist elsewhere but not materially present here

## Why this matters

A subject can look `small` for several entirely different reasons:

- it is mostly placeholders
- excluded files exist but are outside the visible metric
- service/history bytes exist but the list row does not count them
- the seat only knows names or structure, not payloads
- indexing/readiness is still provisional

A single `size` field cannot honestly carry that load.

## Fixed review order

Every subject-footprint page should render sections in this order:

1. **Metric contract**
2. **Resident byte families**
3. **Sparse or off-seat families**
4. **Hidden managed material**
5. **Confidence and last verification**
6. **Action consequences**

## 1) Metric contract

At the top, say explicitly:

- the primary metric label (`counted live bytes`, `resident bytes`, `managed bytes`, etc.)
- whether the headline number includes hidden managed material
- whether excluded bytes are included
- whether placeholder names are included as entries, bytes, or neither
- whether the answer is point-in-time or continuously maintained

The operator should never have to guess what the headline number means.

## 2) Resident byte families

Render a breakdown such as:

- `fully materialized subject bytes`
- `locally cached subtrees`
- `history/rollback bytes`
- `metadata sidecar or fidelity bytes`
- `temp/in-flight bytes`

Each row must say:

- current size
- count of items
- whether counted in headline
- whether safe to reclaim independently
- what would need to remain elsewhere before reclaim is allowed

## 3) Sparse or off-seat families

Render a second block for:

- placeholders / sparse names
- disconnected but remembered items
- remote-only members known by structure only
- partial knowledge derived from prior indexing but not current local payload

Each row must make clear whether the seat currently has:

- names only
- names + metadata only
- some payload
- no local material at all

## 4) Hidden managed material

This section must surface:

- service roots or annexes bound to the subject
- rollback/history stores
- metadata preservation stores
- temporary/in-flight residue
- policy/config material specific to the subject

The page must make these bytes visible **without requiring raw filesystem inspection**.

## 5) Confidence and last verification

Show:

- last local scan / verification time
- whether the answer depends on watchers, scheduled rescans, or manual verification
- whether some byte families are estimated, exact, or stale
- whether source availability is required to complete the answer

A footprint page must admit uncertainty instead of silently flattening it.

## 6) Action consequences

The page should offer a compact action matrix:

- `evict materialized bytes`
- `clear managed temp bytes`
- `compact history bytes`
- `reverify footprint now`
- `open hidden-material review`

Each action must say what family changes and what family does not.

## Receipt

A footprint receipt should prove:

- subject ID
- headline metric contract
- byte-family breakdown
- confidence level
- last verification time
- any destructive or reclaim actions taken afterward

## What must never happen automatically

The product must never:

- call placeholders `present bytes`
- let ignored/excluded bytes silently impersonate deletion
- hide managed history/temp/service residue behind an empty-looking subject row
- display one headline number without a metric contract
- imply completeness when watchers/rescans make the answer provisional

## Resulting product doctrine

A subject is not `small` merely because the visible counted metric is small.
A subject is only `small` when the page can prove which byte families are absent, sparse, excluded, or hidden.
