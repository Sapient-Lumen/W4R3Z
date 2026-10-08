# Maintenance rejoin plan page — local residue, promotion, and authority-choice interface spec

## Purpose

The archive already has maintenance intent, mutation budget, mutation review, and mutation receipts.
What it still lacked was one ordinary page for the next question:

> now that local work happened under a hold or narrow seat, what exact path could return that work to the shared line, if any?

This page exists so a user does not mistake `work still exists somewhere` for `work can rejoin cleanly`.

## Core decision

AnonSync must expose one first-class **Maintenance rejoin plan** page whenever local work performed under a maintenance contract, read-only seat, backup-like lane, encrypted custody lane, or other narrow posture is being evaluated for possible shared-line restoration.

The page exists to answer five things in one place:

1. what local work or residue set is under consideration
2. which rejoin paths are truly available
3. which path changes authority versus merely preserving bytes
4. which path risks overwrite, abandonment, or side-branch creation
5. what sentence is honest before any rejoin step begins

## Fixed page order

1. **Candidate rejoin verdict**
2. **Rejoin path matrix**
3. **Authority and overwrite barriers**
4. **Promotion / successor options**
5. **Actions and receipts**

### 1) Candidate rejoin verdict

Show:

- `maintenance_rejoin_plan_page_id`
- scope (`seat`, `subject`, `path slice`, `held window`, or `residue set`)
- governing maintenance or narrow-posture reference
- candidate work class (`edited-existing`, `added-local`, `renamed-local`, `deleted-local`, `restored-local`, `mixed`, `unknown`)
- current rejoin verdict (`rejoin-in-place`, `rejoin-by-authority-change`, `rejoin-by-promotion`, `preserve-only`, `abandon-or-overwrite`, `unknown`)
- strongest honest summary
- stronger unsupported summary

The operator must be able to answer:

> what exact kind of local work am I trying to bring back into the shared line?

### 2) Rejoin path matrix

This section is mandatory.
Show rows for at least:

- rejoin in place under current authority
- reviewed rights or posture widening
- export to side branch then promote
- compare against remote/source winner
- keep as local-only preserved residue
- overwrite or abandon knowingly
- restore from source / archive instead of promoting local work

Each row must show one state:

- `available now`
- `available after reviewed widening`
- `available only through successor artifact`
- `preserve-only`
- `destructive to local work`
- `blocked`
- `unknown until more evidence`

The page must answer:

> what are the real rejoin paths, not just the comforting ones?

### 3) Authority and overwrite barriers

Show, for each serious path:

- current authority ceiling
- whether remote or source authority still dominates
- whether overwrite can happen before rejoin completes
- whether added files differ from edited existing files
- whether Selective Sync, encryption, or seat-local disconnect posture blocks the path
- strongest safe sentence and stronger forbidden sentence

The operator must be able to answer:

> what must change before this work can honestly count as shared again?

### 4) Promotion / successor options

Show safer structured alternatives such as:

- `Promote exported branch`
- `Open candidate-winner compare`
- `Request reviewed rights widening`
- `Preserve as evidence only`
- `Restore source-authoritative version`
- `Accept abandonment / overwrite`

Each option must state:

- resulting continuity class
- whether the original local work stays canonical, derivative, or abandoned
- what later receipt it will produce

The page must answer:

> if in-place rejoin is weak or impossible, what is the cheapest honest successor lane?

### 5) Actions and receipts

Actions may include:

- `Proceed with in-place rejoin`
- `Request reviewed widening`
- `Promote through successor lane`
- `Open compare before promotion`
- `Preserve local-only and stop`
- `Accept overwrite / abandonment`
- `Cancel`

Receipts must record candidate work, chosen rejoin path, authority barrier, overwrite risk, successor requirement, and strongest safe sentence.

## Public object

### Maintenance rejoin plan page

Fields:

- `maintenance_rejoin_plan_page_id`
- `scope_ref`
- `maintenance_or_narrow_posture_ref`
- `candidate_work_rows[]`
- `rejoin_path_rows[]`
- `authority_barrier_rows[]`
- `promotion_option_rows[]`
- `strongest_safe_sentence`
- `stronger_rejected_sentence`
- `next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. scope
2. candidate work
3. best available rejoin path
4. strongest barrier
5. next action

Example:

```text
Evidence-hold seat     edited-existing     rejoin-by-promotion     remote authority would overwrite in-place heal     Open compare before promotion
```

## Non-goals

This page does **not** prove that rejoin already happened.
It proves only the reviewed **rejoin path matrix, authority barrier, and successor ladder**.
