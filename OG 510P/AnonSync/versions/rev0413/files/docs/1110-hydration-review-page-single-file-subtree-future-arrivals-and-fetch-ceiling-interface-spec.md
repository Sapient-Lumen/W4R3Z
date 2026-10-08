# Hydration review page: single-file, subtree, future arrivals, and fetch ceiling

This page exists so `download`, `open`, and `sync to this device` stop sounding like one undifferentiated action.
Fetching one file, hydrating a subtree, and promoting a subtree into future auto-hydration are different commitments.

## Operator question

> What exactly will be fetched now, what remains placeholder-only, what later arrivals will auto-hydrate, and what fetch ceiling is still blocked by source availability?

## When this page must appear

Render whenever:

- a placeholder file is opened from a browser or file surface
- multiple placeholders are selected for hydration
- a placeholder subtree is hydrated
- the operator promotes a subtree or file into local residency
- a fetch fails or stalls because source bytes are missing or offline

## Fixed page order

1. **Requested hydration scope**
2. **Immediate fetch set**
3. **Post-fetch class**
4. **Future-arrival behavior**
5. **Fetch ceiling and blockers**

## 1) Requested hydration scope

Show:

- requested object: file / subtree / share slice
- byte estimate if known
- whether the request came from open, explicit hydrate, or residency promotion
- whether multi-select or recursive scope is involved

The operator must be able to answer: **what exact slice am I asking to fetch?**

## 2) Immediate fetch set

Show:

- files that will fetch now
- files that remain placeholders after the action
- whether directories are fetched recursively
- whether later open behavior still depends on another network fetch

The operator must be able to answer: **what bytes arrive now and what does not?**

## 3) Post-fetch class

Show the resulting class after success:

- `hydrated-file`
- `hydrated-subtree`
- `pinned-file`
- `pinned-subtree`
- `still-placeholder-due-to-failure`
- `unknown`

The operator must be able to answer: **what class will this object become if the fetch succeeds?**

## 4) Future-arrival behavior

Show:

- whether new files added later under the hydrated subtree will auto-download here
- whether that rule applies only under the selected subtree or the whole share
- whether later arrivals remain placeholders by default outside that boundary

The operator must be able to answer: **what future files will now arrive automatically because of this action?**

## 5) Fetch ceiling and blockers

Show:

- whether at least one source peer with real bytes is online now
- whether fetch is blocked only by source absence vs rights vs disk space vs runtime state
- whether the product can only promise `fetch attempted when a source reappears`
- whether the request enters ghost-risk territory because the object may no longer exist in full on any peer

The operator must be able to answer: **what is the strongest honest promise the product can make about completing this fetch?**

## What this page must never imply

It must never imply that these are the same:

- open placeholder and guaranteed openable offline file
- hydrate one subtree and sync the whole share
- recursive hydration and future-arrival commitment outside the reviewed boundary
- no live source witness and guaranteed fetch success

## Receipt / audit consequence

Completing this review should write a receipt entry that preserves requested scope, resulting class, future-arrival boundary, and blocked stronger fetch sentence.
