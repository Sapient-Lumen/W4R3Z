# Network subject admission page: permission, locking, and service identity review interface spec

## Purpose

This page answers:

> should this remote or service-mounted path be admitted as a sync subject at all, under which runtime identity, with what lock/permission assumptions, and with what explicit receipt if we proceed?

The page exists because `folder selectable` is not the same thing as `fit for honest subject admission`.

## Core rule

Every non-local or service-sensitive path must compile to one first-class **Network subject admission** page before the product creates or reconnects a subject against it.
That page owns:

- permission fitness
- lock / daemon caveats
- runtime identity consequences
- admit / reject decision
- admission receipt

## Primary layout

The page always renders the same regions:

1. admission verdict
2. permission fitness card
3. locking and daemon card
4. runtime identity card
5. admission receipt and follow-on links

### 1) Admission verdict

Show:

- verdict label: `admit`, `admit-with-caveats`, `reject-for-now`, `reject`, `unknown`
- strongest honest one-line summary
- path class in scope
- one safest next action

### 2) Permission fitness card

Show:

- effective runtime account
- read / write / create / delete checks
- strongest missing permission if any
- whether the path is only reachable through a workaround such as UNC typing under service
- strongest non-effect if admission is rejected

The operator must be able to answer: **does the actual runtime have the authority required to keep this subject healthy?**

### 3) Locking and daemon card

Show:

- protocol or daemon class if known
- lock semantics confidence (`ordinary`, `fragile`, `implementation-dependent`, `unknown`)
- strongest risk of stranded or crashed locks
- whether mixed protocol access increases corruption/rollback risk

The operator must be able to answer: **what lock or daemon behavior could invalidate this subject later?**

### 4) Runtime identity card

Show:

- current runtime identity
- any candidate identity change such as Local System
- storage-root migration consequences
- whether re-add / re-share / reconnect work would follow
- strongest reason not to switch identities casually

The operator must be able to answer: **what else changes if we admit this path by changing who runs Sync?**

### 5) Admission receipt and follow-on links

Link to:

- Network path class
- Protocol discipline
- Detection grade

After any accepted action, emit a receipt that preserves:

- path admitted or rejected
- runtime identity used
- permission verdicts
- lock/daemon caveat acknowledged
- required follow-up checks

## Honest outputs

This page may conclude:

- `reject for now · service lacks write access to target namespace`
- `admit with caveats · UNC workaround required and detection grade is rescan-only`
- `reject · mixed direct-plus-Samba mutation makes the namespace unfit`
- `admit · local or well-behaved mounted path with proven permissions and acceptable watcher grade`

It may not collapse these into one generic `Path added` or `Permission denied` outcome.

## Rules

### Rule 1 — admission must be runtime-specific

A path is not admissible in the abstract.
It is admissible or not for the actual process identity touching it.

### Rule 2 — lock uncertainty is part of fitness

Implementation-dependent lock behavior belongs on the admission page, not only in post-failure troubleshooting.

### Rule 3 — workaround admission needs explicit receipts

If admission depends on typing a UNC path manually, switching to Local System, or re-adding shares after state-root relocation, the receipt must preserve that sequence and consequence.

### Rule 4 — rejection can still be a truthful success

If the product determines a remote path is not fit for honest admission, `reject` is the right outcome.
Do not coerce a successful bind anyway.

## Event language

Use explicit phrases such as:

- `subject admission rejected because effective runtime lacks durable write authority`
- `admitted under caveat: UNC path workaround drops live notifications`
- `identity switch would relocate state root and require subject rebuild`
- `path not fit for admission while mixed mutation lanes remain`

Avoid vague lines such as:

- `some folders cannot sync`
- `path issue`
- `try another location`

## Non-clone reason

Current official Resilio docs are usefully candid that service identity, UNC workarounds, permissions, and daemon-specific lock behavior all shape whether a network path is viable.
But the operator still sees that truth mostly as troubleshooting after failure.
AnonSync should instead expose one Network subject admission page where permission fitness, lock caveats, identity consequences, and admit/reject verdict stay adjacent.
