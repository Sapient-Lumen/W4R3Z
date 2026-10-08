# Capture source page: domain, permission, and runtime readiness interface spec

## Purpose

This page answers one ordinary question:

> what exact source domain is this ingest relationship watching right now, what permission proves that scope, and how ready is the source to keep producing ingest without operator babysitting?

The page exists because `camera backup`, `android backup`, `custom folder backup`, and `mobile capture source` are not decorative labels.
They are different source contracts with different scope ceilings and runtime caveats.

## Core decision

Every capture-only ingest relationship must render one first-class **Capture source** page.
That page owns:

- source seat identity
- source domain identity
- permission proof for that domain
- runtime/background readiness
- current narrowing or drift
- the next honest action if the source is not fully ready

The workbench must not force the operator to infer source scope from a menu label or a remembered platform limitation.

## Primary layout

The page always renders the same regions in the same order:

1. source strip
2. source-domain contract card
3. permission proof card
4. runtime readiness card
5. source receipts

### 1) Source strip

Show:

- source seat label
- capture relationship label
- source-domain class: `camera roll`, `custom folder`, `prompted media root`, `provider-limited root`, `other constrained domain`
- current verdict: `ready`, `ready-with-caveats`, `permission-stale`, `runtime-blocked`, `domain-drift`
- one next honest action

### 2) Source-domain contract card

This card publishes:

- canonical source path or domain handle
- whether the domain is broad, filtered, or platform-constrained
- whether the current source is append-like, general mutable content, or provider-mediated
- whether file discovery is expected to be real-time, periodic, foreground-only, or opportunistic
- whether the current source class was chosen by the operator or forced by the platform

The operator must be able to answer: **what exact source domain is attached here?**

### 3) Permission proof card

This card publishes:

- current permission grant or provider token
- when it was last confirmed
- whether the grant is read-only, read-write, or provider-scoped
- what narrower world would remain if the grant disappeared
- whether the product has current evidence that the grant still reaches the advertised domain

The operator must be able to answer: **why does the product believe it may watch this source at all?**

### 4) Runtime readiness card

This card publishes:

- background eligibility
- battery/network gates
- app-open or foreground requirement if any
- last successful discovery time
- oldest unobserved or unprocessed source event, if known
- freshness floor under current runtime conditions

The operator must be able to answer: **how ready is this source to keep feeding ingest right now?**

### 5) Source receipts

Receipts show:

- source-domain changes
- permission grants or losses
- runtime verdict changes
- acknowledged caveats
- the actor and time

## Non-negotiable rules

### Rule 1 — source domain is not a nickname

`Camera backup` or `Backup` is never enough by itself.
The page must publish what real source domain that label resolved to.

### Rule 2 — permission and runtime are separate truths

A valid provider grant does not imply viable background delivery.
A currently open app does not imply broad domain access.
The page must keep those truths distinct.

### Rule 3 — narrowed scope must be explicit

If a platform only exposes Camera Roll, or only a custom selected subtree, the page must show that as a first-class ceiling rather than a footnote.

## Honest outputs

The page may conclude:

- `Camera roll only; permission current; foreground required for timely ingest.`
- `Custom folder attached; provider grant current; battery saver delays discovery.`
- `Source grant stale; last successful read 3d ago; safe delete guidance downgraded.`
- `Domain drift detected; advertised root and observed root no longer match.`

It may not collapse those outcomes into one generic `backup enabled` badge.
