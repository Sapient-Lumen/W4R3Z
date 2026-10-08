# Remedy-hardening-attestation survivor-reroute contract sheet page — resurfacing carriers, canonical route, and re-closure budget

## Purpose

This contract sheet exists so the archive can say exactly what a rediscovered stale survivor is supposed to do for the finder.
It should prevent the operator from silently collapsing `we can reopen if it resurfaces` into `the resurfacing artifact itself can route the finder to current truth`.

## Required sections

The page must render the same sections in the same order:

1. **Resurfacing carrier inventory**
2. **Supersession explanation and canonical route**
3. **Re-closure budget and dependency posture**
4. **Strongest honest self-routing sentence**

### 1) Resurfacing carrier inventory

This section must show:

- stale artifact or survivor identifier
- carrier class for rediscovery
- whether the carrier is active, latent, detached, or third-party-held
- whether the carrier can be edited, withdrawn, expired, or only annotated
- audience slices likely to encounter this carrier later

The operator must be able to answer: **what exactly may resurface later, and in what form will a late finder meet it?**

### 2) Supersession explanation and canonical route

This section must show:

- whether the survivor surface can state it is superseded
- what proof class anchors that statement
- canonical reroute target
- whether the reroute target is human-readable, machine-readable, or both
- whether the reroute is embedded, adjacent, or operator-supplied later

The operator must be able to answer: **if someone finds the stale thing later, how do they learn what replaced it and where to go next?**

### 3) Re-closure budget and dependency posture

This section must show:

- whether following the route is enough to restore closure for that finder
- whether the path requires a specific client, account, app handoff, or manual copy/paste ritual
- whether operator approval or support intervention is still required
- maximum honest lag before rediscovery can be re-closed
- which carrier classes can never self-route and therefore always reopen the claim

The operator must be able to answer: **can rediscovery repair itself, or does it still depend on bespoke support?**

### 4) Strongest honest self-routing sentence

This section must preserve two separate sentences:

- strongest honest self-routing sentence now
- blocked stronger self-routing sentence

Examples:

- `rediscovered stale folder can route a linked user to the current replacement but not an outsider with only a detached copy`
- `survivor can explain supersession, but re-closure still requires operator approval`
- `rediscovery reopens the claim; no survivor-carried reroute exists`
- `one stale carrier self-routes; forwarded copies do not`

## Hard rules

The page must never:

- equate rediscovery invalidation with self-routing
- omit the carrier class
- omit required client or manual-step dependencies
- emit `self-routes` without naming how the finder reaches current truth
