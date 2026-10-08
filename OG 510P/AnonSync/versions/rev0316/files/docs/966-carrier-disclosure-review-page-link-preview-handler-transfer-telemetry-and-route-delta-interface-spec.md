# Carrier disclosure review page — link preview, handler transfer, telemetry, and route delta interface spec

## Purpose

This page exists for moments when the operator is about to choose a carrier or enable a helper and needs to know the disclosure delta before apply.

It answers:

> if I switch from local parse to browser landing page, from direct peer path to relay-eligible path, or from telemetry-off to telemetry-on, what new observer classes and fact families enter the path?

## Core decision

Any serious disclosure-affecting change must open a first-class **Carrier disclosure review** page before apply.

That review owns:

- old carrier set
- proposed carrier set
- observer delta
- fact-family delta
- strongest safe sentence after apply
- stronger rejected sentence after apply

## Page layout

The page renders the same order:

1. current posture
2. requested change
3. observer delta
4. fact-family delta
5. confidence and proof basis
6. apply / cancel / safer-neighbor actions

### 1) Current posture

Show:

- current carrier set
- current observer set
- strongest safe sentence now
- current proof freshness

### 2) Requested change

Show:

- exact requested mutation (`open in browser`, `register handler`, `allow relay`, `allow tracker discovery`, `enable telemetry`, `issue preview-bearing artifact`)
- requested reason / operator intent if available
- whether the change is reversible immediately, only later, or only on new artifacts

### 3) Observer delta

Render explicit adds / removes / unchanged for observer classes.

Examples:

- `browser landing page enters path`
- `tracker infrastructure remains in path`
- `telemetry recipient newly enters path`
- `relay remains possible but not currently active`

### 4) Fact-family delta

Render only changed cells.

Examples:

- `subject label changes from local-only parse to explicit browser-visible preview`
- `route facts change from peer-only to tracker-visible`
- `OS/version posture changes from not exported to telemetry-visible`
- `payload bytes remain unreadable to relay`

### 5) Confidence and proof basis

Show whether the delta is:

- `implementation-proved`
- `artifact-structure-proved`
- `route-observed`
- `policy-stated`
- `weakly inferred`
- `unknown`

The operator should never have to guess whether the change is protocol-proven or just product-copy prose.

### 6) Apply / cancel / safer-neighbor actions

Only allow actions that fit the review result:

- `Apply requested carrier change`
- `Choose safer local-only carrier`
- `Narrow preview facts`
- `Keep relay disabled`
- `Keep telemetry disabled`
- `Export review receipt`

## Rules

### Rule 1 — carrier changes must publish their disclosure delta

No checkbox or share action may silently add a new observer class.

### Rule 2 — reversible and artifact-baked changes stay separate

A route helper can often be changed later; an already-issued artifact may already carry outward-facing hints.
The review must not flatten those cases.

### Rule 3 — route participation and payload readability stay separate

Relay or tracker entry into the path is not the same statement as payload readability.
Both must be rendered independently.

## Receipt fields

A carrier-disclosure review receipt must preserve:

- old carrier set
- new carrier set
- entered observer classes
- exited observer classes
- changed fact families
- strongest safe sentence
- blocked stronger sentence
- proof basis class
- completion time

## Result

AnonSync should force disclosure deltas into one review surface instead of making the operator combine security docs, handler folklore, relay docs, and telemetry settings by memory.
