# Exclusion policy page: rule editor, scope, and impact accounting interface spec

## Purpose

`46`, `58`, and the policy-lineage work already imply that `not indexed`, `not transferred`, and `not counted` are product semantics, not hidden implementation details.
This document gives those semantics one ordinary page.

The page exists to answer one ordinary operator question:

> which rules currently exclude material here, what scope do they have, and how do they change what the product counts or ignores?

## Core decision

Every subject that supports exclusion rules must render one first-class **Exclusion policy** page.
That page is the semantic home of:

- current exclusion rules and their source
- scope and matching semantics
- accounting consequences
- peer-divergence truth
- simulation before commit
- receipts for policy mutation

The page must not require operators to edit a hidden text file to understand the live exclusion contract.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. policy verdict strip
2. effective-rule set card
3. scope and matching card
4. accounting and visibility impact card
5. divergence and portability card
6. simulation / draft review
7. receipts and retired rules

### 1) Policy verdict strip

The strip shows:

- subject name
- ruleset version or policy revision
- one exclusion verdict
- one portability verdict
- one next-honest-action button

Allowed exclusion verdicts:

- `no exclusions`
- `baseline exclusions active`
- `custom exclusions active`
- `review required before apply`
- `conflicting policy sources`

Allowed portability verdicts:

- `rules aligned across seats`
- `local-only divergence present`
- `platform-sensitive matching risk`
- `scope ambiguity blocked`

### 2) Effective-rule set card

Show typed rule rows with:

- rule text or structured pattern summary
- source (`baseline`, `local override`, `imported policy`, `temporary override`)
- action class (`exclude from indexing`, `exclude from transfer`, `exclude from accounting` when coupled)
- current enablement
- actor / origin

The page must make shipped defaults visibly different from later local edits.

### 3) Scope and matching card

For each rule or candidate rule show:

- scope root
- subtree behavior
- case-sensitivity or normalization behavior
- wildcard or token semantics
- examples of matched and non-matched paths

The page should answer `what exactly will this catch?` without folklore.

### 4) Accounting and visibility impact card

Show:

- number of excluded paths or estimated candidate matches
- bytes omitted from indexed/accounted size
- whether excluded material remains present on disk
- whether excluded material is still visible in local browse surfaces
- whether exclusions affect future-arrival behavior only or current material too

The page must keep `hidden from accounting` distinct from `deleted`.

### 5) Divergence and portability card

Show:

- whether peers share the same exclusion rules
- whether divergence is deliberate or accidental
- platform-specific risk such as case handling or path separator translation
- likely observation differences caused by divergent rules

### 6) Simulation / draft review

Before applying a rule change, render a simulation section with:

- candidate rule list
- predicted new matches
- predicted removals from indexed/accounted totals
- risky collisions with existing allow/deny logic
- smallest honest apply action

### 7) Receipts and retired rules

Show recent exclusion-policy receipts with:

- actor
- rule delta
- affected scope
- accounting delta
- portability warning if any
- rollback availability

## Narrow-width behavior

In narrow width the page may stack cards, but it may not hide:

- whether exclusions are active
- matching scope examples
- accounting consequences
- divergence or portability risk

## Acceptance criteria

This spec is satisfied when:

- operators can inspect live exclusion semantics from one ordinary page
- scope and case-sensitivity truth no longer live mainly in raw file syntax
- the product shows accounting consequences before commit
- peer divergence is visible instead of surfacing later as mysterious size mismatch
- any rule mutation leaves a durable receipt naming the actual semantic delta
