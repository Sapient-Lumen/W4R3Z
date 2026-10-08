# Home, Now, Soon, Quiet, and review rhythm interface spec

## Purpose

This document decides what the product feels like when it first opens.
The goal is not to maximize summary widgets.
The goal is:

> the default landing page should help an operator enter the right review rhythm without making the system feel either sleepy or panicked.

`rev0122` decided that Home defaults to `Now` plus near-due `Soon` while `Quiet` stays collapsed.
This document turns that into a fuller interaction contract.

## Core decision

Home is not a generic analytics dashboard.
It is the operator's **attention rhythm page**.
It should answer three questions in order:

1. `What actually needs me now?`
2. `What is approaching the point where waiting stops being neutral?`
3. `What is calm enough to stay collapsed without becoming invisible?`

The default landing therefore keeps four main regions:

- a compact global answer strip
- a visible `Now` lane
- a visible but calmer `Soon` lane
- a collapsed `Quiet` lane with counts and reopen reasons

## What Home must not become

Home should not become:

- a raw event stream
- a vague green/red health score
- a bucket of every object that changed recently
- a dashboard where risk, freshness, and volume are mixed into one ornamental graph

AnonSync already has subject pages, proof drawers, receipts, and history for detail.
Home exists to stage attention honestly.

## Lane meanings

### `Now`

`Now` contains items where delaying action would already be misleading, risky, or operationally expensive.
Examples include:

- review-required actions blocked on a human decision
- overdue divergence requiring either wait justification or intervention review
- expiring override leases that need renewal, promotion, or rejoin decisions
- high-confidence blockers on intended mutation apply
- disclosure or diagnostic packets awaiting final human gate

Every `Now` card must say **why it is now** in text.
Not just a color.

### `Soon`

`Soon` contains items that are not urgent yet but have a clear promotion path into `Now`.
Examples include:

- near-due leases
- review drafts whose proof freshness will soon expire
- members or shares approaching policy drift thresholds
- convergence windows that are still within honest delay but trending toward overdue review

`Soon` is visible by default because hiding it completely recreates surprise.
But it must feel calmer than `Now`.

### `Quiet`

`Quiet` contains items worth tracking that are not currently asking for intervention.
Examples include:

- healthy but watch-listed subjects
- long-running settled shares with informative but non-actionable activity
- completed drafts/receipts relevant to recent context
- future-only defaults that have no current outlier or due horizon

`Quiet` should collapse by default into counts, grouped reasons, and a reopen affordance.
It should not vanish entirely.

## Home anatomy

### 1) Global answer strip

One or two sentences should summarize the attention posture, for example:

- `Three items need review now. Two override leases become decision-relevant within six hours. Quiet work remains collapsed.`
- `No urgent action is required. One draft will need fresh proof tomorrow morning.`

This is the answer to `how tense should I feel on entry?`

### 2) `Now` lane

Each card should contain:

- subject label
- one-line current answer
- why-now reason
- freshness summary
- safest next action
- one jump to proof/explanation

A `Now` card should never require the operator to open the detail page just to know why it is here.

### 3) `Soon` lane

Cards may be more compact than `Now`, but they should still name:

- subject
- promotion trigger
- due horizon or watch threshold
- default next action if promoted

`Soon` should visually indicate that these are review candidates, not failures.

### 4) `Quiet` summary block

The collapsed `Quiet` block should at least show:

- total quiet count
- grouped reason counts
- any newly arrived quiet item count since last visit
- explicit affordance to open the lane fully

A single collapsed line like `Quiet: 27` is too little.
The operator still needs texture.

### 5) Recent receipts strip

Recent successful applies may appear in a small strip or drawer so Home can answer `what just changed?` without turning into history-first clutter.
This strip must stay secondary to active review work.

## Promotion and demotion rules

### Promotion into `Now`

An item should promote into `Now` when at least one of these becomes true:

- a due threshold is crossed
- the strongest honest recommendation changes from `watch` to `review`
- the item blocks a currently intended action
- freshness falls below the safe threshold for remaining deferred
- a prior calm state becomes contradicted by newer proof

### Promotion into `Soon`

An item should promote into `Soon` when:

- it has a known due or expiry horizon inside the configured look-ahead window
- trend or staleness suggests imminent review need
- a new draft or review object exists but does not yet require immediate action

### Demotion

Demotion should happen only when the reasons that promoted the item have genuinely cleared.
A manual dismissal must not silently rewrite the underlying classification.

## Home memory rules

The page may remember:

- which quiet groups were last expanded
- sort preference within a lane
- whether recent receipts were expanded

The page should not remember state so aggressively that newly promoted `Soon` or `Now` items become easy to miss.
The product must privilege fresh truth over layout nostalgia.

## Cross-projection rules

Every projection should preserve the same lane semantics.
GUI, local web, TUI, and CLI may render them differently, but each must still be able to say:

- why an item is `Now`
- why an item is `Soon`
- why `Quiet` remains collapsed
- what would promote or clear the item

## Result

A good Home rhythm prevents three bad outcomes at once:

- an anxious dashboard where everything feels red
- a sleepy dashboard where near-due work hides until it is late
- a history-heavy dashboard where recent change displaces real next action

If Home cannot tell the operator both `what needs action now` and `what can still wait without surprise`, it is not doing its job.
