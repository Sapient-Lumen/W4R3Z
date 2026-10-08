# Cognitive-effort budget and construct-preservation defaults

The archive already has learning-first interaction defaults and answer-release triggers. It now
needs a smaller operational rule for a growing evidence pattern: AI can improve learning when it is
pedagogically shaped, but unrestricted assistance can also replace the cognitive work that makes
learning durable.

So every AI-supported task should publish a **cognitive-effort budget**: what work must remain with
the learner before, during, and after AI assistance.

## Effort ladder

| Code | Learner work preserved | Default use |
|---|---|---|
| `CE0-INDEPENDENT-FIRST` | learner attempts the task unaided before AI feedback | fluency, retrieval, diagnostic, and construct-sensitive practice |
| `CE1-HINT-ONLY` | AI may ask questions, give hints, or point to concepts but not solve | routine study help, early drafts, problem-solving practice |
| `CE2-DIAGNOSE-EXAMPLE-NO-DIRECT-SOLUTION` | AI may diagnose error patterns and show analogous examples | math/science procedures, writing revision, coding debug practice |
| `CE3-SOLUTION-COMPARISON-AFTER-EXPLANATION` | AI solution appears only after learner explains their approach | worked-example comparison, reflection, exam review |
| `CE4-AI-PRODUCTION-WITH-PROOF-SHIFT` | AI may help produce an artifact, but proof shifts to defense, transfer, logs, or live demonstration | open production tasks where AI use is part of the construct or professional practice |
| `CE5-AI-INCOMPATIBLE-WITH-CONSTRUCT` | AI assistance would replace the measured construct | decoding, unaided writing, no-executor symbolic procedure, live oral fluency, secure exams |

## Required task fields

A course, programme, assessment, or official support route should be able to answer these questions.

| Field | Meaning |
|---|---|
| `construct_being_measured` | the knowledge, skill, judgment, performance, or access function that must remain real |
| `allowed_ai_role` | tutor, critic, translator, accessibility support, simulator, search assistant, editor, generator, calculator, code assistant, no role |
| `effort_code` | one of `CE0-CE5` |
| `answer_release_rule` | when the AI may show a full answer, model, or rewrite |
| `proof_shift` | what proof replaces artifact trust when AI production is allowed |
| `protected_access_carveout` | whether an accommodation or accessibility support is allowed even where ordinary AI use is restricted |
| `teacher_override_floor` | what human judgment cannot be bypassed |

## Default pairings

| Task family | Default effort code | Reason |
|---|---|---|
| retrieval / fluency practice | `CE0` | durable memory and speed are the construct |
| exploratory concept learning | `CE1` or `CE2` | guidance can help, but answer-first shortcuts learning |
| ordinary writing revision | `CE1-CE3` | feedback can support improvement; replacement authorship changes the construct |
| professional AI-use task | `CE4` | using AI may be part of the authentic construct, so proof must shift to judgment and accountability |
| timed gateway writing | `CE5` unless protected route applies | unaided production or approved access support is the construct |
| no-calculator / no-executor math | `CE5` | external execution replaces the target procedure |
| accessibility support | route-specific | support may be protected even when ordinary production aid is barred |

## Anti-patterns

The following are not acceptable effort budgets:

- “AI allowed because everyone uses it” without naming the construct.
- “Students must use AI responsibly” without an answer-release rule.
- “Teacher will check” without proof of what the learner actually knows.
- “AI detector says no” as a substitute for assessment redesign.
- “AI output is high quality” as evidence of learning.
- “AI saves time” as evidence of educational value.

## Relation to proof-of-learning

Where the effort code moves upward toward `CE4`, proof must move upward too. The archive should
prefer oral defense, live transfer, process explanation, revision history, teacher sampling, or
performance demonstrations over ambient log capture. Where the effort code is `CE5`, the system
should publish the protected-access exception path separately from ordinary AI permission.

See `B278` and `B279`.
