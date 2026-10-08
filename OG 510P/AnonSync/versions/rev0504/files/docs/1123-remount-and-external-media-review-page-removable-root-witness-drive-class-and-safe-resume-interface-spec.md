# Remount and external media review page: removable-root witness, drive class, and safe-resume interface spec

## Operator question

> the path came back, or I want to land bytes on an external target — is this the same returned root, a different removable device, or really a same-host derivative / backup-style target with different continuity rules?

## Why this page exists

External and removable targets create a stronger ambiguity class than ordinary local folders.
A returned drive letter or mount point is not enough.
Same-computer internal→external work may also belong to a self-edge / local-share family rather than simple subject relocation.

## Mandatory fields

- current drive / root class (`internal-fixed`, `external-fixed`, `usb-removable`, `network-mounted`, `unknown`)
- last-seen root witness
- current root witness
- witness comparison verdict (`matches`, `plausibly-same`, `conflicts`, `unknown`)
- runtime visibility / principal access
- subject continuity candidate (`same-subject-return`, `fresh-target`, `self-edge-derivation`, `unknown`)

## Review sections

### 1. Root witness card

Show:

- path spelling
- root identifier(s) known to the product
- last-seen vs current witness
- whether only the mount point matched or the stronger witness matched

### 2. External-target intent card

Separate these intents:

- repair prior bind to returned external target
- create same-host derivative to external target
- export / backup copy to external target
- adopt external tree as fresh subject

### 3. Safe-resume consequences

For each allowed branch show:

- whether peers remain attached
- whether local-share / self-edge rules apply instead
- whether removal of the root later will suspend, detach, or merely pause bytes
- whether continuity claim ceiling drops because the root is removable

## Strong statements blocked here

- `The drive letter came back, so continuity is proven.`
- `External target equals backup target equals moved subject.`
- `Safe to resume without separate review.`

## Example safe sentence

- `A removable root returned at a familiar mount path, but the product has only mount-path similarity, not full root witness proof. Resume as prior subject remains weaker than reviewed remount.`

## Allowed actions

- `Treat as returned root and continue to rebind proof`
- `Treat as fresh external target`
- `Convert to same-host derivative review`
- `Emit receipt`

Never collapse these into one `Use this drive` action.
