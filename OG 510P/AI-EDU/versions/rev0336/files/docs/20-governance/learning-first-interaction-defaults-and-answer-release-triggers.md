# Learning-first interaction defaults and answer-release triggers

This document closes the archive's next governance gap about **how official study companions and
guided learning surfaces should actually behave once an institution has decided they are allowed**.

The archive already had a course grammar (`NO-AI`, `GUIDED-AI`, `OPEN-AI`), a student-facing
deployment ladder, and a clear preference for guided or pedagogically explicit support over
unmanaged answer engines. What it still lacked was the narrower operating rule in the middle:

> **when a governed educational AI is meant to help someone learn, what should it do before it gives
the answer, when may it give the answer anyway, and how should it return the learner to evidence of
understanding afterwards?**

That gap matters because “guided” can hide two opposite failures:

- **answer laundering** — the tool asks one or two cosmetic questions and then behaves like a fast
  solution engine anyway;
- **fake Socratic theater** — the tool withholds answers indefinitely, exhausting learners who are
  stuck, time-boxed, language-constrained, or using the tool as an accessibility support.

Current public signals point in the same direction. OECD's 2026 Digital Education Outlook argues
that successful task completion with generative AI does not automatically produce learning and that
pedagogically guided use matters more than generic answer delivery. RAND's 2026 youth survey shows
rising student homework use alongside rising concern that AI use can harm critical thinking.
Provider-side “study mode” and “learning mode” signals from OpenAI and Anthropic matter here not as
proof by themselves, but as market evidence that the interaction shape is now the real pedagogical
question. UNESCO's 2026 competency frameworks for teachers and students sharpen the same point by
tying AI use to human agency, AI pedagogy, and critical use rather than tool access alone. See
`B11`, `B14`, `B15`, `B17`, `B151`, `B152`, `B153`.

## Relationship to the course grammar and deployment ladder

This document does **not** replace
[`../30-operations/course-level-ai-use-grammar.md`](../30-operations/course-level-ai-use-grammar.md),
[`student-facing-function-deployment-defaults-and-handoff-triggers.md`](student-facing-function-deployment-defaults-and-handoff-triggers.md),
or
[`persistent-memory-personalization-and-learner-model-boundaries.md`](persistent-memory-personalization-and-learner-model-boundaries.md).

It adds one thing only:

- a **compact interaction contract** for recurring student-facing learning surfaces.

The course grammar still says **what a task allows**. The deployment ladder still says **what kind
of institutional service is being operated**. This document says **how a learning-oriented
interaction should usually unfold inside those allowed and governed conditions**.

## The default interaction order

The archive's current default order is:

1. **orient and diagnose** — clarify the goal, current confusion, or attempted step;
2. **give the next productive move** — hint, question, retrieval cue, constraint, or error
   localization;
3. **add bounded scaffold** — partial worked step, contrast case, smaller subproblem, or modelled
   check;
4. **release the fuller answer only on named triggers**;
5. **return to learning** — ask for explanation, variation, transfer, correction, or comparison so
   answer release does not become the end of the pedagogical claim.

This is the archive's default because it best matches the archive's wider commitments: learning over
task completion, teacher-visible pedagogy, assessment redesign rather than denial, and
lower-surveillance evidence of understanding.

## Starter interaction defaults by function family

| Function family | Default interaction posture | Earliest ordinary full-answer release | Required return-to-learning move |
|---|---|---|---|
| `SF-STUDY` | hint-first, question-first, retrieval-first, misconception diagnosis before solution delivery | after a visible attempt, a clearly named stuck point, or an explicit compare-your-work request in a permitted task mode | ask for the learner's explanation, correction, or one near-transfer item |
| `SF-FEEDBACK` | critique, criteria reminder, and revision cue before rewriting | only after the learner has produced a draft or fragment and the task mode permits modelled revision help | require the learner to choose, adapt, or justify what changed rather than pasting the rewrite blindly |
| `SF-TUTOR` | sequenced scaffold with fading, misconception repair, and optional worked-example modelling | after bounded struggle, repeated failed attempts, or a teacher/tutor-configured example-first phase | require a new analogous item, a teach-back, or a shortened independent retry |

