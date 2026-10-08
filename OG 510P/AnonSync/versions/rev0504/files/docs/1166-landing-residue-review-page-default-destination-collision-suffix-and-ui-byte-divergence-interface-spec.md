# Landing and residue review page: default destination, collision suffix, and UI-byte divergence interface spec

## Purpose

This page answers:

> where will received bytes land on this surface, what exact name will appear if something already exists there, and what remains if the operator clears rows or files later?

The page exists because `Download`, `Receive`, and `remove from list` do not by themselves describe landing or survivor truth.

## Core rule

Every receive or receive-default mutation for offer families must expose one first-class **Landing and residue review**.

That page owns:

- destination authority
- default-root source
- collision policy
- landed-name preview
- ui-row vs local-byte divergence
- survivor boundary after cleanup

## Primary layout

The page always renders the same regions:

1. landing verdict
2. destination-authority card
3. collision-result card
4. residue-divergence card
5. next-safe action and receipt

### 1) Landing verdict

Show:

- verdict (`user-chooses-target`, `desktop-default-download`, `android-fixed-syncdownloads`, `ios-downloads-surface`, `config-authored-default`, `unknown`)
- strongest honest operator summary
- stronger rejected summary

### 2) Destination-authority card

Show:

- whether the operator can choose location now
- default path source (`desktop preferences`, `config files_default_path`, `android fixed inbox`, `unknown`)
- whether the lane is path-fixed on this surface
- whether another lane would allow different destination authorship

### 3) Collision-result card

Show:

- whether same-name items already exist
- exact rule (`suffix-(1)`, `replace`, `merge`, `block`, `unknown`)
- resulting landed basename
- whether the operator must review before continuing

### 4) Residue-divergence card

Show separately:

- transfer-row survivor (`history stays`, `row removable only`, `row tracks file presence`, `unknown`)
- byte survivor (`bytes remain`, `bytes removed with ui action`, `device removal leaves ui residue`, `unknown`)
- post-expiry survivor (`artifact gone but landed bytes remain`, `unknown`)

### 5) Next-safe action and receipt

Show links to:

- offer family contract sheet
- offer-family lineage receipt

## Required distinctions

Keep these differences explicit whenever relevant:

- `defaulted location`
- `chosen location`
- `fixed inbox`
- `collision suffix`
- `ui-only removal`
- `byte-only removal`
- `history survives local delete`

## Success condition

The operator should be able to answer before claim or cleanup:

1. who chose this landing path?
2. what exact basename will appear here?
3. if a same-name file exists, what exact suffix or other rule applies?
4. does removing the row remove the bytes?
5. does deleting the bytes remove the row?
