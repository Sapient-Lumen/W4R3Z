# Construct map and AI-use disclosure matrix

The archive already says that assessment should be construct-first. This surface turns that
principle into a working matrix: before deciding whether AI is allowed, required, disclosed,
limited, or prohibited, name what the task is supposed to measure.


## Current overlay

Use [`construct-family-crosswalk-for-proof-profiles.md`](construct-family-crosswalk-for-proof-profiles.md) when translating `CF1-CF9` into subject-family proof profiles, course AI-use grammar, and assignment-level disclosure rules.

## Construct-first rule

AI use is not good or bad in the abstract. It is compatible or incompatible with a construct.

If the construct is unaided recall, live fluency, independent drafting, handwriting, mental
calculation, or spontaneous oral explanation, AI assistance may destroy the evidence. If the
construct is critique, revision, source evaluation, tool fluency, project management,
accessibility-enabled expression, or workplace-style production, AI may be part of the construct.

## Construct families

| Construct family | Examples | Default AI posture | Proof shift |
|---|---|---|---|
| `CF1-UNAIDED-FLUENCY` | spelling under exam conditions, mental arithmetic, live language fluency, safety-critical recall | prohibit operational AI during the measured act | live task, oral defense, proctored or observed sample |
| `CF2-FOUNDATIONAL-PRACTICE` | early writing, basic algebra, decoding, procedural fluency | hints or diagnosis only; answer release delayed | independent attempt, checkpoint, error analysis |
| `CF3-CONCEPTUAL-EXPLANATION` | explain a concept, justify a method, compare strategies | AI may prompt or question, not replace explanation | oral/written explanation, transfer problem, misconception check |
| `CF4-RESEARCH-INQUIRY` | literature search, inquiry project, source synthesis | AI may help search, brainstorm, summarize, or critique with disclosure | source trail, process note, teacher checkpoint, defense of choices |
| `CF5-CREATIVE-PRODUCTION` | essay, design, media, code, performance | AI depends on course grammar; authorship boundary must be explicit | draft history, process artifact, artist/designer statement, live edit |
| `CF6-PROFESSIONAL-WORKFLOW` | workplace simulation, data analysis, lesson planning, clinical-style documentation | AI may be part of authentic workflow if limitations are taught | tool-use log, judgment rationale, error review, supervisor signoff |
| `CF7-ACCESS-ENABLED-EXPRESSION` | speech-to-text, translation support, reading support, assistive planning | allowed where the support is not the assessed construct | protected route, accommodation record, equivalent proof without stigma |
| `CF8-META-AI-LITERACY` | evaluate AI output, detect hallucination, prompt responsibly, assess bias | AI use is part of the task | reflection, critique, comparison, risk explanation |
| `CF9-HIGH-STAKES-CERTIFICATION` | gateway exam, licensure, qualification, readiness-to-practice | follow assessment-body rule; default conservative until construct map is explicit | official rule, human examiner, appeal path, secure proof |

## Disclosure matrix

| AI role | Student disclosure | Teacher/institution duty | Common proof |
|---|---|---|---|
| none / prohibited | affirm no operational AI use if required by assessment rule | make rule and consequences clear in advance | observed task, secure exam, oral check |
| brainstorming | disclose use category, not necessarily every prompt for low stakes | teach limits and source responsibility | planning note or checkpoint |
| tutoring/hinting | disclose where it shaped final work or task rules require it | preserve independent attempt when that matters | attempt log, misconception correction, transfer sample |
| drafting/editing | disclose material contribution and preserve authorship boundary | define acceptable edit depth before submission | draft history, author statement, live revision |
| translation/accessibility | use protected disclosure route where needed | separate access support from misconduct suspicion | accommodation/access record, equivalent demonstration |
| data/code/media generation | disclose tool, role, and human verification | require verification and explainability where construct requires judgment | code review, data provenance, process trace |
| assessment security / detection | learner should not be forced to prove innocence from opaque detector alone | no AI-only allegation, sanction, or score cancellation | human review, multiple evidence sources, appeal route |

## Link to cognitive-effort budget

| Construct family | Starting `CE` posture |
|---|---|
| `CF1` | `CE5`: AI incompatible during the measured act |
| `CF2` | `CE1` or `CE2`: hinting/diagnosis before answer release |
| `CF3` | `CE2` or `CE3`: explanation remains learner-owned |
| `CF4` | `CE3` or `CE4`: AI-assisted process with defense of choices |
| `CF5` | `CE3-CE5` depending on authorship target |
| `CF6` | `CE4`: AI may be authentic, but judgment proof rises |
| `CF7` | support route overrides generic suspicion; construct decides limit |
| `CF8` | AI use is the object of analysis |
| `CF9` | official rule controls; proof and appeal must be human-accountable |

## Minimal course statement

A course or program should be able to publish this compact statement for each major task family:

```text
Task family:
Construct measured:
AI role allowed:
AI role prohibited:
Disclosure required:
Independent proof required:
Accessibility/protected route:
Consequence of misuse:
Appeal/correction route:
```

The statement should be shorter than the assignment itself. If the AI-use statement becomes more
complex than the task, the task probably needs redesign.

## Misuse boundary

Misuse is not merely “AI was used.” Misuse occurs when the learner uses AI in a way that contradicts
the published construct, hides a material contribution where disclosure is required, fabricates
sources or evidence, violates an assessment-body rule, or bypasses a protected/human-only route.

Do not use AI detectors as the sole proof of misuse. Treat detection output as at most a weak lead
requiring human review, context, process evidence, and contestability.

## Accessibility boundary

Accessibility support should not be converted into ordinary authorship suspicion. When a support
tool changes the mode of expression but not the measured construct, the correct response is
equivalent proof, protected handling, and clear task design.

## Assessment redesign trigger

Redesign the task when any of these are true:

- ordinary AI use can produce a high-quality submission without the target understanding;
- disclosure rules require more effort to police than the task teaches;
- students with legitimate access supports are chilled by suspicion;
- teachers need opaque detection to preserve the old task;
- the task rewards prompt access or paid tools more than learning;
- oral defense or transfer checks repeatedly reveal false mastery.

See
[`authentic-assessment-and-proof-of-learning.md`](authentic-assessment-and-proof-of-learning.md),
[`proof-of-learning-bundles.md`](proof-of-learning-bundles.md),
[`../20-governance/cognitive-effort-budget-and-construct-preservation-defaults.md`](../20-governance/cognitive-effort-budget-and-construct-preservation-defaults.md),
[`../20-governance/evidence-grade-and-claim-strength-ladder.md`](../20-governance/evidence-grade-and-claim-strength-ladder.md),
and `B26`, `B278`, `B279`, `B281`.

## Rev0214 action-authority overlay

Assessment tables must now state action authority explicitly.

| Assessment-adjacent use | Default AA ceiling | Human-only boundary |
|---|---|---|
| formative feedback or hinting | `AA1-AA2` | no grade, misconduct, or official proof effect |
| rubric-aligned draft comment for teacher review | `AA2` | human teacher owns final feedback and score |
| moderation aid or sampling support | `AA2-AA3` | no hidden triage or exclusive evidence |
| official marking writeback | `AA5` only with named human signoff | no unattended gradebook, qualification, or transcript write |
| detector or assessment-security signal | `AA1-AA3` as one signal only | `AA6` for AI-only allegation, sanction, or score cancellation |

See
[`../20-governance/action-authority-ceiling-backfill-for-high-risk-functions.md`](../20-governance/action-authority-ceiling-backfill-for-high-risk-functions.md).