This table is deliberately small. The archive does not want separate interaction grammars for every
product family.

## Answer-release triggers

A fuller answer, worked solution, or rewrite may be released when one or more of the following
triggers is true.

### `AR1` — visible attempt or named stuck point

The learner has already tried, can say where they are stuck, or has produced a fragment worth
comparing against a model.

### `AR2` — the task mode actually permits it

The course, teacher, or service context is `OPEN-AI`, an explicit worked-example phase, or another
setting where fuller model output is part of the intended activity rather than a hidden shortcut.

### `AR3` — further hinting has stopped being educationally productive

The tool is looping, the learner is repeatedly confused, or the next best move is a clean model
rather than another indirect prompt. The system should name that it is switching posture instead of
pretending the release is still ordinary hinting.

### `AR4` — accessibility, language, or comprehension support requires a fuller model

Sometimes the barrier is not productive struggle but access to the form of explanation itself. In
those cases, fuller modelling may be the more rights-compatible and educationally honest response.
This does **not** collapse protected support routing into ordinary authorship judgment; it only
prevents the interaction contract from becoming an access barrier. See
[`accommodation-aware-disclosure-and-accessibility.md`](accommodation-aware-disclosure-and-accessibility.md).

### `AR5` — the teacher or tutor has intentionally assigned example-first instruction

Some lessons use worked examples before independent performance. The archive is not banning that. It
is saying those phases should be named, bounded, and followed by independent or transfer work rather
than silently becoming the permanent default.

### `AR6` — the learner is in compare, check, or debug mode after a substantive attempt

Once a learner has tried, showing the full method or solution can be legitimate as long as the
interaction still returns them to explanation, diagnosis, or transfer rather than stopping at
inspection.

## Non-release and handoff triggers

The archive also names three clear cases where this contract should not be stretched past its proper
domain.

### `NR1` — `NO-AI` or live proof event

If the task is explicitly `NO-AI`, or the learner is inside a controlled proof event, the system
should not provide substantive solution help. It may restate the rule, suggest permissible study
moves later, or route to the teacher. See
[`../30-operations/course-level-ai-use-grammar.md`](../30-operations/course-level-ai-use-grammar.md)
and
[`../40-assessment/authentic-assessment-and-proof-of-learning.md`](../40-assessment/authentic-assessment-and-proof-of-learning.md).

### `NR2` — the interaction has crossed into advising, rights, or consequence-bearing judgment

Pathway decisions, official accommodations, discipline, formal progression judgments, and other
consequence-bearing acts belong under other service families and human-accountable review paths.
They are not solved by a smarter hint-first contract.

### `NR3` — distress, manipulation, safeguarding, or acute-risk signal

If the learner's state or the service shape raises safeguarding, coercion, or well-being concerns,
the right move is human handoff, not better pedagogical prompting. See
[`student-facing-function-deployment-defaults-and-handoff-triggers.md`](student-facing-function-deployment-defaults-and-handoff-triggers.md).

## The release-and-return rule

When a fuller answer is released, the interaction should do three things immediately afterwards.

1. **name why the release happened** — attempt made, explicit compare request, bounded struggle,
   access need, or teacher-assigned example phase;
2. **mark what remains the learner's work** — explain, adapt, correct, complete the analogous item,
   or defend the changed draft;
3. **shift back toward transfer** — do not simply ask whether the learner wants another full answer.

A learning surface that releases answers but never asks for reconstruction is still drifting toward
answer-engine behavior.

## Anti-patterns the archive is trying to prevent

### 1. Answer laundering

The system performs a token hint or one leading question and then hands over the whole solution.
This produces the appearance of pedagogy without the substance.

### 2. Endless refusal

The system blocks or delays fuller help even when the learner has attempted the work, the task mode
permits comparison, or access needs make modelling the more educationally honest move.

### 3. Relational stickiness

