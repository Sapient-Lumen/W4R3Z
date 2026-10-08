# Fact authorship buckets, lane exactness, and non-inference interface spec

## Purpose

The archive already had strong language about truth layers, route explanation, control trust, import preview, and installation readiness.
What it still lacked was one public contract for a quieter but pervasive honesty problem:

> when the interface shows a value, event, warning, identity hint, scope claim, or readiness row, who actually authored that fact, and how far is the product allowed to promote it before it turns one weak surface into a stronger claim than the evidence deserves?

AnonSync repeatedly mixes facts from different origins:

- local measurements
- peer-declared state
- sender-declared artifact metadata
- operator-entered values
- config-declared defaults
- browser-observed events
- derived verdicts produced by the product itself

These are all useful.
They are not interchangeable.

## Core decision

AnonSync must assign every consequential visible fact to an explicit authorship bucket and must forbid silent authority upcasts between buckets.

The operator must be able to answer:

- who authored this fact
- what scope that author could honestly know
- whether the row is raw observation, declaration, or derivation
- whether a stronger statement is being inferred from a weaker one
- whether nearby fields contradict the claimed scope or authority class

## Authorship buckets

Use one explicit bucket on any consequential row:

- `local-observed`
- `peer-declared`
- `sender-declared`
- `operator-entered`
- `config-declared`
- `browser-observed`
- `derived`

These buckets are not confidence scores.
They are authorship classes.

## Fixed review order

Every truth-bearing pane that matters to trust, route, readiness, adoption, or repair must render the same sections in the same order:

1. **Visible fact**
2. **Authorship bucket**
3. **Scope and lane exactness**
4. **Allowed promotions**
5. **Fact receipt**

### 1) Visible fact

Show the user-facing claim exactly as the surrounding pane depends on it:

- endpoint class
- import target
- peer reachability hint
- route class
- effective rate
- install readiness
- authority identity
- any other consequential visible fact

### 2) Authorship bucket

Show one explicit bucket and explain it in plain language:

- who authored the row
- whether the row came from observation, declaration, entry, or derivation
- whether the author could directly know the claim or only report a limited slice of it

### 3) Scope and lane exactness

Show:

- what scope the row claims (`local`, `peer`, `sender artifact`, `global config`, `browser session`, `derived summary`, `other`)
- whether adjacent fields are exact with that scope
- whether any nearby value only sounds stronger because it inherited wording from another lane
- whether the row should instead be split into multiple rows

A lane that says `peer-declared reachable` must not quietly behave like `locally proven reachable`.
A lane that says `organization scoped` must not quietly carry adjacent `user` semantics that contradict it.

### 4) Allowed promotions

Show which stronger claims, if any, may be inferred from the row:

- `may not be promoted`
- `may become a derived hint only`
- `may support a reviewed recommendation`
- `may support a local proof claim after additional evidence`

The rule should be strict by default.
Useful hints should remain visible without becoming stronger than they are.

### 5) Fact receipt

Record:

- fact id
- authorship bucket
- claimed scope
- any explicit non-claim boundary
- any allowed promotion
- actor or source identity where relevant
- time and freshness
- supersession pointer when later evidence upgrades or invalidates the row

## Main surface

Every consequential pane should allow the operator to expand **Why this row says that**.

That expansion should answer:

- `who said this`
- `what exactly they could know`
- `what the product inferred`
- `what the product refused to infer`
- `whether nearby wording stayed exact`

## Public rules

AnonSync should hold the following rules:

- authorship bucket precedes confidence decoration
- weaker buckets may inform stronger rows only through explicit derivation
- derivations must preserve their inputs
- scope contradictions are not polish defects; they are truth defects
- a peer hint, sender hint, or browser event may remain useful without masquerading as local proof

## Acceptance criteria

This spec is satisfied when:

- operators can tell whether a row is locally observed, peer declared, operator entered, browser observed, config declared, or derived
- visible scope claims do not quietly contradict adjacent fields
- the interface can keep weak-but-useful hints without overstating them
- later stronger evidence can supersede earlier rows without pretending the earlier wording was always stronger than it was
