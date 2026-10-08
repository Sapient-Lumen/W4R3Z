
# Remedy-hardening-attestation policy-rollout contract sheet page — deployment scope, exception budget, and enforcement class

## Purpose

This page is the compact contract for deciding whether a precedent that is already portable for some future-case class has actually been deployed as governing policy for a named estate slice.
It exists so the product can distinguish `portable but not rolled out`, `rollout active`, `deployed with bounded waivers`, `grandfathered debt still open`, `enforced for named slice`, and `estate-wide sentence blocked`.

## Core fields

- policy rollout identifier
- source precedent receipt identifier
- current governing receipt identifier
- current policy-rollout class
- named estate slice in scope
- estate slices explicitly out of scope
- deployment owner
- enforcement owner
- waiver owner
- required control family
- deployment mechanism family
- platform or surface classes covered
- platform or surface classes uncovered
- manual override inventory count
- grandfathered population count
- active waiver count
- expired waiver count
- exception budget
- current exception debt
- verification coverage percentage or class
- last verification time
- next required review time
- strongest currently safe rollout sentence
- strongest blocked broader sentence
- next evidence that upgrades enforcement confidence
- next evidence that forces narrowing, pause, or rollback now

## Policy-rollout classes

The page must model at least these distinct classes:

- precedent not yet portable enough for rollout review
- portable but rollout not proposed
- rollout proposed, target slice named
- rollout approved, deployment not started
- deployment active for named slice only
- deployed but verification incomplete
- enforced for named slice with bounded waivers
- grandfathered population still outside policy
- exception debt above budget
- waiver expired or review overdue
- policy narrowed, paused, retired, or superseded
- broader estate-wide claim blocked

## Deployment axes

The page must support at least these deployment axes:

- platform family
- interface surface family
- folder or object class
- topology or authority model
- configuration lane
- manual override exposure
- local-share or derived-share exposure
- exception or waiver family
- verification mechanism family
- review or expiry schedule

## Fixed rendering order

Every policy-rollout contract sheet must render the same sections in the same order:

1. **Strongest currently rollout-safe sentence**
2. **Named estate slice in scope and current enforcement class**
3. **Deployment mechanism, uncovered populations, and override debt**
4. **Waivers, grandfathered populations, and exception budget**
5. **Next evidence that upgrades or collapses the rollout claim**

## Hard rules

The contract sheet must never let an operator hide:

- a portable precedent behind an `already deployed` sentence
- a Standard-only rollout behind an estate-wide control claim
- a desktop-only preference behind a cross-surface enforcement sentence
- a manual per-share override behind `default now governs everywhere`
- a grandfathered or waived population behind `policy in force for all`
