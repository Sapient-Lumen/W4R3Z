# Existing-folder adoption review page — lineage proof and duplicate-suffix veto interface spec

## Purpose

Give the operator one reviewed answer to:

- whether an existing non-empty path is the intended continuation of this share
- whether the existing material is unrelated, partially matching, or same-lineage enough to adopt
- whether the safest answer is adopt, compare deeper, choose another path, or keep the share unbound
- why duplicate-suffix fallback is forbidden here

This page is the collision and adoption companion to `99-arrival-placement-suggestion-and-collision-review-interface-spec.md` and the repair companion to `158-adopt-rebind-reconnect-and-pre-existing-path-repair-interface-spec.md`.

## Inputs

- share identifier
- seat identifier
- candidate path
- current path occupancy (`empty`, `nonempty`, `managed-bind-held`, `case-fold-collision`, `unreadable`, `unknown`)
- lineage evidence grade (`strong-match`, `probable-match`, `ambiguous`, `conflict`, `none`, `unknown`)
- candidate namespace risk (`would-create-sibling-duplicate`, `would-shadow-intended-old-path`, `clean`, `unknown`)
- strongest safe sentence
- stronger forbidden sentence
- available next actions

## Primary questions this page must answer

1. Is this existing directory actually the right continuation for this share?
2. What evidence supports or blocks adoption?
3. Would suffixing or cloning create misleading duplicates?
4. What is the safest next action now?
5. What receipt will later prove why adoption was or was not allowed?

## Layout

### A. Adoption verdict strip

Fields:

- share label
- candidate path
- occupancy class
- lineage evidence grade
- namespace risk
- strongest safe sentence

Example verdicts:

- `Existing directory /srv/photos/Photos-2026 is a probable continuation but still contains unmatched local-only material; adopt only after compare.`
- `Candidate path would create a sibling duplicate beside a remembered prior bind; suffix creation is vetoed.`

### B. Occupancy card

Show:

- whether the path is empty or non-empty
- whether another managed bind already holds it
- whether the filesystem comparison could be completed
- freshness of the inspection

### C. Lineage-evidence card

Show:

- strongest lineage evidence available
- what matched (`subject identity`, `custody markers`, `content signatures`, `prior receipt`, `path continuity`)
- what did not match
- what remains unknown

The operator must be able to answer: `why does the product think adoption is safe, risky, or blocked?`

### D. Duplicate-veto card

Show explicitly:

- whether automatic `(1)` suffix creation would hide a real continuity problem
- whether creating a fresh sibling directory would misstate reconnect or restoration success
- policy line: `duplicate-suffix fallback is not a valid resolution for managed-bind collisions`

### E. Outcome ladder

Show only honest actions:

- `Adopt existing directory`
- `Compare deeper before adopt`
- `Choose alternate empty path`
- `Keep share unbound`
- `Escalate because another managed bind owns this path`

Each action should state what claim the receipt will later be allowed to make.

### F. Claim-ceiling card

Show together:

- strongest approved sentence
- stronger forbidden sentence
- blocker basis

Example:

- approved: `This existing directory may be adopted only after compare; automatic sibling creation is vetoed.`
- forbidden: `Reconnect is safe here, so create Photos-2026(1) and continue.`
- blocker basis: `non-empty target plus unresolved lineage gaps`

## Compact row contract

A truthful compact adoption row should preserve this order:

1. share
2. candidate path
3. occupancy class
4. lineage grade
5. duplicate risk
6. next honest action

Example:

```text
Photos-2026    /srv/photos/Photos-2026    non-empty    probable-match    suffix veto    Compare before adopt
```

## Success criteria

A good page lets a later operator answer:

1. whether the existing path was empty, occupied, or disputed
2. what evidence supported or blocked adoption
3. why automatic suffix fallback was rejected
4. what exact next action remained honest
5. what later receipt would prove the verdict
