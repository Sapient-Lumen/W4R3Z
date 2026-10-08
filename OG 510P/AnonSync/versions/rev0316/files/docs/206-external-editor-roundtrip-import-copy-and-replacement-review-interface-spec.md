# External-editor roundtrip, imported copy, and replacement continuity interface spec

## Purpose

The archive already had writer-contention, quiescent-commit, snapshot-transfer, restore, and continuity-cost language.
What it still lacked was one explicit contract for a different but equally common mutation path:

> a constrained seat that cannot edit the authoritative file in place, so the user exports a copy to another app, edits there, and later tries to push a modified copy back into the shared subject.

Current official Resilio docs make this seam much sharper than a generic `Open in another app` affordance suggests.
They still say iOS apps cannot read files outside the application folder, that opening a file in another app copies it there, that changes are not reflected in the file stored in Sync until the user sends the modified file back, that Sync cannot replace the original document with the returned one, that the user may briefly have to delete the original and later re-add the modified copy, and that the old file can therefore disappear on other peers for a while before the edited version returns.
They also still say Sync cannot access files of other applications unless they are explicitly transferred back.

That is not an edge-case footnote.
It is a distinct mutation contract.

## Core decision

AnonSync should treat external editing on constrained seats as an explicit **roundtrip branch**.

The product must distinguish four objects:

- the authoritative shared object
- the exported working copy
- the returned candidate
- the reviewed replacement or merge action

The interface must never pretend that `open in editor` still means `edit the same authoritative object in place` when the seat actually forces copy-out and copy-back semantics.

## Why this matters

Current Resilio docs still reveal five interface mistakes AnonSync should not clone:

- the operator can begin an edit flow without first being told that the editor receives a copy rather than the authoritative file
- the return path is manual and therefore easy to forget, which hides the true state of the edited work
- replacement is not the same as return, because the old object may survive beside the new one unless a separate decision is taken
- temporary disappearance on peers can become part of the workaround rather than part of a visible reviewed replacement plan
- permissions for the return path matter, but the warning can arrive only after the user has already done editing work elsewhere

AnonSync should therefore keep one stronger rule:

> external editing must produce a visible branch/return object with replacement options, not just a hopeful import/export ritual.

## Fixed review order

Every external-editor flow should render the same sections in the same order:

1. **Export review**
2. **Working-copy status**
3. **Return and reconcile**
4. **Replacement receipt**

### 1) Export review

This section should show:

- authoritative object identity
- chosen editor/app destination
- whether the seat can edit in place or only export a copy
- write permission required for later return
- warning if return requires a reviewed replacement step

The operator must be able to answer: **am I editing the real shared object or a branch copy?**

### 2) Working-copy status

This section should show:

- export timestamp
- working-copy location/app
- whether the working copy has been returned
- whether the authoritative object changed elsewhere since export
- whether later return will require replace, merge, or duplicate retention review

The operator must be able to answer: **what is the status of the copy I exported, and is it already stale?**

### 3) Return and reconcile

This section should show:

- returned candidate identity and hash if available
- authoritative object currently in the subject
- diff/size/timestamp hints
- replacement options:
  - keep both as separate lineage
  - replace authoritative object
  - merge via external tool
  - discard returned candidate
- blast radius if replacement will temporarily withdraw or overwrite the old object

The operator must be able to answer: **how will the returned copy relate to the existing shared object?**

### 4) Replacement receipt

This section should show:

- final action taken
- whether continuity stayed on the original object or forked to a new lineage
- whether peers ever saw a temporary withdrawal
- proof that the returned candidate was applied, retained, or discarded

The operator must be able to answer: **what happened to the exported edit, and what did peers actually receive?**

## Main surface

Whenever a seat exports a file to an external editor, the subject workspace should show a persistent row such as:

- `exported working copy pending return`
- `returned candidate waiting for replacement review`
- `authoritative object changed since export`
- `returned copy retained as sibling; no in-place replace occurred`

This row must not vanish merely because the operator switched apps.

## Object model implications

AnonSync should add or strengthen these objects:

- `external_edit_export`
- `working_copy_branch`
- `returned_candidate`
- `replacement_review`
- `replacement_receipt`

Suggested fields for `external_edit_export`:

- `subject_id`
- `object_id`
- `seat_id`
- `editor_target`
- `export_kind` (`in-place`, `copy-out`)
- `return_permission_required`
- `authoritative_version_at_export`
- `working_copy_handle`

## Event language

Use explicit phrases such as:

- `copy exported to external editor`
- `working copy pending return`
- `returned candidate conflicts with newer authoritative version`
- `replacement would temporarily withdraw prior object`
- `returned candidate applied as sibling lineage`

Avoid vague lines such as:

- `opened in editor`
- `file updated`
- `changes synced`

## CLI shape

Example commands:

```text
anonsync external-edit export <object> --to <editor>
anonsync external-edit status <working-copy>
anonsync external-edit review-return <working-copy>
anonsync external-edit apply <review>
```

The CLI must preserve the same authoritative-versus-copy distinction as the GUI/local web projection.

## Failure and edge cases

### Return lacks write permission

The flow must surface `cannot return candidate: seat lacks write authority` before the operator expects automatic replacement.

### Authoritative object changed elsewhere during editing

The returned candidate must enter a real reconciliation review, not silently win by late arrival.

### Operator wants to preserve both versions

Keeping both should be an explicit lineage choice with naming proof, not an accidental duplicate caused by platform limits.

### Export was abandoned

The system should support `abandon working copy` so stale exported copies do not masquerade as pending authoritative work forever.

## The non-clone reason

This is another clean example of why AnonSync should not merely copy Resilio's surface.
Current official Resilio docs still leave too much meaning about exported copies, manual return, duplicate-versus-replace, and temporary peer disappearance scattered across iOS architectural caveats and how-to pages.
AnonSync should instead treat external editing as a first-class roundtrip branch with explicit reconciliation and receipts.
