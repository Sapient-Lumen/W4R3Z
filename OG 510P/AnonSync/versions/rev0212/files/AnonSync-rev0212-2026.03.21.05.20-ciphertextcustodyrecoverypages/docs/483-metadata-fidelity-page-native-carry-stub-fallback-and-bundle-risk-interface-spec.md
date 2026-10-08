# Metadata fidelity page: native carry, stub fallback, and bundle risk interface spec

## Purpose

This page answers:

> are metadata and bundle semantics carried natively on this target, routed through fallback stubs, or silently narrowed; and what real risk follows for portability and object fidelity?

The page exists because `metadata supported` is not enough truth when native xattr carriage and hidden fallback are materially different contracts.

## Core rule

Every subject whose metadata semantics matter must compile to one first-class **Metadata fidelity** page before the product claims cross-host fidelity.
That page owns:

- native versus fallback carriage
- whitelist / policy source
- omitted or narrowed metadata classes
- bundle / portability risk
- fidelity receipt

## Primary layout

The page always renders the same regions:

1. fidelity verdict
2. carriage-mode card
3. policy / whitelist card
4. portability and bundle-risk card
5. receipt and follow-on links

### 1) Fidelity verdict

Show:

- verdict label: `native-fidelity`, `native-with-limits`, `stub-backed`, `narrowed`, `unknown`
- strongest honest one-line summary
- metadata families in scope
- one safest next action

### 2) Carriage-mode card

Show:

- whether metadata is stored natively on this target
- whether fallback stubs exist in managed state
- whether carriage is mixed across peers
- strongest reason for fallback or narrowing

The operator must be able to answer: **where does metadata actually live here?**

### 3) Policy / whitelist card

Show:

- active StreamsList or equivalent policy source
- classes explicitly carried
- classes explicitly omitted
- whether IgnoreList is irrelevant to this metadata path
- strongest policy-drift caveat

The operator must be able to answer: **what exact metadata are we trying to preserve, and why?**

### 4) Portability and bundle-risk card

Show:

- bundle-sensitive risk class (`none`, `review`, `high`, `unknown`)
- whether cross-platform limits are active
- whether the target may preserve content while degrading metadata meaning
- strongest user-visible consequence

The operator must be able to answer: **what kind of fidelity loss could a human actually notice?**

### 5) Receipt and follow-on links

Link to:

- Volume capability
- Affordance ceiling
- Volume repair

After any accepted action, emit a receipt that preserves:

- fidelity verdict before and after
- native versus fallback mode
- carried and omitted metadata classes
- strongest bundle / portability warning
- chosen next review

## Honest outputs

This page may conclude:

- `native xattr carriage; bundle fidelity acceptable`
- `stub-backed metadata; payload portable but metadata meaning downgraded`
- `whitelist narrowed; some metadata classes intentionally omitted`
- `cross-platform limits active; review bundle-sensitive subjects before migration`

It may not compress all of those into one generic `metadata synced`.

## Rules

### Rule 1 — native and stub-backed fidelity must never share one label

Those two states have different browse, repair, and migration consequences.

### Rule 2 — policy source must be inspectable

If the operator cannot reveal which whitelist or rule source chose the carried metadata set, the page is not explicit enough.

### Rule 3 — payload success does not erase metadata loss

A subject can converge by bytes while still narrowing meaning in ways the operator should review.

### Rule 4 — hidden fallback must not stay hidden

If managed stubs are preserving semantics, the page must say so directly rather than forcing hidden-directory archaeology.

## Event language

Use explicit phrases such as:

- `metadata fidelity is stub-backed on this target`
- `native xattr carriage narrowed by active whitelist`
- `payload converged; metadata meaning still degraded`
- `bundle-sensitive subject on limited-fidelity target`

Avoid vague lines such as:

- `some metadata may vary`
- `compatibility issue`
- `special files handled internally`

## Non-clone reason

Current official Resilio docs are usefully candid that xattr carriage can be whitelisted, limited, or stub-backed.
But the operator still has to infer practical fidelity from architecture notes and hidden-sidecar explanations.
AnonSync should instead expose one Metadata fidelity page where carriage mode, policy source, and bundle risk stay adjacent.
