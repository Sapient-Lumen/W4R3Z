# Quiet cohort page — target seats, local posture, and coverage interface spec

## Purpose

The archive already has quiescence review and residual activity matrices.
What it still needs is the page that answers a different question:

> quiet for **whom**?

A serious maintenance or evidence workflow often depends on more than one seat.
One local pause may be useful, yet still insufficient.
AnonSync should therefore model the affected participant set as a first-class **quiet cohort** object.

## Core decision

Every maintenance-grade quiet request must define an explicit cohort before the product allows strong language like:

- `window started`
- `quiet enough to inspect`
- `quiet enough to migrate`
- `quiet enough for destructive repair`

The quiet cohort page answers four things:

1. which seats matter
2. what stillness class each seat is expected to match
3. what evidence currently exists for each seat
4. whether uncovered seats still weaken the claim

## Fixed review order

1. **Operation and quiet intent**
2. **Target cohort**
3. **Per-seat posture**
4. **Coverage summary**
5. **Uncovered seats and residual movers**
6. **Next safest action**

## 1) Operation and quiet intent

Show:

- operation kind (`maintenance`, `evidence-capture`, `migration-cut`, `destructive-repair`, `custom`)
- target subject
- requested stillness class
- requested time window
- initiating seat / actor
- why local-only quiet would be insufficient here

## 2) Target cohort

The page must list the seats or roles that matter for this operation.

Each row must distinguish:

- explicitly targeted seat
- inferred relevant seat
- optional observer seat
- seat currently unknown but plausibly relevant

Every row must preserve why it belongs in the cohort, such as:

- currently writable peer
- currently visible source peer
- current delete-capable peer
- expected uploader during the window
- maintenance owner / witness seat

## 3) Per-seat posture

Each seat row must show:

- current state (`matched`, `locally-quiet-only`, `not-requested`, `declined`, `unreachable`, `unknown`)
- requested stop class for that seat
- current evidence basis
- strongest safe sentence for that row

Evidence basis may include:

- matched reviewed quiet receipt
- active quiet-window token
- explicit acknowledgement without proof
- recent presence with no matching quiet proof
- stale or missing evidence

## 4) Coverage summary

Publish one coverage verdict for the cohort:

- `local-only`
- `partially-covered`
- `covered-for-declared-risk`
- `fully-covered`
- `unknown`

The verdict must be computed from both:

- seat relevance
- evidence strength

Never mark a cohort `fully-covered` just because every currently visible seat is quiet if relevant absent or stale seats remain unresolved.

## 5) Uncovered seats and residual movers

List uncovered seats separately.
For each uncovered seat, show:

- why it still matters
- what perturbation class it may still cause
- cheapest next action

Perturbation classes include:

- send payload bytes
- receive payload bytes
- propagate deletes
- detect and publish new local changes
- remain only socially acknowledged, not technically matched

## 6) Next safest action

The page should recommend the lightest honest next step, such as:

- request quiet from two remaining writable seats
- narrow the operation so uncovered seats no longer matter
- proceed with weaker language only
- wait for quiet receipts to land
- abandon maintenance-grade quiet and switch to local-only operation wording

## Example projection

```text
Quiet cohort — finance/share-a

Operation ............... evidence-capture
Requested stillness ..... maintenance isolation
Window .................. 2026-03-22 01:00–02:00 UTC
Initiating seat ......... wkstn-02

Coverage summary
  verdict ............... partially-covered
  matched seats ......... 2 / 4
  uncovered movers ...... 1 writable, 1 unknown

Seat rows
  wkstn-02 .............. matched
    proof ............... local quiet receipt qrc_...
    safe sentence ....... quiet on initiating seat

  nas-01 ................ matched
    proof ............... quiet-window token qwin_...
    safe sentence ....... quiet on remote source seat

  laptop-ops ............ not-requested
    why it matters ...... writable peer still online
    risk ................ may publish local edits

  phone-audit ........... unknown
    why it matters ...... observer seat; low perturbation risk
    safe sentence ....... coverage not blocked, but watch visibility claims
```

## Commands

```text
anonsync quiet-cohort show <subject>
anonsync quiet-cohort create --subject <subject> --operation maintenance
anonsync quiet-cohort show <cohort_id> --json
```

## Success condition

A good quiet cohort page lets an operator answer:

- who still matters for this operation
- who already matched the quiet request
- who can still perturb the subject
- whether the strong maintenance sentence is actually earned yet
