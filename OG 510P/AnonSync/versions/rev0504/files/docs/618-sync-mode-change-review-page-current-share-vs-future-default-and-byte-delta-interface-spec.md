# Sync mode change review page — current share vs future default and byte-delta interface spec

## Purpose

Make mode mutation a reviewed action instead of a toggle whose scope has to be inferred.
This page exists to answer:

> if I change this mode, am I changing the current share, the seat's future default, the byte posture, the path basis, or some combination of them?

Current official Resilio docs make this seam concrete because mode meaning still spans linked-device defaults, per-share selective toggles, mobile clear actions, and reconnect articles.
AnonSync should own the review directly.

## Core decision

Any meaningful mode mutation must compile to one first-class **Sync mode change review** page before the product treats the result as routine.

The page owns:

- requested mutation target
- current-share delta
- future-default delta
- byte delta
- path / return-contract delta
- receipt and re-entry path

## Fixed page order

1. **Requested mode mutation**
2. **Current-share delta**
3. **Future-default delta**
4. **Byte and path delta**
5. **Claim ceiling after apply**
6. **Receipt and re-entry**

### 1) Requested mode mutation

Show:

- current mode sentence
- requested mutation (`set-current-disconnected`, `set-current-placeholder-backed`, `set-current-full`, `set-future-default-disconnected`, `set-future-default-placeholder`, `set-future-default-full`, `mixed`, `unknown`)
- initiating surface and scope
- whether the surface can apply directly or must branch into path review

The operator must be able to answer:

> what exact mode change is being requested here?

### 2) Current-share delta

Show rows for:

- local row visibility
- bind/path state
- peer participation state
- local byte posture
- reconnect burden

Each row should state before, after, and strongest changed behavior.

### 3) Future-default delta

Show:

- before and after default for future arrivals
- whether existing shares remain untouched
- whether linked-device arrival path suggestion changes
- whether the mutation widens or narrows automation

The operator must be able to answer:

> am I changing today's share, tomorrow's arrivals, or both?

### 4) Byte and path delta

Show together:

- current byte posture before and after
- whether placeholders are created, preserved, or removed
- whether the current path remains authoritative
- whether a later reconnect may propose a default path or duplicate suffix

### 5) Claim ceiling after apply

Show together:

- strongest approved sentence if apply succeeds
- strongest approved sentence if the operator changes only the future default
- stronger forbidden sentence
- blocker or residue that prevents the stronger claim

### 6) Receipt and re-entry

Show:

- receipt class to emit
- whether later clear/disconnect review is still needed
- whether path review remains open
- best reopen path after apply

## Main surface

The compact mutation sheet should never collapse to `Set to Selective` or `Use this mode`.
It should always show:

- current share versus future default scope
- byte delta
- path / return-contract consequence
- strongest safe sentence afterward

## States

Use a small stable vocabulary:

- `current-share-only`
- `future-default-only`
- `both`
- `requires-path-review`
- `blocked`
- `unknown`

## Receipt fields

Suggested durable receipt fields:

- `sync_mode_receipt_id`
- `seat_ref`
- `share_ref` nullable
- `mutation_scope`
- `current_share_before`
- `current_share_after`
- `future_default_before`
- `future_default_after`
- `byte_delta_rows[]`
- `path_delta_summary`
- `strongest_safe_sentence`
- `generated_at`

## Success criteria

The page is successful only when an operator can answer:

1. what mode mutation is happening
2. whether current share and future default are changing separately or together
3. what byte posture changes now
4. what path / reconnect contract changes now
5. what sentence the product is allowed to say afterward
