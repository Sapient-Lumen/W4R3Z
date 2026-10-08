# Downstream-consequence contract sheet page — decision use, world mutation, and compensation debt

## Purpose

This page defines the contract for how a sentence version moves from being merely used as decision basis into actual downstream world change, unwind attempts, compensation, and residue.
It exists so the product can answer not just `who used it?` but `what did that use already change, and what kind of repair is still honest?`

## Core doctrine

The sheet must preserve these orderings:

- decision-used is weaker than world-mutation-started
- world-mutation-started is weaker than world-mutated
- world-mutated is weaker than unwind-cleared
- unwind-issued is weaker than compensation-cleared

## Mandatory fields

### 1. Sentence identity

- case identifier
- source consumer-uptake receipt identifier
- sentence version handle
- decision-use class that triggered downstream consequence tracking
- fallback sentence if unwind or supersession occurs

### 2. Consequence families

The page must track at minimum:

- local filesystem mutations
- multi-peer propagation mutations
- permission or access mutations
- publication or notification emissions
- automation-triggered mutations
- external/public-facing mutations
- compensation-only residue surfaces

### 3. Strongest honest consequence rung

For each named consequence family or target cohort, the page must track exactly one strongest honest rung:

- not armed
- armed
- emitted
- mutation-started
- world-mutated
- partially unwound
- compensation-owed
- compensation-issued
- compensation-cleared
- irreversible residue
- unknown / contested

### 4. Mutation semantics

- whether the mutation is local only, connected-cohort, required-cohort, or external/public
- whether the mutation changes bytes, permissions, visibility, deadlines, or external commitments
- whether the mutation is reversible in place, reversible only by inverse action, or irreversibly residue-bearing
- whether a halt lane exists before completion
- whether later reconnect or rescan can re-materialize the mutation

### 5. Compensation semantics

- whether ordinary rollback is still possible
- whether repair requires compensation rather than direct reversal
- who is owed compensation
- what form compensation may take: bytes restored, access restored, notice corrected, payment made, residue annotated, probation imposed
- whether compensation can fully clear the consequence or only narrow the residue

### 6. Residue semantics

The page must separately preserve:

- surviving bytes
- surviving access or copies on prior peers
- surviving public or external knowledge
- surviving automation side effects
- surviving audit obligations
- strongest blocked stronger reversal sentence

## Required operator questions

- what downstream consequences have already fired from this sentence version?
- which consequences are merely armed and which are already world-mutated?
- where can we still halt rather than compensate?
- where has direct rollback become too weak?
- who is owed repair, and what residue survives even after repair?
- what is the smallest honest repair sentence right now?

## Forbidden shortcuts

This page must not let the operator infer world mutation from shortcuts such as:

- `the sentence was current`
- `a consumer used it`
- `the folder appeared`
- `access was later revoked`
- `history shows activity`

Those facts may contribute evidence.
They may not replace explicit downstream-consequence classification.
