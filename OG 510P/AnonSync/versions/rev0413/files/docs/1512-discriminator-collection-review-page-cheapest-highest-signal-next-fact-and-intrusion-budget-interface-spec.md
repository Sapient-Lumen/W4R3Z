# Discriminator collection review page: cheapest highest-signal next fact and intrusion budget interface spec

## Purpose

The contract sheet names the open gaps and candidate asks.
The **Discriminator collection review** decides which ask wins now.
It exists to stop the operator from over-asking, under-asking, or jumping to logs before cheaper discriminators are exhausted.

## Core decision

AnonSync must ship one review page that ranks candidate evidence asks by **decision value**, **burden**, **intrusion**, **freshness**, and **capture feasibility**.

## Fixed page order

1. **Review header**
2. **Ask ranking matrix**
3. **Intrusion budget card**
4. **Unavailable-channel handling card**
5. **Live route consequences card**
6. **Review verdict**

### 1) Review header

Show:

- review id
- linked acquisition sheet id
- current ambiguity posture
- current governing-candidate count
- current burden budget
- current strongest safe sentence

Supported `burden_budget` values:

- `read-only-only`
- `light-guided-checks`
- `multi-peer-acceptable`
- `restart-acceptable`
- `artifact-capture-acceptable`

Hard rule:

The review must publish what class of burden is presently acceptable before ranking asks.

### 2) Ask ranking matrix

Columns:

- ask label
- discriminator value
- burden rung
- freshness sensitivity
- capture failure probability
- time-to-answer class
- privacy or ops cost
- recommended rank

Supported `recommended_rank` values:

- `ask-first`
- `ask-second`
- `hold-in-reserve`
- `not-worth-it-yet`
- `avoid-unless-escalated`

Hard rule:

The matrix must not sort only by burden.
A trivial ask with no discriminator value should not outrank a slightly heavier route-collapsing ask automatically.

### 3) Intrusion budget card

Required rows:

- permitted restarts now
- permitted reproductions now
- permitted cross-peer requests now
- permitted disclosure scope now
- forbidden capture classes now
- who can widen the budget

Hard rule:

A heavier ask cannot be selected unless its intrusion class fits the current budget or the budget is widened explicitly.

### 4) Unavailable-channel handling card

Required rows:

- best ask that is currently unavailable
- reason unavailable
- substitute ask
- quality loss from substitution
- sentence ceiling if substitution is used

Hard rule:

Unavailable evidence channels must weaken the resulting sentence explicitly.
They may not vanish into a silent note.

### 5) Live route consequences card

For the leading two asks, show:

- what route wins if answer is yes
- what route wins if answer is no
- what routes remain live either way
- whether an intervention can proceed before answer
- what claim stays blocked while waiting

Hard rule:

The review must show why the ask matters, not just that it exists.

### 6) Review verdict

Supported `review_verdict` values:

- `cheap-high-signal-ask-selected`
- `observe-window-selected`
- `multi-peer-check-selected`
- `restart-bound-capture-approved`
- `heavy-artifact-capture-deferred`
- `weaker-claim-without-further-capture`

Render one sentence only:

- `Review verdict: [review_verdict]. Selected ask is [ask] because it gives [value] at acceptable burden [rung]; all stronger sentences above [ceiling] remain blocked until answered.`

## Required interactions

- **Re-rank asks**
- **Change burden budget**
- **Mark channel unavailable**
- **Approve heavier capture**
- **Accept weaker claim ceiling**

## Failure state

If all live asks exceed the current budget, show:

- `All remaining discriminators exceed the current burden budget. Widen the budget explicitly or proceed under the weaker claim ceiling.`
