# Live capability proof page: online, source-capable, authority-capable, and serve-eligible evidence interface spec

## Purpose

The cohort contract sheet explains what the counts mean.
This proof page exists for the narrower question:

> which current rows can actually do something useful right now?

`Online` is not enough.
A participant may be online yet not be source-capable for the byte you need, may not have mutation authority, or may be a self-derived local branch rather than an independent resilience contributor.

## Proof outputs

The page must separately prove four things:

1. `online_now`
2. `source_capable_now`
3. `serve_eligible_now`
4. `authority_capable_now`

Each claim must be independently evidencable and independently fail.

## Evidence classes

Supported evidence classes must include:

- current transport witness
- current byte-presence witness
- current subject-binding witness
- current seat-posture witness
- self-derived lineage witness
- stale roster only
- unknown

## Fixed proof order

### 1. Candidate row table

For every row under proof, show:

- row handle
- live status
- independent vs self-derived
- source-capable verdict
- serve-eligible verdict
- authority-capable verdict
- evidence freshness
- blocked stronger sentence

### 2. Online proof

Online proof requires:

- current reachability witness
- freshness timestamp
- route witness grade

Online proof does **not** by itself prove byte availability or source usefulness.

### 3. Source-capability proof

Source-capability proof requires:

- byte-presence witness or materialization witness
- subject membership still valid
- no stronger contradictory evidence such as ghost status or detached-only visibility

### 4. Serve-eligibility proof

Serve-eligibility proof requires:

- current reachability witness
- source-capability proof
- seat posture that still allows byte serving
- no current local suspension or equivalent serve block known to the product

### 5. Authority-capability proof

Authority-capability proof requires:

- seat posture proof
- governance / grant proof
- no current detachment or revocation proof overriding it

## Supported verdict vocabulary

For each capability, use:

- `proved`
- `not-proved`
- `contradicted`
- `stale`
- `unknown`

## Example safe sentences

- `Peer amber is online now, but source capability for this subject is not proved.`
- `Peer cedar is source-capable and serve-eligible now, but it is a self-derived local branch and does not add independent remote resilience.`
- `Peer slate remains authority-capable in roster history, but live reachability is stale.`

## Hard rules

- `online` must never imply `source-capable`
- `source-capable` must never imply `authority-capable`
- `serve-eligible` must never imply `independent`
- proof freshness must be shown next to every capability claim
