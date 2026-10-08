# Local-web history witness, back-forward continuity, and fragment-miss interface spec

## Purpose

The archive already had strong local-web, shell, deep-link, and import-handoff language.
What it still lacked was one explicit contract for browser-session continuity itself:

> when the product projects into a browser, what exactly should back, forward, refresh, deep-link, and fragment navigation mean, and how does the operator tell session continuity apart from action proof?

Comparative reading and current web-platform guidance make this seam concrete.
A browser session preserves history entries, replacement, and back/forward traversal differently.
If the product leaves those behaviors accidental, operators end up learning important product law from frontend folklore instead of from AnonSync itself.

## Core decision

AnonSync must treat local-web history behavior as a first-class projection contract.

The product must distinguish:

- navigation that creates a new history entry
- navigation that replaces the current entry
- navigation that restores prior review context
- navigation that fails because a target no longer exists
- action receipts, which are related to navigation but not proved by it

The operator must be able to answer:

- did I move to a new review object or just refine the current one
- should back return me to the prior object or only the prior filter/detail state
- can refresh recover this draft or receipt safely
- what exactly was missing when a fragment or handle could not be restored
- why browser history is not itself proof that an action applied

## Fixed review order

Every local-web continuity surface must render the same sections in the same order:

1. **Navigation event class**
2. **Restored context**
3. **Miss or divergence handling**
4. **Action-proof boundary**
5. **History receipt**

### 1) Navigation event class

Show one explicit class:

- `push new object`
- `replace current object`
- `restore prior object from history`
- `refresh current object`
- `typed miss / unavailable target`

This section must explain what changed in the session and why.

### 2) Restored context

Show what the product is trying to preserve:

- object id or route handle
- selected proof drawer, tab, or review step when safe
- draft handle and mutation state when safe
- filter or search state when safe
- whether the restoration is exact, partial, or impossible

### 3) Miss or divergence handling

If the target cannot be restored exactly, show a typed miss surface that preserves the initiating verb and target class, such as:

- `open receipt fragment failed`
- `restore review draft failed`
- `jump to section missed`
- `back target no longer available`

The miss surface must explain:

- what target was attempted
- whether the target never existed, expired, was superseded, or is locally unavailable
- what nearest durable fallback exists
- whether any prior action receipt is still intact

### 4) Action-proof boundary

Show clearly:

- that history restoration is not proof of apply
- that seeing a prior screen again does not mean the underlying action was replayed
- that action receipts and navigation continuity are adjacent but distinct
- that destructive actions may require an explicit receipt handle rather than replayable history state

### 5) History receipt

Record:

- event class
- old and new route handle
- whether push or replace was used
- whether restoration was exact, partial, or missed
- miss reason if any
- actor/seat/session
- pointer to durable receipt or review object when one exists

## Main surface

Every local-web projection should expose one **Session continuity** expansion for serious reviews, drafts, and receipts.

That expansion should answer:

- `why back behaved that way`
- `why this state was push versus replace`
- `what survived refresh`
- `what exactly went missing`
- `which durable object to trust if history cannot restore the same view`

## Public rules

AnonSync should hold the following rules:

- browser history is allowed to describe session continuity but not to imply action success
- exact-object changes should prefer new history entries
- refinements to the same object may replace the current entry when that keeps the trail honest
- typed misses must preserve the initiating action and target class
- anchored landings must remain visible below persistent chrome rather than technically present but visually obscured

## Acceptance criteria

This spec is satisfied when:

- operators can use back/forward on local web without replaying actions accidentally
- refresh can preserve exact or partial review state honestly, and says when it cannot
- failed deep links and fragment restores name the attempted action and target instead of collapsing into generic failure copy
- durable receipts remain the source of action truth even when the browser session moves around them
