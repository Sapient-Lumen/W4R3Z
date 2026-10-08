# Subject delivery review page — absent, visible, blocked, and ghost class

## Purpose

Give the operator one reviewed answer to:

- what is currently true about this subject's non-arrival or non-advancement
- whether the strongest honest verdict is `still-processing`, `blocked`, `excluded`, `ghost`, `continuity-broken`, or something else
- what evidence supports that verdict right now
- what the first safe next move actually is

This page is the subject-level companion to warning pages and the pre-remedy companion to local-fault ladders.
It should appear even when the operator started from a file row or missing path rather than from a warning banner.

## Inputs

- selected subject identifier and current path
- current seat and surface
- local visibility posture (`missing`, `placeholder-visible`, `partially-local`, `fully-local`, `unknown`)
- current byte-source posture if known
- policy state (IgnoreList / metadata / role / permission / overwrite posture)
- warning rows if any
- history and recent transfer / queue evidence
- continuity state for the containing subject (`healthy`, `service-files-missing`, `database-error`, `unknown`)
- route / peer / tracker / relay observations if relevant
- local environment evidence (lock, free space, watchers, time skew, path portability, fs fault)

## Primary questions this page must answer

1. What is the strongest honest current verdict for this subject?
2. Is the issue policy exclusion, source absence, route weakness, local obstruction, hidden-work delay, or continuity damage?
3. What evidence supports that verdict, and what stronger diagnosis remains unsupported?
4. What is the least-strong justified next move?
5. What stronger intervention should stay blocked for now?

## Subject delivery verdict classes

At minimum:

- `delivering-now`
- `still-processing`
- `waiting-for-source`
- `excluded-by-policy`
- `blocked-by-local-lock`
- `blocked-by-local-permission`
- `blocked-by-readonly-divergence`
- `blocked-by-portability-or-path`
- `notification-gap-rescan-needed`
- `space-blocked`
- `time-invalid`
- `ghost-no-source`
- `continuity-broken`
- `filesystem-fault`
- `unknown-needs-deeper-evidence`

## Layout

### A. Verdict card
Top card with:

- subject path / name
- current verdict badge
- strongest safe sentence
- first safe next move

Example sentences:

- `This subject appears to be excluded by current policy, not merely delayed.`
- `This subject is visible in tree state but no confirmed source peer currently has the bytes.`
- `This subject may still be progressing through hashing / merge / write work rather than being stuck.`
- `This subject cannot currently advance because continuity-bearing service files are missing.`

### B. Evidence strip
Show compact evidence chips grouped by plane:

- `policy`
- `source`
- `route`
- `local execution`
- `filesystem / continuity`
- `chronology`

Each chip shows one of:

- `supports verdict`
- `contradicts stronger claim`
- `unknown / not yet observed`

### C. First-move pane
Show one primary move and bounded alternatives.

Primary moves can include:

- `Wait and observe`
- `Fetch from healthy source`
- `Touch / rescan only`
- `Fix permission`
- `Review overwrite posture`
- `Raise watcher limit and restart`
- `Free space`
- `Repair same-lineage continuity`
- `Retire stale ghost visibility`

### D. Stronger interventions blocked
Examples:

- `Do not remove and re-add yet; current evidence does not justify successor rebuild.`
- `Do not call this stuck; background work evidence is still active.`
- `Do not call this deleted; the subject may still exist on an offline source.`
- `Do not call this fetchable now; route/source evidence is incomplete.`

## Required interactions

- `Review absence-cause matrix`
- `Choose minimal intervention`
- `Keep waiting with receipt`
- `Escalate to recovery ladder`
- `Export delivery truth receipt`

## Guardrails

- Never collapse `still-processing` into `stuck` without contradiction evidence.
- Never collapse `ghost-no-source` into ordinary slow delivery.
- Never collapse `excluded-by-policy` into transport failure.
- Never collapse continuity damage into a mere queue delay.
- Never offer remove/re-add as a primary action unless lower rungs have been ruled out or exhausted.

## Output

A reviewed subject-level verdict and first-move contract that downstream wait, fetch, repair, or cleanup flows must inherit without reinterpretation.
