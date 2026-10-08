# Cube deep audit rev0240: first-contact target inversion

## Bottom line

The riskiest unfinished work is still `FT-0181`: no `SRC2+` owner-reviewed pilot packet has arrived.
The highest-value correction in this pass was not another downstream gate. It was changing the first
owner target.

Earlier revisions kept `AIEDU-SR-004` middle-school hint tutor as the preferred first target, with
`AIEDU-SR-003` capped assignment-reminder workflow as the fallback. That was substantively tempting
because the hint tutor tests learning and construct preservation, but it made the first real-contact
step harder than it needed to be. Minor-facing tutoring evidence is more likely to need raw learner
attempts, prompts, teacher samples, family notice, small-cell judgment, and protected-route caution.
That makes it a bad first packet if the objective is to prove the cube can safely receive any real
owner-reviewed evidence at all.

Rev0240 inverts the target: ask first for the staff-facing capped reminder workflow and reserve the
hint tutor for a later, better-controlled import unless a teacher owner already has an aggregate
no-trace packet ready.

## What was wasteful

The cube had a quiet prestige bias toward the harder pedagogical case. Starting with the hardest
learning-rich lane made the archive look substantively ambitious, but it also increased the chance
that `FT-0181` would remain stuck while maintainers added more doctrine around an unavailable
packet.

That is the wrong failure mode for this stage. The first real import should test the evidence
pipeline, not the hardest possible learning claim. A staff-facing, draft-only workflow can still
test source truth, action authority, rollback, false-positive handling, public claim ceilings,
workload measurement, and security boundaries. Those are enough to move the cube from rehearsal to
real-source discipline without touching raw learner work.

## What changed

- Added `docs/30-operations/ft0181-first-contact-reminder-workflow-packet.md`, a concrete first
  contact packet for `AIEDU-SR-003` with copy/paste request text, response table, triage outcomes,
  and a short outreach clock.
- Changed the real-data request target from `AIEDU-SR-004` first / `AIEDU-SR-003` fallback to
  `AIEDU-SR-003` first / `AIEDU-SR-001` fallback, while reserving `AIEDU-SR-004` for a later
  no-trace teacher-owned packet.
- Added an `outreach_preflight` section to the real-data-request schema and validator so a ready
  request must name a contact packet, owner roles, response clock, time ceiling, success definition,
  and no-silence escalation rule.
- Added an example lifecycle decision for the capped reminder workflow so the selected first target
  has the same no-real-data closure boundary as the hint tutor.
- Refactored FT-0181 sprint, owner-workbench, decision-board, change-ticket, live-window,
  data-dictionary, readiness, handoff, release, and audit language around the lower-friction first
  contact.

## New invariant

> First import should prove the pipeline with the safest real packet, not prove the hardest learning
> claim first.

That does not make the reminder workflow educationally more important than the hint tutor. It makes
it operationally more useful as the first real-source test.

## What should happen next

1. Send or adapt the reminder-workflow first-contact packet for one real course/team owner.
2. If the owner can answer from aggregate workflow logs, route the packet through the owner packet
   workbench and decision board.
3. If the owner needs a full export, raw learner rows, gradebook data, protected facts, or vendor
   telemetry, block and record the reason instead of widening the request.
4. If the owner is silent after one follow-up, record `NO-OWNER-PACKET`; do not add a new control.
5. Reopen the hint-tutor lane only when a teacher owner already has aggregate no-trace evidence.

## Speculative diagnosis

The cube tends to prefer the most pedagogically meaningful case because that is where overclaiming
risk is sharpest. That instinct is good during governance design and bad during first evidence
acquisition. Evidence acquisition should minimize contact friction and privacy risk. Once a real
packet has safely crossed the boundary, the cube can tackle richer learning evidence.

## Closure boundary

Rev0240 does not import real pilot evidence, does not close `FT-0181`, does not upgrade synthetic
examples into source evidence, and does not prove learning, safety, access, workload, compliance, or
service effectiveness. It makes the first owner contact more likely to happen and less likely to
require protected or raw learner data.
