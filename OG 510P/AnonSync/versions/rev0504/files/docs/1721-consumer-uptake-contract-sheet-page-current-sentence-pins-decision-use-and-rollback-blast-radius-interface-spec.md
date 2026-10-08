# Consumer-uptake contract sheet page — current-sentence pins, decision use, and rollback blast radius

## Purpose

This page defines the contract for how a current sentence moves from being merely available to being pinned, used for a bound decision, acted on downstream, and eventually cleared for rollback.
It exists so the product can answer not just `is the sentence current?` but `who has already done something that makes reversal harder?`

## Core doctrine

The sheet must preserve these orderings:

- committed-current is weaker than decision-pinned
- decision-pinned is weaker than decision-used
- decision-used is weaker than downstream-action-complete
- rollback-possible is weaker than rollback-cleared

## Mandatory fields

### 1. Sentence identity

- case identifier
- current sentence identifier
- source current-sentence receipt identifier
- sentence version hash or equivalent immutable handle
- lower sentence that remains available for fallback

### 2. Consumer families

- required consumer families
- optional consumer families
- automation consumers
- human reviewers
- external/public consumers
- adjudicator or override consumers

### 3. Uptake classes

For each named consumer or consumer family, the page must track exactly one strongest honest uptake class:

- not delivered
- delivered
- rendered
- fetched
- cached
- opened
- pinned
- decision-bound
- action-started
- action-completed
- rollback-cleared
- unknown / contested

### 4. Pin semantics

- whether the consumer pinned a moving latest view or an immutable sentence version
- pin creation time
- pin expiry or refresh rule
- whether the pin is human-confirmed, automation-held, or inferred
- whether later supersession invalidates the pin automatically or only by explicit recall

### 5. Decision-use semantics

- what decision was bound to the sentence
- whether the decision is provisional, reversible, or irreversible
- whether the decision launched any downstream action
- whether downstream action can be halted, compensated, or only annotated after the fact

### 6. Rollback blast-radius semantics

The page must compute rollback difficulty by uptake class, not by raw audience size.
At minimum it must distinguish:

- unseen or unrendered consumers
- rendered but unpinned consumers
- pinned but not yet decision-bound consumers
- decision-bound but not yet acting consumers
- action-started consumers
- action-completed reversible consumers
- action-completed irreversible consumers

## Required operator questions

- who merely had access to the sentence?
- who actually pinned a version?
- who used the sentence for a bound choice?
- which downstream acts are already underway or complete?
- what is the smallest honest rollback sentence right now?
- what residue remains even after supersession or rollback?

## Forbidden shortcuts

This page must not let the operator infer consumer uptake from shortcuts such as:

- `the sentence was current everywhere`
- `the bell fired`
- `the WebUI showed it`
- `the API returned it`
- `history has an event`

Those facts may contribute evidence.
They may not replace explicit uptake classification.