The system turns pedagogical patience into emotional dependence, pseudo-friendship, or manipulative
return prompts. OECD's 2026 safety writing is especially clear that learner-facing AI should avoid
pseudo-friend roles and keep human judgment central. See `B137`.

### 4. Hidden profile escalation

The system starts remembering struggle history, inferred ability, or repeated confusion in ways that
shape later treatment without a published memory rule. Interaction posture and memory posture are
different questions, and neither should quietly smuggle the other in.

### 5. Rewrite substitution

Feedback surfaces quietly become ghostwriting surfaces. The archive permits modelled revision only
when task mode and instructional intent make that honest, and it still expects the learner to
choose, adapt, justify, or reproduce the improvement.

## The disposition rule: harden unchanged, branch, stay provisional, or retreat

The archive now gives these interaction defaults the same kind of disposition rule it gives other
starter profiles.

A learning-first interaction profile should harden unchanged only when all five of these still
travel together under ordinary conditions:

1. **construct fit** — the same posture still protects the main thing being learned, rather than
   quietly replacing authorship, method reconstruction, or independent judgment;
2. **developmental fit** — the same pace of hinting, modelling, and release still fits the learner's
   age, self-regulation, and need for adult framing;
3. **access fit** — the same posture remains accessible across language, disability, literacy, and
   comprehension conditions without turning access support into disguised refusal or disguised
   ghostwriting;
4. **task-mode fit** — the same posture still matches the allowed mode (`NO-AI`, `GUIDED-AI`,
   `OPEN-AI`, worked-example phase, compare/check phase) rather than drifting across them;
5. **handoff fit** — the same teacher/tutor visibility, recovery path, and anti-dependence
   safeguards still hold, rather than the service quietly becoming the only meaningful route
   forward.

When those five do **not** travel together, the archive prefers one of three other dispositions.

### 1. Branch

Branch when the same answer-release posture starts doing a different pedagogical job than the parent
profile assumed.

Examples:

- ordinary study help becomes explicit worked-example teaching for novices;
- critique-first feedback becomes de facto rewriting in an authorship-sensitive task;
- compare/check help in mathematics or coding becomes first-pass generation before any substantive
  attempt;
- or access-oriented modelling for language/comprehension support begins shaping ordinary authorship
  judgments for everyone else.

### 2. Stay provisional / local

Stay provisional when a posture still looks promising, but the archive does not yet have enough
ordinary-operating evidence to say that the same release trigger, return-to-learning move, and human
recovery path really travel across teachers, cohorts, or contexts.

### 3. Retreat

Retreat toward teacher-owned or human-only handling when the interaction no longer looks like
bounded pedagogical support at all — for example because the construct is too hot, the learner is
too dependent, the task is a live proof event, or the service has drifted into rights-,
progression-, or safeguarding-bearing treatment.

## The first branch map the archive now treats as knowable in advance

The archive keeps this map intentionally small. It still does **not** want a separate interaction
grammar for every product.

| Interaction branch | Ordinary fit | Default release posture | What must stay true for unchanged hardening | Portability default |
|---|---|---|---|---|
| **hint-first study/help** | ordinary concept explanation, misconception repair, retrieval support, and sequenced tutoring where the learner can show an attempt or name a stuck point | hints, questions, or bounded scaffolds before fuller answer release | the main construct still benefits from productive struggle, the learner can re-enter with explanation or transfer, and the service is not silently replacing first-pass generation | may often harden unchanged across `SF-STUDY` and much of `SF-TUTOR` |
| **critique-first feedback** | writing, design, lab-report, and other revision settings where the learner has already produced a draft, fragment, or plan | critique, criteria reminder, and revision cue before any modelled rewrite | the learner still owns the draft, the task mode allows revision help, and the service still requires choice, adaptation, or justification rather than blind paste-in | may harden unchanged only after learner production; does **not** travel as blank-page generation or final-author substitute |
| **example-first teaching** | novice instruction, bounded worked-example phases, language/comprehension support, or moments where further hinting has stopped being educationally productive | earlier release of a fuller model, but only inside a named teaching or access phase | the example phase is explicit, bounded, followed by independent or transfer work, and not smuggled in as the permanent default for all tasks | may harden only as a named branch; it should not inherit invisibly from ordinary hint-first help |
| **check / compare / debug** | mathematics, coding, data, and other constrained problem-solving where the learner has already made a substantive attempt and now needs inspection or correction | compare-your-work, debug, or method-check release after attempt | the system is helping the learner inspect, repair, or transfer rather than giving the first-pass solution without effort | may harden for constrained after-attempt uses, but not as a universal first-answer posture |

