# Subject-kind migration and capability-upgrade review interface spec

## Purpose

The archive already has authority mutation, successor/cutover, reconnect/repair, target custody, and share-class doctrine.
What it still lacked was one explicit interface contract for **changing subject kind without lying about continuity**:

> when an operator wants a live subject to gain capabilities that were not native to its original substrate, what page tells them whether this is a true in-place upgrade, a reviewed migration with preserved continuity, or a new subject that only looks familiar?

Current Resilio docs make this seam unusually explicit.
Standard and Advanced folders still differ architecturally, Standard folders still cannot be upgraded in place, and the documented path is still to remove the Standard folder and re-add it as Advanced.
That is honest support guidance.
It is not a sufficient product contract for a system that wants continuity to stay inspectable.

## Core decision

A meaningful subject-kind change must compile to a first-class **kind-migration review**.
The product should never treat `needs stronger capability model` as equivalent to `remove old subject and add a new one`.

The review must classify the proposal as one of:

1. **True in-place uplift** — same subject handle, same bind continuity, stronger capability epoch
2. **Reviewed migration** — continuity can be preserved, but receipts, artifacts, or grants need explicit translation
3. **Side-by-side successor** — a new subject should be created beside the old one and cutover reviewed later
4. **Blocked conversion** — the requested kind change would destroy too much meaning to call it upgrade

## Why this matters

Current Resilio docs still show three practical truths that AnonSync should not clone:

- some rights and governance features exist only on one subject class
- capability uplift can require disconnect/remove/re-add ritual
- a familiar path can survive while the governance substrate underneath it changes completely

AnonSync should therefore keep path continuity, authority continuity, and subject identity continuity visible even when capability substrate changes.

## The fixed review order

Every kind-migration review should render the same sections in the same order:

1. **Current subject and requested new kind**
2. **Continuity that can be preserved**
3. **Capabilities that change**
4. **Artifacts, grants, and dependents affected**
5. **Admissible migration shapes**
6. **Receipt promise**

## 1) Current subject and requested new kind

Show:

- subject label and stable handle
- current kind / capability substrate
- requested target kind / capability substrate
- acting seat
- whether the request came from issuance, rights editing, topology change, or rollout policy

The operator should be able to answer:

> what subject am I changing, and what new kind am I actually asking for?

## 2) Continuity that can be preserved

Show separately whether the following stay the same, gain a new epoch, or must be re-established:

- subject handle
- current local bind/path continuity
- lineage / custody markers
- member visibility and publication posture
- route policy identity
- durable receipts and audit lineage

Good status labels include:

- `preserved as-is`
- `preserved with new capability epoch`
- `translated during migration`
- `must be reissued explicitly`
- `cannot be preserved honestly`

The operator should never have to guess whether the product means `same subject but stronger` or `new subject at same path`.

## 3) Capabilities that change

This section should state clearly which features become available, remain unavailable, or must be narrowed during migration.
Examples:

- live rights mutation becomes available
- onward delegation becomes governed rather than bearer-style
- per-member identity becomes first-class instead of aggregate/device-only
- approval memory and future-arrival policy become admissible
- imported legacy semantics still cap some options until follow-up cleanup

The point is not only to celebrate new power.
It is to show the semantic price of the uplift.

## 4) Artifacts, grants, and dependents affected

Show fallout on:

- outstanding offers and claim artifacts
- existing grants and delegation chains
- linked or announced members
- same-machine derivatives
- retained-copy / revocation receipts
- rollout and config posture if the old kind came from imported substrate

For each, say whether it is:

- preserved
- translated
- narrowed automatically
- requires reissue / rereview
- blocked pending cutover

A capability upgrade should not quietly strand old artifacts or dependent children.

## 5) Admissible migration shapes

The review must choose the safest honest path, such as:

- `Upgrade in place`
- `Prepare reviewed migration`
- `Create side-by-side successor`
- `Stop and open authority cleanup first`
- `Blocked until imported substrate is retired`

Actions that would blur continuity, such as `Remove and recreate now`, should never be the product's primary suggestion when a safer reviewed migration exists.

## 6) Receipt promise

The resulting receipt must prove:

- original kind and target kind
- whether subject identity continuity was preserved
- which capability epoch changed
- which artifacts/grants were translated, reissued, or invalidated
- whether dependent subjects were narrowed, detached, or left unchanged

A later auditor should be able to answer:

> did this subject truly evolve, or did we actually replace it and call that an upgrade?

## Good action labels

Good primary actions include:

- `Review kind migration`
- `Upgrade with preserved continuity`
- `Prepare side-by-side successor`
- `Translate grants and reissue artifacts`

Poor labels include:

- `Convert`
- `Re-add as new`
- `Enable advanced mode`

Those labels hide the semantic boundary that matters most.

## What must never happen automatically

The product must never automatically:

- delete the old governance substrate and claim continuity afterward
- keep the same friendly label while silently assigning a new subject handle
- imply that path continuity alone proves identity continuity
- retain live artifacts whose meaning widened or changed without review
- strand dependents and only explain the fallout after apply

## Why this is worth the trouble

Capability uplift is one of the places where sync products most often fall back to folklore.
If AnonSync wants to be meaningfully better, it should make `stronger subject kind` read like a reviewed migration of continuity-bearing objects, not like an uninstall/reinstall ritual that happened to keep the same bytes on disk.
