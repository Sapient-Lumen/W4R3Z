# Cleanup intent review page: local reclaim, detach, uninstall, and preserve-first interface spec

## Purpose

This page answers one ordinary operator question:

> I want to clean something up — free space, disconnect, remove, prune hidden residue, or uninstall — but what kind of cleanup is this really, what evidence is at risk, and should I preserve anything first?

The page exists because `clear`, `remove`, `disconnect`, `cleanup`, and `uninstall` are not honest enough by themselves.
A serious sync product must classify cleanup intent before apply.

## Core decision

Every consequential cleanup action must compile to one first-class **Cleanup intent review** page.
That page owns:

- requested cleanup family
- scope of byte/path/presence change
- witness classes currently at risk
- preserve-first recommendations
- strongest honest sentence after apply
- stronger claims that remain unsupported

The operator must not have to infer cleanup meaning from menu location, platform shape, or support folklore.

## Primary page layout

The page always renders the same regions in the same order:

1. action strip
2. cleanup-family card
3. scope and non-effects matrix
4. witness-at-risk card
5. preserve-first choices card
6. post-cleanup language card
7. apply recommendation and receipt target
8. recent cleanup receipts
9. expert details drawer

### 1) Action strip

Show:

- subject / seat / path or app target
- requested cleanup phrase
- classified cleanup family
- strongest current risk verdict (`safe-local-reclaim`, `preserve-first-recommended`, `evidence-narrowing`, `presence-severing`, `platform-loss`, `unknown`)
- safest next action

The strip should answer `what kind of cleanup is this really?`

### 2) Cleanup-family card

Show exactly one primary family:

- `evict-local-bytes`
- `drop-placeholder-view`
- `disconnect-local-bind`
- `remove-linked-presence`
- `prune-hidden-witness`
- `remove-app-keep-data`
- `remove-app-with-local-platform-loss`
- `full-local-clearance`
- `unknown-mixed-intent`

Also show:

- why this family was chosen
- nearby families that looked similar but are not the same
- whether the action is reversible, conditionally reversible, or not honestly reversible

### 3) Scope and non-effects matrix

Rows should cover:

- local materialized bytes
- placeholders / namespace visibility
- local filesystem path or sandbox presence
- linked-device row / share visibility
- non-linked remote retainers
- hidden archive or service-state residue
- event/history witness
- ordinary shared folders outside app state

For each row show:

- `after apply` posture
- whether it weakens, preserves, or does not affect later evidence
- one explicit non-effect sentence

### 4) Witness-at-risk card

Show the witness families currently at risk:

- prior-version bytes
- delete history / chronology witness
- placeholder discoverability
- hidden archive residue
- service logs / config roots
- external peer witness only

For each one show:

- current location
- current reachability
- whether cleanup narrows, removes, or leaves it unchanged
- urgency (`preserve now`, `safe for now`, `already absent`, `unknown`)

### 5) Preserve-first choices card

If any meaningful witness is at risk, the page must show preserve-first actions such as:

- `Export witness now`
- `Pin archive / extend retention`
- `Move recovery locus to another seat`
- `Leave cleanup local-only`
- `Proceed without preservation`

The product must present one strongest recommended preserve-first action when evidence would otherwise narrow silently.

### 6) Post-cleanup language card

Show three lines together:

- requested phrase
- strongest approved phrase after apply
- stronger forbidden phrase

Examples:

- requested: `remove this`
- approved: `local copies evicted; placeholder view preserved`
- forbidden: `deleted everywhere`

Or:

- requested: `uninstall and clear it`
- approved: `app removed; shared folders remained; hidden witness cleanup required separately`
- forbidden: `all sync residue erased`

### 7) Apply recommendation and receipt target

Show exactly one recommendation:

- `apply now`
- `preserve first`
- `switch to different cleanup family`
- `stop; evidence too fragile`
- `blocked by unknown witness state`

Also show the cleanup receipt page that will prove the final outcome.

## Non-negotiable rules

### Rule 1 — cleanup family must be singular before apply

If the product cannot classify the action, it must surface `unknown-mixed-intent` rather than pretending the cleanup is ordinary.

### Rule 2 — evidence risk and byte scope must stay adjacent

Never show freed bytes or reduced presence without the witness-at-risk card beside it.

### Rule 3 — preservation is part of cleanup truth

If evidence is worth preserving, preservation choices must be offered before apply, not only afterward as regret management.

### Rule 4 — uninstall may not imply residue erasure

Program removal, local byte loss, linked-row disappearance, and hidden-residue cleanup must stay separate claims.

## Honest outputs

The page may conclude:

- `This is local-byte eviction only; placeholders and later fetch remain.`
- `This is linked presence removal, not remote recall; external retainers may still exist.`
- `This cleanup would narrow rollback evidence unless you export the witness first.`
- `App removal will not erase hidden archive residue on this platform.`
- `This surface cannot classify the request honestly; switch to detailed cleanup review.`
