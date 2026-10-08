# Execution return review page: attempted, partial, complete, disputed, and needs-acceptance interface spec

## Purpose

This page exists to stop one dangerous collapse:

- mandate issued
- operator did work
- some evidence exists
- therefore completion must be accepted

That collapse is not allowed.

## Page question

> given the returned work and witnesses, what is the strongest honest verdict on this completion claim?

## Layout

1. **Return claim strip**
2. **Evidence-versus-scope matrix**
3. **Reviewer verdict ladder**
4. **Residual routing card**
5. **Blocked stronger sentence**

### 1) Return claim strip

Show side by side:

- assignee claimed class
- evidence freshness
- mandate scope requested
- scope actually evidenced
- side effects introduced
- residual duty declared by assignee

### 2) Evidence-versus-scope matrix

Rows are mandate obligations.
Columns are:

- `requested`
- `attempted`
- `effect observed`
- `evidence attached`
- `reviewer accepted`
- `needs follow-on`

Hard rule:

A green matrix cell in `effect observed` may still leave `reviewer accepted` gray.
Observation is weaker than acceptance.

### 3) Reviewer verdict ladder

Supported `reviewer_verdict` values:

- `insufficient-evidence`
- `attempt-confirmed-no-sufficient-effect`
- `effect-confirmed-scope-incomplete`
- `complete-needs-requester-acceptance`
- `accepted-exact-scope`
- `accepted-partial-scope`
- `accepted-with-side-effect-debt`
- `disputed-overclaim`
- `return-invalid-because-authority-shifted`

Hard rules:

- `accepted-exact-scope` requires that all requested obligations for the covered scope are reviewer-accepted
- `accepted-partial-scope` requires an explicit split of the uncovered remainder
- `accepted-with-side-effect-debt` requires a linked debt or case object
- `complete-needs-requester-acceptance` may be used when reviewer sees strong evidence but cannot finalize claimant success alone

### 4) Residual routing card

Route every non-exact verdict to one or more of:

- `collect-more-evidence`
- `continue-observation-window`
- `spawn-cleanup-mandate`
- `spawn-repair-mandate`
- `reopen-case`
- `downgrade-certificate`
- `cancel-remaining-work`

Hard rule:

`accepted-partial-scope` without an explicit routing for the uncovered remainder is illegal.

### 5) Blocked stronger sentence

Always end with:

- strongest now safe sentence
- next stronger blocked sentence
- condition that would unlock the stronger sentence

## Review shortcuts

Allowed reviewer actions:

- **Confirm attempt only**
- **Accept covered scope**
- **Split remainder**
- **Mark disputed**
- **Return for rework**
- **Invalidate due to supersession**

Forbidden shortcut:

- **Mark all done from status badge alone**

## Empty state

If the delegate has not returned anything yet, show:

- `No execution return has been received for this mandate.`
