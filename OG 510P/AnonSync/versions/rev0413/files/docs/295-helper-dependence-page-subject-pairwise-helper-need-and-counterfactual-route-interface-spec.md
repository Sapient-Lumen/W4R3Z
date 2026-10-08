# Helper dependence page — subject pairwise helper need and counterfactual route interface spec

## Purpose

The archive already has route evidence, directness grades, and relay posture.
What it still lacked was one ordinary page for the question operators actually ask during stubborn troubleshooting or privacy review:

> for this subject and this peer pair, which helpers are actually needed right now, which are merely allowed, and what exact counterfactual would remove that dependence?

This page exists so helper need does not hide behind one relay icon or one failed directness attempt.

## Core rule

Pairwise helper dependence is explanatory state.
The product must separate at least:

- current path class
- helper need class
- helper cause
- directness blockers
- counterfactual repairs

If the operator still has to infer pairwise dependence from scattered route logs and support lore, the page is not explicit enough.

## Fixed review order

Every serious helper-dependence page should render the same sections in the same order:

1. **Current pairwise verdict**
2. **Needed versus allowed helper rows**
3. **Blockers to cleaner path**
4. **Counterfactuals**
5. **Receipt and audit trail**

### 1) Current pairwise verdict

This section should answer:

- subject
- local seat
- remote seat or peer group
- current path class (`direct`, `lan-direct`, `known-host direct`, `relay-assisted`, `relay-inevitable`, `blocked`, `unknown`)
- confidence grade

The operator must be able to answer: **what path is this pair actually using or needing now?**

### 2) Needed versus allowed helper rows

This section should show rows for:

- tracker/discovery
- relay
- LAN discovery
- pinned host set
- cached endpoint memory
- proxy mediation

For each row show:

- `needed now` yes/no/conditional
- `merely allowed` yes/no
- `why needed`
- `which side needs it`

The operator must be able to answer: **which helpers are genuinely carrying this pair and which are just available?**

### 3) Blockers to cleaner path

This section should show typed blockers such as:

- both sides egress-only
- blocked inbound listener
- blocked tracker/bootstrap access
- blocked relay access
- multicast unavailable across the relevant LANs
- multiple-NIC or address-family mismatch
- stale cached endpoint confusion

The operator must be able to answer: **what specifically prevents the route I wanted?**

### 4) Counterfactuals

This section should show reviewed statements such as:

- `if relay were disabled now, this pair would stall`
- `if pinned hosts were added on both peers, relay would become unnecessary`
- `if inbound direct were restored on one side, the pair would become direct-capable`
- `if stale endpoint residue were cleared, local-only policy would stop leaking into WAN fallback`

The operator must be able to answer: **what exact change would produce the better path?**

### 5) Receipt and audit trail

This section should show:

- path-change receipts
- helper-narrowing receipts
- blocker acknowledgments
- exported pairwise explanation snapshots

The operator must be able to answer: **what proof explains why this pair was relay-bound, direct, or blocked at a given moment?**

## States

Use a small stable vocabulary:

- `direct`
- `direct-capable-not-chosen`
- `relay-assisted`
- `relay-inevitable`
- `helper-missing`
- `blocked`
- `unknown`

## Main surface

A compact **Helper dependence** card should show:

- pairwise path verdict
- currently needed helpers count
- strongest blocker
- primary action: `Inspect helper dependence`

## Detailed surface

The detailed page should provide five panes.

### Pane A — Verdict strip

Shows:

- subject
- local seat
- remote seat
- current path verdict
- primary blocker

### Pane B — Helper dependence matrix

Columns:

- helper
- needed now
- allowed
- side relying on it
- evidence
- counterfactual

### Pane C — Blockers

Rows may include:

- inbound prohibition
- multicast gap
- tracker unreachable
- relay unreachable
- proxy asymmetry
- route-cache residue

### Pane D — Counterfactual planner

Shows one-step and two-step reviewed route improvements and their likely observer/capability costs.

### Pane E — Receipts

Shows:

- pairwise path explanation export
- helper policy change receipts
- narrowing acknowledgments

## CLI parity

Minimum commands:

- `anonsync helper dependence show --subject <subject> --peer <peer>`
- `anonsync helper dependence preview --subject <subject> --peer <peer> --disable relay`
- `anonsync helper dependence preview --subject <subject> --peer <peer> --add pinned-host <host>`
- `anonsync helper dependence receipt <receipt-id>`

## Acceptance criteria

A user can:

- tell which helpers a specific peer pair actually needs now
- distinguish `relay allowed` from `relay inevitable`
- see which concrete blocker prevents a cleaner path
- preview counterfactual route improvements before changing policy
- export a durable explanation of pairwise helper dependence
