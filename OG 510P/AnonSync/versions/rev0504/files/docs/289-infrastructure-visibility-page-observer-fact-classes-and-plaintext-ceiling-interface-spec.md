# Infrastructure visibility page — observer fact classes and plaintext ceiling interface spec

## Purpose

The archive already has disclosure doctrine and route/discovery objects.
What it still lacked was one explicit ordinary page for a narrower but very practical question:

> for this subject on this seat right now, which outside observers can learn which exact facts, and what is the strongest plaintext ceiling for each observer?

This page exists so privacy truth does not dissolve into `tracker on/off`, `relay on/off`, or vendor-marketing reassurance.

## Core rule

Infrastructure visibility is a matrix, not a slogan.
The product must distinguish at least:

- **observer class**
- **fact class**
- **transport/content visibility ceiling**
- **why that observer is currently in play**
- **how the observer can be removed or narrowed**

If the operator still has to read separate service articles to know whether an observer sees IP addresses, click counts, share IDs, encrypted bytes, version strings, or nothing at all, the page is not explicit enough.

## Fixed review order

Every serious infrastructure-visibility page should render the same sections in the same order:

1. **Effective observer set**
2. **Fact matrix and plaintext ceiling**
3. **Why each observer is active**
4. **Narrowing and residue**
5. **Receipt and audit trail**

### 1) Effective observer set

This section should answer:

- which subject, seat, and runtime profile are under review
- whether the current effective observer set is `none`, `private-only`, `mixed`, or `vendor-infra-present`
- whether the answer is subject-specific or host-wide
- whether any observer is active only because of a temporary override or fallback path

The operator must be able to answer: **who outside the current local world is in the loop at all?**

### 2) Fact matrix and plaintext ceiling

This section should list every relevant observer row, such as:

- tracker / discovery service
- relay service
- link landing page
- update-check service
- telemetry / statistics service
- license / account service
- named private discovery or relay service

For each row the page should show:

- `observer class`
- `currently active` yes/no
- `fact classes visible` (`ip`, `port`, `share-id`, `click-count`, `version`, `os`, `email`, `none`, etc.)
- `payload visibility ceiling` (`none`, `metadata-only`, `encrypted-bytes-in-transit`, `account-data-only`)
- `retention / residue posture`
- `strongest current disable path`

The operator must be able to answer: **what exactly can each observer learn, and does any observer ever see plaintext content?**

### 3) Why each observer is active

This section should show:

- which standing policy, temporary lease, or operator action enabled the observer
- whether the observer is active because of direct necessity, convenience acceleration, upgrade checks, telemetry opt-in, or account management
- whether the observer is active host-wide or only for one subject
- whether a fallback or degraded route activated it unexpectedly

The operator must be able to answer: **why is this observer active right now instead of remaining absent?**

### 4) Narrowing and residue

This section should show:

- which observers can be removed immediately
- which observers stop future contact but may leave time-bound or provider-defined residue
- which disablement still preserves local-only/manual workflows
- which disablement would change reachability, convenience, update awareness, or account features

The operator must be able to answer: **how do I narrow this observer set, and what lingering traces or capability losses remain?**

### 5) Receipt and audit trail

This section should show:

- recent visibility-changing actions
- prior observer acknowledgments
- disablement receipts
- residual-risk acknowledgments
- exportable visibility snapshot for audit or external review

The operator must be able to answer: **what proof shows why this observer matrix looks the way it does now?**

## States

Use a small stable vocabulary:

- `no outside observer`
- `private observer only`
- `vendor infra metadata only`
- `vendor infra encrypted transit only`
- `mixed observer set`
- `residual visibility acknowledged`

## Main surface

A compact **Infrastructure visibility** card should show:

- current observer-set verdict
- count of active observer rows
- strongest plaintext ceiling across all rows
- primary action: `Inspect infrastructure visibility`

## Detailed surface

The detailed page should provide five panes.

### Pane A — Verdict strip

Shows:

- subject
- seat
- observer-set verdict
- strongest plaintext ceiling
- primary narrowing action

### Pane B — Observer matrix

Columns:

- observer
- active now
- fact classes
- plaintext ceiling
- enabled by
- disable path

### Pane C — Residue and retention

Rows may include:

- click counts retained by landing service
- tracker endpoint/cache residue
- update-check history
- telemetry sent earlier in clear
- license/account linkage

### Pane D — Capability impact of narrowing

Shows two explicit summaries:

- `privacy gain if disabled`
- `convenience/reachability cost if disabled`

The product should never force the operator to choose between silence and ignorance.

### Pane E — Receipts

Shows:

- observer-change receipts
- residual-risk acknowledgments
- exported visibility snapshots

## CLI parity

Minimum commands:

- `anonsync infra visibility show`
- `anonsync infra visibility show --subject <subject>`
- `anonsync infra visibility preview --subject <subject> --disable tracker,relay`
- `anonsync infra visibility receipt <receipt-id>`

## Acceptance criteria

A user can:

- tell exactly which outside observers are currently in play
- see which facts each observer can learn
- see whether any observer ever sees plaintext content or only encrypted transit / metadata
- preview what disabling one observer changes
- prove later why a given observer set was accepted or narrowed

