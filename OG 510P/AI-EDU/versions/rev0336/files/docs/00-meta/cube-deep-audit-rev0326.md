# rev0326 deep audit: mission recovery and field truth

## Executive finding

The cube's strongest principle is sound: pedagogy first, human judgment retained, no evidence
laundering. Its most serious failure is **mission-machinery inversion**. The archive has treated the
production and closure of control artifacts as if that were delivery of educational value.

At the rev0325 baseline, the cube contained 796 tracked files, about 645,000 Markdown words, 128
Python tools, 83 registered lint checks, 45 utility tools, 279 assumptions, 92 open questions, and
198 follow-through items. Of the follow-through items, 197 were marked done, yet no accountable owner
had been contacted and no real teacher/tutor cycle had run. More than half of the Markdown words sat
under governance. The bibliography called itself intentionally short while containing 291 entries.

The archive is internally consistent. It is not yet field-proven.

## The heart

The heart is not a policy library, reminder workflow, or validation suite. It is this:

> Help a learner think and transfer more independently by helping a teacher or tutor choose a better
> next move, while preserving human authority, access, privacy, and the ability to stop.

The cleanest success test is not whether the AI produces a good answer. It is whether the learner can
perform or explain without AI, and whether the educator can make a better decision at acceptable
cost.

## What is missing

### A real user and a discovered problem

The cube names roles but no actual partner, teacher, tutor, learner community, jurisdiction, or
locally observed instructional pain point. The earlier equality-one-step default was executable but
arbitrary. A solution should not choose the problem merely because its packet is ready.

### A theory of change tied to one outcome

The present materials mix learning, move quality, transfer, access, safety, and workload in a tiny
cycle. The first cycle should ask a narrower feasibility question. Learning efficacy belongs in a
later, larger, pre-specified evaluation.

### Learner voice and legitimate participation

The packet protects identifiers but says little about learner notice, age-appropriate assent or
consent where applicable, whether use felt optional, whether prompts confused learners, or whether
learners believed the interaction helped them think.

### Reproducible intervention identity

The cube did not require the tool, model, version, configuration, or prompt-card hash in the owner
plan. Without these, a later result can refer to an intervention that no longer exists.

### A privacy-and-equity bridge

Aggregate-only release is sensible, but it can hide harms in small or protected groups. The owner
needs a local suppression threshold and a protected local disaggregation route that never enters the
release archive.

### External assurance

The 83 checks are maintained by the same archive they validate. They demonstrate consistency with
local rules, not independent pedagogical validity, accessibility, privacy compliance, security, or
causal effectiveness.

## Where things went severely wrong or wasteful

### 1. Paper completion became the progress metric

`done` mostly means a document, schema, example, or check was produced. It does not mean a human used
it, a learner benefited, or a decision changed. This is a measurement design error in the project
itself.

Correction: split future status language into `artifact_complete`, `field_observed`, and
`outcome_supported`. Never use one word for all three.

### 2. Anticipatory bureaucracy outran experience

Multiple revisions added packet generators, dry-run harnesses, readiness scorers, routers,
owner-review recorders, and result recorders before the first real cycle. These may eventually be
useful, but building the whole lifecycle before observing one event increases the chance that the
system is exquisitely controlling the wrong workflow.

Correction: freeze new controls until an actual field event exposes a missing safeguard.

### 3. The administrative rail displaced the educational rail

`FT-0181` is an evidence-import and owner-contact path around a reminder-service record. It became the
single live follow-through and gravitational center of an education project. That infrastructure can
remain, but it should be secondary to the teacher-selected learning cycle.

### 4. Validation missed operator truth

The full suite passed while active instructions still referenced the obsolete
`scratch/pedagogy/teacher-tutor-micro-pilot/...` path. This is a concrete example of endogenous
assurance: the checks proved their own contracts but failed to test the command a human would copy.

Correction in rev0326: align defaults and active documentation on the versioned field-handoff path,
and make the existing re-entry check reject the stale path.

### 5. Tiny-cycle language drifted toward efficacy

Phrases such as “continue if transfer is flat or better” invite causal interpretation from a tiny,
uncontrolled aggregate cycle. Random variation, selection, item difficulty, and teacher adaptation
can dominate such a signal.

Correction in rev0326: classify the cycle as feasibility and usability only. Transfer remains a
safety and learning-alignment signal, not an effect estimate.

### 6. Evidence accumulation replaced evidence synthesis

A 291-entry bibliography is difficult to use and contains duplicates. Sources are not consistently
summarized by design, population, intervention, outcome, effect, limits, and relevance.

Correction over time: keep a 12-to-20-source evidence kernel for current decisions and move the rest
to a watchlist or historical ledger.

### 7. Synthetic examples could look operationally real

