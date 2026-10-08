# Bootstrap source page — catalog origin, cache residue, and private override interface spec

## Purpose

The archive already has route policy and state-root language.
What it still lacked was one ordinary page for a narrower bring-up and narrowing question:

> where did this seat learn its helper catalog and peer coordinates from, what residue still survives, and what local or private override replaced the default source?

This page exists so bootstrap truth does not hide inside config files, caches, and troubleshooting recipes.

## Core rule

Bootstrap is a public provenance story.
The product must separate at least:

- catalog source
- catalog freshness
- cached learned facts
- private/manual override source
- residue that survives after narrowing

If an operator still has to guess whether a route was possible because of vendor catalog bootstrap, pinned helper data, cached endpoints, or manual host entries, the page is not explicit enough.

## Fixed review order

Every serious bootstrap-source page should render the same sections in the same order:

1. **Active bootstrap verdict**
2. **Catalog provenance**
3. **Learned residue and freshness**
4. **Override and replacement paths**
5. **Clearance and receipts**

### 1) Active bootstrap verdict

This section should answer:

- whether bootstrap is `default-catalog`, `private-catalog`, `manual-only`, `cached-only`, or `degraded`
- whether helper discovery is currently fresh, stale-but-usable, or missing
- whether the result is host-wide or subject-scoped

The operator must be able to answer: **what bootstrap source is actually carrying this seat right now?**

### 2) Catalog provenance

This section should show:

- source kind (`vendor-catalog`, `private-catalog`, `embedded-static`, `manual-host-set`, `cached-endpoints-only`)
- how it was configured
- last successful refresh
- which helper classes it governs
- what trust or failure domain it belongs to

The operator must be able to answer: **who told this seat where to find helpers or peers?**

### 3) Learned residue and freshness

This section should show:

- cached endpoints or peer coordinates
- cached helper addresses
- freshness horizon / expiry expectation
- whether the residue still widens the effective route beyond current narrowing wishes

The operator must be able to answer: **what old knowledge is still helping or hurting me?**

### 4) Override and replacement paths

This section should show:

- manual/pinned host sets
- subject-local bootstrap overrides
- seat-wide or host-wide helper overrides
- private helper or local discovery substitution
- explicit fallback order

The operator must be able to answer: **what replaced the default bootstrap, and how complete is that replacement?**

### 5) Clearance and receipts

This section should show:

- cache-clear previews
- helper-catalog replacement receipts
- narrowing receipts
- stale-bootstrap warnings

The operator must be able to answer: **what proof shows that the old bootstrap knowledge is really gone or still present?**

## States

Use a small stable vocabulary:

- `default-catalog`
- `private-catalog`
- `manual-only`
- `cached-only`
- `degraded-bootstrap`
- `stale-residue-present`

## Main surface

A compact **Bootstrap source** card should show:

- active bootstrap verdict
- freshness age
- whether stale residue is present
- primary action: `Inspect bootstrap source`

## Detailed surface

The detailed page should provide five panes.

### Pane A — Verdict strip

Shows:

- seat
- bootstrap verdict
- freshness verdict
- residue verdict
- primary action

### Pane B — Provenance table

Columns:

- source
- governs
- freshness
- trust domain
- failure domain
- currently active

### Pane C — Learned residue

Columns:

- residue kind
- scope
- learned at
- expires / review by
- still widening route?

### Pane D — Overrides and replacements

Shows:

- pinned hosts
- private catalogs
- offline/manual helper sets
- fallback ordering
- missing coverage gaps

### Pane E — Receipts

Shows:

- clear-cache receipt
- adopt-private-catalog receipt
- revert-to-default receipt
- stale-bootstrap acknowledgment

## CLI parity

Minimum commands:

- `anonsync bootstrap show`
- `anonsync bootstrap show --subject <subject>`
- `anonsync bootstrap preview --clear-residue`
- `anonsync bootstrap preview --source private:<catalog>`
- `anonsync bootstrap receipt <receipt-id>`

## Acceptance criteria

A user can:

- tell whether bootstrap currently comes from default, private, manual, or cached sources
- see exactly what stale or learned helper knowledge remains
- clear or replace bootstrap sources through reviewed actions
- prove later whether narrowing actually removed old route knowledge
