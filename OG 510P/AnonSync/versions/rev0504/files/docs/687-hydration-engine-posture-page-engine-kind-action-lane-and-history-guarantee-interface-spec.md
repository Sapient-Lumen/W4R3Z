# Hydration-engine posture page: engine kind, action lane, and history guarantee interface spec

## Purpose

This page exists because `Selective Sync`, `online only`, `keep on device`, `placeholder`, and `hydrated` do not by themselves identify one stable contract.
A subject can be using:

- a basic placeholder engine
- an OS-native hydration engine
- an in-app-only fallback lane
- a degraded lane with missing shell/provider affordances
- a history/collision ceiling that is narrower than the main product story

The page must let an operator answer one blunt question without article archaeology:

> what hydration engine is active here right now, what local lanes are actually usable, and what rollback/conflict guarantees are still honest on this seat?

## Core decision

AnonSync should make **hydration-engine posture** first-class.
Every subject that can expose partial materialization must publish, in one stable object:

- engine kind
- lane health
- path / substrate eligibility
- history guarantee
- collision guarantee
- co-tenant exclusions
- strongest safe sentence

## Fixed review order

Every hydration-engine posture page should render the same sections in the same order:

1. **Engine now**
2. **Action lanes**
3. **Eligibility basis**
4. **History guarantee**
5. **Collision guarantee**
6. **Co-tenant ceilings**
7. **Claim ceiling**

### 1) Engine now

Show:

- current engine: `none`, `basic-placeholder`, `os-hydration`, `in-app-fallback`, `degraded`, `unknown`
- exact policy source: seat default, subject override, imported legacy, runtime fallback
- whether the engine is mutable live, recreate-only, or path-class dependent

The operator must be able to answer: **what kind of hydration contract is active?**

### 2) Action lanes

Show:

- shell/provider lane health: `healthy`, `degraded`, `missing`, `unknown`
- in-app lane health
- whether open/double-click hydration is supported
- whether right-click / contextual actions are supported
- whether subtree pin / keep-local / evict-local actions are available

The operator must be able to answer: **which hydration actions are real here and through what lane?**

### 3) Eligibility basis

Show:

- OS / API prerequisite class
- filesystem / path prerequisite class
- whether the current path is `eligible`, `degraded`, `ineligible`, or `unknown`
- strongest unmet prerequisite if any

The operator must be able to answer: **is this path/seat truly eligible for the requested engine?**

### 4) History guarantee

Show:

- rollback posture: `full-version-history`, `delete-only-history`, `local-only-history`, `no-history-guarantee`, `unknown`
- whether hydrated-file replacement stores prior versions
- whether placeholder updates create retained versions
- whether the current engine changes cleanup or reclaim expectations

The operator must be able to answer: **what retained-history sentence is still honest under this engine?**

### 5) Collision guarantee

Show:

- collision posture: `full-detection`, `narrowed-detection`, `not-supported`, `unknown`
- reason for any narrowing
- whether the narrowing is engine-local, path-local, or version-line specific

The operator must be able to answer: **does the product still detect file-edit collisions honestly here?**

### 6) Co-tenant ceilings

Show:

- other provider / cloud-file engine conflicts
- parallel-runtime or multi-agent prohibitions
- inherited local flags/attributes that may override expected defaults
- virtualization or driver caveats if they materially change the engine claim

The operator must be able to answer: **what other local systems can invalidate or distort this contract?**

### 7) Claim ceiling

Show:

- strongest safe sentence
- stronger forbidden sentence
- evidence basis timestamp
- main uncertainty if present

Examples of safe sentences:

- `This seat uses OS hydration and supports shell-open downloads plus in-app pin/evict controls.`
- `This seat presents basic placeholders only; shell context actions are degraded, but in-app fetch remains available.`
- `This hydration engine keeps delete history only; prior file versions are not retained under remote replacement.`
- `Collision detection is narrowed on this seat because the active hydration engine does not support full rollback witness.`

## Main card

The subject workspace should expose a **Hydration** card with:

- engine chip
- lane chip
- eligibility chip
- history chip
- collision chip
- `Inspect hydration contract`

## Detailed page

### Pane A — Engine summary

Columns:

- engine kind
- policy source
- lane health
- path eligibility
- strongest safe sentence

### Pane B — Local prerequisites

Rows:

- OS / provider API
- filesystem / volume class
- current path class
- extension / provider health
- co-tenant conflicts
- inherited local flags

### Pane C — Guarantee matrix

Rows:

- open placeholder
- pin subtree
- evict local bytes
- retain previous versions
- detect edit collisions
- preserve local-only hydrate state across restart

Columns:

- status
- basis
- main ceiling
- next repair rung

## Rules

### Rule 1 — engine kind and lane health must stay separate

A healthy daemon on a bad lane is different from a bad engine choice.
The page may not collapse them.

### Rule 2 — history/collision ceilings travel with the hydration engine

The product may not advertise `online-only` or `keep local` without also publishing whether rollback or collision claims narrowed.

### Rule 3 — eligibility failures are not generic bugs

If the path, filesystem, provider, or co-tenant world makes the engine ineligible, the page must say so directly.

### Rule 4 — one label may not hide two materially different contracts

If a later operator could not tell basic placeholders from deeper OS hydration from this page alone, the page is not explicit enough.

## Event language

Events written by this page should include:

- `hydration.engine.changed`
- `hydration.lane.degraded`
- `hydration.eligibility.failed`
- `hydration.history.ceiling.changed`
- `hydration.collision.ceiling.changed`
- `hydration.cotenant.conflict.observed`

## Acceptance criteria

A later operator can:

- identify the active hydration engine
- see which local action lanes are actually usable
- see whether the current path is truly eligible
- see whether rollback and collision guarantees narrowed
- know exactly what the product may and may not claim afterward
