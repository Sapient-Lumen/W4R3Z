# Remedy-hardening-attestation discoverability contract sheet page — canonical replacement surface, late-arrival routing, and resurfacing ceiling

## Purpose

This page is the operator-facing sheet for deciding whether a later outsider who rediscovers stale material will land on the corrected replacement or fall back into stale residue.
It exists to stop `we withdrew the old thing`, `the corrected thing exists`, or `we can still find it locally` from being mistaken for `late rediscovery is now safe`.

## Core question

The page must answer:

**for this named rediscovery surface map, what is the strongest honest sentence about whether latecomers will find the corrected replacement rather than the stale thing?**

## Minimum fields

The contract sheet must show at least:

- action identifier
- source public-claim receipt identifier
- rediscovery surface identifier
- rediscovery surface boundary rule
- canonical correction identifier
- canonical replacement pointer class (`redirect`, `supersession banner`, `replacement landing page`, `signed replacement receipt`, `manual explanation only`, `none`)
- in-scope rediscovery surfaces (`old links`, `landing pages`, `search surfaces`, `forwarded artifacts`, `screenshots`, `embedded references`, `quoted fragments`, `other`)
- late-arrival route quality
- intended replacement coverage threshold
- current replacement coverage threshold
- unresolved resurfacing channel count
- highest-risk resurfacing channel
- strongest honest replacement-findability sentence now
- blocked stronger rediscovery-safe sentence now

## Standing ladder

The page must support at least these distinct standings:

- stale artifact retired only
- corrected replacement exists but rediscovery route unproven
- some surfaces route to replacement, others still surface stale residue
- redirect or pointer exists for one surface only
- late-arrival route still needs operator context
- named rediscovery surfaces now prefer corrected replacement
- broader rediscovery safety still blocked
- later contradiction reopened resurfacing risk
- receipt superseded

## Required comparisons

The sheet must compare:

- public-claim repair versus discoverability replacement
- stale artifact withdrawal versus canonical replacement routing
- operator-local findability versus outsider late-arrival findability
- surface-specific replacement success versus broader rediscovery safety
- current best sentence versus blocked stronger rediscovery-safe sentence

## Required layout

### Header

Show:

- correction name
- rediscovery surface-map name
- current discoverability standing
- strongest honest replacement-findability sentence now

### Left column — intended replacement contract

Show:

- rediscovery surface boundary rule
- in-scope resurfacing channels
- required canonical replacement pointer class
- required late-arrival route quality
- required replacement coverage threshold

### Center column — observed resurfacing facts

Show:

- old-link route status
- landing-page replacement status
- search-surface replacement status
- forwarded-artifact pointer status
- screenshot / quote disclaimer status
- embedded-reference update status
- evidence freshness for rediscovery map

Every row in this column must have:

- current value
- evidence source
- whether it strengthens or weakens rediscovery safety

### Right column — consequence for truth

Show:

- whether only artifact retirement is proven
- whether replacement exists without safe rediscovery
- whether named surfaces now route to the corrected replacement
- whether broader resurfacing safety is still blocked
- what stronger sentence remains blocked

### Footer decision rail

The footer must make it impossible to flatten these into one answer:

- stale artifact retired only
- corrected replacement exists only
- some surfaces route correctly
- named rediscovery map is replacement-safe
- broader rediscovery-safe sentence still blocked

## Interaction requirements

The interface must support:

- clicking any rediscovery-surface chip to open route quality, pointer class, evidence age, and exclusions
- pinning one surface while comparing several replacement thresholds
- filtering the surface map to links, landing pages, search surfaces, forwards, screenshots, quotes, or embedded references
- opening the blocked stronger sentence and seeing exactly which unresolved resurfacing channels keep it blocked

## Hard rules

The page must never allow:

- public-claim retirement to silently become discoverability replacement
- local operator findability to silently become outsider findability
- one redirect to silently become full resurfacing safety
- a named-surface result to silently become broader rediscovery safety