Some service-record examples carry plausible statuses, dates, and public summaries. They are marked
`realistic_example` in metadata, but that label can disappear when a public subset is rendered.

Correction in rev0326: every rendered realistic-example summary must visibly say “synthetic example”
and “not a deployed service.”

### 8. Release provenance was too thin

The release manifest contained only project, revision, timestamp, slug, bundle, and status. It did
not identify a tree digest, receipt digest, prior revision, file count, or the absence of a source
commit.

Correction in rev0326: package metadata now includes those fields without claiming a bit-reproducible
ZIP.

## External research signals

The evidence does not support either blanket enthusiasm or blanket rejection.

- OECD's 2026 Digital Education Outlook distinguishes improved task performance from learning and
  argues that pedagogical design is decisive:
  <https://www.oecd.org/en/publications/oecd-digital-education-outlook-2026_062a7394-en.html>
- Stanford SCALE found only 20 high-quality causal studies in its 2026 K-12 AI evidence review,
  indicating that the rigorous base is still thin:
  <https://scale.stanford.edu/research-in-action/understanding-evidence-base-ai-k12-education>
- Tutor CoPilot offers a relevant positive model: AI assists human tutors with pedagogical moves;
  the randomized study reported a four-percentage-point increase in topic mastery and larger gains
  for lower-rated tutors, while also noting grade-level appropriateness problems:
  <https://arxiv.org/abs/2410.03017>
- Bastani and colleagues found that an unguided GPT interface improved practice performance but
  reduced later unassisted performance, while a safeguarded tutor mitigated the harm:
  <https://www.pnas.org/doi/10.1073/pnas.2422633122>
- Kestin and colleagues reported strong results from a purpose-built, pedagogy-informed tutor in a
  specific Harvard physics context. The result is promising, not automatically portable:
  <https://www.nature.com/articles/s41598-025-97652-6>
- An EEF randomized trial found a 31% reduction in lesson-preparation time for participating science
  teachers using ChatGPT with a guide; workload was the primary outcome, not student learning:
  <https://educationendowmentfoundation.org.uk/projects-and-evaluation/projects/choices-in-edtech-using-generative-ai-chatgpt-for-ks3-science-lesson-preparation-2024-teacher-choices-trial>
- The IES AmplifyGAIN program begins with classroom case studies and teacher surveys, then usability
  work, then a larger pilot. That sequencing is a useful corrective to designing a complete control
  lifecycle before discovery:
  <https://ies.ed.gov/use-work/awards/amplifygain-generative-ai-transformative-learning>
- UNESCO emphasizes human agency, age appropriateness, privacy, and pedagogical validation:
  <https://www.unesco.org/en/articles/guidance-generative-ai-education-and-research>

## Speculation to test, not fact

1. The revision history may reflect a generator reward function that favored producing a closed
   artifact over waiting for messy human evidence.
2. The dense “hot-exam,” public-record, recognition, and reminder-service branches may have migrated
   from a broader governance cube and displaced the narrower education mission.
3. The archive may be serving as a safety demonstration or governance research object more than as a
   product intended for educator adoption.
4. The lack of a named field partner may be the root constraint; more internal refinement cannot
   solve a missing relationship.

Each hypothesis should be tested against provenance and the project owner's intent before deletion.

## Recovery sequence

### Now: field-truth repair

- Keep the mission kernel and one field handoff in the hot path.
- Require a locally selected problem and concept.
- Treat the first cycle as feasibility/usability only.
- Capture tool/model/version, learner notice and aggregate voice, privacy threshold, and protected
  local equity review.
- Fix stale command paths and synthetic watermarks.
- Allow no new control family without a field event or reproducible defect.

### Next: compression

- Merge branch families into concise canonical digests and move historical tails to an archive ZIP.
- Reduce the active bibliography to a decision-bearing evidence kernel.
- Replace `done` with status terms that distinguish paperwork from observation and supported outcome.
- Set a release-surface budget. A reasonable first target is a 50% reduction in hot-path Markdown and
  Python control surface, measured without deleting source-truth history.

### Then: field learning

- Conduct discovery with at least one real educator and, where appropriate, learners or advocates.
- Run one genuine local feasibility cycle.
- Revise the packet from observed friction, not imagined edge cases.
- Only after feasibility is demonstrated, pre-specify a larger pilot with a primary outcome,
  comparison condition, implementation measures, and subgroup/access analysis.

## Stop rule

If another revision adds more controls but records no field event, fixes no reproducible defect,
deletes nothing, and changes no decision from evidence, it should not ship.

## Boundary

This audit is a reasoned diagnosis. Internal counts are observations from the rev0325 bundle;
external findings are context-specific; the speculative hypotheses are explicitly unverified. No
real pilot evidence exists and `FT-0181` remains live.