The archive is therefore making a sharper portability judgment than in rev0064:

1. **ordinary hint-first study help** is the clearest case that may really travel unchanged;
2. **critique-first feedback** also travels, but only after genuine learner production;
3. **example-first teaching** can be honest and educational, but it should harden only as a named
   branch rather than as a hidden vendor exception;
4. **check / compare / debug** can travel in constrained subjects after a substantive attempt, but
   should not be mistaken for permission to skip first-pass thinking.

## The branch triggers the archive now treats as predictable

| Trigger | What usually changes | Archive move |
|---|---|---|
| **younger learners or weak self-regulation** | fewer open-ended Socratic turns, shorter hint loops, earlier adult visibility, and faster reset when confusion persists | branch earlier toward tighter teacher/tutor framing |
| **extended-authorship or construct-sensitive tasks** | full rewrites, modelled interpretations, or polished exemplar answers become hotter because they can replace the thing being assessed | branch later on answer release, or retreat toward teacher-owned handling |
| **explicit worked-example pedagogy** | the right move may be a fuller model earlier, especially for novices, but only in a named phase followed by reconstruction or transfer | branch to example-first teaching rather than laundering direct answers through faux hinting |
| **language, comprehension, or accessibility barriers** | fuller modelling, simpler explanation, translation, or reformulation may need to arrive earlier than ordinary productive-struggle defaults would suggest | branch on access grounds without dropping the return-to-learning rule |
| **repeated non-transfer or dependency** | the issue stops being one more interaction turn and becomes a support-path problem requiring adult inspection | retreat toward teacher-owned recovery or human-only handling |

## What now forces retreat toward teacher-owned or human-only handling

The archive now treats five cases as presumptive retreat signals rather than mere interaction tuning
problems:

1. **`NO-AI` or live proof events** — the construct is being checked directly, so substantive help
   should stop;
2. **hot consequence-bearing drift** — the interaction has crossed into grading, progression,
   official advising, accommodation determination, discipline, or comparable judgment;
3. **safeguarding, distress, or manipulation risk** — the problem is now care, safety, or relational
   vulnerability rather than pedagogy;
4. **repeated fuller-answer release without later reconstruction** — the learner is no longer
   returning to explanation, correction, or transfer, so the service should not simply release
   faster or remember more;
5. **missing meaningful human recovery path** — if no teacher, tutor, or staff owner can actually
   inspect and reset the path, the archive prefers cooling the service over pretending the
   interaction can self-govern.

The important shift is this: repeated struggle does **not** always mean the service should become
more answer-forward or more persistent. Sometimes it means the AI-owned interaction has reached its
limit.

## The dependence-and-recovery rule

The archive now makes that limit operational. Once ordinary interaction has started producing
repeated answer-dependence, non-transfer, or relational stickiness, the next move should be a
**recovery disposition**, not another undifferentiated round of hinting.

The archive keeps this recovery ladder intentionally short.

