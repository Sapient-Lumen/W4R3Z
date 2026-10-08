# Removal intent disambiguation page: disconnect, local evict, global delete, hide, unlink, and uninstall interface spec

## Purpose

This page appears when the operator asks to `remove`, `delete`, `clear`, `disconnect`, `hide`, or `unlink` and the ordinary verb is too overloaded to be safe.
The page exists to force one explicit answer before apply:

> which exact removal family do you mean, and which stronger meanings are you explicitly not choosing?

## When this page must appear

Trigger this page whenever:

- the initiating affordance uses a generic remove-like word
- the target is a placeholder, selective-sync subtree, disconnected share, seat roster entry, or installed runtime
- more than one mutation plane is plausible
- the platform projection could change the implied meaning of deletion

## Fixed page order

1. question header
2. removal-family chooser
3. counterfactual consequence panel
4. forbidden stronger interpretations
5. continue rail

### 1) Question header

Show:

- operator's original wording
- target object
- why the verb is ambiguous here
- strongest safe sentence before disambiguation

### 2) Removal-family chooser

Render exclusive choices such as:

- `Disconnect here only`
- `Evict local bytes but keep shared continuity`
- `Remove from linked seats under this identity`
- `Delete material for everyone this authority can reach`
- `Hide roster entry only`
- `Unlink this seat`
- `Uninstall runtime and clean residue`

Each option must preview:

- mutated planes
- remote effect
- local residue
- comeback path

### 3) Counterfactual consequence panel

For the currently highlighted option, show:

- what definitely disappears
- what definitely remains
- what may reappear later
- what stronger deletion claim would be false

### 4) Forbidden stronger interpretations

Include plain-language statements such as:

- `This does not delete the file for everyone.`
- `This does not unlink the seat.`
- `This does not remove archive residue.`
- `This does not stop a hidden device from reappearing later.`
- `This does not uninstall the runtime.`

### 5) Continue rail

Actions:

- `Continue to chosen review`
- `Export residue summary`
- `Cancel`

## Rules

### Rule 1 — ambiguity is resolved before approval, not inside it

Approval pages inherit a typed verb family; they do not invent it.

### Rule 2 — local and global delete must not neighbor each other silently

They must differ in wording, preview, and confirmation burden.

### Rule 3 — uninstall is not cleanup by implication

If runtime removal can still leave subject or archive residue, the page must say so.
