# Override mutation review page — UI, power-user, config, and scope-collision interface spec

## Purpose

Review a requested rule change before apply when behavior might be governed by more than one settings plane.
The page should stop the operator from treating every rule edit as the same class of mutation.

## Inputs

- requested mutation
- current effective rule
- requested target value
- provenance chain before apply
- authoritative edit surface
- shadow rules likely to remain after apply
- whether the mutation is live, restart-required, reconnect-required, or config-commit-required
- whether the mutation changes only future subjects or also current ones
- whether the mutation substitutes product mode (`ui-owned` -> `config-owned`, etc.)
- strongest safe sentence after apply
- stronger forbidden sentence after apply

## Primary questions this page must answer

1. Is this a live edit, a deeper override, a config commit, or a mode substitution?
2. Which rules will still remain beneath the new one?
3. Which subjects change immediately, and which do not?
4. What restart, reload, reconnect, or relaunch boundary exists?
5. What stronger post-apply sentence is still forbidden?

## Layout

### A. Mutation class strip

Labels:

- `live ui edit`
- `power-user override`
- `config-owned commit`
- `default-for-future-only`
- `runtime-store substitution`
- `blocked until authoritative surface`

### B. Before / after provenance compare

Two columns:

- effective rule before apply
- expected effective rule after apply

Each column should show:

- winning origin
- shadow residue
- authoritative surface
- product mode

### C. Scope collision card

Fields:

- current subject set affected now
- future subject set affected later
- unaffected subjects that preserve older rules
- operator language substitution for mixed scope

### D. Apply mechanics card

Fields:

- needs restart?
- needs reconnect?
- needs config file commit?
- needs runtime relaunch?
- can current surface execute it or only draft it?

### E. Claim ceiling block

Four lines:

- requested sentence
- strongest approved sentence
- stronger forbidden sentence
- residue plane causing the ceiling

## Required interactions

- `See winning rule provenance`
- `Open hidden override surfacing`
- `Switch to authoritative surface`
- `Apply and issue receipt`

## Guardrails

- Never preview only the requested value; always preview the winning value after apply.
- Never imply all existing subjects inherit a new default.
- Never hide that a config commit may disable or supersede the live UI surface.
- Never let a successful draft read as a successful behavior change when a restart or reconnect still gates effect.
- Never discard shadow rules from the after-state model.

## Output

A reviewed mutation verdict that says what kind of policy change this really is, what it will actually govern, and what stronger sentence it still does not earn.
