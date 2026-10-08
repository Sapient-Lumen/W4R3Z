# Remedy-hardening-attestation public-claim contract sheet page — external representation scope, carrier set, and claim ceiling

## Purpose

This page is the operator-facing sheet for deciding whether stale meaning retired only inside the governed audience or also across the outsider-facing representations that still describe the subject to third parties.
It exists to stop `the audience is repaired`, `the link expired`, or `the share was revoked` from being mistaken for `outsiders no longer encounter a stale public claim`.

## Core question

The page must answer:

**for this named public surface and representation carrier set, what is the strongest honest sentence about stale public-claim retirement now?**

## Minimum fields

The contract sheet must show at least:

- action identifier
- source audience-reliance receipt identifier
- public surface identifier
- public surface boundary rule
- canonical correction identifier
- representation carrier class set (`share links`, `landing pages`, `exported files`, `forwarded attachments`, `screenshots`, `quoted summaries`, `embedded copies`, `other`)
- circulation path summary
- withdrawal / supersession / disclaimer carrier set
- intended public-surface coverage class
- current public-surface coverage class
- unresolved stale-public-representation count
- highest-risk unresolved public surface
- strongest honest outsider-facing sentence now
- blocked stronger public-truth sentence now

## Standing ladder

The page must support at least these distinct standings:

- internal audience repaired only
- named public surface under review
- some public representations superseded, others still circulating
- link expired, but already-circulating representations still open
- disclaimer applied without full withdrawal
- named public surface repaired, broader public truth unproven
- later contradiction reopened public-claim risk
- receipt superseded

## Required comparisons

The sheet must compare:

- internal audience truth versus public-claim truth
- future-access revocation versus already-circulating representation retirement
- withdrawal versus disclaimer versus supersession
- named public surface versus broader public reach
- current best sentence versus blocked stronger public-truth sentence

## Required layout

### Header

Show:

- correction name
- public surface name
- current public-claim standing
- strongest honest outsider-facing sentence now

### Left column — intended public-truth contract

Show:

- public surface boundary rule
- representation carrier classes in scope
- circulation path summary
- required withdrawal / supersession / disclaimer carriers
- required coverage threshold

### Center column — observed representation facts

Show:

- active stale link count
- forwarded-copy residue count
- screenshot / quote residue count
- superseded export count
- withdrawn artifact count
- disclaimer coverage status
- evidence freshness for the public surface map

Every row in this column must have:

- current value
- evidence source
- whether it strengthens or weakens public-truth confidence

### Right column — consequence for truth

Show:

- whether only the internal audience is known-clean
- whether named public surfaces were repaired but broader public reach remains open
- whether stale outsider-facing artifacts still circulate
- whether the public-truth sentence is honest or still blocked
- what stronger sentence remains blocked

### Footer decision rail

The footer must make it impossible to flatten these into one answer:

- internal audience repaired only
- some public artifacts superseded
- link expired but public residue remains
- named public surface repaired
- broader public-truth sentence still blocked

## Interaction requirements

The interface must support:

- clicking the public-surface badge to open the exact boundary rule and exclusions
- clicking any public-representation chip to open its carrier, circulation path, age, and retirement status
- pinning one public surface while comparing several coverage thresholds
- filtering the surface map to links, exports, forwards, screenshots, quotes, or embedded copies

## Hard rules

The page must never allow:

- internal audience repair to silently become public-truth repair
- link expiration to silently become retirement of already-circulating artifacts
- one superseded export to silently become full public-surface repair
- a named public surface sentence to silently become broader public truth
