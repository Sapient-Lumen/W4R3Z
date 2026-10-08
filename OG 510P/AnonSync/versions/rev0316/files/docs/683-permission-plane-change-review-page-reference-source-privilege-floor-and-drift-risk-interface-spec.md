# Permission-plane change review page: reference source, privilege floor, and drift risk interface spec

## Purpose

This review page exists because changing permission behavior is not one scalar toggle.
A change can:

- remove permissions from the comparison equation
- switch from reference authority to local inheritance
- widen from portable subset to full owner/group application
- create a privilege gap that turns a promised mode into a lie
- require subject recreation or epoch split instead of a live flip

The operator must review those consequences before commit.

## Review sections

Render the following sections in order:

1. **Current contract**
2. **Requested contract**
3. **Authority consequences**
4. **Privilege and substrate consequences**
5. **Drift and resettlement risk**
6. **Action choices**
7. **Receipt promise**

### 1) Current contract

Show:

- current mode
- current authority basis
- current substrate/apply class
- whether permissions participate in drift detection
- current safe sentence

### 2) Requested contract

Show:

- requested mode
- requested authority basis
- whether the change is live, recreate-only, or blocked
- subjects / seats affected

### 3) Authority consequences

Show:

- whether a reference seat becomes required, optional, replaced, or removed
- whether pre-seeded RW peers must re-settle against one source
- whether missing reference authority will suspend, degrade, or merely warn

The operator must be able to answer: **who becomes authoritative after this change?**

### 4) Privilege and substrate consequences

Show:

- seats that can apply the requested mode natively
- seats that will only preserve for later application
- seats that will fall back to local re-inheritance or reduced claim ceilings
- missing privilege rights that would make the requested mode dishonest

The operator must be able to answer: **which seats can actually honor the requested contract?**

### 5) Drift and resettlement risk

Show:

- whether permission differences will start or stop participating in sync decisions
- whether existing trees need re-comparison, initial settlement, or explicit re-rooting
- whether scrambled / merged RW permission state is currently suspected
- expected blast radius: `seat-local`, `subject-wide`, `reference-wide`, `epoch-split`

The operator must be able to answer: **what new work or drift becomes possible after apply?**

### 6) Action choices

Offer only honest actions:

- `Apply live`
- `Create successor epoch`
- `Recreate subject with requested mode`
- `Set reference first`
- `Keep current contract`
- `Block until privilege gap is repaired`

Each choice must state claim ceiling afterward.

### 7) Receipt promise

The resulting receipt must prove:

- requested mode
- effective mode
- authority basis after apply
- seats downgraded to deferred-apply / local-reinherit / no-compare
- whether recreation or resettlement was required
- strongest safe sentence afterward

## Review object

Fields:

- `permission_plane_review_id`
- `subject_ref`
- `current_mode`
- `requested_mode`
- `current_authority_basis`
- `requested_authority_basis`
- `current_compare_participation`
- `requested_compare_participation`
- `affected_seats[]`
- `privilege_findings[]`
- `substrate_findings[]`
- `authority_findings[]`
- `resettlement_required` boolean
- `apply_path` (`live`, `recreate`, `successor-epoch`, `blocked`)
- `claim_ceiling_after_apply`

## Acceptance criteria

A user can:

- see whether the change is really live or recreate-only
- see whether reference authority changes
- see which seats cannot honor the requested mode
- see whether permission differences will begin or stop triggering sync work
- prove afterward what actually became effective
