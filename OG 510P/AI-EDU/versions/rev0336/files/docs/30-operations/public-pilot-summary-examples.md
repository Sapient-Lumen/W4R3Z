# Public pilot-summary examples

Internal service records are not public notices. A public pilot summary should tell affected people
what the service does, what it does **not** do, what data is used at a high level, whether the AI can
affect records, how to reach a human, what alternative exists, what claim is still unproven, and
what would stop or narrow the pilot.

Do not publish protected support facts, security details, vendor secrets, learner-level traces, or
unsupported claims.

## Public summary template

| Public field | Plain-language answer |
|---|---|
| What is being piloted? |  |
| Who may use it? |  |
| Is use required? |  |
| What does it not do? |  |
| What data is used at a high level? |  |
| Can AI output affect records or decisions? |  |
| What claims are still unproven? |  |
| What public claim will be removed if evidence stays weak? |  |
| What human help or alternative exists? |  |
| How can someone correct or appeal a problem? |  |
| What would pause or stop the pilot? |  |
| Last reviewed / next review |  |

## Example A: algebra hint tutor

| Field | Public wording |
|---|---|
| What is being piloted? | A hint tool for selected practice problems. |
| Who may use it? | Learners in the participating course section. |
| Is use required? | No. A non-AI practice path is available. |
| What does it not do? | It does not grade, report misconduct, or decide whether a learner has mastered the topic. |
| Data used | Practice problem text, learner-entered attempts, and short session logs. |
| Record effect | No gradebook or transcript effect. |
| Unproven claim | Whether the tool improves durable learning or transfer. |
| Claim to remove | “Improves algebra learning outcomes” if delayed evidence stays weak. |
| Human help | Teacher help and ordinary practice supports remain available. |
| Correction / appeal | Report wrong hints to the course team; no penalty attaches to tool errors. |
| Stop trigger | Wrong-answer pattern, access gap, or evidence of answer dependence. |
| Review | Review after the first unit cycle. |

## Example B: writing feedback assistant

| Field | Public wording |
|---|---|
| What is being piloted? | A draft-feedback tool that comments on clarity, organization, and revision questions. |
| Who may use it? | Students working on one draft assignment. |
| Is use required? | Optional. Teacher and peer feedback remain available. |
| What does it not do? | It does not write the final submission, grade the work, authenticate authorship, or accuse misconduct. |
| Data used | Student-provided draft text and tool feedback. |
| Record effect | No direct grade or misconduct effect. |
| Unproven claim | Whether it improves independent writing ability. |
| Claim to remove | “Improves writing skill” if later independent proof does not support it. |
| Human help | The teacher remains the feedback and grading owner. |
| Correction / appeal | Students can ignore tool suggestions and ask the teacher to review confusing feedback. |
| Stop trigger | Hidden rewriting pressure, fabricated sources, or use as detector evidence. |
| Review | Review after the assignment cycle. |

## Example C: program navigation assistant

| Field | Public wording |
|---|---|
| What is being piloted? | A source-linked navigation assistant for registration and program-route questions. |
| Who may use it? | Learners in the participating advising route. |
| Is use required? | No. Human advising remains available. |
| What does it not do? | It does not decide transfer credit, financial aid, eligibility, standing, or deadlines. |
| Data used | Public program information and learner-entered questions. |
| Record effect | No record changes without a human record owner. |
| Unproven claim | Whether it reduces advising burden without increasing wrong next steps. |
| Claim to remove | “Makes advising faster and more reliable” if error or burden evidence does not support it. |
| Human help | A named advising route handles uncertain or high-stakes questions. |
| Correction / appeal | Learners can request correction and no-deadline-loss review for pilot-caused errors. |
| Stop trigger | Stale advice, missed deadline, subgroup access gap, or unowned escalation. |
| Review | Review before the next peak registration period. |

## Example D: accessibility and language-access support

| Field | Public wording |
|---|---|
| What is being piloted? | Support for accessible formats, navigation help, and language-access materials where the task permits it. |
| Who may use it? | Learners in the participating support route or course context. |
| Is use required? | No. Existing accommodation and human support routes remain available. |
| What does it not do? | It does not infer disability, change accommodations, grade work, or create misconduct suspicion. |
| Data used | Materials or text supplied for access support. Protected facts stay in the protected route. |
| Record effect | No ordinary grade or misconduct record effect. |
| Unproven claim | Whether the support improves access for all affected subgroups. |
| Claim to remove | “Improves access for all learners” if subgroup evidence or protected-route evidence is weak. |
| Human help | Accessibility / accommodation staff remain the protected-route owner. |
| Correction / appeal | Learners can use the protected support channel without explaining private facts publicly. |
| Stop trigger | Support facts appear in ordinary metadata, or approved support is treated as authorship risk. |
| Review | Review after one support cycle. |

## Example E: capped reminder workflow

| Field | Public wording |
|---|---|
| What is being piloted? | A workflow that drafts reminders about low-stakes practice submissions for staff review. |
| Who may use it? | One participating course team. |
| Is use required? | No learner is required to interact with the AI. |
| What does it not do? | It does not write grades, send penalties, contact families, or infer protected status. |
| Data used | Course roster and low-stakes practice-submission status needed for draft reminders. |
| Record effect | Staff must review before any message is sent; no automatic penalty. |
| Unproven claim | Whether it saves staff time after review and correction burden are counted. |
| Claim to remove | “Saves staff time” if total-labor evidence does not support it. |
| Human help | Course staff own the queue and correction route. |
| Correction / appeal | Wrong reminders can be corrected without penalty. |
| Stop trigger | Unauthorized write, false penalty, prompt-injection success, or protected fact leakage. |
| Review | Review after two reminder cycles. |

## Words to avoid

Avoid public language such as “proven,” “personalized for every learner,” “safe,” “fair,” “secure,”
“teacher-saving,” or “improves outcomes” unless the specific claim family has fresh evidence. Prefer
plain limits: “being tested,” “optional,” “draft only,” “human reviewed,” “not used for grades,” or
“not yet proven.”

## Current archive bet

Public summaries should reduce trust debt. They are not marketing copy. The best summary tells users
what the institution is **not** allowing the AI to do.

See
[`ai-pilot-packet-and-filled-examples.md`](ai-pilot-packet-and-filled-examples.md),
[`machine-readable-service-record-schema-and-validator.md`](machine-readable-service-record-schema-and-validator.md),
[`../20-governance/claim-family-evidence-matrix.md`](../20-governance/claim-family-evidence-matrix.md),
[`../20-governance/evidence-expiry-and-renewal-clocks.md`](../20-governance/evidence-expiry-and-renewal-clocks.md),
and `B275`, `B276`, `B279`, `B280`, `B281`.
## Rev0215 redaction-profile note

The examples in this file are now treated as source summaries, not final notices. Before publication,
each should be rendered through a profile from
[`public-summary-redaction-profiles.md`](public-summary-redaction-profiles.md). Learner and family
notices should stay short and limit-forward; teacher, partner, and vendor extracts may carry more
operating detail only when that audience has a defined role.


## Rev0216 render smoke-test note

The archive now tests the service-record public summaries against the shipped redaction profiles with
`tools/check_public_summary_renders.py`. The test is not publication approval; it checks that the
candidate text can be rendered without forbidden phrases, missing human-contact routes, or weak/stale
claim phrases. Human reviewers still decide whether a local notice is complete and appropriate.
