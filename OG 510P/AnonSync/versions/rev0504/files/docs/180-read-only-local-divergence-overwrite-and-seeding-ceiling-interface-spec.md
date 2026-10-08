# Read-only local divergence, overwrite, and seeding ceiling interface spec

## Purpose

The archive already had rights doctrine and helper-role discussion.
What it still lacked was one dedicated interface contract for the overloaded phrase `Read Only`:

> if a member may not write back, can it still edit locally, can those edits be repaired automatically, and can it still relay bytes to others?

Current Resilio docs make this seam sharper.
They still say read-only peers can make local changes but those changes are not synced back, that changed files can stop synchronization for that file, that `Overwrite any changed files` can restore deleted or edited content and re-download the old name after a rename, that added files are neither deleted nor synced, and that read-only peers can still transfer unmodified files to newly joined peers.
That is useful operational candor.
It is not one clean public truth.

## Core decision

One-way or read-only posture must be modeled through three separate public axes:

1. **Write propagation right**
2. **Local divergence handling**
3. **Seeding/relay capability**

A single `Read only` badge is not enough.
The operator should never have to infer seeding ability or local-repair outcome from a permission label alone.

## The fixed review order

Any one-way/right-limited subject or member page should render sections in this order:

1. **Granted authority**
2. **Local divergence policy**
3. **Relay/seeding posture**
4. **Current local exceptions**
5. **Receipt shelf**

### 1) Granted authority

Show clearly:

- may read namespace?
- may fetch bytes?
- may materialize locally?
- may publish edits upstream?
- may issue offers or grants?
- may relay already-held bytes to other authorized members?

This prevents `read-only` from hiding network-participation truth.

### 2) Local divergence policy

Show exactly what happens if the restricted member:

- edits a file
- deletes a file
- renames a file
- adds a new file
- creates a new directory

For each case, say whether the result is:

- local-only fork retained
- automatic revert to upstream truth
- restored old name / old bytes
- blocked pending review
- divergence that stops sync for that path

The product should never require support-article memory to answer basic local-edit questions.

### 3) Relay/seeding posture

Show separately whether the member can:

- seed unchanged bytes it already possesses
- satisfy new member fetches
- serve as a transit/helper for ordinary replication
- relay only while policy epoch remains current

This is a network role, not a write right.
It deserves its own row.

### 4) Current local exceptions

If the member already has local divergent paths, the page should list them as classified exceptions:

- `local rename retained`
- `local edit diverged`
- `deleted locally, restore pending`
- `new local file unsynced`
- `local fork sealed`

Primary actions should include:

- `Restore upstream truth here`
- `Keep local fork sealed`
- `Promote through reviewed authority change`
- `Exclude from local mount only`

### 5) Receipt shelf

Every relevant mutation or repair must emit a receipt proving:

- authority posture at time of action
- divergence class
- whether overwrite/revert policy acted
- whether local-only bytes were preserved, restored, or sealed
- relay/seeding posture in effect

A later operator should be able to answer:

> was this member merely forbidden to write upstream, or also unable to seed, and what happened to its local edits?

## What must never happen automatically

The product must never automatically:

- imply that `may not write upstream` also means `cannot relay authorized bytes`
- silently destroy local divergent bytes without a receipt
- pretend a rename or delete behaved like an edit when the consequences differ
- hide per-path sync stoppage behind a generic read-only badge

## Why this is worth the trouble

One-way sharing is valuable, but it becomes misleading when one label stands in for rights, repair policy, and network role all at once.
AnonSync can do better by separating write denial, local divergence handling, and relay/seeding truth into one explicit contract.
