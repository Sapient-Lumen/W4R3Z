# Acceptance lane review page: browser handoff, manual paste, QR, and WebUI fallback interface spec

## Purpose

This page answers:

> how exactly is this artifact entering the product, what can fail in that lane, and what fallback preserves meaning without hiding the same artifact behind a different verb?

The page exists because `open link`, `scan QR`, and `Enter a key or link` are not the same contract.

## Core rule

Every offer claim must expose one first-class **Acceptance lane review** before commit.

That page owns:

- intake lane
- handoff dependency
- failure reason
- typed fallback
- whether the fallback changes only carrier or also governance

## Primary layout

The page always renders the same regions:

1. lane verdict
2. intake-path card
3. handoff-health card
4. fallback card
5. next-safe action and receipt

### 1) Lane verdict

Show:

- verdict (`browser-handoff`, `manual-paste`, `qr-scan`, `webui-manual-entry`, `unknown`)
- strongest honest sentence
- stronger rejected sentence

Example honest sentence:

- `This artifact is being claimed through manual paste because browser or WebUI handoff is not the governing lane here.`

### 2) Intake-path card

Show:

- carrier seen by the user (`clicked link`, `copied text`, `qr code`, `email template`, `unknown`)
- parsing surface (`desktop app`, `web surface`, `mobile app`, `unknown`)
- whether the lane itself is authoritative or just an accelerator
- whether the lane can choose destination during claim

### 3) Handoff-health card

Show one explicit state:

- `automatic handoff succeeded`
- `browser blocked scheme`
- `protocol registration missing`
- `web surface cannot consume direct link`
- `manual paste chosen intentionally`
- `artifact malformed or unsupported`

### 4) Fallback card

The fallback lane must always preserve:

- typed artifact inspection
- same family verdict if only the carrier changed
- visibility into whether destination choice becomes available now
- a warning when WebUI or browser behavior narrows claim convenience without changing artifact meaning

### 5) Next-safe action and receipt

Show links to:

- bearer capability review
- landing and residue review
- offer-family lineage receipt

## Rules

### Rule 1 — handoff failure may not masquerade as artifact invalidity

The product must say whether the artifact is bad or whether the lane is bad.

### Rule 2 — WebUI fallback stays explicit

If direct click-open does not work in WebUI, the review must state that manual `Enter a key or link` is the supported lane.

### Rule 3 — carrier change is not automatically governance change

A copied link and a clicked link may represent the same artifact even when the lane health differs.

### Rule 4 — QR is not a decorative skin

If QR materially changes which surfaces can claim the artifact, keep that visible.
