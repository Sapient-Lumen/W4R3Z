# Off-product execution page: browser, shell, admin lane, and observed witness interface spec

## Purpose

Not every serious external action is best represented as a shell command.
Some happen in human-operated lanes such as browsers, OS trust prompts, service managers, or admin consoles.

This document defines the interface contract for one first-class **off-product execution** page.

## Core rule

Whenever execution happens in a lane outside the main product surface, the product must preserve:

1. which lane is active
2. what action is expected there
3. what witness proves the lane action happened
4. what that witness still fails to prove
5. how the operator returns to the product for verification

The product must not leave the operator stranded in external UI folklore.

## Public object

### Off-product execution

Suggested fields:

- `off_product_execution_id`
- `external_recipe_ref`
- `lane_kind` (`browser-warning`, `browser-settings`, `shell`, `service-manager`, `admin-console`, `os-trust-prompt`, `support-portal`, `other`)
- `lane_target_ref`
- `expected_human_action`
- `expected_observed_witness`
- `possible_partial_or_contradictory_outcomes[]`
- `return_path`
- `required_postcondition_ref`
- `execution_state` (`awaiting-entry`, `in-lane`, `witnessed`, `contradicted`, `returned`, `abandoned`)

## Fixed page order

1. **Lane identity**
   - lane kind
   - where the operator is about to go
   - whether the lane is local-only or touches shared/admin infrastructure

2. **Expected action**
   - precise human step
   - what not to do while there
   - whether screenshots / notes / receipts are worth keeping

3. **Observed witness**
   - what visible sign means the lane action happened
   - what would count as contradiction or mismatch

4. **Partial / contradictory outcomes**
   - action appeared to succeed but product truth may still be unchanged
   - action partially worked
   - action widened exposure or reset state unexpectedly
   - action requires a follow-on stop/start before meaning anything

5. **Return path and receipt**
   - how to come back to the product
   - which postcondition page is mandatory next
   - durable `lane completed` receipt

## Example lanes this page must cover

- browser self-signed certificate warning bypass / HSTS cleanup
- OS trust prompt or SmartScreen-style allowance
- service-manager stop / start / restart
- admin-console edit of service-owned config or package settings
- support-portal upload or log handoff

## Dense row contract

A dense off-product-execution row should preserve these labels in this order:

- `Lane`
- `Action`
- `Witness`
- `Still not proven`
- `Return to`
- `State`

## Anti-goals

- no external lane steps that disappear into prose
- no assumption that browser access equals product health
- no assumption that service restart equals config success
- no ending in the external lane without an explicit return path

## Acceptance test

This surface is good enough when a cautious operator can answer all of the following while away from the main product UI:

- what lane they are in
- what exact action they are trying to perform
- what observation counts as success in that lane
- what observation still fails to prove product success
- how to get back to the right verification page afterward
