# Helper policy page — tracker, relay, LAN, proxy, known-host, and scope-stack interface spec

## Purpose

The archive already has route evidence, egress-only posture, exposure rules, and observer pages.
What it still lacked was one ordinary page for a simpler operator question:

> for this subject on this seat right now, what helper stack is actually in force after subject policy, seat policy, proxy posture, route leases, and remembered environment facts are combined?

This page exists so helper use does not dissolve into a few scattered toggles.

## Core rule

Helper policy is a stack, not a list of checkboxes.
The product must distinguish at least:

- subject-scoped helper policy
- seat-scoped helper policy
- transport posture constraints such as proxy / egress-only
- learned/cached route residue
- temporary overrides or emergency narrowing

If the operator still has to merge multiple preference panes mentally to know whether tracker, relay, LAN, or known hosts really apply, the page is not explicit enough.

## Fixed review order

Every serious helper-policy page should render the same sections in the same order:

1. **Effective helper verdict**
2. **Scope stack**
3. **Current helper matrix**
4. **Constraints and overrides**
5. **Mutations and receipts**

### 1) Effective helper verdict

This section should answer:

- which subject, seat, and runtime profile are under review
- whether the effective posture is `direct-friendly`, `helper-assisted`, `local-only`, `relay-permitted`, `relay-probable`, `relay-forbidden`, or `helper-blocked`
- whether the verdict is steady, temporary, or degraded
- whether a proxy, outage, or override is dominating the outcome

The operator must be able to answer: **what helper story is really in force right now?**

### 2) Scope stack

This section should show the source layers in order:

- subject policy
- seat policy
- host policy
- route lease / temporary override
- environment-derived constraints

Each row should show:

- origin
- relevant fields changed
- whether the row widened, narrowed, or merely documented helper use
- whether the row is still active

The operator must be able to answer: **which layer won, and why?**

### 3) Current helper matrix

This section should have stable rows for:

- tracker / discovery service
- relay service
- LAN discovery / multicast
- known or pinned hosts
- proxy egress posture
- direct inbound expectation
- manual/offline helper substitution

For each row the page should show:

- `allowed` yes/no/reviewed
- `required` yes/no/conditional
- `scope` (`subject`, `seat`, `host`, `temporary`)
- `current rationale`
- `counterfactual if changed`

The operator must be able to answer: **what is merely allowed, what is actually needed, and what is blocked?**

### 4) Constraints and overrides

This section should show:

- egress-only posture or inbound prohibition
- multiple-NIC or address-family constraints
- cached endpoint or learned helper residue
- outage or partial-degradation posture
- any override expiry or review requirement

The operator must be able to answer: **what is stopping the cleaner route I expected?**

### 5) Mutations and receipts

This section should show:

- recent helper-policy changes
- resulting helper verdict changes
- route-impact preview before commit
- exported receipt after commit

The operator must be able to answer: **what changed the helper story, and when?**

## States

Use a small stable vocabulary:

- `direct-friendly`
- `helper-assisted`
- `helper-optional`
- `relay-probable`
- `relay-inevitable`
- `local-only`
- `helper-blocked`

## Main surface

A compact **Helper policy** card should show:

- effective helper verdict
- active helper rows count
- strongest narrowing in force
- primary action: `Inspect helper policy`

## Detailed surface

The detailed page should provide five panes.

### Pane A — Verdict strip

Shows:

- subject
- seat
- effective helper verdict
- primary blocker or helper dependence
- primary action

### Pane B — Scope stack

Columns:

- layer
- source
- effect
- changed fields
- active now

### Pane C — Helper matrix

Columns:

- helper
- allowed
- required
- effective source
- rationale
- counterfactual

### Pane D — Constraints and residue

Rows may include:

- proxied egress-only posture
- blocked inbound listener
- learned remote endpoint cache
- local-only narrowing with lingering non-LAN knowledge
- temporary relay allowance

### Pane E — Receipts

Shows:

- preview receipts
- applied change receipts
- expiry of temporary overrides

## CLI parity

Minimum commands:

- `anonsync helper policy show --subject <subject>`
- `anonsync helper policy preview --subject <subject> --disable relay`
- `anonsync helper policy preview --subject <subject> --mode local-only`
- `anonsync helper policy receipt <receipt-id>`

## Acceptance criteria

A user can:

- see all helper-relevant layers in one place
- tell whether tracker, relay, LAN, proxy, and known-host rules are allowed or required
- identify which layer made relay inevitable or blocked directness
- preview the route effect of policy changes before commit
- prove later why helper posture looked the way it did
