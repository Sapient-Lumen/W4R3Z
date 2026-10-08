# Restart provenance page: stop source, re-entry trigger, and chronology risk

This page exists so later restart does not pretend to be a neutral continuation.
A sync runtime can re-enter because of startup policy, service supervision, explicit reopen, update workflow, or platform reboot.
That re-entry can matter because indexing and overwrite chronology can change after offline edits.

## Operator question

> Why did this runtime come back, from which authority, and what chronology or evidence risks does this restart create?

## When this page must appear

Render whenever:

- the runtime reappears after the operator believed it was stopped
- startup or service policy is edited
- an update/install flow restarts the runtime
- chronology-sensitive offline edits may now contend with reopened indexing

## Fixed page order

1. **Latest stop event lineage**
2. **Re-entry trigger and authority**
3. **Continuity class**
4. **Chronology / indexing risk**
5. **Next action / receipt promise**

## 1) Latest stop event lineage

Show:

- most recent stop receipt id
- stop scope that was actually reached
- proof rung reached at stop time
- whether future re-entry remained armed even then

The operator must be able to answer: **what stop story preceded this restart?**

## 2) Re-entry trigger and authority

Show:

- restart trigger: `manual-open`, `service-restart`, `boot-startup`, `login-startup`, `update-relaunch`, `task-recovery`, `unknown`
- triggering authority: human, service manager, OS boot item, updater, policy automation, unknown
- whether the restart used the same principal and same parameters as before

The operator must be able to answer: **who or what brought it back?**

## 3) Continuity class

Show:

- continuity verdict: `same-runtime-lineage`, `new-runtime-same-world`, `new-runtime-different-world-risk`, `unknown`
- whether storage-home or principal drift is suspected
- whether the restart should be treated as ordinary continuation or reopen review

The operator must be able to answer: **is this the same operational world or a new one with continuity risk?**

## 4) Chronology / indexing risk

Show:

- whether re-indexing is expected
- whether offline edits existed during the down window
- whether overwrite chronology or conflict order may be affected
- strongest safe sentence: `restart observational only`, `restart may reorder later overwrite claims`, `chronology risk unknown`, `restart created different-world risk`

The operator must be able to answer: **what can this restart still change about later file-fate or evidence claims?**

## 5) Next action / receipt promise

Offer:

- `Accept and continue`
- `Open continuity review`
- `Disable future startup`
- `Re-stop with stronger proof`
- `Inspect contested chronology`

And show what the next receipt will preserve about trigger, authority, continuity class, and chronology risk.

## What this page must never imply

It must never imply that these are the same:

- reopen and neutral continuity
- same binary and same world
- update relaunch and manual restart
- runtime return and unchanged chronology/evidence posture

## Receipt / audit consequence

The resulting receipt should preserve stop lineage, re-entry trigger, supervising authority, continuity class, chronology-risk verdict, and the stronger safe-continuation sentence that remained blocked.
