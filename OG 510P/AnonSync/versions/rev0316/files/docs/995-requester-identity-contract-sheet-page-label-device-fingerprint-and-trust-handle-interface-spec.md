# Requester identity contract sheet page — label, device, fingerprint, and trust handle

## Purpose

Show, in one durable place, the exact requester identity facts the operator may rely on before granting or reusing trust.

This page exists to answer:

- `who is asking?`
- `what parts of this are just labels?`
- `what proof handle was actually reviewed?`
- `would approval stop at this requester or widen to a linked family?`

## Required sections

### 1. Request header

Must show:

- requester display label
- requester device label
- canonical requester handle
- request lane (`link`, `manual artifact`, `linked-family arrival`, `stored approval reuse`, `other`)
- requested subject and requested capability ceiling

### 2. Identity planes

Render separate rows for:

- **Human label**
- **Device label**
- **Proof handle**
- **Family / constellation handle**

Each row must publish:

- value
- provenance (`claimed by requester`, `stored locally`, `cryptographically presented`, `derived from prior reviewed linkage`, `unknown`)
- stability class
- whether it is sufficient alone for trust decisions

### 3. Proof handle block

Must show the reviewed proof handle in a copyable form and must say:

- whether the handle is freshly presented or previously remembered
- whether it matches a prior receipt
- whether it is unique in the current roster
- whether it is a seat handle, family handle, or ambiguous

### 4. Collision block

Must detect and show if any of the following exist:

- same human label, different proof handle
- same device label, different proof handle
- same family label, multiple distinct requester handles
- previously approved label now arriving with a different proof handle

### 5. Trust scope block

Must distinguish:

- `approve this requester only`
- `approve future requests that match this exact handle bundle`
- `consider widening to linked family`
- `family expansion unavailable or unreviewed`

### 6. Strongest safe sentence

Examples:

- `This requester's human label matches a previously seen name, but the reviewed proof handle is different.`
- `You are reviewing one seat handle; linked-family widening is a separate step.`
- `This approval can be reused only for future requests matching the stored handle bundle.`

### 7. Blocked stronger sentence

Examples:

- `This is definitely the same requester because the name matches.`
- `Approving this seat automatically means the whole family is trusted.`
- `Device label and proof handle are interchangeable.`

## Interaction rules

- primary approve action must stay disabled until the proof handle section is visible
- collision warnings must render inline, not behind secondary disclosure
- widening from seat to family must route through a separate review surface
- copied/exported summaries must preserve the distinction between label and proof handle

## Receipt obligations

Any receipt derived from this page must preserve:

- reviewed handle bundle
- trust scope chosen
- collision verdict
- strongest safe sentence
- blocked stronger sentence