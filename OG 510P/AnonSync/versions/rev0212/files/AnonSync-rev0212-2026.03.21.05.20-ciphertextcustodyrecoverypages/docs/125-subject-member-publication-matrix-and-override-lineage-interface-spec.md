# Subject-member publication matrix and override-lineage interface spec

## Purpose

`124-constellation-publication-and-arrival-policy-interface-spec.md` makes publication a reviewed per-subject act.
That is necessary.
It is still not sufficient.

A real operator also needs one at-a-glance answer to a broader operational question:

> across all the members I care about, which subjects are actually published where, through what template or override, with what arrival posture, and with what unresolved local work still left?

Without that answer, the product can still recreate the Resilio seam in a slower, more respectable-looking way.
The operator stops reading one explicit publication review and starts reconstructing the living publication truth from memory, defaults, and whichever member currently looks familiar.

This document defines the matrix view and override lineage needed to keep publication inspectable after the first review moment is over.

## Why this needs its own spec

Current Resilio docs again make the need visible by negative example.
They describe linked devices, global synchronization modes, default arrival behavior for new folders, reconnect behavior that can suggest a different path, and duplicate `(1)` folders when that suggestion is not corrected.
Those docs are individually understandable.
Together they imply that the operator often learns the living publication state indirectly:

- from what happened to appear on one device
- from which device-wide mode was set earlier
- from whether reconnect created a new path or reused an old one
- from whether the user remembers which members are linked and therefore ambiently eligible

AnonSync should refuse that reconstruction burden.

If publication is per-subject and per-member explicit, then the operator should be able to inspect it as a first-class matrix rather than by reading a stream of historical publication receipts one by one.

## Core rule

The product must be able to render current publication truth as a **subject × member matrix** with explicit override lineage.

The matrix is not a cosmetic dashboard.
It is the public explanation of why a subject is or is not visible on a member.

Every visible matrix cell must keep seven truths inspectable:

1. whether the subject is unpublished, published, withdrawn, or stale on that member
2. what arrival posture that member currently receives
3. whether the cell comes from direct review, inherited template, or later override
4. whether local claim/bind/materialization is still unresolved on that member
5. whether authority widened or visibility only changed
6. which receipt most recently established or changed the cell
7. what the next honest action is from this cell

If the operator still has to remember `that laptop is in the selective device mode, so it probably sees new work shares`, the matrix is not strong enough yet.

## Public objects

### Publication matrix view

A read object for one matrix projection over some subject and member scope.

Suggested fields:

- `publication_matrix_view_id`
- `view_scope` (`subject-family`, `member-class`, `constellation`, `named-subject-set`)
- `subject_refs[]`
- `member_refs[]`
- `default_template_refs[]`
- `cell_refs[]`
- `generated_at`

### Publication matrix cell

A compact explanation object for one `(subject, member)` pair.

Suggested fields:

- `publication_matrix_cell_id`
- `subject_ref`
- `member_ref`
- `cell_state` (`unpublished`, `announced-only`, `claim-review-required`, `metadata-visible`, `encrypted-only`, `locally-claimed`, `withdrawn`, `stale-drift`)
- `authority_effect_summary`
- `local_unresolved_summary`
- `provenance_kind` (`direct-review`, `template-inherited`, `member-override`, `subject-override`, `withdrawal`)
- `provenance_ref`
- `latest_receipt_ref`
- `next_honest_action`

### Publication override review

A reviewed object for changing one inherited or direct cell without pretending to rewrite the whole matrix.

Suggested fields:

- `publication_override_review_id`
- `subject_ref`
- `member_ref`
- `current_cell_ref`
- `requested_cell_state`
- `template_ref` nullable
- `override_reason`
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Publication override receipt

A durable proof that one cell was overridden, reverted to template, or withdrawn.

Suggested fields:

- `publication_override_receipt_id`
- `subject_ref`
- `member_ref`
- `cell_before`
- `cell_after`
- `provenance_before`
- `provenance_after`
- `recorded_at`
- `proof_refs[]`

## Cell vocabulary

### `unpublished`

No reviewed publication currently makes the subject visible on this member.

### `announced-only`

The member can see that the subject exists, but still has no local bind or claimed role.

### `claim-review-required`

The member has reviewed visibility, but still needs one explicit local arrival/adoption review before any path or durable role outcome exists.

### `metadata-visible`

The member receives bounded metadata visibility only, often for routing or staging.

### `encrypted-only`

The member may store or route encrypted material without plaintext authority.

### `locally-claimed`

A local reviewed claim exists on that member.
This must still say which role and byte posture exist there rather than merely painting the cell green.

### `withdrawn`

A prior publication existed, but future publication to this member has been stopped.
Residual local state may still exist and must be inspectable separately.

