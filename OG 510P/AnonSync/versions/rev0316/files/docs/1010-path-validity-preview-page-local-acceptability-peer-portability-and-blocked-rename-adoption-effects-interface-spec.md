# Path validity preview page — local acceptability, peer portability, and blocked rename/adoption effects

## Purpose

Preview the exact consequences of adopting or renaming a path that may be acceptable on one surface but unsafe across the reviewed cohort.

This page exists to answer:

- `will this name be accepted locally?`
- `will peers preserve it, rewrite it, reject it, or collide it?`
- `what downstream effects follow if I continue anyway?`

## Required sections

### 1. Current and candidate paths

Must show:

- current path
- candidate path
- operation type
- reviewed horizon
- immediate local validity verdict

### 2. Portability matrix

Must classify each reviewed peer/surface as:

- preserves candidate unchanged
- canonicalizes candidate
- rewrites or substitutes candidate
- rejects candidate
- unknown

### 3. Downstream effects

Must show the expected effect family:

- no downstream hazard
- future conflict artifact risk
- blocked sync / non-arrival risk
- archive / restore replay ambiguity
- rename divergence across peers
- same-looking duplicate branch risk

### 4. Safer alternatives

Must offer:

- choose cohort-safe name
- keep local alias only
- branch subject locally
- stop and repair existing portability issues first

### 5. Strongest safe sentence

Examples:

- `The candidate is acceptable on the current seat but not portable across the reviewed cohort.`
- `Proceeding would create a rename that cannot be stated honestly as preserved everywhere.`

### 6. Blocked stronger sentence

Examples:

- `This rename will be preserved exactly across all peers.`
- `The only question is whether the current filesystem accepts it.`

## Interaction rules

- the primary action must reflect the actual winning outcome (`Rename locally only`, `Choose new canonical name`, `Stop and repair`, etc.)
- portability matrix entries must be visible without extra drilling when any peer is blocked or rewritten
- this page must preserve action-plane separation from local aliasing and other non-path mutations

## Receipt obligations

Any receipt derived from this page must preserve:

- local validity verdict
- portability matrix summary
- downstream effect family
- chosen action
- blocked stronger sentence
