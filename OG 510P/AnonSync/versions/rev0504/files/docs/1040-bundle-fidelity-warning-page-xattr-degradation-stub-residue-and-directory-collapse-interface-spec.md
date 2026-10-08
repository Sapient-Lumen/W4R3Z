# Bundle fidelity warning page — xattr degradation, stub residue, and directory collapse

## Purpose

Warn when a seemingly single high-level object depends on metadata lanes that the current cohort cannot fully preserve.

## Trigger conditions

Show this page when:

- bundle semantics depend on xattrs / streams
- any peer cannot store required metadata natively
- StreamsList excludes required metadata names
- troubleshooting or prior observation indicates bundle collapse risk

## Required sections

### 1. Bundle semantics summary

Must explain:

- what makes this object a bundle rather than merely a directory here
- which metadata lanes are required to preserve that interpretation
- which peer classes can or cannot apply those lanes natively

### 2. Degradation ladder

Must render the possible outcomes in descending order:

1. preserved bundle semantics
2. metadata propagated with compatibility stub residue
3. bytes preserved but rendered as plain directory/subtree
4. blocked because fidelity floor is below requested claim

### 3. Compatibility residue section

Must show:

- whether `.sync/Streams` residue will be created
- whether that residue is authoritative, temporary, or merely forwarding compatibility state
- whether deleting residue would reduce future fidelity

### 4. Operator decision

Must offer clear verbs:

- `require bundle fidelity`
- `allow stub-backed propagation`
- `accept plain-directory degradation`
- `exclude this object from current cohort`

### 5. Claim boundary

Must show:

- strongest safe sentence
- blocked stronger sentence such as `all peers will see the same bundle semantics`
- reopen triggers
