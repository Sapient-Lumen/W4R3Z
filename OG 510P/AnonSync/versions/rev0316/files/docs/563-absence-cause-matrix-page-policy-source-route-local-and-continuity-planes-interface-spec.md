# Absence-cause matrix page — policy, source, route, local, and continuity planes

## Purpose

When a subject is absent, stale, or not advancing, this page makes the evidence decomposition explicit before remedy language hardens.

## When this page appears

Show this page when the operator needs to understand *why* a verdict was chosen or when two or more causes remain plausible.

Typical triggers:

- the subject is visible but not arriving
- a warning exists but its subject-level meaning is ambiguous
- multiple remedial options are plausible
- the operator disputes `wait` versus `repair`
- a stronger diagnosis is being requested than current evidence supports

## Questions this page must answer

1. Which evidence planes were checked?
2. What does each plane support, contradict, or leave unknown?
3. Which verdict is strongest under the current evidence?
4. Which stronger verdicts remain unsupported or contradicted?
5. What evidence would change the verdict?

## Planes

### 1. Policy plane
Examples:

- IgnoreList / metadata exclusion
- read-only overwrite posture
- role / permission ceiling
- portability / path / encoding policy

### 2. Source plane
Examples:

- confirmed full-byte source online
- source exists but offline
- placeholder-only source
- no confirmed full-byte source

### 3. Route / transport plane
Examples:

- peers connected
- tracker / relay unavailable
- direct path blocked
- waiting for source return

### 4. Local execution plane
Examples:

- lock present
- write permission missing
- free-space pressure
- watcher exhaustion / rescan-only discovery
- hidden background work still active

### 5. Filesystem / continuity plane
Examples:

- service files missing
- database error
- merge failure
- filesystem fault
- stuck partial-download residue

### 6. Chronology plane
Examples:

- time difference beyond safe window
- stale observation only
- current timestamps still trustworthy

## Layout

### A. Verdict header
Top summary with:

- strongest current verdict
- confidence posture (`strong`, `guarded`, `mixed`, `weak`)
- first safe next move

### B. Plane matrix
Columns:

- plane
- evidence seen
- supports
- contradicts
- still unknown

Example row:

`source | no online full-byte witness; tree still advertises file | waiting-for-source / ghost | fetch-now | whether offline peer still has healthiest bytes`

### C. Stronger-diagnosis blocklist
A visible list of stronger claims that remain blocked, for example:

- `stuck`
- `deleted everywhere`
- `permissions are fine`
- `transport is the only problem`
- `remove-and-readd required`

Each blocked claim must name the missing or contradicting evidence.

### D. Evidence-to-verdict delta pane
Show what fresh fact would shift the verdict.

Examples:

- `A confirmed online full-byte source would downgrade ghost suspicion to waiting-for-source.`
- `A successful same-lineage continuity reread would move this from continuity-broken to blocked-by-local-cause or healthy.`
- `A lock-free write retry would remove the local-lock hypothesis.`

## Actions

- `Accept current verdict`
- `Gather missing evidence`
- `Move to minimal intervention chooser`
- `Open deeper recovery ladder`
- `Export cause matrix`

## Guardrails

- Never let one plane silently dominate the verdict when another plane contradicts it.
- Never let `unknown` collapse into the most dramatic explanation.
- Never let `ghost-no-source` be claimed while a healthy full-byte source is confirmed.
- Never let `policy exclusion` be hidden behind network rhetoric.

## Result

A typed evidence map that explains why the product chose the current subject-delivery verdict and what would be needed to strengthen or overturn it.
