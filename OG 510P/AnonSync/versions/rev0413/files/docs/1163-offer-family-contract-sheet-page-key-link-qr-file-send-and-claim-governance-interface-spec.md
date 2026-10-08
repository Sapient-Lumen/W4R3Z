# Offer family contract sheet page: key, link, QR, file-send, and claim-governance interface spec

## Purpose

Before an operator issues a folder share, copies a key, sends a QR, opens a browser link, or generates a single-file transfer link, they need one ordinary page that answers:

> what exact offer family is this, what authority does it carry, what approval model comes with it, and what stronger sentence is still blocked?

This page exists so `Share`, `Copy link`, `Copy key`, and `Send file` never remain magical verbs.

## Core decision

Every serious issuance or intake-affecting action must open one first-class **Offer family contract sheet**.

The sheet owns:

- offer family
- subject class
- approval model
- bearer openness
- expiry authority
- claim-lane options
- landing and residue preview
- strongest safe sentence
- stronger rejected sentence

## Fixed page order

1. offer claim header
2. family and governance card
3. approval and openness card
4. claim-lane card
5. landing and residue preview card
6. claim ceiling and next-safe action rail

### 1) Offer claim header

Show at minimum:

- requested offer family (`advanced-folder-link`, `standard-folder-key`, `folder-qr`, `single-file-link`, `manual-intake-only`, `unknown`)
- subject class (`live folder`, `bounded transfer`, `identity/invite`, `unknown`)
- lane delta (`new offer`, `reissue`, `manual-claim`, `carrier-only change`, `unknown`)
- strongest safe sentence
- stronger rejected sentence
- evidence freshness

Example safe sentence:

- `This action issues a bounded file-transfer link with bearer-style redemption and no usage-count ceiling; it does not create a live shared folder.`

### 2) Family and governance card

Render rows for:

- governance family (`certificate-grant`, `key-capability`, `bounded-transfer-link`, `unknown`)
- mutable-rights class (`owner-editable`, `key-borne`, `not a live grant`, `unknown`)
- subject continuity (`live`, `snapshot-like`, `one-way`, `unknown`)
- carrier family (`link`, `key text`, `QR`, `email template`, `manual paste`, `unknown`)

### 3) Approval and openness card

Separate these truths explicitly:

- approval model (`required`, `required-only-for-new`, `required-for-all`, `none`, `unknown`)
- bearer openness (`named-only`, `open possession`, `reviewed requester`, `unknown`)
- usage ceiling (`unlimited`, `bounded`, `single-use`, `not published`, `unknown`)
- expiry class (`never`, `date-based`, `desktop-configurable`, `mobile-fixed`, `reissue-required`, `unknown`)
- onward-fanout ceiling (`recipient may re-share`, `recipient may not re-share`, `unknown`)

### 4) Claim-lane card

Show:

- intake options (`browser handoff`, `manual paste`, `QR scan`, `web surface manual entry`, `unknown`)
- handoff dependency (`protocol registration`, `browser allowlist`, `none`, `unknown`)
- claim-proof class (`approval needed`, `possession sufficient`, `reviewed seat`, `unknown`)

### 5) Landing and residue preview card

Show:

- landing authority (`choose-at-claim`, `desktop default path`, `mobile fixed inbox`, `config-authored default`, `unknown`)
- collision policy (`suffix`, `replace`, `merge`, `block`, `unknown`)
- residue preview (`ui row may remain`, `bytes may remain`, `ui-only removal`, `byte-and-row removal`, `unknown`)

### 6) Claim ceiling and next-safe action rail

Only show actions that preserve meaning, such as:

- `Open bearer capability review`
- `Open acceptance lane review`
- `Open landing and residue review`
- `Emit offer-family lineage receipt`

## Rules

### Rule 1 — offer family may not collapse into a generic share noun

The page must publish whether this is a live folder grant, approval-capable folder link, approval-free key, or bounded file transfer.

### Rule 2 — approval and openness must stay separate

`requires approval` and `anyone with the link can redeem` must never be blurred together.

### Rule 3 — claim lane must remain explicit

Browser handoff and manual paste must stay separate even when they parse the same artifact.

### Rule 4 — landing preview must remain attached

A user should not have to issue or claim the artifact before learning where bytes likely land and how collisions resolve.
