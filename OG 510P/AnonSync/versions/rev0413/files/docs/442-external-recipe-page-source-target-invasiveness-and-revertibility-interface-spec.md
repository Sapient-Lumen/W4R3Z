# External recipe page: source, target, invasiveness, and revertibility interface spec

## Purpose

The archive already has recipe catalogs and external-guidance intake, but it still lacked one ordinary page for this narrower question:

> what exact outside-the-product recipe is being proposed, who said so, what will it touch, and how reversible is it?

This document defines the interface contract for one first-class **external recipe** page.

## Core rule

Any recipe whose execution materially happens outside the normal product surface must declare:

1. its reviewed source and authority basis
2. its exact target tuple
3. its recipe class
4. its invasiveness and revertibility posture
5. what must already be true before execution
6. what return-proof is expected afterward

The product must not hide those answers in article prose or in a generic `advanced troubleshooting` drawer.

## Public object

### External recipe

Suggested fields:

- `external_recipe_id`
- `incident_ref`
- `source_ref`
- `source_kind` (`official-doc`, `support-reply`, `community-post`, `teammate-note`, `self-authored`, `other`)
- `source_authority_confidence`
- `recipe_title`
- `recipe_class` (`observe-only`, `cache-clear`, `config-edit`, `runtime-stop-start`, `state-mutation`, `destructive-reset`, `measurement-only`)
- `target_tuple_ref`
- `invasiveness` (`low`, `moderate`, `high`)
- `revertibility_class` (`none-needed`, `auto-revert`, `one-step-revert`, `manual-revert`, `non-revert-without-new-state`)
- `continuity_risk` (`none-known`, `low`, `material`, `successor-epoch-likely`)
- `precondition_refs[]`
- `expected_execution_witness`
- `required_postcondition_ref`
- `approval_state` (`draft`, `reviewed`, `approved`, `running`, `finished`, `abandoned`, `rejected`)
- `created_at`

### Target tuple

A normalized scope object that says exactly what the recipe will touch.

Suggested fields:

- `target_tuple_id`
- `seat_ref`
- `runtime_ref`
- `surface_ref`
- `path_ref`
- `process_ref`
- `profile_or_store_ref`
- `browser_or_trust_store_ref`
- `hidden_state_families[]`
- `cross-seat_effects_possible` bool

## Fixed page order

1. **Recipe verdict**
   - one-sentence summary
   - why this recipe is being considered now
   - current approval state

2. **Source and authority**
   - source title
   - source kind
   - authority confidence
   - reviewed excerpt or translation
   - what remained ambiguous

3. **Target scope**
   - full target tuple
   - whether scope is local-seat-only or may change future peer truth

4. **Invasiveness and revertibility**
   - recipe class
   - continuity risk
   - rollback class
   - expected residue

5. **Preconditions and return proof**
   - runtime stop requirements
   - path visibility requirements
   - privilege / access requirements
   - required postcondition page

6. **Apply / handoff receipt**
   - either approve for execution
   - convert into command-step / off-product-execution pages
   - or reject as unsupported

## Dense row contract

A dense external-recipe row should preserve these labels in this order:

- `Recipe`
- `Source`
- `Target`
- `Class`
- `Risk`
- `Rollback`
- `Needs after-check`

## Anti-goals

- no silent conversion from article prose into live side effects
- no target scope hidden in footnotes
- no destructive reset presented as routine cleanup
- no closure without a required return-proof page

## Acceptance test

This surface is good enough when a cautious operator can answer all of the following before execution:

- who recommended this recipe
- what exact local thing it will touch
- how invasive it is
- how to undo it, if undo is possible
- whether continuity may be preserved or recreated
- what reread will later prove success
