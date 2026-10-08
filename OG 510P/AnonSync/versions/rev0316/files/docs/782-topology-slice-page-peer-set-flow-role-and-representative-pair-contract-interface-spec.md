# Topology slice page — peer set, flow role, and representative-pair contract interface spec

## Purpose

The archive already had measurement planning and peer connection attribution.
What it still lacked was one fixed page for another ordinary question:

> before we treat one pair, one chart row, or one benchmark as meaningful, what exact topology slice does this evidence cover?

A topology slice is not just a list of peers.
It is the reviewed boundary of who is in-scope for the current claim.
AnonSync should therefore model it as a first-class **topology slice page** before any pairwise measurement is promoted into wider language.

## Core decision

Every serious performance or connectivity claim must preserve five truths before generalization:

1. covered peers
2. covered directions
3. covered workload / subject scope
4. excluded peers or routes
5. why this slice might or might not be representative

## Fixed review order

1. **Incident scope and subject**
2. **Covered peer set**
3. **Flow-role map**
4. **Direction and route coverage**
5. **Representative-pair hypothesis**
6. **Known exclusions**

## 1) Incident scope and subject

Show:

- share / subject / workload under discussion
- observation or run window
- whether the question is speed, directness, asymmetry, or network ceiling
- whether the slice is live-observation, benchmark, or mixed-evidence

The operator must be able to answer:

> what incident does this slice belong to?

## 2) Covered peer set

List all peers currently treated as in-scope and classify each as:

- `measured directly`
- `observed live only`
- `inferred similar`
- `required but missing`
- `explicitly out of scope`

The page must never let `visible in share` quietly become `covered by evidence`.

## 3) Flow-role map

For each in-scope peer show its current or expected role, for example:

- dominant uploader
- dominant downloader
- alternate source
- receiver only
- relay/fallback participant
- suspected counterexample seat

This lets the operator see whether a measured pair actually touches the flow role that matters.

## 4) Direction and route coverage

Publish:

- forward direction covered or not
- reverse direction covered or not
- direct versus relayed route class covered or not
- LAN versus WAN class covered or not
- whether helper policy differs across peers or folders

A pairwise measurement must never read as complete if it only covers one direction or one route class while the incident spans more.

## 5) Representative-pair hypothesis

The page must force one explicit claim class:

- `illustrative pair only`
- `likely representative pair`
- `representative for one route segment`
- `representative for one uploader cohort`
- `not representative enough for generalization`

Also show the basis, such as:

- peers share same route class
- peers share same uploader role
- peers share same hardware/network class
- no evidence of stronger alternate sources
- or none of the above

## 6) Known exclusions

Show which peers, directions, or path classes remain outside the slice and why:

- not measured yet
- different route class
- different hardware/network envelope
- different uploader role
- missing witness / unavailable peer
- changed topology since original symptom

## Compact rendering obligations

Any compact card for a candidate representative pair must still preserve:

- subject scope
- covered pair or cohort
- uncovered peers count
- representative-pair verdict
- strongest safe sentence

## Anti-clone rule

Do not clone workflows that show a peer table row or finished benchmark without first publishing whether that row covers one pair, one cohort, or the whole incident.

## Receipt consequence

Every later measurement receipt must link back to the exact topology slice version used when the claim was made.
