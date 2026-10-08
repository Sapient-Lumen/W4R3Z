# Role-first arrival and path-materialization review interface spec

## Purpose

The archive already has:

- claim/adoption intake review
- local presence and mode decomposition
- placement suggestion and collision review
- publication review and matrix visibility

What still remained too easy to blur was the first local choice after a subject becomes visible on a member:

> before the operator chooses a path, default folder, or byte posture, what role should this member actually have for this subject?

Current Resilio docs make the problem plain by the workaround they still recommend.
When the goal is `this linked device should get this folder read-only` or `this one member should pick its own safe location`, the operator is still often sent through device-wide mode changes, disconnect/reconnect ritual, or manual read-only key flows.
That is not because the user wanted a weird path ritual.
It is because role, path, and arrival mode are still too entangled.

AnonSync should refuse that shape.

## Core rule

For every newly visible or newly re-reviewed arrival, the product must ask **role before path and materialization**.

The public question order is:

1. what role may this member honestly hold for this subject
2. which local outcome follows from that role
3. which path and byte posture best fit that chosen role

Not the other way around.

The product may offer path hints.
It may not let a path picker, a device-wide arrival mode, or a remembered key class decide the role by accident.

## Why this needs its own spec

If a product lets the operator choose a folder path first, three kinds of confusion return quickly:

- a path that looks local and durable gets mistaken for accepted authority
- a byte posture such as placeholders or full sync gets mistaken for the actual granted role
- least-privilege goals (`observer`, `encrypted replica`, `writer later after review`) are translated into transport ritual instead of one honest choice

Resilio's current docs still point to exactly this seam:

- linked devices default to broad owner-like treatment
- custom placement often depends on switching the whole target member into `Disconnected` first
- read-only on a linked member still goes through a read-only key workflow and reconnect choreography
- reconnect may suggest a different path and create `(1)` duplicates unless the operator catches it

The non-clone answer is therefore not `make the path picker prettier`.
It is:

> make the role sheet first, then make every later path or materialization choice subordinate to that role.

## Public objects

### Arrival role sheet

A review object that states the admissible roles for one subject on one member and the consequences of each role.

Suggested fields:

- `arrival_role_sheet_id`
- `subject_ref`
- `member_ref`
- `source_publication_ref`
- `current_cell_ref`
- `admissible_roles[]`
- `recommended_role`
- `current_role` nullable
- `role_findings[]`
- `receipt_refs[]`

### Path-materialization review plan

A plan object prepared only after a role has been chosen.

Suggested fields:

- `path_materialization_review_plan_id`
- `subject_ref`
- `member_ref`
- `chosen_role`
- `path_hint_ref` nullable
- `chosen_path` nullable
- `materialization_posture` (`announce-only`, `metadata-only`, `placeholder-capable`, `partial`, `full`, `encrypted-store`)
- `collision_findings[]`
- `effect_summary`
- `non_effect_summary`
- `receipt_promise`

### Arrival adoption receipt

A durable proof that one member adopted one subject with one role and one later path/materialization posture.

Suggested fields:

- `arrival_adoption_receipt_id`
- `subject_ref`
- `member_ref`
- `role_before` nullable
- `role_after`
- `path_before` nullable
- `path_after` nullable
- `materialization_before` nullable
- `materialization_after`
- `recorded_at`
- `proof_refs[]`

## Role vocabulary

### `announce-only`

The member may see the subject exists but has not yet adopted a local role.

### `observer`

The member may inspect and fetch according to policy, but cannot publish mutations for others.

### `writer`

The member may hold writable local state and publish legitimate mutations.

### `issuer`

The member may issue narrower offers or continue sharing within reviewed policy.

### `approval-seat`

The member may act as a reviewed approval seat for bounded future requests.

### `encrypted-replica`

The member may store or relay ciphertext without plaintext authority.

### `quarantined-review`

A temporary posture for suspicious or ambiguous arrivals where local inspect may continue but broader role adoption is blocked.

## Fixed review order

Every arrival/adoption surface should preserve the same order:

