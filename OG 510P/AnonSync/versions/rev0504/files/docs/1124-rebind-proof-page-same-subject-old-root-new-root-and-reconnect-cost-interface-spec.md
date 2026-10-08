# Rebind proof page: same subject, old root, new root, and reconnect-cost interface spec

## Operator question

> what proof do we actually have that this repaired path is the same subject as before, and what reconnect or resharing debt still remains if I commit?

## Proof ladder

The page must publish one explicit proof ladder:

1. `path-spelling only`
2. `root witness only`
3. `service-capsule / subject marker witness`
4. `same-subject strong proof`
5. `same-subject and same-peer-continuity proven`

## Required evidence rows

- last bound path
- current candidate path
- root witness comparison
- subject marker / service-capsule witness if available
- whether peer relationships survive automatically, require reconnect, or require re-share
- whether default reconnect proposal drifts from the original path
- whether a same-name `(1)` sibling would be created instead

## Reconnect-cost classes

- `none`
- `manual path correction only`
- `reviewed reconnect`
- `remove and re-add`
- `re-share / reapprove`

## Stronger claims that may only appear at higher rungs

Only rung 4 or higher may allow:

- `This is the same subject as before.`
- `You are resuming prior continuity rather than creating a new bind.`

Only rung 5 may allow:

- `Peer continuity and subject continuity both remain intact.`

## Example safe sentences by rung

- rung 1: `This candidate matches the prior path spelling only.`
- rung 2: `The root appears to be the same, but subject continuity is not yet proven.`
- rung 3: `The product found prior subject markers consistent with the earlier bind.`
- rung 4: `This candidate is strongly evidenced as the same subject.`
- rung 5: `This candidate is strongly evidenced as the same subject and prior peer continuity survives without re-share.`

## Action rail

Allow:

- `Commit reviewed rebind`
- `Downgrade to fresh bind`
- `Escalate to re-share plan`
- `Emit receipt`

Do not allow `Continue` without naming the proof rung and reconnect-cost class.
