# Affordance ceiling page: placeholder, shell action, and volume prerequisite interface spec

## Purpose

This page answers:

> which placeholder or materialization affordances are actually honest on this seat and this target volume, and are missing actions caused by client health, sync posture, or a real volume prerequisite?

The page exists because `action missing` is not one state.
A healthy client on the wrong target volume is different from a broken shell integration on a healthy target.

## Core rule

Whenever a meaningful file-level action depends on volume capability or shell support, the product must compile one first-class **Affordance ceiling** page before it blames the client or hides the action.
That page owns:

- action family in scope
- subject posture prerequisite
- client / extension health
- volume prerequisite
- equivalent fallback action
- affordance receipt

## Primary layout

The page always renders the same regions:

1. action verdict
2. prerequisite card
3. cause separation card
4. equivalent-action card
5. receipt and follow-on links

### 1) Action verdict

Show:

- verdict label: `available`, `available-in-app-only`, `blocked-by-posture`, `blocked-by-volume`, `blocked-by-client-health`, `unknown`
- strongest honest one-line summary
- action family in scope (`sync to device`, `remove from device`, `status overlays`, `open placeholder`, `batch materialize`)
- one safest next action

### 2) Prerequisite card

Show:

- subject posture prerequisite (`selective`, `connected`, `full`, `detached`, `unknown`)
- volume prerequisite
- seat/runtime prerequisite
- strongest unmet prerequisite

The operator must be able to answer: **what had to be true before this action could ever appear?**

### 3) Cause separation card

Show:

- shell / extension health
- volume capability verdict
- whether the subject posture itself suppresses the action
- strongest separating fact between `client issue` and `real ceiling`

The operator must be able to answer: **why is this action absent or degraded here?**

### 4) Equivalent-action card

Show:

- in-app equivalent if it exists
- CLI / local-web equivalent if it exists
- semantic differences between the equivalents
- strongest non-effect if the operator uses the fallback path

The operator must be able to answer: **what is the nearest honest way to do the same work anyway?**

### 5) Receipt and follow-on links

Link to:

- Volume capability
- Metadata fidelity
- Volume repair

After any accepted action, emit a receipt that preserves:

- action family reviewed
- cause verdict
- equivalent path chosen or declined
- remaining blocked promises

## Honest outputs

This page may conclude:

- `shell action absent because target volume is not eligible; in-app equivalent still available`
- `action blocked because subject is not in selective posture`
- `client-health issue suspected; target volume itself is eligible`
- `no honest equivalent on this target volume`

It may not collapse these into one vague `feature unavailable`.

## Rules

### Rule 1 — volume ceilings and client failures must be separate causes

The product may not merge those into one troubleshooting bucket.

### Rule 2 — equivalent actions must preserve semantic warnings

If the fallback path differs in scope or proof, the page must say so before launch.

### Rule 3 — hidden prerequisites are product debt

If the operator needs to remember NTFS, selective posture, or another hidden prerequisite from old lore, the page is not explicit enough.

### Rule 4 — absent action can still be the truthful outcome

If the target can never support the stronger action, the honest answer is to publish that ceiling, not to keep suggesting retries.

## Event language

Use explicit phrases such as:

- `action absent because target volume does not meet prerequisite`
- `subject posture suppresses this action even though target is eligible`
- `shell health degraded; in-app equivalent remains safe`
- `no equivalent action without changing target or posture`

Avoid vague lines such as:

- `context menu missing`
- `try again`
- `action not shown`

## Non-clone reason

Current official Resilio docs are candid that some materialization/shell actions depend on NTFS, Selective Sync, and healthy extensions.
But the operator still has to reconstruct which prerequisite failed.
AnonSync should instead expose one Affordance ceiling page where volume prerequisites, posture prerequisites, client-health verdicts, and fallback equivalents stay adjacent.
