# Remedy-hardening-attestation-freshness review page — is the sealed verifier bundle still current enough to trust?

## Purpose

This page is the operator's decision surface for answering whether a case that already has a sealed verifier bundle may honestly claim freshness-aware verifier trust.
It exists so later readers can review time horizon, revalidation, and identity continuity directly rather than reconstructing them from short history, rotating logs, fingerprints, and restart-driven support flows.

## Review question

The page must ask:

`Could a skeptical verifier rely on this sealed bundle as a live sentence now, rather than only as a historical sentence, after checking freshness horizon, identity continuity, approval carry-forward, cache-sensitive facts, and current revalidation evidence?`

## Required review panes

### 1. As-of and horizon pane

Show:

- seal identifier
- historical capture completion time
- current as-of claim time
- freshness horizon
- freshness budget remaining
- strongest blocked stronger sentence caused by horizon weakness

### 2. Identity and approval pane

Show:

- identity fingerprint basis status
- whether identity was recreated, unlinked, or relinked after sealing
- linked-device approval carry-forward status
- required currentness cohort
- strongest blocked stronger sentence caused by identity or approval weakness

### 3. Evidence-horizon pane

Show:

- history horizon coverage status
- debug-log horizon coverage status
- whether important evidence would now require restart-driven recapture
- whether rotated or discarded evidence changed the claim ceiling
- strongest blocked stronger sentence caused by evidence-horizon weakness

### 4. Revalidation pane

Show:

- revalidation required flag
- last revalidation time
- last revalidation actor or lane
- peer cache or routing cache status
- revocation or identity challenge status
- highest honest current freshness-aware sentence
- strongest blocked stronger freshness-aware sentence

## Required review outcomes

The page must support outcomes such as:

- `sealed historical proof only`
- `sealed and still current for named lanes only`
- `revalidation overdue, stronger live sentence blocked`
- `identity or approval continuity challenged`
- `freshness-aware verifier readiness now holds for the required cohort`

## Review discipline

The review must forbid these shortcuts:

- seal standing equals freshness standing
- old fingerprint match equals current identity continuity
- remembered approval equals current approval legitimacy
- short history equals currentness proof
- existing logs equals live verifier trust
- no visible contradiction equals no freshness decay
- restart/recapture possibility equals current proof already present
