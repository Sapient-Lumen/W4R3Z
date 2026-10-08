# Teacher/tutor move-coach feasibility run card

Evaluation class: `FEASIBILITY_AND_USABILITY_ONLY`

## Purpose

Test whether a teacher or tutor can use AI-generated next-move suggestions without answer leakage,
loss of human judgment, hidden workload, access failure, or obvious harm to independent transfer.
This is not an efficacy trial.

## Before the cycle

Open `DISCOVERY-FIRST-CONTACT.md` first and use it to secure the local educator conversation.
Then complete `OWNER-PLAN.md` and use `CYCLE-RUN-SHEET.md`; do not let the archive choose the concept or stretch beyond one local cycle.

1. The owner names a real local instructional problem and selects one concept.
2. The owner writes one baseline item and one no-AI transfer or explanation check before coach use.
3. The owner records tool, provider, model/version, configuration, date, and prompt-card hash.
4. The owner confirms age-appropriate notice, assent/consent or participation rules under local
   policy, and a no-penalty non-AI route.
5. The owner defines the local small-cell/suppression threshold and names the protected local reviewer
   for any subgroup or access concern.
6. The owner chooses one aggregate learner-voice prompt: helped me think, neutral, confused me, or
   preferred the non-AI route.
7. The owner names the post-cycle local attestation route without putting a signature, name, email, or
   contact route in the packet.

## During the cycle

AI may suggest one probing question, one misconception check, and one smallest-useful hint after a
learner attempt. The human chooses, edits, or rejects every suggestion.

Stop for final-answer leakage, grade/record/discipline/risk/disability inference, unavailable human
review, access or fallback failure, unacceptable burden, model/configuration drift, or obvious
transfer harm.

## Readiness split

Before the cycle, readiness may return `READY_FOR_LOCAL_CYCLE_NOT_EVIDENCE` when entry fields are complete and the generated run sheet is present. That status permits exactly one locally approved cycle; after the cycle, rerun readiness with aggregate rows. Only `READY_FOR_LOCAL_OWNER_REVIEW_NOT_EVIDENCE` can route to owner-review stop recording.

## After the cycle

Record aggregate counts and minutes only. Transfer and learner voice are descriptive. The owner may
retire, repeat narrower, continue one more bounded feasibility cycle, or escalate to formal pilot
review. None of those choices is an effectiveness claim.

```bash
make micro-pilot-readiness PACKET=scratch/field-handoff/rev0336/teacher-tutor-micro-pilot/teacher-selected-concept WRITE=1
make micro-pilot-next PACKET=scratch/field-handoff/rev0336/teacher-tutor-micro-pilot/teacher-selected-concept WRITE=1
```

## Boundary

No names, raw work, screenshots, transcripts, small cells, gradebook rows, protected facts, or
security payloads enter the release archive. No real pilot evidence or `FT-0181` closure is created.

## rev0336 prompt/run-sheet stability

Do not edit `COACH-PROMPT.md`, `RUN-CHECKLIST.md`, `MEASURE-CARD.md`, `DISCOVERY-FIRST-CONTACT.md`,
or `CYCLE-RUN-SHEET.md` after packet generation. If the local owner needs a different run definition,
regenerate the packet and rerun readiness. Owner review and result recording now depend on those
hashes staying stable.

## rev0336 event chronology boundary

For any post-cycle packet, `SESSION-LOG.csv` dates must be ISO and ordered baseline <= coach-use <= transfer. Owner review and result recording must occur after the latest session row. This boundary is a hot-path execution check, not evidence acceptance.

## rev0336 result-decision boundary (prior)

After a local result receipt exists, follow only the bounded decision map: `retire` stops; `repeat-narrower` and `continue-bounded` require a fresh packet and cannot be pooled as evidence; `escalate-to-pilot-review` requires a separate future accepted route and emits no evidence-import command.

## rev0336 fresh-packet seed rule

A `repeat-narrower`, `continue-bounded`, or `escalate-to-pilot-review` decision must be accompanied by a source-result hash-linked fresh-packet before owner review. The seed names the next local constraint and one required change, but it remains local. The archive records status only.

## rev0336 repeat/continue bridge

After a legitimate local result, do not manually reuse the old packet. A repeat or continue decision must generate a fresh source-linked packet. Use `make micro-pilot-followthrough-pack SOURCE_RESULT=scratch/.../MICRO-PILOT-RESULT.json CONFIRM=source-result-read-for-local-followthrough-not-evidence ...` and complete a new owner plan before any next local cycle.
