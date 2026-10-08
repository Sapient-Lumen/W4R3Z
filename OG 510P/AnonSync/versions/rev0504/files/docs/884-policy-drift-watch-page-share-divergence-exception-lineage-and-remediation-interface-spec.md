# Policy drift watch page: share divergence, exception lineage, and remediation interface spec

## Purpose

This page answers one ordinary question:

> which related subjects no longer follow the same policy, why do they differ, and what is the cheapest honest way to bring them back into a readable cohort?

The page exists because multi-plane policy produces exceptions over time, and exceptions should not remain invisible folklore.

## Core decision

Any cohort with meaningful shared defaults or expected common posture must render a first-class **Policy drift watch** page whenever divergence appears.

## Fixed page order

1. cohort strip
2. divergence matrix
3. exception lineage card
4. remediation ladder
5. safety / blast-radius card
6. drift receipt rail

### 1) Cohort strip

Show:

- cohort name
- governing default or expected posture
- number of conforming subjects
- number of exceptions
- strongest next-safe action

### 2) Divergence matrix

List the key subjects and policy fields with at least:

- effective value
- expected value
- origin plane
- difference class
- age of divergence

Difference classes should include at minimum:

- `reviewed exception`
- `legacy override`
- `config-owned split`
- `temporary divergence`
- `accidental drift`
- `blocked from convergence`

### 3) Exception lineage card

For the selected divergent subject, publish:

- first divergence event
- last reviewed change
- source-of-truth plane
- whether the exception is still justified
- whether newer cohort defaults have bypassed it

### 4) Remediation ladder

Offer ordered repair verbs such as:

- keep exception and receipt it
- rejoin inheritance
- promote to new cohort default
- split into separate cohort
- open config-plane review

### 5) Safety / blast-radius card

Before any convergence action, show:

- which subjects will change
- which dangerous or destructive implications follow
- which reviewed exceptions must be preserved
- which receipts will be superseded

### 6) Drift receipt rail

Link to latest change preview, inheritance rejoin receipt, config review receipt, or drift classification receipt.

## Rules

### Rule 1 — drift must be named, not merely implied

A divergent subject cannot hide inside a quiet settings page.
The product must show that it differs from expectation.

### Rule 2 — expected value must be visible beside actual value

The operator should not have to remember the cohort default from another page.

### Rule 3 — remediation must preserve legitimate exceptions

Convergence tools must not steamroll reviewed, necessary deviations.

## Acceptance criteria

A later operator can:

- tell which subjects are exceptions
- tell why each one differs
- tell whether the difference is justified, legacy, or accidental
- choose an honest convergence or split action without guessing blast radius
