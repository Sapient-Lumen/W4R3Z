# Change publication page — detected, indexed, announced, fetchable, and landed state interface spec

## Purpose

The archive already has work-phase, completeness, and availability language.
What it still lacked was one ordinary page for the changed-file question:

> where exactly is this fresh change right now between local detection, indexing, publication, remote fetchability, and landed proof?

Current official Resilio docs still let that answer sprawl across `How soon does synchronization start?`, `Some internal tasks are taking time to complete`, queue/history inspection, and generic troubleshooting.
AnonSync should instead publish one explicit chain.

## Core decision

AnonSync must expose one first-class **Change publication** page for any changed object or subtree whose freshness or propagation is materially in question.

## Fixed page order

1. **Current publication stage**
2. **Local proof chain**
3. **Current blocker and next proof**
4. **Remote availability / landed state**
5. **Honest next actions**

### 1) Current publication stage

Show a single current stage from this fixed family:

- `unseen`
- `detected-awaiting-index`
- `indexed-awaiting-verify`
- `verified-awaiting-announce`
- `announced-awaiting-fetch`
- `fetchable`
- `landed-on-some`
- `landed-on-required`
- `stalled-needs-review`

The operator must be able to answer:

> what is the strongest true thing the product can say about this change right now?

### 2) Local proof chain

Show:

- first observation time
- latest index / scan evidence
- latest verification or hash evidence
- latest announce/publication evidence
- whether current freshness basis weakens any link in the chain

### 3) Current blocker and next proof

Show:

- dominant blocker class (`detection`, `indexing`, `verification`, `route`, `source-availability`, `write-target`, `policy`, `unknown`)
- next proof point the product expects
- whether the system is progressing, retrying, or stalled
- whether the blocker is local-only or mesh-visible

### 4) Remote availability / landed state

Show:

- whether peers can fetch now
- whether any peer has already landed the change
- whether the current subject policy requires more landed sinks before stronger claims are honest
- whether a peer only knows the name, only has placeholder state, or holds full bytes

### 5) Honest next actions

Actions may include:

- `wait for next proof point`
- `inspect detection downgrade`
- `run rescan review`
- `inspect work phases`
- `inspect route / source availability`
- `open landed-proof page`

## Public object

### Change publication page

Fields:

- `change_publication_page_id`
- `subject_ref`
- `path_ref`
- `current_stage`
- `local_proof_rows[]`
- `blocker_class`
- `next_proof_point`
- `remote_fetchability_verdict`
- `landed_state_verdict`
- `next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. path
2. current stage
3. blocker class
4. remote verdict
5. next proof point

Example:

```text
/Photos/trip/IMG_0021.heic     indexed-awaiting-verify     verification     not yet fetchable     next proof: verified announce
```

## Non-goals

This page does not replace the deeper work ledger.
It gives the operator one trustworthy answer for the current **publication stage** of a concrete change.
