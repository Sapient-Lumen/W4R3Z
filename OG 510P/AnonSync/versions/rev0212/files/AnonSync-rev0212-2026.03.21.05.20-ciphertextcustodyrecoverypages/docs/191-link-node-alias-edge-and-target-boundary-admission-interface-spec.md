# Link-node alias edge and target-boundary admission interface spec

## Purpose

The archive already had subtree topology, service-root boundary, and name portability reviews.
What it still lacked was one interface contract for filesystem indirection itself:

> when a tree contains symbolic links, junctions, hard links, or other alias edges, what page proves whether the product is syncing a name, a pointer, a target tree, or a conflict-prone unsupported shape?

Current official Resilio docs make this seam more concrete than an abstract `symlinks are tricky` warning would.
They still say Windows soft links, junctions, hard links, and symbolic links are unsupported and may produce `.Conflict` files for each entry, while on Unix symbolic links can be synchronized as links but their target folders are not synchronized unless separately added.

That is a strong present-day reason not to clone the default contract.
The operator-visible truth is not merely `contains symlink`.
It is:

- alias-edge type
- platform-specific support ceiling
- whether target bytes are actually in scope
- whether following the edge would cross a subject boundary
- whether preserving the edge versus expanding it would fork meaning

## Core decision

AnonSync should make **alias-edge admission** first-class.

Every bind or scan that encounters a link-like edge must always declare:

- the alias-edge type
- whether the edge is preserved as metadata, expanded into content, blocked, or review-required
- whether the target is inside the same admitted subject boundary
- what cross-platform portability risk exists
- whether target content is in scope now or only the edge object is

If an operator still has to learn the difference between `pointer preserved` and `target not in scope` by observing missing files on another machine, the interface is not explicit enough.

## Why this matters

Current Resilio docs still reveal five truths AnonSync should not clone:

- filesystem indirection is a graph question, not just a filename question
- platform support differences can turn the same tree into preserved links on one system and conflict generators on another
- an alias edge can make a target appear conceptually nearby while remaining operationally out of scope
- unsupported edge classes deserve admission review before indexing starts, not only after conflicts appear
- preserving the edge object and syncing its target bytes are separate choices that must be stated explicitly

AnonSync should therefore keep one stronger rule:

> alias edges must surface as typed topology objects with a declared scope decision, not as incidental caveats buried in platform notes.

## Fixed review order

Every alias-edge encounter or review should render the same sections in the same order:

1. **Edge classification**
2. **Boundary and scope**
3. **Portability and risk**
4. **Admission receipt**

### 1) Edge classification

This section should show:

- edge type (`symlink`, `junction`, `hardlink`, `reparse-like`, `unknown`)
- path of the edge object
- discovered target
- whether the target currently resolves
- whether the product can preserve the edge object at all

The operator must be able to answer: **what kind of indirection is this?**

### 2) Boundary and scope

This section should show:

- whether the target is inside the same subject root
- whether target expansion would cross a service root, another subject, or an unadmitted path
- whether the current decision is `preserve-edge`, `expand-target`, `block`, or `split-into-separate-subject`
- whether downstream peers will receive bytes, metadata only, or nothing

The operator must be able to answer: **what exactly is in scope here — the pointer, the target, both, or neither?**

### 3) Portability and risk

This section should show:

- platform compatibility ceiling
- conflict risk
- target-cycle or loop risk
- whether the decision is portable across peers
- what review is required before changing the edge policy

The operator must be able to answer: **will this meaning survive on all peers?**

### 4) Admission receipt

This section should show only honest next actions, such as:

- `Preserve edge only`
- `Expand target into same subject`
- `Create separate subject for target`
- `Block unsupported edge`
- `Replace with concrete copy under review`

The receipt must record both the edge decision and the target-boundary decision.

## Public objects

### Alias edge report

Fields:

- `alias_edge_report_id`
- `subject_ref`
- `path`
- `edge_type`
- `target_path` nullable
- `target_resolution` (`resolved`, `broken`, `relative-uncertain`, `unknown`)
- `boundary_relation` (`inside-subject`, `outside-subject`, `crosses-service-root`, `crosses-other-subject`, `unknown`)
- `generated_at`

### Alias edge admission review

Fields:

- `alias_edge_admission_review_id`
- `report_ref`
- `requested_policy` (`preserve-edge`, `expand-target`, `block`, `separate-subject`)
- `portability_risks[]`
- `loop_risk`
- `generated_at`
- `expires_at` nullable

### Alias edge receipt

Fields:

- `alias_edge_receipt_id`
- `review_ref`
- `applied_policy`
- `target_scope_decision`
- `portability_verdict`
- `completed_at`

## Compact row contract

A truthful compact row should keep these facts in stable order:

1. edge path
2. edge type
3. target-boundary relation
4. applied policy
5. next honest action

Example:

```text
/project/assets -> ../shared     symlink     outside-subject     preserve-edge only     Review separate subject for target
```

The product should not reduce that to `symlink unsupported` or silently omit target scope.

## CLI implications

A minimum public surface should include:

```text
anonsync edges scan --subject <subject>
anonsync edges show --path <path>
anonsync edges plan --path <path> --policy <policy>
anonsync edges apply <alias_edge_admission_review_id>
anonsync edges receipt show <alias_edge_receipt_id>
```

The CLI should let an operator prove whether a link-like edge preserves meaning, expands meaning, or crosses a boundary before it surprises another peer.
