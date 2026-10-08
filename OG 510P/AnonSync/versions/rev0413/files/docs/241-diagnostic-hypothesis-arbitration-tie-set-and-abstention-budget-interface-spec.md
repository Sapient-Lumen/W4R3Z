# Diagnostic hypothesis arbitration, tie-set, and abstention budget interface spec

## Purpose

The archive already had reviewed probes, evidence packets, remediation ladders, route explanation, and post-action recompute receipts.
What it still lacked was one explicit contract for a diagnostic truth problem that becomes more visible as the product gets more serious:

> what should the interface do when several explanations or repair paths remain honestly alive at once, and why should the operator trust a recommended action if the product never shows the nearby rivals, the tie-break rule, or the point where it should abstain instead of pretending certainty?

Comparative reading outside AnonSync made this seam clearer.
The strongest imported pressure was simple:

- several candidates can be simultaneously eligible
- ranking them is not the same thing as proving that only one remains
- a vivid row can win by proximity or presentation rather than by evidence separation
- the honest answer is sometimes `recommend this branch for now while preserving the live rival set`
- and the honest answer is sometimes `abstain, gather more evidence, or escalate`

## Core decision

AnonSync must treat diagnostic arbitration as a first-class reviewed object.

Whenever two or more diagnostic hypotheses, route explanations, or remediation recipes remain simultaneously plausible after current evidence review, the product must preserve:

- the live tie set
- the present arbitration rule
- the strongest current recommendation, if any
- the nearby fallback or abstention path
- the instability budget that would revoke confidence

A sorted list is not enough.
The operator must be able to answer:

- what is the current leading explanation
- what rival explanations are still alive
- why this one is recommended first
- what evidence would collapse the tie or overturn the lead
- when the product would rather abstain than pretend the tie is solved

## Fixed review order

Every ambiguous diagnostic, route-explanation, or remediation review must render the same sections in the same order:

1. **Claim under stress**
2. **Live tie set**
3. **Arbitration rule**
4. **Abstention and fallback boundary**
5. **Decision receipt**

### 1) Claim under stress

Show:

- the operator question being answered
- the current failure or ambiguity class
- the observation window and freshness
- the evidence family summary
- whether the product is choosing a likely cause, a likely next step, or both

### 2) Live tie set

Show one compact table where each row includes:

- candidate hypothesis or recipe id
- current fit grade
- evidence supporting it
- evidence cutting against it
- what would most efficiently separate it from the nearest rival
- whether it is safe to act on before separation

The interface must not hide the second-place row merely because the first row currently sorts above it.

### 3) Arbitration rule

Show:

- the rule currently allowed to recommend a leader (`strongest evidence`, `least-destructive first`, `lowest-cost separating probe`, `safety-first fallback`, `other`)
- whether the rule is selecting an explanation, a next probe, or a first repair step
- what assumptions the rule currently relies on
- whether the recommendation is robust or near-tied

This is where the product explains why one candidate is first without claiming the others are dead.

### 4) Abstention and fallback boundary

Show:

- what the product will recommend if the tie stays unresolved
- when it will require another probe before action
- when it will allow a low-blast-radius attempt despite ambiguity
- when it will stop and route to escalation/export rather than keep guessing
- what instability budget is tolerated before the current leader loses authority

### 5) Decision receipt

Record:

- question under stress
- tie set ids at decision time
- current leader, if any
- arbitration rule used
- abstention or fallback branch kept nearby
- actor, seat, and time
- follow-up probe or review handle
- supersession pointer when the tie later collapses or flips

## Main surface

Every serious troubleshooting or repair flow should expose one **Diagnostic arbitration** pane.

That pane should answer:

- `what else is still alive`
- `why this is first`
- `how sure this recommendation really is`
- `what separates action now from evidence first`
- `what receipt proves the product stayed honest about uncertainty`

## Public rules

AnonSync should hold the following rules:

- a recommendation may be strong while still admitting a live rival set
- a live rival set must be shown whenever nearby candidates remain materially plausible
- the system may recommend the least-destructive separating step before it recommends the strongest destructive action
- abstention is an allowed honest outcome
- the tie set belongs to the operator-facing record, not only to hidden scoring internals

## Acceptance criteria

This spec is satisfied when:

- operators can see when diagnostics still have multiple live explanations
- the current recommendation names its arbitration rule rather than implying inevitability
- low-blast-radius probes and repairs can be recommended without falsely claiming certainty
- the product can abstain or escalate without looking broken
- later receipts can explain why an earlier recommendation was reasonable even if a rival hypothesis eventually won
