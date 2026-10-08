# Remedy-hardening-attestation surface-claim timeline page — publication, downgrade, recall, and supersession events

## Purpose

This page is the chronological spine for how case statements became visible on different surfaces and how later downgrades, supersessions, or recall actions changed what those surfaces were allowed to say.
It exists to preserve the difference between publishing a sentence, exporting a sentence, superseding a sentence, and proving that stale stronger wording is no longer authoritative.

## Event classes

The timeline must support at least these event classes:

- sentence template approved
- surface publication enabled
- audience budget widened
- audience budget narrowed
- qualifier added
- blocked phrase added
- notification emitted
- export artifact generated
- clipboard or relay artifact created
- outward quote detected
- governing receipt strengthened
- governing receipt downgraded
- supersession banner attached
- stale artifact watermarked historical-only
- stale artifact recall requested
- stale artifact recall confirmed
- export freeze opened
- export freeze lifted
- public sentence floor changed

## Required timeline columns

Every event row must print at least:

- event timestamp
- actor or subsystem
- event class
- affected surface or artifact
- affected audience class
- prior sentence budget class
- resulting sentence budget class
- evidence attached
- whether the event widened publication, narrowed publication, or only changed historical treatment

## Required chronology guarantees

The timeline must preserve:

- whether a stronger sentence was ever public before a downgrade
- whether copied or exported artifacts existed before qualifiers were added
- whether recall happened before or after supersession
- whether a surface stayed live while its budget had already narrowed elsewhere
- whether the current public floor became speakable only after a later receipt
- whether older artifacts remained quoteable after they ceased to be authoritative

## Required timeline summaries

The page must compute and print:

- first time any audience-facing sentence was published
- first time an outward export or relay artifact existed
- latest time a broader sentence remained visible anywhere
- first time the current strongest public sentence became speakable
- latest time stale stronger wording was still unrecalled

## Blocking rules

The timeline must never flatten:

- internal receipt issuance into public publication
- export generation into persistent authority
- supersession into stale-artifact recall completion
- watermarking into deletion
- a narrower replacement sentence into proof that nobody saw the older stronger sentence
- current safety into historical harmlessness
