# Construct-family crosswalk for proof profiles

The construct map names `CF1-CF9`. This crosswalk applies those construct
families to recurring proof profiles so assignment-level AI rules start from the
measured construct rather than from generic tool categories.

## Use rule

For every major task family, publish seven fields:

```text
Construct family:
AI-compatible role:
AI-incompatible role:
Starting CE posture:
Disclosure required:
Independent proof:
Protected support route:
```

If those seven fields cannot be stated briefly, the task is not ready for an AI
use rule.

## Crosswalk table

| Task / subject family | Likely construct family | Starting `CE` | AI-compatible role | AI-incompatible role | Independent proof |
|---|---|---|---|---|---|
| early decoding / foundational literacy | `CF1` or `CF2` | `CE1-CE5` depending on measured act | access support, teacher-approved hints, practice diagnosis | direct reading substitution when decoding is the construct | observed reading, short comprehension transfer, teacher questioning |
| ordinary writing process | `CF5` with `CF3/CF4` elements | `CE2-CE4` | brainstorming, critique, local edits with disclosure | undisclosed drafting where authorship is the construct | draft checkpoint, source/reasoning memo, live revision or oral explanation |
| timed or gateway writing | `CF1`, `CF3`, or `CF9` | usually `CE5` during measured act | approved access route only | operational AI composing the judged response | secure sample, live explanation, assessment-body rule |
| research inquiry | `CF4` and `CF8` | `CE3-CE4` | search support, critique, comparison, source triage | fabricated sources or hidden synthesis replacing judgment | source trail, method note, defense of inclusion/exclusion |
| mathematics / symbolic procedure | `CF1-CF3` | `CE1-CE3`; `CE5` for no-tool segments | hints, error diagnosis, worked-example comparison after attempt | executor use where symbolic fluency is measured | first attempt, altered problem, method explanation |
| coding / data work | `CF3`, `CF6`, `CF8` | `CE3-CE4` | debugging help, API lookup, comparison, workflow reflection | unverified generated artifact where architecture/debug skill is measured | code walk-through, live modification, test/error analysis |
| language learning / communicative proficiency | `CF1`, `CF2`, `CF3` | `CE1-CE5` by mode | vocabulary practice, pronunciation feedback, access support | translation or generated speech during spontaneous proficiency measurement | live speaking/listening/writing, comprehension check, correction explanation |
| studio / media / design | `CF5` and `CF8` | `CE3-CE5` | critique, ideation, comparison where course grammar allows | AI generation where original creation process is the judged construct | process checkpoint, critique, live modification, artist/designer statement |
| lab / empirical inquiry | `CF3`, `CF4`, `CF6` | `CE2-CE4` | planning critique, uncertainty analysis, code/data checking | generated report replacing method and interpretation judgment | notebook/checkpoint, data artifact, uncertainty explanation, nearby-case transfer |
| clinical / practicum / trade performance | `CF6` and `CF9` | `CE4-CE5` | supervised workflow support where authentic to practice | AI substitution for live judgment, safety, or professional responsibility | observation, simulation, rationale, supervisor signoff |
| accessibility-enabled expression | `CF7` plus target construct | construct-specific | speech-to-text, reading support, translation, planning support where not the construct | treating protected access as misconduct proof | equivalent demonstration through protected route |
| AI literacy task | `CF8` | AI use is part of task | critique, red-team, compare, verify, reflect | hiding AI use where analysis of AI use is the construct | reflection, comparison, risk explanation, corrected output |

## Disclosure defaults by construct

| Construct posture | Disclosure default |
|---|---|
| AI incompatible during measured act | clear pre-task rule; simple affirmation if required |
| AI supports planning or critique | category disclosure for major tasks; low-stakes practice may need only course-level notice |
| AI helps produce submitted artifact | material contribution disclosure plus proof of human judgment |
| AI is access support | protected or accommodation-aware disclosure, not ordinary suspicion metadata |
| AI use is the task | full enough disclosure to let the evaluator assess critique, verification, and judgment |

## Proof shifts

When AI moves from hinting to production, proof must move too.

| Shift | Required proof response |
|---|---|
| hinting after independent attempt | retain attempt and error-analysis evidence |
| critique before revision | add live revision, explanation, or transfer sample |
| generated code/data/media/prose | add verification, authorship, and modification proof |
| AI-assisted professional workflow | add supervisor signoff and judgment rationale |
| AI use becomes high-stakes or record-adjacent | add human examiner/owner, appeal route, and official rule alignment |

## Anti-patterns

Do not publish AI rules that say only:

- “AI is allowed if cited”; 
- “AI is banned unless approved”; 
- “AI may help but not replace your work”; 
- “Use AI ethically”; 
- “AI detectors will be used.”

Those statements do not name the construct, permitted role, prohibited role,
proof shift, protected route, or appeal path.

## Current archive bet

The archive now prefers **construct-family crosswalks** over tool lists. Tool
lists go stale quickly. Construct families remain useful even when models,
interfaces, and product names change.

See
[`construct-map-and-ai-use-disclosure-matrix.md`](construct-map-and-ai-use-disclosure-matrix.md),
[`subject-family-proof-intensity-defaults.md`](subject-family-proof-intensity-defaults.md),
[`sector-and-age-profile-splits-for-proof-intensity-defaults.md`](sector-and-age-profile-splits-for-proof-intensity-defaults.md),
[`../30-operations/course-level-ai-use-grammar.md`](../30-operations/course-level-ai-use-grammar.md),
[`../20-governance/cognitive-effort-budget-and-construct-preservation-defaults.md`](../20-governance/cognitive-effort-budget-and-construct-preservation-defaults.md),
and `B26`, `B278`, `B279`, `B281`.
