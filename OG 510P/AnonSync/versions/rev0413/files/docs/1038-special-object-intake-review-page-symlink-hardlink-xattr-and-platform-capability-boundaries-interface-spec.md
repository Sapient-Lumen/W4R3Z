# Special object intake review page — symlink, hardlink, xattr, and platform-capability boundary

## Purpose

Force a reviewed decision before importing, publishing, or adopting a filesystem object whose semantics are not guaranteed to survive unchanged across the current cohort.

## Entry conditions

Trigger this page whenever any of the following are true:

- object kind is not plain file/directory
- symbolic-link or junction witness exists
- hard-link-style aliasing is suspected
- bundle semantics depend on xattrs / streams
- a peer class is known to reject or degrade the object kind
- fidelity ceiling is weaker than the operator’s requested claim

## Required review blocks

### 1. Requested intent

Must render the operator’s intent in plain language:

- `preserve the reference object itself`
- `sync the referenced target instead`
- `preserve bundle semantics`
- `allow degraded ordinary-folder behavior`
- `exclude this object class from sync`

### 2. Platform boundary matrix

Must list peer classes and show:

- native preserve support
- degrade-to-ordinary behavior
- conflict risk
- outright block reason
- whether the boundary is local-only, current-cohort, or future-cohort risk

### 3. Metadata dependency block

Must show:

- whether preserving semantics depends on xattrs/streams
- whether the required metadata names are currently whitelisted
- whether any peer is expected to store them only through stub residue
- whether disabling metadata lanes will collapse behavior

### 4. Decision paths

Must offer separate reviewed outcomes:

1. preserve as special object
2. preserve bytes only and explicitly accept metadata/reference loss
3. re-model target as its own subject
4. block publication until cohort changes

### 5. Receiptable claims

Before apply, must show:

- strongest safe sentence
- stronger blocked sentence
- invalidators that would reopen review
