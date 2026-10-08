# Stale peer debt watch page — peer expiration gap, missing sources, and quorum risk

## Purpose

Keep excluded or stale peers visible as debt instead of letting them disappear from the operator's mental model once they go offline long enough, get hidden, or fall outside the current route/source window.

## Questions this page answers

- Which peers are outside the current completion horizon?
- Were they intentionally excluded or merely aged out / hidden?
- Is there source risk if they remain absent?
- Does their absence weaken completion, freshness, or repair claims?

## Sections

### 1. Debt roster

For each stale peer show:

- seat / peer name
- relationship class
- last connected time
- last proved-fresh time
- current visibility state: visible, hidden, expired, forgotten-from-active-list
- source role: source, witness, optional recipient, unknown

### 2. Debt severity

Each peer gets one severity class:

- `blocking completion`
- `blocking freshness only`
- `blocking strong recovery claims`
- `historical only, not operationally blocking`

### 3. Expiration-gap explainer

If the active UI or horizon no longer shows a peer due to aging rules, the page must say:

- when the peer left the active set
- which policy moved it out
- why that does **not** automatically erase its historical relevance

### 4. Quorum risk

Show whether stale peers weaken:

- intended propagation quorum
- source availability
- future hydration confidence
- conflict/repair witness strength
- governance or approval assumptions

## Interaction rules

- The page is reachable from every reduced completion or freshness claim.
- A hidden/expired peer cannot silently vanish from receipts that used to include it.
- Operators can intentionally retire a stale peer only through a distinct reviewed action.
