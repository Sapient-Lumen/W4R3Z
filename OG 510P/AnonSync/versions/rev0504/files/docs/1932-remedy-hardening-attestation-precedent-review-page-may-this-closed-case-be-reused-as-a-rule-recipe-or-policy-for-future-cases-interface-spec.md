# Remedy-hardening-attestation precedent review page — may this closed case be reused as a rule, recipe, or policy for future cases?

## Purpose

This page is the operator-facing review that answers the practical reuse question after a case has closed cleanly: does the product know enough to treat that outcome as portable beyond the source case, or must it stay case-specific?

## Primary review prompts

The review must answer these prompts in order:

1. **Is the source case itself closure-safe enough to be considered for reuse at all?**
2. **Which future-case classes are being asked to inherit this rule or recipe?**
3. **Which invariants must match before portability is allowed?**
4. **Which differences are material enough to block or narrow generalization?**
5. **What pilot reuse evidence or counterexamples already exist?**
6. **What is the strongest sentence the product may say right now?**

## Review sections

### 1. Source-case fitness board

Show:

- source closure class
- unresolved contest or reopen risk
- irreversibility or compensation residue that still limits reuse
- whether the source case is stable enough for portability review

### 2. Target-class map

Show:

- named future-case classes being considered
- topology families in scope
- platform or surface families in scope
- explicit out-of-scope populations

### 3. Similarity and difference matrix

For each required axis, show:

- match confirmed, mismatch confirmed, or unreviewed
- whether the difference blocks all reuse or only broader policy
- exact invariant the future case must satisfy

### 4. Reuse evidence board

Show:

- prior pilot reuses
- successes and failures
- counterexamples and near-misses
- ratification or policy-owner state

### 5. Portability sentence chooser

The review must output one and only one primary sentence class such as:

- case closed, case-specific only
- portability proposed, similarity review pending
- portable for named topology class only
- pilot reuse allowed for named cohort only
- pilot succeeded, policy ratification pending
- policy ratified for named scope only
- counterexample opened, scope narrowed
- precedent revoked or sunset due

## Hard rules

The review must never let an operator hide:

- one successful support path behind estate-wide precedent
- a workaround behind a policy sentence
- a platform-specific success behind cross-platform confidence
- an unreviewed difference behind `substantially similar`
- one clean pilot behind a still-open counterexample in another class