### `stale-drift`

The system cannot yet prove the live cell truth matches the last reviewed posture because receipts, member state, or policy lineage no longer line up cleanly.

## Fixed inspection order

Every matrix or cell-detail surface should preserve the same order:

1. **Subjects and members in scope**
2. **Cell state and arrival posture**
3. **Why this cell has this state**
4. **What is still unresolved locally**
5. **Authority effect and non-effect**
6. **Override / rollback actions**
7. **Receipts and lineage**

### 1) Subjects and members in scope

The surface should state clearly whether the operator is looking at:

- one subject across many members
- many subjects across one member class
- a filtered constellation view
- only cells with drift, overrides, or unresolved local work

### 2) Cell state and arrival posture

The matrix should not force the operator to decode colors alone.
Each cell needs explicit text such as:

- `Announced only`
- `Claim review required`
- `Encrypted only`
- `Locally claimed: observer`

### 3) Why this cell has this state

The cell detail should say whether the current state came from:

- direct per-subject review
- inherited publication template
- subject-specific override
- member-specific override
- withdrawal or later narrowing

### 4) What is still unresolved locally

This section should say whether the target member still needs to decide:

- local role
- path
- materialization posture
- no further local work

### 5) Authority effect and non-effect

The matrix must keep visibility and authority separate.
Examples:

- `Visibility widened only`
- `Encrypted replica only; no plaintext writer`
- `Observer role claimed locally; no re-share right`

### 6) Override / rollback actions

The operator should be able to review one cell without rewriting the whole matrix.
Typical actions include:

- `Override this cell`
- `Revert to template`
- `Withdraw from member`
- `Escalate stale drift`

### 7) Receipts and lineage

Every cell detail should link to the most recent establishing receipt and, when relevant, the template or override lineage that explains current state.

## Matrix anatomy

A matrix view should preserve stable textual axes:

- rows: subjects
- columns: members or member classes
- cells: explicit state + role/effect summary
- side drawer: lineage, unresolved local work, and receipt links

Illustrative matrix:

```text
                 Travel-Laptop        Home-NAS             Phone
Finance-Q2       Claim review         Encrypted only       Unpublished
Family-Photos    Locally claimed      Announced only       Announced only
Scans            Unpublished          Locally claimed      Metadata visible
```

Hover, focus, or selection detail for `Family-Photos × Home-NAS` should say:

```text
State: Announced only
Why: inherited from Personal-media template
Local unresolved: path and claim still local
Authority effect: visibility only
Receipt: pubr_01J...
Next: review member override or leave as-is
```

## Cross-surface rules

### Rule 1 — the matrix is explanation, not merely monitoring

It should answer `why visible here?` and `why not visible here?`, not just paint activity.

### Rule 2 — inherited defaults must be inspectable as defaults

A template-inherited cell must say that it is inherited.
Do not let inheritance masquerade as a direct one-off review.

### Rule 3 — override scope must stay narrow

Changing one cell should not silently rewrite sibling cells that merely share a member, subject family, or template unless the review explicitly says so.

### Rule 4 — local claim state must not erase publication provenance

A cell that progressed from `claim-review-required` to `locally-claimed` must still preserve how the member first became eligible to see the subject.

### Rule 5 — stale drift must stay visible

If the product cannot currently prove the live member state matches the last receipted publication posture, the cell should show `stale drift` rather than bluffing certainty.

## Workbench expectations

The workbench should expose a dedicated matrix view where the operator can filter by:

- subject family
- member class
- cells with unresolved local work
- cells with overrides
- cells with stale drift
- cells where authority widened

This is the practical answer to the Resilio-style `remember which device mode is doing what` problem.

## CLI/TUI parity

Textual clients should offer both tabular and per-cell detail forms.

Example:

```text
anonsync publication matrix --subjects work,media --members all

SUBJECT         Travel-Laptop         Home-NAS              Phone
workdocs        Claim review          Unpublished           Unpublished
family-photos   Announced only        Encrypted only        Announced only
scans           Locally claimed       Locally claimed       Metadata visible
```

Cell detail:

```text
anonsync publication matrix show --subject family-photos --member home-nas

State: encrypted only
Why: direct review, later member override
Local unresolved: no local plaintext claim needed
Authority effect: storage visibility only; no plaintext writer
Receipt: pubor_01J...
Next: revert to template or keep current override
```

## Acceptance test

The matrix is good enough when a cautious operator can answer all of the following without reading a pile of old receipts manually:

- which subjects are currently visible on which members
- what posture each visible cell actually means
- whether a cell came from direct review, template inheritance, or override
- what local work is still unresolved on the target member
- whether the cell widened authority or visibility only
- what exact receipt most recently established or changed that cell
