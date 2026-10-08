# External edit lane page — live provider, copy-return, branch creation, and commit-back contract interface spec

## Purpose

This page answers one ordinary question:

> when I open this file in another app, is that app editing the authoritative synced bytes, a temporary copy, or a new branch that must be committed back manually?

The page exists because `Open in another app` can mean very different things on different substrates and seats.
The operator needs one direct statement of what authority and replacement contract actually holds.

## Core decision

Every subject that can be handed to another app must expose one first-class **External edit lane** page.
The page owns:

- current lane class
- source of authority while editing
- commit-back path
- duplicate/branch risk
- permission and replacement constraints

## Primary layout

The page always renders the same regions in the same order:

1. lane verdict strip
2. authority path card
3. commit-back contract card
4. branch / duplicate risk card
5. permission and replacement card
6. receipt history

### 1) Lane verdict strip

Show:

- subject label
- lane class (`live-provider`, `copy-return`, `copy-branch`, `view-only-export`, `blocked`, `unknown`)
- authority holder during edit (`same file`, `imported copy`, `temporary export`, `outside-app branch`, `unknown`)
- strongest honest summary
- one honest next action

### 2) Authority path card

This card publishes:

- whether the outside app edits the authoritative bytes directly
- whether the file is imported or copied into the outside app
- whether Sync continues to observe the edited object automatically
- whether the operator must bring the modified object back explicitly

The operator must be able to answer: **what object am I really editing?**

### 3) Commit-back contract card

This card publishes:

- how a modified result returns (`automatic`, `save in place`, `send back manually`, `re-import manually`, `not supported`)
- target folder / original-path expectation
- whether the original can be replaced
- whether old and new versions may coexist

The operator must be able to answer: **how do the changed bytes become authoritative again?**

### 4) Branch / duplicate risk card

This card publishes:

- whether the original and modified versions may coexist
- whether the product can automatically replace the original
- whether the result is better described as `updated original` or `new sibling version`
- what cleanup or adjudication remains manual

The operator must be able to answer: **am I editing in place or creating a branch that I must settle?**

### 5) Permission and replacement card

This card publishes:

- minimum permission needed to commit back
- whether read-only / observer posture blocks commit-back
- whether mobile/platform rules forbid automatic replacement
- strongest safe sentence about what the operator is allowed to claim afterward

The operator must be able to answer: **can I actually publish this edit back from here?**

### 6) Receipt history

Show the latest external-edit receipt, recent commits, unresolved duplicates, and blocked commit attempts.

## Public object

### `external_edit_lane_explainer`

Fields:

- `external_edit_lane_explainer_id`
- `subject_ref`
- `seat_ref`
- `lane_class`
- `authority_holder`
- `commit_back_method`
- `replacement_capability`
- `duplicate_risk_class`
- `required_permission`
- `claim_ceiling`
- `generated_at`

## Non-negotiable rules

### Rule 1 — never collapse copy-return into live editing

If the outside app edits a copy, the page must say `copy-return` or `copy-branch` directly.

### Rule 2 — replacement capability must stay explicit

If the platform cannot replace the original automatically and may leave old/new versions side by side, the page must say so directly.

### Rule 3 — commit permission must stay adjacent

If the operator lacks the permission needed to commit the edit back, the page must say so before they leave for the outside app.

## Honest outputs

The page may conclude:

- `This seat uses copy-return editing. The outside app edits an imported copy, not the authoritative synced object.`
- `Modified bytes must be sent back manually to the original folder; automatic replacement is not available on this platform.`
- `The result may appear as both old and new versions until the operator settles the branch.`

It may not flatten those truths into `Edit externally` or `Open in…` alone.
