# Capture sink page: durable-copy target, sink authority, and disconnect residue interface spec

## Purpose

This page answers:

> where are these mobile-origin bytes going to live durably, and what exact authority does that sink have?

The page exists because a backup sink is not just `another peer`.
It may be the durable copy while still lacking collaborative write-back authority.

## Core rule

Every capture-only or backup-style mobile flow must expose one first-class **Capture sink** page before apply.
That page owns:

- selected sink or pending sink
- sink authority class
- default landing path / name
- disconnect residue and retention contract

## Primary layout

The page always renders the same regions:

1. sink verdict
2. sink selection card
3. authority and retention card
4. disconnect residue card
5. receipt

### 1) Sink verdict

Show:

- chosen sink or `pending external recipient`
- sink class verdict: `linked-durable-sink`, `manual-link-sink`, `collaborative-peer`, `one-off-recipient`, `unknown`
- strongest honest contract summary
- one next honest action

### 2) Sink selection card

Show:

- whether the sink was chosen from linked devices, discovered later by link delivery, or auto-created on claim
- whether multiple candidate sinks are eligible
- default landing root / folder name if auto-created
- whether the sink is a desktop/NAS-style durable copy or merely a temporary recipient

The operator must be able to answer: **what exact sink am I choosing, and how will it materialize there?**

### 3) Authority and retention card

Show:

- whether the sink has collaborative write-back power, read-only storage posture, or bounded receipt posture
- whether sink-side deletes or edits can ever propagate upstream
- what source-side deletes do after the sink has a copy
- whether the sink is the intended durability anchor

The operator must be able to answer: **what rights does the sink get, and what retention promise comes with them?**

### 4) Disconnect residue card

Show:

- what remains on source and sink after disconnect
- whether disconnect stops transfer only or also clears bytes
- whether already-landed bytes remain on both sides
- whether reconnect continues same-lineage backup or starts a new epoch

The operator must be able to answer: **what stays behind if I pause, disconnect, or replace the sink?**

### 5) Receipt

After apply, emit a receipt that preserves:

- sink identity or delivery artifact
- sink authority class
- landing path / default folder name
- disconnect residue contract

## Honest outputs

This page may conclude:

- `desktop durable sink with no delete-back propagation`
- `linked-device backup target chosen from existing cohort`
- `manual-link sink pending claim`
- `collaborative peer rather than backup sink`
- `disconnect preserves already-landed copies on both sides`

It may not compress all of these into one generic `shared with device` row.

## Rules

### Rule 1 — sink authority must be named explicitly

The page must distinguish `durable copy` from `collaborative writer`, even if both are technically peers in transport terms.

### Rule 2 — landing defaults must be published

If the sink will auto-create a default backup folder name or root, the page must say so directly.

### Rule 3 — disconnect residue must stay adjacent to sink choice

Operators should not discover after disconnect that copies were retained, stranded, or recreated under a new epoch.

## Acceptance test

This page is good enough when a cautious operator can answer all of the following without leaving it:

- where the durable copy will land
- whether the sink can write or delete back upstream
- whether source-side deletes preserve the sink copy
- what disconnect leaves behind on each side
- whether a future replacement sink would continue or restart the backup lineage
