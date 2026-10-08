# Service-root contamination, self-embedding boundary, and whole-tree admission interface spec

## Purpose

The archive already had hidden service-state and seat-switch attribution language.
What it still lacked was one interface contract for a more basic admission mistake:

> when a user points sync at a broad tree that already contains the daemon's own storage, identity, logs, or licensed-control state, what page blocks the bind and explains the self-embedding hazard before the product mutates anything?

Current official Resilio docs make this seam more concrete than a generic `don't sync your home directory` warning.
They still describe a dedicated storage folder that contains current configuration, auxiliary settings, shares' database, debug logs, and identity details, and they still list different storage locations for normal desktop runs, service runs, Linux packages, NASes, and mobile installations.
A current troubleshooting page still says trying to add the user's home folder can fail specifically because it contains Sync's storage folder with a `License` directory inside, and warns more broadly that syncing the whole home folder may be flawed because it also contains system settings and other applications' configuration files that are unavailable or change too frequently.

That is a useful warning.
It is still not a good path-admission contract.

## Core decision

AnonSync should enforce one explicit **service-root boundary**.

Any attempted bind of a large tree must classify whether it includes:

- daemon storage state
- identity or credential material
- logs, dumps, or diagnostic evidence
- license/control state
- other application config churn that should not be treated as ordinary shared data

The product must then either:

- block the bind
- require explicit exclusions with receipt
- or suggest narrower child roots that preserve the user's intent without self-embedding service state

If an operator still has to discover the problem from an error after the fact, the interface is not explicit enough.

## Why this matters

Current Resilio docs still reveal six truths AnonSync should not clone:

- service state lives in ordinary filesystem paths, not in a magic invisible realm
- storage-root location changes with seat or runtime context
- identity and licensing material may sit inside broad user-visible trees
- `sync my whole home` is not a neutral convenience choice when runtime state lives there too
- broad trees also pick up high-churn config files that are poor sync subjects even when they are not security-sensitive
- support guidance still solves the problem mainly by telling the user to sync smaller folders separately

AnonSync should therefore keep one stricter rule:

> subject roots and service roots must be visibly separated, continuously policed, and reviewed before broad-tree admission.

## Fixed review order

Every non-trivial broad-tree admission should render the same sections in the same order:

1. **Candidate root and embedded state classes**
2. **Hazard classification**
3. **Safer alternatives**
4. **Receipt and policy promise**

### 1) Candidate root and embedded state classes

This section should show:

- the candidate path
- which embedded service-state classes were found
- whether those classes are currently active for this runtime seat
- whether the path also contains other high-churn non-subject state

The operator must be able to answer: **what kinds of non-user data are living inside this tree?**

### 2) Hazard classification

This section should show:

- whether the issue is security-sensitive, churn-sensitive, recursion-sensitive, or all three
- whether the hazard comes from current seat placement, historical residue, or another application's files
- whether bind is blocked, guarded, or admissible only with exclusions

The operator must be able to answer: **why is this path unsafe or noisy as a sync root?**

### 3) Safer alternatives

This section should show only honest next actions, such as:

- `Choose narrower child folders`
- `Relocate service root first`
- `Exclude embedded service state with a recorded rule`
- `Abort broad-tree admission`

The operator must be able to answer: **what narrower path or prerequisite would preserve intent without syncing runtime guts?**

### 4) Receipt and policy promise

This section should show:

- the admission review receipt
- any exclusions being recorded
- whether future scans will continue policing this boundary
- whether the service-root seat is expected to move again later

The operator must be able to answer: **what proof will later show why this broad tree was blocked or allowed?**

## Public objects

### Broad-tree admission review

Fields:

- `broad_tree_admission_review_id`
- `candidate_path`
- `runtime_seat_ref`
- `embedded_state_classes[]`
- `hazard_classes[]`
- `admission_verdict` (`allow`, `guarded`, `blocked`)
- `suggested_child_roots[]`
- `required_exclusions[]`
- `generated_at`
- `expires_at` nullable

### Service-root boundary policy

Fields:

- `service_root_boundary_policy_id`
- `runtime_seat_ref`
- `service_root_paths[]`
- `protected_state_classes[]`
- `continuous_policing` (`enabled`, `disabled`)
- `last_scan_at`
- `violation_count`

### Broad-tree admission receipt

Fields:

- `broad_tree_admission_receipt_id`
- `review_ref`
- `applied_verdict`
- `chosen_child_root` nullable
- `recorded_exclusions[]`
- `post_apply_boundary_policy_ref`
- `completed_at`

## Compact row contract

A truthful compact row should keep these facts in stable order:

1. candidate root
2. embedded state classes
3. hazard verdict
4. allowed alternative
5. next honest action

Example:

```text
/home/alex     storage + identity + license + app-config churn     blocked     /home/alex/Documents, /home/alex/Projects     Choose narrower child roots
```

The product should not let `cannot add folder` be the first moment the operator learns that service state lived inside the tree.

## CLI implications

A minimum public surface should include:

```text
anonsync root review --path <path>
anonsync root policy show --seat <seat>
anonsync root apply <broad_tree_admission_review_id>
anonsync root receipt show <broad_tree_admission_receipt_id>
```

The CLI should let an operator prove that a candidate root is free of service-state self-embedding before they commit the bind.
