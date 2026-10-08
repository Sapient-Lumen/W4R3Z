# Proxy action substitution page — requested local verb versus actual effect

## Purpose

Prevent local-looking verbs from executing with hidden non-local meaning.
This page rewrites the operator's requested verb into the smallest honest action contract available.

## Typical triggers

- delete on placeholder proxy
- delete on conflict derivative
- move or rename on conflict derivative
- remove on hidden witness or service-state path
- any action where visible entry class and actual scope do not match

## Inputs

- requested verb from the prior surface
- reviewed artifact class
- counterpart map
- current authority posture
- last-full-copy risk if known
- witness and archive consequences

## Questions this page must answer

1. What verb did the operator request?
2. What would that verb actually do on this artifact class?
3. What smaller or safer substitute exists?
4. What sentence should the product use instead of the operator's shorthand?
5. What stronger claims remain forbidden even after apply?

## Layout

### A. Requested-versus-effective card
Fields:

- requested verb
- reviewed artifact class
- effective action class
- affected scope

Example rows:

- `Delete` + `placeholder-proxy` → `all-peer delete` or `local eviction only` depending on chosen substitute
- `Delete` + `conflict-derivative` → `unsafe; may delete real remote counterpart`
- `Open` + `archive-witness` → `inspect witness only; not restore yet`

### B. Substitute ladder
Order substitutes from narrowest to broadest:

1. inspect only
2. local-only reclaim
3. rename / isolate for review
4. all-peer action
5. blocked pending healthier witness selection

### C. Safe-language rewrite
Three stacked lines:

- **operator asked for**
- **product can honestly do**
- **product may honestly say afterward**

### D. Residual-risk pane
Show residuals such as:

- last full copy may disappear
- remote counterpart remains unresolved
- witness still needed before cleanup
- service-state damage risk remains too high

## Required actions

- `Use safer substitute`
- `Proceed with broad effect`
- `Return to counterpart map`
- `Export substitution receipt`
- `Cancel`

## Guardrails

- Never let `delete` remain unlabeled when its effective scope is broader than local.
- Never let `remove confusion` execute as `delete counterpart`.
- Never let `inspect` be labeled `restore`.
- Never let the rewrite hide stronger forbidden claims.

## Output

A reviewed action contract that replaces the original local-looking verb with the narrowest accurate effect and language.
