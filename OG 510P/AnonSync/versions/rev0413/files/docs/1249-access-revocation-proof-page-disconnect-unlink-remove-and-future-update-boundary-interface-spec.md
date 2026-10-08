# Access revocation proof page: disconnect, unlink, remove, and future-update boundary interface spec

This page exists so `disconnected`, `revoked`, `removed`, and `unlinked` stop laundering different consequences through one action verb.
A serious operator needs to know not just that a relationship changed, but **which future rights ended and which already-landed state survived**.

## Operator question

> whose future access or convergence was actually cut off, and what bytes or rights were already beyond the reach of this action?

## When this page must appear

Render whenever the product is about to:

- revoke a selected peer from a subject
- disconnect a subject from one seat
- remove a subject from linked-family management
- unlink a seat from an identity
- describe why an apparently removed peer still has data
- describe why a future update stopped while local bytes stayed present

## Fixed page order

1. **Revocation verdict**
2. **Rights matrix**
3. **Survivor matrix**
4. **Propagation boundary**
5. **Blocked stronger sentence**

## 1) Revocation verdict

Show one verdict:

- `future updates suspended for selected peer`
- `local seat detached from subject`
- `linked-family management removed`
- `local seat unlinked from identity`
- `revocation claim unproved`

The operator must be able to answer: **what future channel was cut, and for whom?**

## 2) Rights matrix

Separate these rights explicitly:

- receive future metadata
- receive future bytes
- publish future mutations
- onward-share or approve
- appear in linked-device family
- reconnect without fresh grant

Each right must show:

- `still allowed`
- `stopped by this action`
- `outside action scope`
- `unknown`

## 3) Survivor matrix

Separate these survivor classes explicitly:

- bytes already present on remote peer
- local placeholders and directory names
- archive/service history
- standing approval memory
- remote independent copies outside linked family

This matrix exists so the operator can see the difference between **future flow cutoff** and **historical survivor residue**.

## 4) Propagation boundary

Show where the action does and does not travel:

- only this seat
- selected remote peer only
- all seats in linked family
- unlinked remote peers excluded
- filesystem bytes out of scope
- remote deletion out of scope unless separately issued

## 5) Blocked stronger sentence

Allowed examples:

- `Selected peer will not receive future updates for this subject.`
- `Local seat is detached, but the subject still exists on other linked seats.`
- `Previously synchronized bytes remain outside the scope of this revocation.`

Blocked examples:

- `No remote copy remains.`
- `Every approval everywhere was revoked.`
- `This subject is gone from the ecosystem.`

## Main actions

Examples:

- `Confirm revocation boundary`
- `Inspect survivor scope`
- `Escalate to destructive removal review`
- `Export revocation proof`
