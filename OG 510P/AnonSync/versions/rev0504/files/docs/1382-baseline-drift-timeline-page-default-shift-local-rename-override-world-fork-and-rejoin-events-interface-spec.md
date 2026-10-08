# Baseline-drift timeline page — default shift, local rename, override, world fork, and rejoin events

## Timeline question

> how did this subject or cohort stop matching the baseline, and what sequence would be required to become truly conformant again?

## Timeline event classes

### 1) Baseline revision event

Shows:

- baseline id before and after
- changed setting fields
- affected cohort class
- stronger historical sameness sentence now blocked

### 2) Default-shift event

Shows:

- prior default and new default
- inheriting subjects that moved
- detached subjects that stayed behind
- future divergence expectation

### 3) Explicit-override event

Shows:

- subject id
- previous inheritance state
- new explicit value
- whether visible equality with baseline remained or ended

### 4) Explicit-none event

Shows:

- whether `none/off` was chosen explicitly
- why this is distinct from inherit
- later comparison confusion risk

### 5) Reattach event

Shows:

- proof detachment ended
- baseline/governance state restored
- first later default shift that would now apply

### 6) Local-label / alias event

Shows:

- old local label and new local label
- whether canonical subject id changed or not
- whether the alias propagates elsewhere or remains local only
- comparison confusion introduced or resolved

### 7) World-fork event

Shows:

- source world and successor world ids
- migration continuity vs clean fork
- inherited baseline state carried forward vs reset
- cross-world comparison ceiling after the fork

### 8) Rejoin / rebaseline event

Shows:

- how a previously forked or detached subject re-entered a baseline
- whether rejoin happened by restore-inheritance, explicit edit, import, or re-share
- any residual divergence that still survives

## Rendering rules

- The timeline must keep value drift, governance drift, label drift, and world drift on separate tracks.
- Coincidental value matches must remain visually weaker than restored governance matches.
- Local-label events must not masquerade as subject-identity changes unless canonical identity truly changed.

## Required ending block

The page ends with:

- current equality grade
- last event that changed that grade
- earliest event that could restore full baseline conformance
- blocked stronger sentence
