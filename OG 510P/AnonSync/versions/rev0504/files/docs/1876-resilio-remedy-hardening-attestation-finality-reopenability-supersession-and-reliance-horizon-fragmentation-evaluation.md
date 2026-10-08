# Resilio remedy hardening attestation finality, reopenability, supersession, and reliance-horizon fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for being candid that a seemingly calm present is not the same thing as permanent closure.
That candor matters.

The strongest present ingredients are:

- current `Sync Main View (Desktop)` docs still say History shows only the last 30 days and that offline peers disconnect after 7 days by default, which means visible continuity has a bounded memory horizon
- current `Increasing Debug Log size` docs still say log rotation discards an existing `sync.log.old` on later rotation, which means some support evidence naturally decays unless captured in time
- current `Collecting debug logs automatically` and `Collecting debug logs manually` docs still say useful evidence often requires enabling logging, restarting Sync, reproducing the issue, and waiting at least 15 minutes
- those same current support articles still say direct technical support is available only for Sync Business customers and that direct support is not available for Sync v3, which means some investigations end in community or self-service lanes rather than a first-class adjudication object
- current `Some internal tasks are taking time to complete` docs still say hidden work can continue beneath the surface and may later recover or may require support evidence
- current `Service files missing / Cannot identify destination folder` docs still say a corrupted `.sync` state can suspend synchronization and that repair may require deleting `.sync` and creating a new synchronization instance
- current `Cloning Sync` docs still say cloning an instance is unsupported and may create strange behavior or non-transferring twins
- current `Resilio Sync 3.0 change log` still records blank-UI and other visible-state fixes, which is another reminder that calm presentation is not automatically a final durable ruling

## Where the current contract still fragments

The problem is not that Resilio lacks ingredients for later confidence.
The problem is that it still lacks a first-class, case-scoped **finality and supersession** object.

Today an operator can often infer only weaker truths such as:

- the challenge seemed answered at the time
- the warning is gone now
- the peer list looks calm again
- the current logs no longer show the earlier fault
- the old logs rotated away
- the `.sync` state was rebuilt and things work again
- the support lane, if any, accepted the current explanation
- the UI no longer shows the confusing state that the change log says was later fixed

Those are useful clues.
They are not the same as an explicit answer to `is this adjudicated standing still reopenable, final only for named consumers, final only for this world-line, superseded by a successor receipt, or genuinely non-reopenable enough to rely on as settled precedent?`

## Why that matters for AnonSync

AnonSync needs stronger post-challenge truth than `we ruled and nothing currently looks wrong`.
It needs to support claims such as:

- the challenge was adjudicated, but the ruling is still inside a reopen window
- the ruling is final enough for one downstream consumer class but not for another
- the ruling was final for the predecessor world only, and successor-world repair superseded rather than vindicated it
- the original ruling remains historical, but a later receipt has explicit precedence for future reliance
- the old receipt is frozen, not erased, because later evidence changed the strongest honest sentence
- the case can no longer honestly say `permanently resolved` because the decisive evidence was restart-gated, rotated, or world-changing

AnonSync therefore needs first-class objects for **finality class, reopen triggers, supersession order, reliance audience, and historical-vs-current precedence** rather than leaving operators to reconstruct closure from warnings, calm UI, decaying logs, service-file resets, and support folklore.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `is this ruling final enough to rely on, or only presently uncontradicted?` — only by making the operator combine several partially overlapping operational surfaces:

- short-horizon history and peer visibility
- rotating debug logs and support capture rituals
- hidden-task warnings that admit surface calm may lag truth
- repair articles that can change the observed world by re-add, rebuild, or fresh instance creation
- clone warnings that acknowledge instance identity can fork in unsupported ways
- change-log memory that some visible states previously needed fixes before they were trustworthy enough to lean on

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **remedy-hardening attestation finality** directly.
Its interface family should let the product separate at least these truths:

- adjudicated but reopenable
- final on current record for named consumers only
- final for predecessor world only
- superseded by successor receipt
- historically preserved but no longer current
- non-reopenable for the named claim floor
- reopened after later contradiction
- permanently blocked from `same sentence still stands` language

That is why this revision adds five more first-class pages:
**Remedy-hardening-attestation-finality contract sheet**, **Remedy-hardening-attestation-finality review**, **Remedy-hardening-attestation-finality proof**, **Remedy-hardening-attestation-finality timeline**, and **Remedy-hardening-attestation-finality lineage receipt**.
