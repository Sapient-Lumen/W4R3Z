# Remedy-hardening-attestation downstream audience reliance contract sheet page — audience scope, dependency graph, and retirement ceiling

## Purpose

This page is the operator-facing sheet for deciding whether stale dependence retired only for one beneficiary or across the governed audience that consumes derived outputs, exports, caches, delegated copies, or neighboring automations.
It exists to stop `beneficiary stayed switched`, `peer disconnected`, or `one dependent refreshed` from being mistaken for `the governed audience stopped relying on stale state`.

## Core question

The page must answer:

**for this governed audience and stale-artifact class set, what is the strongest honest sentence about downstream stale-dependency retirement now?**

## Minimum fields

The contract sheet must show at least:

- action identifier
- source beneficiary-adherence receipt identifier
- governed audience identifier
- governed slice identifier
- canonical correction identifier
- audience boundary rule
- dependency graph summary
- stale-artifact class set (`forwarded files`, `exports`, `derived reports`, `local derivatives`, `delegated peers`, `caches`, `neighboring automations`, `other`)
- retirement carrier set
- intended coverage class
- current retirement coverage class
- unresolved stale-dependency count
- highest-risk unresolved downstream node
- strongest honest reliance sentence now
- blocked stronger audience-wide sentence now

## Standing ladder

The page must support at least these distinct standings:

- beneficiary-local repair only
- narrow downstream repair, audience-wide reliance unproven
- most direct dependents refreshed, delegated residue still open
- stale exports or caches still active
- future updates revoked, landed stale copies still live
- audience-wide stale-dependency retirement proven for named boundary only
- later contradiction reopened downstream reliance risk
- receipt superseded

## Required comparisons

The sheet must compare:

- beneficiary-local adherence versus downstream audience reliance
- future-access revocation versus stale-copy retirement
- refreshed direct dependents versus refreshed transitive dependents
- named audience boundary versus broader public reach
- current best sentence versus blocked stronger audience-wide sentence

## Required layout

### Header

Show:

- correction name
- governed audience name
- current reliance standing
- strongest honest reliance sentence now

### Left column — intended downstream retirement contract

Show:

- governed slice
- audience boundary rule
- dependency graph summary
- stale-artifact classes in scope
- retirement carrier set
- required coverage threshold

### Center column — observed downstream retirement facts

Show:

- refreshed dependents count
- unresolved stale dependents count
- active stale export count
- cache-expiry status
- delegate-repair status
- local-derivative residue
- evidence freshness for the audience graph

Every row in this column must have:

- current value
- evidence source
- whether it strengthens or weakens audience-wide reliance confidence

### Right column — consequence for truth

Show:

- whether only the beneficiary is known-clean
- whether direct dependents are repaired but transitive dependents remain uncertain
- whether stale copies remain active downstream
- whether the audience-wide sentence is honest or still blocked
- what stronger sentence remains blocked

### Footer decision rail

The footer must make it impossible to flatten these into one answer:

- beneficiary repaired only
- narrow downstream repair
- future access revoked but stale copies remain
- audience-wide stale-dependency retirement proven
- broader public-representation sentence still blocked

## Interaction requirements

The interface must support:

- clicking the audience badge to open the exact boundary rule and exclusions
- clicking any stale-dependency chip to open its node, carrier, age, and retirement status
- pinning one audience while comparing several coverage thresholds
- filtering the graph to direct, transitive, delegated, or local-only dependents

## Hard rules

The page must never allow:

- one beneficiary's adherence to silently become audience-wide retirement
- `peer disconnected` to silently become `stale copies retired`
- one refreshed dependent to silently become transitive coverage
- an internal audience sentence to silently become a public-truth sentence
