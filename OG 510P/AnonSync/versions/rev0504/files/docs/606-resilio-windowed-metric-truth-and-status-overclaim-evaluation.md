# Resilio windowed-metric truth and status-overclaim evaluation

## What current official docs still make clear

Another current Resilio pass again strengthens the main archive conclusion rather than weakening it.

Current official docs still show real product substance:

- the desktop main view still says a green check means files are synced with all **connected** peers
- the same page still says `X of Y peers` means `X` online now and `Y` total peers, including offline peers
- the same page still says an offline peer is disconnected from the folder after 7 days by default and that the threshold is configurable
- the still-official functionality overview still says mobile folder details show size, file count, and `last synced date`
- the still-official historical change log still says the optional `Last transferred` column means the last time files were changed in a folder
- that same still-official change log still records a fix where the `Date synced` column was not empty when peers went offline
- the same change log still records peer-list accuracy and receiving-performance-stat accuracy fixes
- the current v3 line still appears active through `3.1.2.1076`

That is useful candor.
Resilio is not pretending one row proves everything.
The problem is that the operator still has to reconstruct **which window each row is speaking about**.

## What still should not be cloned

The ordinary operator question is simple:

> what does this row actually prove right now?

Current official docs still leave that answer spread across desktop UI docs, mobile overview docs, and older-but-still-official change-log notes.
That means one row can quietly combine several different windows:

- `connected now`
- `ever connected`
- `last files changed`
- `last synced date`
- `historical activity window`
- `configured aging threshold`

Those are all real and useful windows.
They just should not remain implicit.

The current clone-veto sentence for this seam is therefore:

> borrow Resilio's candor that counters and timestamps speak about materially different windows; refuse any interface contract where the operator still has to infer those windows from several articles before trusting a row.

## Why this matters for AnonSync

AnonSync should borrow four habits directly:

- say which metric family a row belongs to
- say which time window it speaks about
- say what subject scope it covers
- say what stronger sentence the row does **not** earn

But AnonSync should refuse four weaker habits:

- generic `synced` chips that silently mean `with connected peers only`
- peer counts that look like quorum without publishing live-vs-historical split
- timestamps that mix `changed`, `landed`, and `seen` without explicit labels
- status rows that require change-log archaeology to know their claim ceiling

## Replacement pages added for this seam

This revision therefore adds four narrower replacement pages:

- `607` — Windowed metric
- `608` — Metric interpretation review
- `609` — Status row proof
- `610` — Metric receipt

These pages keep the Resilio candor and reject the mixed-window row contract.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor that `online now`, `ever connected`, `last synced`, and `last files changed` are different windows; refuse any interface contract where one row can look like present-tense proof without publishing its window and claim ceiling.
