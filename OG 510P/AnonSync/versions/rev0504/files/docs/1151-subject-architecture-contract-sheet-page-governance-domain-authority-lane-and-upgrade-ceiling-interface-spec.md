# Subject architecture contract sheet page: governance domain, authority lane, and upgrade ceiling interface spec

## Purpose

Before an operator creates a new subject, chooses its architecture family, branches into encrypted backup, or attempts to re-home a subject into a different governance system, they need one ordinary page that answers:

> what governance domain am I choosing, what authority and re-share lane comes with it, what linked-device defaults apply, and what stronger migration or exception sentence is still blocked?

This page exists so `Standard / Advanced / Encrypted` never remains a cosmetic picker.

## Core decision

Every serious architecture-affecting action must open one first-class **Subject architecture contract sheet**.

The sheet owns:

- architecture family
- governance domain
- default authority lane
- re-share lane
- linked-device compatibility / exception class
- config authorship support
- migration ceiling
- strongest safe sentence
- stronger rejected sentence

## Fixed page order

1. architecture claim header
2. governance-domain card
3. authority and re-share card
4. linked-lane and exception card
5. migration / automation ceiling card
6. claim ceiling and next-safe action rail

### 1) Architecture claim header

Show at minimum:

- requested family (`key-domain`, `certificate-domain`, `encrypted-derivative`, `unknown`)
- current family if an existing subject is involved
- architecture delta (`new subject`, `same-family change`, `family migration`, `derivative branch`, `unknown`)
- strongest safe sentence
- stronger rejected sentence
- evidence freshness

Example safe sentence:

- `This choice creates a certificate-governed subject with Owner-based delegation, not a key-governed subject with unrestricted onward re-share.`

### 2) Governance-domain card

Render rows for:

- identity primitive (`key`, `certificate`, `encrypted key derivative`, `unknown`)
- peer-recognition model (`device-level only`, `user-level via certificate`, `encrypted store only`, `unknown`)
- permission-mutation class (`reissue-only`, `owner-mutable`, `hardwired limited`, `unknown`)
- owner concept (`not present`, `present`, `not applicable`, `unknown`)

### 3) Authority and re-share card

Separate these truths explicitly:

- write lane (`ro`, `rw`, `owner-rw`, `encrypted-store`, `unknown`)
- onward re-share lane (`all peers with possessed key`, `owners only`, `encrypted-only further share`, `unknown`)
- permission-change lane (`remove-and-readd`, `on-the-fly allowed`, `not available`, `unknown`)

### 4) Linked-lane and exception card

Show:

- linked-device compatibility (`native lane`, `native with owner-default`, `manual exception required`, `unknown`)
- linked default arrival class (`owner-lane`, `mode-only decision`, `must remain disconnected before manual attach`, `unknown`)
- RO exception path (`native`, `manual Standard-key workaround`, `not meaningful`, `unknown`)

### 5) Migration / automation ceiling card

Show:

- in-place conversion support (`supported`, `remove-and-readd`, `not supported`, `unknown`)
- config / automation support (`supported`, `standard-only`, `unsupported`, `unknown`)
- survivor map class (`app subject preserved`, `bytes survive but subject changes`, `unknown`)

### 6) Claim ceiling and next-safe action rail

Only show actions that preserve meaning, such as:

- `Open governance-domain review`
- `Open authority and re-share review`
- `Open architecture migration watch`
- `Emit subject architecture lineage receipt`

## Rules

### Rule 1 — architecture family may not be reduced to iconography

The page must publish governance consequences, not just a label.

### Rule 2 — write, delegate, and mutate may not collapse into one capability word

The operator must be able to see whether this lane allows edits, onward sharing, and later permission changes independently.

### Rule 3 — linked-device defaults and manual exceptions must stay separate

A manual Standard RO workaround must never masquerade as a native Advanced-linked feature.

### Rule 4 — migration language must stay honest

Blocked examples:

- `we can always upgrade this later`
- `encrypted is basically the same thing but safer`
- `changing family will preserve everything in place`
