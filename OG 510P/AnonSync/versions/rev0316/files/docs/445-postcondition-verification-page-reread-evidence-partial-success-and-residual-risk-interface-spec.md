# Postcondition verification page: reread evidence, partial success, and residual risk interface spec

## Purpose

External recipes are not complete when the step has merely run.
The product needs one first-class place to answer the harder question:

> what changed in product truth after the outside step, what did not, and what residual risk remains?

This document defines the interface contract for one first-class **postcondition verification** page.

## Core rule

Every external recipe, command step, or off-product lane must end in a product-side reread that states:

1. the claim under test
2. the fresh evidence now observed
3. what success would require
4. whether the result is full, partial, contradicted, or inconclusive
5. what residual risk or residue remains
6. whether continuity was preserved or recreated

No recipe may close on `step executed` alone.

## Public object

### Postcondition verification

Suggested fields:

- `postcondition_verification_id`
- `recipe_or_step_ref`
- `claim_under_test`
- `fresh_reread_refs[]`
- `result_class` (`verified`, `partially-verified`, `contradicted`, `inconclusive`)
- `changed_truths[]`
- `unchanged_truths[]`
- `residual_risks[]`
- `continuity_outcome` (`preserved`, `unclear`, `recreated-successor-state`, `not-applicable`)
- `next_action_kind` (`close`, `monitor`, `follow-on-recipe`, `rollback`, `escalate`)
- `created_at`

## Fixed page order

1. **Claim under test**
   - what the recipe was trying to achieve
   - what would count as success

2. **Reread evidence**
   - the fresh product evidence after execution
   - timestamps / surfaces / states reread
   - what those observations directly support

3. **Still-missing truth**
   - what remains unproven
   - what evidence would be needed to upgrade confidence

4. **Residual risk**
   - reset residue
   - widened exposure
   - duplicate seat rows
   - recreated continuity
   - stale caches or still-pending restart semantics

5. **Close / escalate receipt**
   - can this incident close?
   - must the recipe roll back?
   - should another recipe or escalation packet begin now?

## Result ladder

The page must classify the outcome explicitly:

- **Verified** — the intended product truth now holds
- **Partially verified** — something improved but the original claim is not fully true
- **Contradicted** — the step ran but the intended truth is false
- **Inconclusive** — evidence is still too weak or stale to conclude

## Dense row contract

A dense postcondition-verification row should preserve these labels in this order:

- `Claim`
- `Fresh evidence`
- `Result`
- `Still missing`
- `Residual risk`
- `Next move`

## Anti-goals

- no closure on ritual completion alone
- no success language without a reread basis
- no hiding recreated-successor state under the word `fixed`
- no missing residual-risk section after destructive or trust-widening steps

## Acceptance test

This surface is good enough when a cautious operator can answer all of the following after an outside step:

- what exact claim the step was meant to prove or repair
- what fresh product evidence was reread
- whether the result is full, partial, contradicted, or inconclusive
- whether continuity was preserved or recreated
- what residue or risk remains
- whether to close, monitor, roll back, or escalate
