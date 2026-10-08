# Hidden service state, rule ledger, and repair review interface spec

## Purpose

The archive already had filesystem fidelity, projection policy, and continuity repair.
What it still lacked was one concrete interface contract for the oldest kind of sync folklore:

> when critical state lives in hidden service folders and editable text files, what page tells the operator what that state means, whether it drifted, and whether a repair preserves continuity or starts a new subject epoch?

Current Resilio docs make this seam sharper than before.
They still say `.sync` is critical, that deleting or corrupting it suspends synchronization, that the fix for `Service files missing` is remove the share, delete `.sync`, and add it back, that `IgnoreList` and `StreamsList` live in hidden `.sync` files, and that cloning a Sync instance is unsupported because copied internal state can produce strange behavior.
That is candid and useful support guidance.
It is not the user contract AnonSync should inherit.

## Core decision

Hidden service artifacts may exist internally, but they must never be the only public explanation for operator-meaningful behavior.
Anything that changes tracking, visibility, xattr propagation, subject identity, or repair outcome must surface through one explicit **rule and service-state ledger**.

That ledger must answer at least four distinct questions:

1. **What hidden state exists?**
2. **Which parts are operator-meaningful policy versus daemon-owned machinery?**
3. **What continuity would be preserved or broken by repair?**
4. **Which durable receipt proves what happened?**

## Why this matters

Current Resilio docs still reveal six truths AnonSync should not clone:

- `.sync` is critical enough that losing it suspends sync entirely
- share identity lives partly in hidden service state such as the ID file
- ignore behavior and xattr behavior are configured through hidden text files
- xattrs are governed by `StreamsList`, not ordinary ignore semantics
- same `IgnoreList` across peers is only advisory, so two peers can truthfully differ while looking superficially aligned
- cloning/copied internals and service-file corruption still fall back to `remove and add back` style repair

AnonSync should therefore make hidden service state visible as **classified contract data** instead of leaving it as support-lore background radiation.

## Ledger sections

Every share or subject should expose one **Rules and service state** page with these sections in fixed order:

1. **Subject continuity identity**
2. **Operator-visible policy ledgers**
3. **Daemon-owned service state**
4. **Repair classification**
5. **Receipt shelf**

### 1) Subject continuity identity

Show:

- subject label and stable handle
- current continuity epoch
- mount/bind count
- whether service identity is fresh, drifted, missing, foreign, or cloned-risk
- whether the current path owns the live service state or merely contains copied residue

The operator should be able to answer:

> is this still the same subject with damaged internals, or has continuity already forked?

### 2) Operator-visible policy ledgers

Show policy objects that may have hidden implementations but explicit public truth:

- ignore/project rules
- namespace suppression rules
- xattr/stream policy
- special-entry policy
- archive/history policy
- portability or warning-tier target policy

Each row should say:

- effective behavior
- scope
- source
- peer-visibility consequences
- whether the daemon stores implementation copies in hidden files

The operator should never have to inspect `IgnoreList` or `StreamsList` directly just to understand what the product will do.

### 3) Daemon-owned service state

Show service-owned machinery separately from policy:

- identity markers
- indexing state
- materialization markers
- in-flight temp material
- archive service paths
- repair blockers or corruption warnings

This section is visible because it matters, but editable only through reviewed actions.
It should not masquerade as user-authored policy.

### 4) Repair classification

When hidden state is missing, foreign, or cloned-risk, the page must classify the repair options:

- `Reconstruct daemon-owned state and preserve continuity`
- `Seal evidence and fork into new continuity epoch`
- `Detach copied residue from this path`
- `Import as historical evidence only`
- `Abort because active overlap or loop risk exists`

The review must say explicitly whether the result will:

- preserve subject handle
- preserve grants and approvals
- preserve archive/history continuity
- require reissue of offers or lineage receipts
- create a new epoch with a continuity break receipt

### 5) Receipt shelf

Every high-signal repair emits one durable receipt proving:

- prior state class (`healthy`, `missing`, `foreign`, `cloned-risk`, `corrupt`, `mixed`)
- chosen repair class
- preserved continuity versus broken continuity
- preserved policy ledgers versus regenerated daemon state
- whether hidden artifacts were quarantined, reused, or discarded

A later operator should be able to answer:

> did we repair the same subject, or did we create a new one after hidden-state loss?

## What must never happen automatically

The product must never automatically:

- require direct hidden-file editing to understand ordinary semantics
- treat daemon-owned service state as if it were user-authored policy
- silently promote copied service residue into live continuity
- silently discard archive/history material during service-state repair
- claim continuity was preserved when the repair actually minted a new epoch

## Why this is worth the trouble

The moment a sync product teaches hidden control files as the real explanation, the public interface has already ceded too much ground.
AnonSync can do better by giving hidden state one visible ledger, one repair classifier, and one receipt model that keeps continuity honest.