1. **Subject, member, and source posture**
2. **Admissible roles**
3. **Chosen role and authority consequences**
4. **Path and materialization choices**
5. **What this does not mean yet**
6. **Receipt promise and later promotion/demotion**

### 1) Subject, member, and source posture

This section should say:

- which subject is in scope
- which member is about to adopt or re-review it
- how the subject became visible here
- whether the current posture is only `announced`, `claim review required`, or something already stronger

### 2) Admissible roles

The sheet should list only roles that are actually admissible under the current publication, offer, and approval posture.
The operator should not see a `writer` choice if the upstream posture only allows `observer`.

### 3) Chosen role and authority consequences

This section should state:

- what the chosen role allows
- what it forbids
- whether later promotion would require another review
- whether the role says anything about re-share, approval, or successor rights

### 4) Path and materialization choices

Only after role selection should the operator choose:

- no path yet / staged only
- specific reviewed path
- template-derived suggestion
- materialization posture suitable for the role

Examples:

- `observer` + `placeholder-capable`
- `writer` + `full`
- `encrypted-replica` + `encrypted-store`

### 5) What this does not mean yet

This section should aggressively publish non-effects.
Examples:

- choosing a path does not promote `observer` to `writer`
- choosing `full` bytes does not imply `issuer`
- choosing `encrypted-store` does not imply plaintext access
- adopting `announce-only` does not imply a durable bind

### 6) Receipt promise and later promotion/demotion

This section should say which receipt will prove the chosen role and what later review would be required to widen or narrow it.

## Action ordering rules

### Rule 1 — no device-wide mode flip for one subject

If one member needs a special posture for one subject, the interface must offer a per-subject review.
Do not ask the operator to change the whole member's default mode merely to make one arrival safe.

### Rule 2 — path pickers may not smuggle role decisions

A destination chooser cannot silently imply `writer`, `observer`, or `encrypted replica`.
The role sheet must say so explicitly first.

### Rule 3 — byte posture is subordinate to role

`Placeholder`, `full`, `partial`, and `encrypted-store` are byte postures.
They do not define authority.
The surface should never let them masquerade as permission labels.

### Rule 4 — reconnect must preserve prior role truth explicitly

If a subject is re-adopted, the sheet must compare the prior role and new request.
Do not let reconnect ritual accidentally widen rights.

### Rule 5 — role promotion needs fresh review

`Observer → writer`, `writer → issuer`, and `observer → approval-seat` are meaningful authority changes.
They require a new reviewed plan even when path and bytes stay unchanged.

## Dense row contract

An arrival row should preserve these labels in this order:

- `Subject`
- `Visible here as`
- `Role now`
- `Path / bytes`
- `Not enough for`
- `Next action`

Example:

```text
Family-Photos   claim review required   no role chosen yet   no path, no bytes   not enough for write or share   Review role
```

After adoption:

```text
Family-Photos   locally claimed         observer             /srv/media, placeholders   not enough for writer or issuer   Fetch or promote
```

## Workbench expectations

The workbench should expose a role-first adoption sheet from:

- the inbox row
- the publication matrix cell
- the subject detail pane
- any stale-drift or reconnect warning

The operator should never have to infer role from a path picker, an icon, or a device mode badge.

## CLI/TUI parity

Textual surfaces should preserve the same order.

Example:

```text
anonsync arrival review --subject family-photos --member travel-laptop

Visible here as: claim review required
Admissible roles: observer, encrypted-replica
Chosen role: observer
Path options: none yet, /home/ben/Pictures/family-photos
Materialization options: placeholders, partial, full
Not enough for: writer, issuer
Next: prepare reviewed adoption
```

Apply example:

```text
anonsync arrival adopt --subject family-photos --member travel-laptop --role observer --path /home/ben/Pictures/family-photos --materialization placeholders --plan
anonsync arrival apply arplan_01J...
```

## Acceptance test

The role-first arrival surface is good enough when a cautious operator can answer all of the following without relying on device-mode folklore:

- what role this member may honestly have for this subject right now
- which stronger roles are blocked and why
- what local path and byte posture choices follow from the chosen role
- what those path and byte choices do **not** change
- whether reconnect or re-adoption widened anything
- what receipt will later prove the adopted role and local posture
