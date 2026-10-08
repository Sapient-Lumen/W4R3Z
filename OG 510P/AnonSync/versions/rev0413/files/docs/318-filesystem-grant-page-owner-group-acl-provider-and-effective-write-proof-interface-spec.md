# Filesystem grant page: owner, group, ACL, provider, and effective write proof interface spec

## Purpose

This page answers one ordinary question:

> what exact grant makes this path writable by the current execution principal, and how strong is the proof that the claimed grant still reaches the actual files and directories involved?

The page exists because `read/write`, `folder available`, and `permission denied` are not adequate operator answers.
A path may depend on owner match, group membership, ACL entries, package-internal grants, removable-storage provider tokens, or some weaker mixed state.

## Core decision

Every managed path and every blocked path must render one first-class **Filesystem grant** page.
That page owns:

- target path identity
- current execution principal
- grant basis
- effective reach over files and directories
- weak points and stale proof
- the next honest repair candidate

The workbench must not force the operator to guess whether a path is blocked by the file, the directory, the share root, the mount, or a stale provider grant.

## Primary layout

The page always renders the same regions in the same order:

1. target strip
2. grant basis card
3. effective reach card
4. weak-point card
5. repair candidate card
6. grant receipts

### 1) Target strip

Show:

- subject label
- canonical path or provider handle
- current execution principal
- current verdict: `write-proved`, `read-only`, `directory-blocked`, `file-blocked`, `grant-stale`, `grant-unknown`
- one next honest action

### 2) Grant basis card

This card publishes:

- grant family: `owner`, `group`, `acl`, `provider token`, `nas internal-user grant`, `system-level override`, `other`
- principal-to-grant relationship
- where the product observed the grant
- when the grant was last tested
- whether the grant is ordinary, inherited, or exceptional

The operator must be able to answer: **what exact thing makes this path writable at all?**

### 3) Effective reach card

This card publishes:

- read proof for the directory
- write proof for the directory
- read proof for ordinary files
- write proof for ordinary files
- whether create / replace / rename / delete are all covered or only a subset
- whether the proof is direct, inherited, sampled, or inferred

The operator must be able to answer: **what operations are actually proven, not merely assumed?**

### 4) Weak-point card

This card publishes:

- the narrowest blocker still present
- whether the blocker sits at parent, target directory, file subset, mount, or provider boundary
- whether the blocker is deterministic or intermittent
- whether wider authority would solve it or only relocate the problem

The operator must be able to answer: **where is the permission gap really located?**

### 5) Repair candidate card

This card publishes:

- safest available repair rung
- stronger but riskier alternatives
- whether the repair changes only grants or also the runtime principal
- whether a post-repair retest can prove success locally
- what continuity warning must be shown if the repair crosses into another principal or world

### 6) Grant receipts

Receipts show:

- grant observations
- grant losses
- retests
- repaired versus unrepaired verdicts
- the actor and time

## Non-negotiable rules

### Rule 1 — `permission denied` is not a verdict

The page must name the grant family and the blocked operation, not merely the symptom.

### Rule 2 — file and directory proofs remain distinct

The current principal may be able to read a file but not replace it, or write a file but not create siblings.
The page must keep those truths separate.

### Rule 3 — inherited or sampled proof must stay labeled

If full proof is unavailable and the product is extrapolating from sampling, the page must say so plainly.

## Honest outputs

The page may conclude:

- `Group grant currently proves read/write/create/rename/delete on the directory and sampled file set.`
- `Directory writable, but child-file replacement blocked by owner mismatch on 12 legacy items.`
- `Provider token present but stale; create test failed at selected subtree root.`
- `System-level principal would likely clear the blocker, but only through a successor-world review.`

It may not collapse those outcomes into one generic `folder accessible` badge.
