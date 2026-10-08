# Bearer capability review page: approval absence, expiry, usage ceiling, and fanout interface spec

## Purpose

This page answers:

> how open is this artifact really, who can redeem it, what constraints are absent, and what powers does redemption confer?

The page exists because `link`, `key`, and `QR` are carriers, not complete authority statements.

## Core rule

Every offer whose redemption depends partly or wholly on possession must expose one first-class **Bearer capability review**.

That page owns:

- approval absence or presence
- requester-proof ceiling
- expiry authority
- usage-count ceiling or its absence
- onward-fanout rights
- reissue requirement

## Primary layout

The page always renders the same regions:

1. bearer verdict
2. redemption openness card
3. expiry and reissue card
4. fanout and survivor card
5. safe next actions and receipt

### 1) Bearer verdict

Show:

- verdict (`reviewed-gate`, `open-bearer`, `mixed`, `expired`, `unknown`)
- strongest honest operator summary
- strongest blocked summary

Example honest summary:

- `Anyone who possesses this single-file link may redeem it while it remains valid; the sender cannot cap usage count or ban specific devices.`

### 2) Redemption openness card

Show:

- what is sufficient to redeem (`link possession`, `key possession`, `approval plus request`, `unknown`)
- whether requester identity is reviewed before bytes move
- whether remembered approval can narrow future prompts
- whether the artifact allows device-specific bans or usage limits
- whether later redemptions by additional seats remain possible

### 3) Expiry and reissue card

Show:

- current expiry posture (`never`, `date-bound`, `fixed-mobile-default`, `desktop-configurable`, `expired`, `unknown`)
- who may change expiry (`issuer`, `recipient cannot`, `nobody now`, `unknown`)
- whether changed content forces reissue
- whether post-expiry claim requires a fresh artifact

### 4) Fanout and survivor card

Show:

- whether recipients may re-share after receipt
- whether recipients may change expiry or audience
- whether redemption creates a live continuing subject or only landed bytes
- what survives if the originating artifact expires

### 5) Safe next actions and receipt

Show links to:

- acceptance lane review
- landing and residue review
- offer-family lineage receipt

## Required vocabulary

Use these exact distinctions when relevant:

- `approval-gated`
- `approval-free`
- `open bearer`
- `usage ceiling absent`
- `reissue required`
- `landed bytes may survive artifact expiry`

## Blocked language

Never allow statements such as:

- `private link`
- `invite-only`
- `limited to approved devices`
- `one-time send`

unless the product has explicit evidence for those stronger claims.

## Success condition

The operator should be able to answer, before issue or claim:

1. is this artifact open to anyone who possesses it?
2. can the sender limit count or named devices?
3. who can change expiry?
4. does receipt create a live subject or only a landed copy?
5. what survives after expiry?
