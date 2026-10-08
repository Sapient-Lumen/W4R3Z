# Teacher/tutor move-coach feasibility cycle

Evaluation class: `FEASIBILITY_AND_USABILITY_ONLY`

## Purpose

Use AI as a teacher/tutor move coach after a learner attempt, not as an autonomous answer machine.
The first field question is whether a local educator can use the packet, find at least one suggestion
instructionally useful, maintain acceptable burden and access, and avoid obvious harm. It is not
whether the intervention “works” in a causal or generalizable sense.

The coach may suggest one probing question, one misconception check, and one smallest-useful hint.
The human chooses, edits, or rejects every suggestion before learner-facing use. It may not grade,
classify, write records, contact families, discipline learners, or release final answers.

## Discovery comes first

The project does not choose the curriculum problem. A local teacher or tutor must document:

- an observed instructional problem and why it matters now;
- one locally selected concept or reasoning move;
- one baseline item and one no-AI transfer/explanation check selected before coach use;
- tool/provider, model or dated product version, configuration, run date, and prompt-card hash;
- age-appropriate participation rules, an ordinary non-AI fallback, and no-penalty opt-out;
- a numeric local small-cell threshold of at least three and a protected local subgroup/access review role;
- predefined aggregate learner-voice categories without free-text quotations.

The optional equality-one-step worked kit remains available in
[`teacher-tutor-micro-pilot-measure-card-equality-one-step.md`](teacher-tutor-micro-pilot-measure-card-equality-one-step.md),
but packet availability is not evidence that equality is the local priority.

## Default entry

```bash
make field-handoff-bundle OVERWRITE=1
```

Open:

```text
scratch/field-handoff/rev0336/teacher-tutor-micro-pilot/teacher-selected-concept/OWNER-PLAN.md
```

Complete every discovery field before learner-facing use. A blank packet must remain `NOT_READY`; a locally completed owner plan may become `READY_FOR_LOCAL_CYCLE_NOT_EVIDENCE` before any post-cycle rows exist.

## One bounded sequence

| Phase | Human action | Allowed AI use | Descriptive capture | Stop when |
|---|---|---|---|---|
| discovery | name the problem, construct, owner, participation rule, fallback, and measures | drafting support only | completed owner plan and intervention identity | no genuine local problem or owner exists |
| baseline | use ordinary practice without the coach | none during learner interaction | aggregate attempts/successes and owner minutes | raw data would need to leave local control |
| coach use | select or edit teacher-facing next moves | probing question, misconception check, smallest-useful hint | aggregate counts, minutes, incidents, thresholded learner voice and suppressed result receipts | answer leakage, authority drift, access failure, unacceptable burden, or version drift |
| transfer | use a separate no-AI item or explanation check | none during proof check | descriptive aggregate transfer/explanation count | obvious transfer harm or an uninterpretable measure |
| decision | retire, repeat narrower, continue one bounded cycle, or escalate to formal pilot review | summary support after human review | decision memo and public-claim ceiling | anyone treats the micro-cycle as efficacy evidence |

## Interpretation

Task completion is not learning. Exact small-cell counts are not portable results. The transfer count and learner voice can trigger stopping or
redesign, but a tiny feasibility cycle cannot estimate a causal effect. A later efficacy question
requires a pre-specified primary outcome, comparison condition, implementation measures, sufficient
sample, and protected subgroup/access analysis.

## Readiness

Run readiness before the cycle and again after aggregate post-cycle rows exist. Entry readiness is not owner-review readiness.

```bash
make micro-pilot-readiness \
  PACKET=scratch/field-handoff/rev0336/teacher-tutor-micro-pilot/teacher-selected-concept \
  WRITE=1
make micro-pilot-next \
  PACKET=scratch/field-handoff/rev0336/teacher-tutor-micro-pilot/teacher-selected-concept \
  WRITE=1
```

## Boundary

The packet is scratch-local preparation. It does not run a real cycle, accept `SRC2+` evidence,
prove learning, access, safety, fairness, workload, or effectiveness, authorize a service, upgrade a
public claim, or close `FT-0181`.

## rev0336 run-definition provenance

The packet's generated run-definition files are immutable for a cycle. `micro-pilot-readiness` blocks
entry if the discovery card, coach prompt, checklist, measure card, or cycle run sheet has drifted
from the packet manifest or if the prompt hash no longer matches the owner plan.

## rev0336 event chronology boundary

For any post-cycle packet, `SESSION-LOG.csv` dates must be ISO and ordered baseline <= coach-use <= transfer. Owner review and result recording must occur after the latest session row. This boundary is a hot-path execution check, not evidence acceptance.

## rev0336 result-decision boundary (prior)

After a local result receipt exists, follow only the bounded decision map: `retire` stops; `repeat-narrower` and `continue-bounded` require a fresh packet and cannot be pooled as evidence; `escalate-to-pilot-review` requires a separate future accepted route and emits no evidence-import command.

## rev0336 follow-through seed rule

The micro-pilot lane now requires a source-result hash-linked fresh-packet for any non-retire decision. This keeps the lane action-oriented: a fresh packet must be driven by an owner-selected next constraint and one required change, not by a generic repeat command or cumulative evidence logic.
