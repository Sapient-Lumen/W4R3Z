# Completion claim review page — connected peers, known peers, offline debt, and acceptance boundary

## Purpose

Create a deliberate review surface before the operator records, exports, or depends on a completion claim that excludes some peers or some kinds of debt.

## When this page appears

Show this review whenever the operator tries to:

- mark a subject as complete
- export a completion receipt
- dismiss warnings as non-blocking
- approve a workflow that depends on freshness or completed propagation
- accept a reduced claim such as `complete for connected peers`

## Main layout

### Header

`You are about to accept a reduced completion claim.`

Below it, show two sentences side by side:

- strongest safe sentence
- stronger blocked sentence

Example:

- safe: `Complete for 3 connected peers.`
- blocked: `Complete for all 5 intended peers.`

### Scope comparison table

Columns:

- peer / seat
- intended?
- currently connected?
- previously seen?
- freshness proof age
- excluded by policy?
- exclusion reason

### Debt ladder

Ordered from most severe to least:

1. intended peer never proved
2. intended peer offline with stale proof
3. peer hidden or expired from active horizon
4. peer connected but blocked by local/remote issue
5. local detection lag unresolved
6. hidden internal work unresolved

### Acceptance boundary controls

The operator must choose one of these explicit postures:

- `Do not accept reduced claim`
- `Accept connected-peer completion only`
- `Accept connected-and-recently-proved known-peer completion`
- `Record local-complete only; remote freshness unresolved`

No generic `Continue` button.

## Copy rules

- Avoid `everyone` unless the scope truly covers the intended set.
- Use exact numerals and peer names where feasible.
- Mention if peer expiration or hiding changed the visible set.
- Mention if the proof depends on quiet transfer rather than recent explicit verification.

## Approval memory

A reduced completion acceptance may be remembered only with:

- exact subject
- exact peer horizon
- bounded freshness window
- explicit invalidators

It must not silently apply to other subjects or later wider peer sets.