| Recovery disposition | When it fits | What the system may do | What it may not do | Owner |
|---|---|---|---|---|
| **`IR0` — ordinary interaction continues** | struggle still looks productive, the learner is re-entering with explanation or correction, and the same posture still fits the task | continue the default branch with bounded hints, scaffold, or compare/check support | silently grow memory, intensity, or answer depth just because the learner is taking time | AI-owned interaction under published teacher/tutor visibility rules |
| **`IR1` — bounded reset** | the learner is looping, over-requesting fuller answers, or losing the thread, but the problem still looks recoverable inside the same session | restate the goal, shrink the next step, switch branch explicitly, require the learner to paraphrase the worked example, or ask for one smaller reconstructive move before any further release | pretend the reset is new pedagogy while actually giving another faster full answer | AI-owned interaction, still bounded to the session |
| **`IR2` — temporary cool-down** | repeated fuller-answer release, repeated no-transfer after release, or early signs of dependence mean the interaction should stop being answer-forward for this construct or task window | pause fuller-answer release, route the learner to explanation, notes, retrieval, teacher-provided examples, or a later re-entry checkpoint | keep rewarding the same pattern with more model output, or make the cool-down feel punitive or opaque | AI-owned interaction with a visible rule and named adult owner |
| **`IR3` — teacher-owned recovery path** | the learner now needs an accountable adult to inspect the pattern, reset the support mode, or decide whether the issue is pedagogical, access-related, motivational, or service-design-related | send a small recovery packet to the named teacher/tutor/staff owner, allow that owner to set the next posture, and reopen AI support only on the published re-entry condition | turn the packet into a durable risk score, cross-function profile, or hidden discipline/advising record | named teacher, tutor, or service owner |
| **`IR4` — human-only handling** | the interaction has crossed into live proof, safeguarding, rights, formal progression, or severe dependence/manipulation risk | stop substantive AI study help and hand the case to the appropriate human route | leave the learner with no accountable path or hide the reason for withdrawal behind generic error language | human-only handling |

This ladder is deliberately not a punishment scale. It is a way to stop “one more answer turn” from
becoming the archive's default response to dependence.

## The signals that now force movement onto the recovery ladder

The archive now treats five signal families as the main reasons to leave ordinary interaction tuning
behind.

### `DS1` — repeated fuller-answer pull

The learner repeatedly asks for the full answer, exemplar, or rewrite again before attempting
reconstruction, explanation, or transfer. One-off requests do not count by themselves. The concern
is pattern, not impatience.

### `DS2` — repeated non-transfer after release

The learner can inspect the answer but cannot explain it, adapt it, or solve one near-analogue
afterwards. This is the clearest sign that release is no longer doing the pedagogical job the branch
claimed.

### `DS3` — looping confusion

The interaction cycles through similar hints, clarifications, or partial models without changing the
learner's understanding. At that point the issue is not lack of one more prompt but failure to reset
the support path honestly.

### `DS4` — relational or motivational stickiness

The learner starts treating the service as the only tolerable route forward, seeks reassurance
rather than instruction, or shows signs that the interaction pattern itself is becoming
dependency-forming. The archive treats this as a recovery or safeguarding question, not a
prompt-engineering question.

### `DS5` — hidden path pressure

The tool has become required in practice, the teacher path has become too slow or unavailable, or
the system's design now channels the learner back into AI-owned interaction because no real human
recovery path exists. This is not only a learner issue; it is evidence of service-design failure.

## The recovery moves the archive now prefers

### From `IR0` to `IR1`: make the reset explicit

If the problem still looks local to the session, the system should say that it is resetting the
interaction and name the new posture: shorter hint loop, compare/check instead of fresh generation,
or one bounded worked example followed by learner reconstruction. Hidden shifts in help style are
exactly what the archive is trying to stop.

### From `IR1` to `IR2`: cool the answer channel before remembering more

If reset fails, the archive prefers a **temporary cool-down** over deeper persistence, more personal
memory, or faster answer release. The cool-down should be tied to the construct or task window, not
to the learner's identity in general. It should also publish the re-entry condition: for example,
explain the previous model, solve one smaller analogue, complete a teacher-set checkpoint, or wait
for the next class-supported step.

### From `IR2` to `IR3`: move ownership to an accountable adult

When the learner is still not re-entering successfully, the archive now says the issue belongs to a
**teacher-owned recovery path**. The named adult should inspect a small packet, not an ambient
dossier. The default packet shape is now specified in
[`recovery-packets-and-aggregate-dependence-signals.md`](recovery-packets-and-aggregate-dependence-signals.md):
the smallest truthful packet is temporary, purpose-bound, and centred on construct, branch,
dependence-signal family, re-entry condition, and expiry rather than transcript dumping or learner
scoring. The archive explicitly rejects broader transcript dumping, hidden inferred-risk labels, or
silent cross-function reuse of this packet for discipline, admissions, welfare screening, or general
learner profiling.

