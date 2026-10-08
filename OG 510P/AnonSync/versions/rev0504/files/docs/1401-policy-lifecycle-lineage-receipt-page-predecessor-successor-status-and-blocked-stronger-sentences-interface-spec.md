# Policy-lifecycle lineage receipt page — predecessor, successor, status, and blocked stronger sentences

## Purpose

This receipt is the durable artifact for later operators who need one compact answer to:

> what policy changed, what replaced it, what posture the predecessor is in now, who did not move, what happened to the waivers, and what stronger lifecycle sentence did the product refuse to make?

## Receipt fields

Every policy-lifecycle receipt must include:

- receipt id
- policy family id
- predecessor id and revision
- successor id and revision
- relation class
- requested action
- final action taken
- predecessor posture now: `current`, `deprecated`, `retired`, `rolled-back`, `unknown`
- successor posture now: `draft`, `current`, `blocked`, `rolled-back`, `unknown`
- subject outcome counts by posture
- waiver migration counts by verdict
- orphan-risk count
- rollback class
- strongest safe lifecycle sentence
- blocked stronger sentence
- issuance time
- actor

## Display order

1. lifecycle headline
2. predecessor/successor pair
3. action verdict
4. subject outcomes
5. waiver migration verdicts
6. rollback posture
7. blocked stronger sentence

## Hard rules

- A receipt may never omit the predecessor just because the successor is now current.
- A receipt may never say `replaced` without naming relation class.
- A receipt may never say `retired` if any subject remained grandfathered under the predecessor.
- A receipt may never say `all moved` if any subject outcome bucket other than `moves-to-successor` is nonzero.
- A receipt may never say `waivers preserved` without listing verdict counts.

## Example strongest-safe sentence patterns

- `Profile P-042 revision 7 is now current as a compatible successor to P-042 revision 6; most covered subjects moved, but 19 remain grandfathered and predecessor retirement is still deferred.`
- `Profile P-077 branch B is current only for the service world; the desktop predecessor remains deprecated but not retired, and carry-forward waivers remain under rereview.`
- `The predecessor was sunset with no successor; affected subjects were detached before retirement, and no live inheritance path remains.`

