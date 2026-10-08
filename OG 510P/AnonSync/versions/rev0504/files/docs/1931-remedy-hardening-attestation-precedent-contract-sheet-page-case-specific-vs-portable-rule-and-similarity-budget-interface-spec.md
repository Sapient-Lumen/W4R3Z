# Remedy-hardening-attestation precedent contract sheet page — case-specific versus portable rule and similarity budget

## Purpose

This page is the compact contract for deciding whether a case that is already operationally remediated and closure-governed may be reused as a future-facing rule, recipe, or policy.
It exists so the product can distinguish `case-specific only`, `portable for named class`, `pilot reuse only`, `policy ratified for named scope`, and `broader generalization blocked`.

## Core fields

- case identifier
- source affected-party-closure receipt identifier
- current governing receipt identifier
- current precedent-portability class
- candidate future-case class
- target topology classes in scope
- topology classes explicitly out of scope
- required invariants for portability
- known material differences list
- unresolved similarity gaps count
- pilot reuse count
- successful pilot reuse count
- counterexample count
- open counterexample flag
- ratification owner
- policy owner
- current approval state
- effective-from date
- next required review date
- sunset date if any
- strongest currently safe portability sentence
- strongest blocked policy sentence
- next evidence that upgrades portability confidence
- next evidence that forces narrowing, sunset, or revocation now

## Precedent-portability classes

The page must model at least these distinct classes:

- source case not yet closure-safe enough for reuse review
- closure-safe but case-specific only
- portability proposed, similarity review pending
- portable for named topology class only
- pilot reuse allowed for named cohort only
- pilot reuse successful but policy ratification pending
- policy ratified for named scope only
- counterexample open, rule narrowed
- precedent sunset due or review overdue
- precedent revoked or superseded
- broader policy blocked by unresolved differences

## Similarity axes

The page must support at least these similarity axes:

- authority and owner model
- identity and linking topology
- share-lane type
- folder type or object type
- platform family
- interface surface family
- evidence-plane availability
- remediation path shape
- downstream dependency class
- notice or closure policy class

## Fixed rendering order

Every precedent contract sheet must render the same sections in the same order:

1. **Strongest currently portability-safe sentence**
2. **Source-case closure quality and target class in scope**
3. **Required invariants, excluded differences, and similarity gaps**
4. **Pilot reuse, counterexamples, and policy-ratification state**
5. **Next evidence that upgrades or collapses the portability claim**

## Hard rules

The contract sheet must never let an operator hide:

- a topology difference behind one superficially similar success
- a Standard-only path behind an estate-wide policy claim
- a linked-device recipe behind manual-share populations or vice versa
- a desktop-only control behind a cross-surface generalization
- a pilot success behind missing ratification or a live counterexample
