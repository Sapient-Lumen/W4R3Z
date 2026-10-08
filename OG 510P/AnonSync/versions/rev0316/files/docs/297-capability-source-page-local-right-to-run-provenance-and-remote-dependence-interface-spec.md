# Capability source page — local right-to-run, provenance, and remote dependence interface spec

## Purpose

The archive already has entitlement floors, capability owners, and subject-kind migration.
What it still lacked was one ordinary page for a simpler but highly practical question:

> what capabilities does this seat actually have right now, where did they come from, and which of them would disappear if remote/account/expiry conditions changed?

This page exists so `works here` does not dissolve into folklore about editions, trials, keys, accounts, and platform caveats.

## Core rule

Capability is a source stack, not a badge.
The product must distinguish at least:

- capabilities that are purely local and durable
- capabilities that depend on reviewed local activation material
- capabilities that depend on remote/account reachability
- capabilities that are blocked by platform, role, or subject kind
- capabilities that are temporary or expiring

If the operator still has to cross-read purchase, update, platform, and settings pages to know why a verb is present or greyed out, the page is not explicit enough.

## Fixed review order

Every serious capability-source page should render the same sections in the same order:

1. **Effective capability verdict**
2. **Capability source stack**
3. **Remote dependence and failure modes**
4. **Expiry, downgrade, and recovery paths**
5. **Receipts and audit trail**

### 1) Effective capability verdict

This section should answer:

- which seat, runtime profile, and build are under review
- whether the current posture is `local-only`, `locally-activated`, `remotely-dependent`, `time-bounded`, `degraded`, or `blocked`
- whether the verdict is host-wide or subject-specific
- whether any key capability is in a grace/trial window or reviewed exception posture

The operator must be able to answer: **what can this seat really do right now?**

### 2) Capability source stack

This section should list the winning source rows in order, for example:

- local build/runtime family
- local activation material
- optional purchased or provisioned capability pack
- subject-kind requirements
- platform or storage-class constraints
- temporary override or reviewed exception

For each row the page should show:

- `source class`
- `capabilities granted`
- `capabilities withheld`
- `scope`
- `durability`
- `proof or receipt`

The operator must be able to answer: **why does this capability exist here instead of somewhere else?**

### 3) Remote dependence and failure modes

This section should show:

- whether any capability requires current remote/account reachability
- whether remote failure blocks only management/refresh or the underlying local operation itself
- whether the seat can continue in an offline grace period
- which capabilities are intentionally account-free and survive completely offline

The operator must be able to answer: **what breaks if the network, account service, or activation source disappears?**

### 4) Expiry, downgrade, and recovery paths

This section should show:

- upcoming expiry or review checkpoints
- what downgrades first if the source weakens
- which capabilities degrade to read-only/inspect-only versus stop entirely
- how the operator can restore, renew, replace, or intentionally strip the capability

The operator must be able to answer: **if this source weakens, what survives and what is the clean recovery path?**

### 5) Receipts and audit trail

This section should show:

- latest activation or provisioning receipts
- capability-source changes over time
- downgrade or expiry receipts
- exported snapshot for support or audit

The operator must be able to answer: **what evidence explains the current capability posture?**

## States

Use a small stable vocabulary:

- `local-only`
- `locally-activated`
- `remotely-dependent`
- `time-bounded`
- `degraded`
- `blocked`

## Main surface

A compact **Capability source** card should show:

- current verdict
- strongest durable capability class
- strongest remote dependency risk
- next review or expiry point

## Key prohibitions

The product must not:

- collapse all capability truth into one generic `licensed` or `enabled` badge
- hide remote dependence behind success while the network happens to be available
- let an expired or blocked state remove verbs without explaining which source row failed
- make the operator infer subject-kind gates from grey buttons alone
