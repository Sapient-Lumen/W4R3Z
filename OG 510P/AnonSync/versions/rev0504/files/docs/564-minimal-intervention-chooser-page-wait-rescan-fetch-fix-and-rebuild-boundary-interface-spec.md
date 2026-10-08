# Minimal intervention chooser page — wait, rescan, fetch, fix, and rebuild boundary

## Purpose

Prevent operators from jumping straight from `not here` to the broadest repair ritual.
This page rewrites the requested fix into the least-strong justified intervention.

## Typical triggers

- operator asks for `fix sync`, `force sync`, `re-add`, `rebuild`, or `just get it here`
- subject delivery review found multiple plausible remedies
- remove/re-add or successor rebuild is being considered
- current evidence still supports a lower rung first

## Inputs

- requested operator intent
- current subject-delivery verdict
- absence-cause matrix
- local-fault and continuity evidence if any
- current byte-source posture
- current claim ceiling

## Questions this page must answer

1. What fix did the operator ask for?
2. What is the least-strong justified intervention right now?
3. What broader interventions remain blocked and why?
4. What sentence should the product use instead of the operator's shorthand?
5. What proof will show whether the chosen move succeeded?

## Intervention classes

Order from narrowest to broadest:

1. `wait-and-observe`
2. `refresh-observation / inspect-only`
3. `touch-or-rescan`
4. `fetch-from-healthy-source`
5. `fix-local-condition`
6. `adjust-policy / overwrite posture`
7. `raise-environment-capacity and restart`
8. `same-lineage continuity repair`
9. `successor rebuild / remove-and-readd`

## Layout

### A. Requested-versus-effective card
Fields:

- operator asked for
- current verdict
- least-strong justified intervention
- broader blocked interventions

Example rows:

- `Force sync` + `still-processing` → `wait-and-observe`
- `Re-add folder` + `notification-gap-rescan-needed` → `touch-or-rescan`
- `Download now` + `ghost-no-source` → `retire stale visibility or wait for healthier source`, not `fetch`
- `Fix by reconnecting` + `continuity-broken` → `same-lineage continuity repair` if still possible, else `successor rebuild`

### B. Intervention ladder
Show rungs with labels:

- scope widened?
- continuity risk?
- byte risk?
- proof of success?

### C. Safe-language rewrite
Three stacked lines:

- **operator asked for**
- **product can honestly do now**
- **product may honestly say afterward**

### D. Success proof pane
For the chosen rung, say what observation counts as success.

Examples:

- `Subject now advancing with live block-check / transfer evidence`
- `Fresh source witness confirmed and fetch started`
- `Permission gate cleared and write retried successfully`
- `Continuity restored without successor rebuild`
- `New successor instance created; continuity not preserved`

## Required actions

- `Use minimal intervention`
- `Allow broader intervention anyway`
- `Return to cause matrix`
- `Export intervention receipt`
- `Cancel`

## Guardrails

- Never let `force sync` remain unlabeled when the real move is merely rescan or wait.
- Never let remove/re-add appear as the default if lower rungs remain plausible.
- Never let `fetch now` survive when the subject is ghosted or source-less.
- Never let `fixed` be the post-action sentence if the move only suppressed visibility or created a successor instance.

## Output

A reviewed intervention contract that replaces the operator's broad shorthand with the narrowest honest next move and its proof condition.
