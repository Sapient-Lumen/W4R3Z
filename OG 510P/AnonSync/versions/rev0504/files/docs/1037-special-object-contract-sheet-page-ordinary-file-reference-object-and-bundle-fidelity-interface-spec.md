# Special object contract sheet page — ordinary file, reference object, and bundle fidelity

## Purpose

Show, in one durable place, what kind of filesystem object the product believes it is handling and what fidelity ceiling currently applies across the reviewed cohort.

This page exists to answer:

- `what object kind is this really?`
- `is the link/reference object preserved, followed, blocked, or degraded?`
- `what metadata lanes are required to preserve bundle semantics?`
- `what compatibility residue will exist on peers that cannot apply the preferred form?`
- `what exact sentence is still honest about fidelity across the cohort?`

## Required sections

### 1. Object header

Must show:

- object id
- subject id
- current path
- detected object kind (`file`, `directory`, `symbolic-link`, `hard-link-like alias`, `bundle`, `xattr-bearing object`, `compatibility residue`, `unknown`)
- current posture (`ordinary`, `preserved-reference`, `follow-blocked`, `degraded`, `blocked`, `unknown`)

### 2. Kind witness

Must show:

- local detection basis
- whether the object kind is native on this peer only or cohort-reviewed
- whether kind detection is stable across all current peers or inferred from one witness
- strongest safe sentence
- blocked stronger sentence

### 3. Fidelity ceiling

Must show separately:

- byte fidelity ceiling
- metadata fidelity ceiling
- reference fidelity ceiling
- bundle/compound-object fidelity ceiling
- peer horizon for which those ceilings were reviewed

### 4. Capability matrix

For each relevant peer class, show:

- may preserve reference object?
- may follow target locally?
- may store xattrs/streams natively?
- may require stub residue?
- may collapse bundle into ordinary directory semantics?
- proof basis

### 5. Degradation and residue section

Must show:

- whether `.sync/Streams` residue is expected
- whether bundle collapse risk exists
- whether Windows conflict generation risk exists for reference objects
- whether this object is blocked outright because cohort support falls below the reviewed floor

### 6. Action boundary

Must show explicit verbs:

- `preserve object as reference`
- `adopt target as separate subject`
- `drop metadata lane`
- `accept degraded ordinary-directory behavior`
- `block across current cohort`

The page must never present these as one ambiguous `sync object` action.
