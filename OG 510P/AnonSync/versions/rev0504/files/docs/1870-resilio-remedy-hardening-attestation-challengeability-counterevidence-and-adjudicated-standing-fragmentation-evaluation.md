# Resilio remedy hardening attestation challengeability, counterevidence, and adjudicated-standing fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials are still admirably candid that a calm visible state is not the same thing as a closed challenge.
That candor matters.

The strongest present ingredients are:

- current `My files don't sync` docs still tell the operator to inspect Status warnings, History, peers queues, file availability, IgnoreList sameness, read-only overwrite posture, permissions, and path or encoding limits rather than trust one friendly row
- current `Errors and warnings` docs still keep many distinct fault families separate instead of pretending all breakdowns mean the same thing
- current `Database error` docs still say restart, reconnect, or full re-add may each be the operative repair lane depending on scope
- current `Time difference` docs still publish that invalid clocks can directly block trustworthy transfer state
- current `Service files missing / Cannot identify destination folder` docs still say synchronization can be suspended, two instances can corrupt internal files, and a new sync instance may need to be created
- current `Some internal tasks are taking time to complete` docs still say hidden work may continue beneath the surface and can require support plus debug logs when recovery does not arrive in time
- current `Collecting debug logs automatically` docs still say meaningful support evidence often requires enabling logging, restarting Sync, reproducing the issue, and waiting at least 15 minutes
- current `Resilio Sync 3.0 change log` still records UI and WebUI fixes, including previously blank or non-clickable states, which is another reminder that one visible plane can mislead

## Where the current contract still fragments

The problem is not that Resilio lacks challenge ingredients.
The problem is that it still lacks a first-class, case-scoped **attestation challenge** object.

Today an operator can often infer only weaker truths such as:

- the UI looked calm before the objection arrived
- the warning family seems plausible
- the local database may be the only thing broken
- the clocks were wrong so the transfer claim should probably be lowered
- the `.sync` service files may have been damaged so the prior sentence is no longer trustworthy
- logs were collected later and seem to support one branch
- a re-add or reconnect probably fixed the issue

Those are useful clues.
They are not the same as an explicit answer to `did the strongest sealed, current, corroborated sentence survive this typed challenge, which witnesses outranked the others, what narrower sentence still survives, and what must be re-proved before the stronger claim may return?`

## Why that matters for AnonSync

AnonSync needs to support stronger post-corroboration claims than `the current sealed bundle still looks corroborated`.
It needs to support claims such as:

- the strongest sentence is now challenge-open and frozen even though prior corroboration still exists
- the challenge only defeats one witness family, so a narrower sentence still survives
- the challenge overturned the storage-world continuity basis, so the prior seal must not keep speaking for the same world
- the challenge was answered by decisive counterevidence, so the stronger sentence can be re-issued with the loser witnesses scarred
- the challenge triggered rework or reseal, so old corroboration remains historical only

AnonSync therefore needs a first-class object for **challenged sentence preservation, typed counterevidence, witness priority, provisional freeze, adjudicated ruling, and reseal requirements** rather than merely borrowing scattered warnings, troubleshooting pages, queues, support-log rituals, and change-log memory.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `does this strong attestation sentence survive the challenge now in front of us?` — only by making the operator combine several partially overlapping operational surfaces:

- troubleshooting steps that hop from warnings to History to peers to file-specific explanations
- a catalog of warning articles that names many fault families without one case-owned ruling object
- repair articles that branch among restart, reconnect, re-add, or fresh instance creation
- hidden-work warnings that admit surface calm may lag reality
- restart-gated debug capture and support workflows
- change-log memory that some visible states previously needed fixes before they were trustworthy enough to lean on

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **remedy-hardening attestation challengeability** directly.
Its interface family should let the product separate at least these truths:

- challenged sentence preserved but frozen
- weaker sentence still survives during review
- challenge defeats freshness only
- challenge defeats integrity or world continuity
- support-only counterevidence captured but not yet adjudicated
- challenge rejected and stronger sentence restored
- challenge upheld and sentence narrowed
- challenge upheld and prior standing overturned pending rework or reseal

That is why this revision adds five more first-class pages:
**Remedy-hardening-attestation-challenge contract sheet**, **Remedy-hardening-attestation-challenge review**, **Remedy-hardening-attestation-challenge proof**, **Remedy-hardening-attestation-challenge timeline**, and **Remedy-hardening-attestation-challenge lineage receipt**.
