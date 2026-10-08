# Group-write discipline proof page, umask, delivery ownership, and sync-stop risk interface spec

## Why this page exists

Current official Resilio docs do something unusually valuable here: they admit that the pre-login Mac recipe only works cleanly if future local files inside synced folders preserve the right group-write posture.
They also admit the failure mode plainly: otherwise Sync may stop syncing those files.

That truth is too important to live inside setup prose.
AnonSync should turn it into one dedicated proof page whenever a runtime depends on a particular POSIX creation contract.

## Operator questions this page must answer

1. **What file-mode/ownership class does this runtime expect for new local writes?**
2. **What mode class do delivered files currently receive?**
3. **Do ordinary local writers on this host satisfy the same contract?**
4. **What exactly breaks if they do not?**
5. **What proof supports the current claim?**

## Required sections

### 1) Runtime creation contract

Show:

- active principal
- effective umask if known
- expected owner/group class for delivered files
- expected permission bits / writeability class
- whether the contract is strict, advisory, or unknown

### 2) Observed delivered-file posture

Show sampled or authoritative proof of:

- owner
- group
- mode bits / capability class
- representative synced paths
- proof freshness

### 3) Local-writer compatibility

Show whether the product believes ordinary local writers will create compatible files:

- `compatible`
- `compatible with caveats`
- `incompatible likely`
- `unknown`

And explain why.

### 4) Failure semantics

Spell out the exact supported sentence, such as:

- `future local files lacking group write may stop syncing under this runtime`
- `some writers on this host may create incompatible files for this principal/group contract`

Never collapse this into a vague `permission issue`.

### 5) Safer remediation ladder

Offer steps such as:

- switch principal / world
- adjust local creation policy
- narrow synced path ownership
- move back to session-bound app
- export receipt and postpone apply

## Public object

### `group_write_discipline_proof`

Fields:

- `group_write_discipline_proof_id`
- `seat_ref`
- `principal_name`
- `effective_umask` nullable
- `expected_owner_class`
- `expected_group_class`
- `expected_writeability_class`
- `observed_delivery_samples[]`
- `local_writer_compatibility_verdict`
- `failure_semantics`
- `proof_basis`
- `proof_freshness_state`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `generated_at`

## Main surface language

Use language like:

- `Delivered files are group-writable under reviewed pre-login runtime`
- `Future local files may fail this contract`
- `Writer compatibility unproven; sync-stop risk remains`

Avoid language like:

- `permissions okay`
- `folder writable`
- `ACL fine`

Those are too weak.

## Design tests

This page is missing if:

- the product can require a mode/ownership discipline without surfacing it
- sync-stop risk remains generic instead of mode-specific
- proof of delivered-file posture is absent
- remediation skips straight to shell advice without first-class product language

## Non-clone reason

Current official Resilio docs still contain the right warning but only as setup text.
AnonSync should promote file-creation contract and sync-stop semantics into one durable proof surface.