### From `IR3` to `IR4`: stop pretending the service can self-govern

If the adult review finds that the construct is too hot, the learner is too dependent, the service
design is coercive, or the interaction has crossed into rights, safeguarding, or progression
judgment, the archive prefers **human-only handling** to one more branch, one more exception, or one
more memory layer.

## What teacher-owned recovery should actually do

A teacher-owned recovery path should be small and practical, not therapeutic theatre and not a
permanent flag. The archive's default recovery plan has four moves:

1. **diagnose the failure mode** — answer dependence, non-transfer, access barrier, motivational
   stall, or service-design mismatch;
2. **set the next allowed posture** — for example no more full rewrites, example-first only inside
   class, compare/check only after attempt, or temporary `NO-AI` for this construct;
3. **name the re-entry condition** — what the learner must show before ordinary AI help can resume;
4. **set an expiry or next review point** — recovery should not become indefinite unless the case
   has genuinely moved onto a different human-owned rail.

This keeps recovery accountable without letting it harden into a shadow learner record.

## What institutions should publish

For any recurring official study companion, feedback assistant, or tutoring surface, publish one
compact row with only nine fields:

1. function family (`SF-STUDY`, `SF-FEEDBACK`, `SF-TUTOR`, or local equivalent);
2. default interaction posture (`hint-first`, `critique-first`, `example-first`, `check/compare`, or
   named equivalent);
3. which answer-release triggers are active;
4. any named branch conditions (age band, subject family, access condition, or task-mode split) that
   change the default posture;
5. what return-to-learning move the service uses after release;
6. which dependence signal families (`DS1-DS5` or local equivalent) it watches for;
7. the first recovery move it takes on its own (`IR1` or `IR2`);
8. the named human handoff / recovery owner;
9. the re-entry condition after cool-down or teacher-owned recovery.

This keeps the publication burden small while stopping the common failure where a school names the
deployment level of a study tool but never says whether the tool actually behaves like ordinary
hint-first pedagogy, critique-first revision support, explicit example-first teaching, constrained
compare/debug help, or teacher-owned handling.

## What counted as a real archive gain

The archive now does more than say “prefer guided support,” more than say “diagnose, hint, scaffold,
then release on named triggers,” and more than say “publish a branch map instead of one answer
posture.” It now also names:

- **when answer dependence stops being ordinary interaction tuning**;
- **a small recovery ladder from bounded reset to temporary cool-down to teacher-owned recovery to
  human-only handling**;
- **the tiny packet a teacher-owned recovery path may actually use**;
- **the aggregate-only signal families that may improve the service without ranking learners**;
- and **the rule that recovery should reset learning support without turning into a durable
  learner-risk file**.

That is a meaningful operating step because it blocks three familiar mistakes at once:

- treating every failure to learn as a reason to release answers faster;
- treating dependence as proof that the system should remember more about the learner;
- and treating teacher-owned recovery as license for quiet surveillance or cross-function profiling.

## Current archive bet

The archive's current best guess is that **a small learning-first branch-and-recovery map** —
ordinary hint-first study help, critique-first feedback after learner production, explicit
example-first teaching phases, constrained compare/check help after real attempts, then bounded
reset / cool-down / teacher-owned recovery when dependence appears — will preserve learning better
than either of the two easier extremes:

- one universal answer-release posture for every educational context;
- or a universal refusal posture that ignores novice teaching, access needs, and bounded
  worked-example instruction.

That claim is now canon, but still live. The next problem is narrower: which parts of those starter
packet-and-signal defaults really travel unchanged across sectors and age bands, where they should
branch, and where even these cooler starter defaults should retreat further. See
[`recovery-packets-and-aggregate-dependence-signals.md`](recovery-packets-and-aggregate-dependence-signals.md)
and `OQ-0026`.
