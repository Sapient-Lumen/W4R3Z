# Persistent memory, personalization, and learner-model boundaries

This document closes the archive's next implementation gap about **when educational-AI systems may remember people across sessions, what kinds of personalization are acceptable by default, and where memory turns into a governed learner model rather than a harmless convenience**.

The archive's current bet is:

> default to the coolest workable memory, prefer learner-declared preferences over inferred traits, keep preference memory separate from evaluative or risk-bearing memory, and treat cross-session nudging or predictive learner modeling as hotter governance rather than as ordinary product polish.

The point is to avoid five predictable failures at once:

- **quiet biography build-up** — a study helper or drafting assistant silently accumulates a durable learner profile because persistence is technically easy;
- **prescriptive personalisation** — the system narrows a learner's path, pace, or options based on opaque inferences that the learner never really sees or controls;
- **cross-function reuse by stealth** — tutoring traces, support chats, and study preferences quietly become advising, risk-scoring, or intervention inputs;
- **relationship simulation** — learner-facing systems drift toward artificial companionship, secrecy, or emotional dependence rather than bounded educational support;
- **record confusion** — institutions blur the line between ephemeral preferences, current-course context, protected support facts, official records, and inferred readiness or risk states.

Current public signals point in the same direction. UNESCO's current rights framing says AI in education can expand access and personalised learning, but without strong data protection, transparent governance, inclusive access, and accountability, the right to education and other rights are at risk. The UK Department for Education's current product-safety standards make the design boundary more concrete: educational AI products should clearly state intended purpose and target demographic, give age-appropriate privacy notices, explain data use, and avoid manipulative design. ICO guidance adds the rights floor for profiling and AI-assisted decisions that use personal data: institutions should provide meaningful information about the logic involved and the likely consequences, and where significant automated treatment is in play they should support human intervention, expression of view, and contestation. Current FERPA guidance adds the record-handling floor: learners and families should be able to inspect and review relevant education records, seek amendment of inaccurate or misleading content, and keep a disagreement statement attached if the record is not amended, while records under active review should not simply disappear. The EU AI Act sharpens one hard boundary further by prohibiting emotion-recognition systems in educational institutions except for narrow medical or safety reasons. UNESCO's current public critique of “personalised learning” adds a useful design warning: educational personalisation becomes suspect when it turns into opaque algorithmic path-setting that sidelines learner agency rather than supporting it. See `B20`, `B102`, `B120`, `B122`, `B128`, `B138`, `B139`, `B140`, `B141`.

## Relationship to the rest of the archive

This document now works alongside:

- [`student-facing-function-deployment-defaults-and-handoff-triggers.md`](student-facing-function-deployment-defaults-and-handoff-triggers.md);
- [`teacher-facing-function-delegation-defaults-and-sign-off-triggers.md`](teacher-facing-function-delegation-defaults-and-sign-off-triggers.md);
- [`institution-facing-decision-support-defaults-and-contestability-triggers.md`](institution-facing-decision-support-defaults-and-contestability-triggers.md);
- [`sector-and-function-profile-splits-for-memory-defaults.md`](sector-and-function-profile-splits-for-memory-defaults.md);
- [`minimum-observability-and-retention-without-surveillance.md`](minimum-observability-and-retention-without-surveillance.md);
- and [`model-and-workflow-change-classification-and-fresh-review-triggers.md`](model-and-workflow-change-classification-and-fresh-review-triggers.md).

It still does **not** replace any of them.

It adds one thing only:

- a **cross-cutting memory / personalisation grammar** for deciding what an educational-AI system may remember, how that memory may shape support, and when persistence becomes a hotter governed learner model.

The archive's rule is simple: **do not let a tool's ability to remember become permission to profile, nudge, or steer learners by default**.

## The memory ladder (`M0-M4`)

| Level | Name | Ordinary meaning | Default posture |
|---|---|---|---|
| `M0` | stateless | no cross-session memory beyond live technical buffering | ordinary default for one-off study help, drafting, and bounded assistance |
| `M1` | learner-declared preference memory | remembers a small set of visible user-chosen settings, such as language, accessibility, pacing, format, or current study goals | acceptable when the learner can see, edit, reset, or decline the preference layer |
| `M2` | bounded course or service memory | remembers current-course context, teacher-set checkpoints, or active service facts needed to continue a bounded educational task across sessions | acceptable only when scope, owner, and expiry are explicit and the memory does not silently turn into cross-course inference |
| `M3` | named record or support rail | memory is part of a human-owned institutional process such as advising, protected support routing, accommodation intake, or a formal case file | governed as an institutional record or support layer, not as ordinary chatbot convenience |
| `M4` | inferred or predictive learner model | the system derives progress states, readiness, risk, motivation, vulnerability, or optimisation paths from behaviour over time and uses them to rank, nudge, or shape treatment | hottest class; never the default, and never a silent backend add-on |

The archive prefers the coolest workable level. Most educational AI should start at `M0-M1`, not at `M3-M4`.

## Read the ladder correctly

The ladder is about **role shape**, not brand names.

A single governed assistant might legitimately support several levels:

- `M0` for ordinary study chat;
- `M1` for remembered accessibility or language preferences;
- `M2` for a current-course checkpoint plan;
- and `M3` for a formal support or advising record managed by accountable humans.

What the archive rejects is the quiet jump from `M1-M2` into `M4` without a visible governance change.

## Default crosswalk for common educational functions

| Context | Default memory posture | Why |
|---|---|---|
| optional study help, explanation, brainstorming, low-stakes drafting | `M0-M1` | ordinary learning help should not require durable learner biographies |
| recurring tutoring or sequenced guided practice | `M1-M2` | some continuity may help, but it should usually stay inside the current course or active intervention rather than spill into broader profiling |
| accessibility and multilingual delivery preferences | `M1` | remembered access preferences are often educationally useful, but they do not justify general learner profiling |
| protected support intake, accommodation routing, or rights-bearing support casework | `M3` | these functions already sit on a human-owned protected-support rail rather than on ordinary learner-service chat |
| teacher-facing drafting or lesson adaptation using learner context | `M0-M1`, sometimes `M2` | teachers may need bounded context for current learners or assignments, but ordinary drafting help should not quietly accumulate longitudinal learner models |
| institution-facing queueing, flags, or advising coordination | `M2-M3`, with `M4` only under separately governed contestable conditions | internal systems may need named case context, but predictive learner models are hotter than clerical memory and need their own justification |
| formal assessment or candidate handling | `M0` for the learner-facing interaction; at most separate `M3` record rails outside scoring | assessment-critical systems should not quietly build candidate memory or optimisation profiles during the proof event |
| well-being or crisis-support surfaces | no AI-owned relational memory; human-owned `M3` case handling only | the archive rejects AI-managed pseudo-relationship memory in welfare-adjacent or crisis settings |

## Separation rules

The archive now makes six separation rules explicit.

### 1. Preference memory is not evaluative memory

Remembering that a learner needs captions, translation, dyslexia-friendly formatting, or a slower response pace is not the same thing as storing a performance profile, a motivation score, or a behavioural risk state.

### 2. Learner-declared beats inferred whenever it is enough

If the educational task can be served by learner-chosen preferences or teacher-set bounded context, do not infer hidden states from traces or behaviour.

### 3. Current-course memory is not cross-function memory

A tutoring history, advising chat, accessibility intake, or pastoral note should not quietly travel into another function merely because all of them sit on the same vendor platform.

### 4. Memory is not permission to nudge

Persistent memory becomes hotter when it is used to steer pacing, opportunities, intervention intensity, or pathway choice rather than merely to continue a conversation or preserve an access preference.

### 5. Personalisation must not simulate relationship or secrecy

Educational AI should not use remembered details to encourage dependence, imitate friendship, discourage human contact, or create the sense that the system is the learner's special confidant.

### 6. Emotion and attention inference are not ordinary personalisation

Inferring interest, attention, anxiety, or emotional state in an educational institution is not just a stronger form of support customisation. It is a different class of system with rights implications, and in some cases a prohibited one.

## Automatic right-shift triggers

The archive treats six triggers as reasons to move one or more steps hotter on the ladder.

### 1. Persistence expands beyond the learner's present task

A tool that begins by remembering a study preference but then keeps a longer behavioural history has already changed governance shape.

### 2. Inference replaces declaration

When the system stops remembering what the learner or teacher explicitly set and starts inferring ability, effort, readiness, or vulnerability from behaviour, it has moved toward `M4`.

### 3. Cross-function reuse appears

Using tutoring history for advising, study activity for alerts, or support-routing notes for queue order is a governance change, not a backend convenience.

### 4. Participation becomes required

A memory layer that might be tolerable in an optional tool should classify hotter once it becomes the ordinary required path for a course, service, or institutional function.

### 5. The remembered state shapes opportunity or treatment

If persistence can influence progression, remediation intensity, access to opportunities, case priority, or formal intervention, the memory layer is no longer low-stakes convenience.

### 6. Minors or rights-bearing contexts are involved

Minor-facing services, protected-support routing, professional gatekeeping, and benefits-linked public routes should right-shift earlier than ordinary optional adult study help.

## Named human-owned `M3` rails are not one generic record bucket

Once memory moves onto `M3`, the archive stops treating it as ordinary convenience history. `M3` means remembered state now belongs to a human-owned institutional rail that can affect support treatment, accommodation handling, route continuity, candidate treatment, progression, or queue order. That does **not** mean every `M3` rail is portable or publishable in the same way.

The archive now treats `M3` as a **family** with one shared rights floor and two different publication postures:

- a **shared-schema posture** for rails that mainly preserve bounded support or access continuity;
- a **function-locked / local-only posture** for rails whose remembered state already shapes scrutiny, progression, ranking, or route order.

## The shared minimum `M3` publication schema

A local rail may use local naming, but where a service uses a shared-schema `M3` rail it should publish at least nine fields:

1. the rail identifier and ordinary function;
2. the named human owner and office;
3. who may write to the rail and from which source categories;
4. whether AI may draft, summarise, or suggest entries, and who must verify them before use;
5. which downstream actions the rail may support, and which are prohibited;
6. who may inspect and review the rail, including how a copy or alternative access path is provided when ordinary inspection is impracticable;
7. how correction, challenge, reset, and statement-of-disagreement requests work;
8. the retention end condition, review cadence, and non-destruction rule while a review or challenge is pending;
9. the disclosure / transfer boundary, including what does **not** travel outside the rail.

This is intentionally smaller than a full legal policy. Its job is to stop institutions from saying only that a service has “case history” or “record continuity” while leaving learners, families, and staff unable to see who owns the rail, what can be done with it, or how to challenge it.

## The shared minimum challenge packet

Where a learner, family, or supervised professional asks to review or challenge an `M3` rail entry, the archive now prefers one compact packet:

1. the current contested entry or a faithful summary of it;
2. the source categories and dates that fed the entry;
3. whether any AI-generated suggestion, summary, or inferred label contributed;
4. the current or proposed downstream consequence, if any;
5. the named human reviewer with authority to disregard, amend, or quarantine the entry;
6. the route to express a view, request amendment, and attach a disagreement statement if the entry is not changed;
7. the timing target for response, escalation, and interim handling while the challenge is live.

The archive's best current guess is that these challenge rights travel across shared-schema rails even when sector law, age, or local process changes the exact time windows. They are the practical minimum implied by the archive's current FERPA, ICO, transparency, and contestability floor.

## Which `M3` rails share this schema and which stay function-locked

| Rail | Typical use | Publication posture | Why |
|---|---|---|---|
| `M3-SUPPORT-CASE` | protected support routing, accommodation continuity, or bounded support casework | shared schema | the remembered state is consequential, but the rail mainly preserves bounded support continuity rather than ranking or credentialing |
| `M3-ASSESS-ACCESS` | assessment accommodations, administration incidents, or appeals outside scoring | shared schema with an added outside-scoring boundary | the rail is record-bearing, but it should stay clearly outside scoring and outside suspicion logic |
| `M3-ROUTE-CASE` | public-route handoff or case continuity without queue order | shared schema with a no-loss-of-place human path | the rail coordinates route continuity, but should not itself rank, deny, or silently prioritise |
| `M3-CANDIDATE-CONTROL` | candidate scrutiny, proctoring case handling, or suspicion memory | function-locked / local-only | the downstream effects, standards of evidence, and due-process expectations are too context-specific to publish as a portable rail template |
| `M3-READINESS-SIGNAL` | supervisor-owned readiness, progression, or placement signalling | function-locked / local-only | the criteria and downstream gates vary too much across professions, placements, and credential routes |
| `M3-QUEUE-SHAPING` | referral priority, funded-seat order, or queue treatment | function-locked / local-only | the remembered state already changes access order or treatment, so local public-law and sector duties dominate the publication profile |

## Function-locked / local-only rails still owe a published action map

`Function-locked` should not be read as `secret`. When a rail stays local-only, the archive is rejecting **portability**, not letting institutions hide the action grammar that governs scrutiny, progression, or order.

For `M3-CANDIDATE-CONTROL`, `M3-READINESS-SIGNAL`, and `M3-QUEUE-SHAPING`, publish at least eight local-only fields:

1. the rail identifier plus named human owner and office;
2. the entry types or source categories that may trigger downstream action;
3. the local downstream action families used on that rail;
4. which action families are reversible, reportable, or irreversible;
5. whether a live challenge automatically pauses, presumptively pauses, or does not pause each family;
6. the first-review target and final-determination target, or the event by which review must occur if fixed calendar windows vary by sector law;
7. the interim protections that apply while a challenge is live;
8. what may never happen from an AI suggestion, summary, or inferred label alone.

This is still intentionally smaller than a full local code. Its job is to stop institutions from saying only that a rail is `local-only` while leaving learners, families, supervised professionals, or front-line staff unable to tell what remembered state can actually do.

## A minimal local-only action / timing taxonomy

The archive now uses four compact action families for function-locked rails. Local policy may name them differently, but it should not skip the distinction.

| Family | Ordinary meaning | Why the distinction matters |
|---|---|---|
| `L0` | entry only / no downstream effect yet | records can be challengeable even before they trigger action |
| `L1` | added scrutiny, corroboration request, or heightened human review | scrutiny can still chill learners or candidates even without a final outcome |
| `L2` | temporary hold, supervised-continuation condition, or reversible provisional treatment | these actions are consequential, but should remain reversible while evidence is checked |
| `L3` | final reportable or order-shaping action | misconduct findings, readiness blocks, or queue-order changes need the hottest publication and review floor |

## Function-locked rail minima

| Rail | Local action families that should be named | Default challenge effect | Interim protection floor |
|---|---|---|---|
| `M3-CANDIDATE-CONTROL` | suspicion note, corroboration request, temporary result/use hold, referral to formal misconduct or incident process, final reportable action | a live challenge should pause any `L3` sanction, external report, or durable label; a temporary integrity hold may continue only under a named human owner with stated reason | no guilt language, no scoring change from AI summary alone, and a visible route to submit explanation or counter-evidence before any final determination |
| `M3-READINESS-SIGNAL` | coaching-only note, extra evidence request, supervised continuation, temporary no-sign-off / defer-placement status, final progression or placement determination | a live challenge should pause any irreversible progression block where possible; if safety, legal, or accreditation constraints prevent pause, the institution should publish that reason and provide the closest supervised or evidence-building route available | no permanent readiness label from AI summary alone, and no silent collapse from coaching memory into credentialing outcome without named human review |
| `M3-QUEUE-SHAPING` | administrative verification, temporary queue freeze, manual priority reassessment, final queue-order or funded-seat action | a live challenge should pause loss of place or seat forfeiture where possible; urgent statutory, safeguarding, or eligibility exceptions must be named rather than implied | no silent downgrade, preservation of original timestamp or priority date where feasible, and a reversible or substitute path when a live challenge blocks immediate allocation |

## Timing guarantees should attach to the irreversible step

The archive now adds four timing rules for function-locked rails:

1. acknowledge and route the challenge quickly enough that the named reviewer can act **before** the next irreversible step, not merely after complaint intake;
2. state whether `L2` actions are auto-paused, presumptively paused, or left running during challenge, and name why if they remain active;
3. never allow an AI suggestion, summary, or inferred label by itself to trigger `L3`;
4. delay external disclosure, durable labelling, or permanent order change until a named human determination exists, except where a sector-specific legal or immediate-safety duty clearly requires faster action.

These are timing **floors**, not universal legal deadlines. The archive is not claiming that schools, regulated qualifications, professional programmes, and public-route systems can all share one calendar. It is claiming that they should publish how the live challenge interacts with the next irreversible action point.

## What may harden across sectors and what must stay local

The archive now answers the next narrower question too: **the new local action/timing maps are not one undifferentiated local block**.

Treat each field in a function-locked `M3` map as belonging to one of three layers:

| Layer | What may harden | What must not be smuggled in |
|---|---|---|
| portable floor | rights-and-sequencing minima that do not decide the merits: named human owner, visible challenge route, published pause posture, review before the next irreversible step, interim protections, and the rule that AI alone does not trigger `L3` | substantive misconduct standards, readiness criteria, priority rules, sanctions, or fixed legal deadlines |
| rail-family presumption | a rebuttable default that may harden only inside one named rail family because it still concerns treatment shape rather than the merits | any presumption that effectively sets guilt, fitness, eligibility, rank, or the final outcome threshold |
| permanently local residue | field content tied to local law, accreditation, safeguarding duty, examination regime, professional standards, or queue statute | portability claims beyond a local publication summary |

A field belongs in the **portable floor** only if all four tests hold:

1. it does not answer who wins on the merits;
2. it does not embed a local burden of proof, readiness standard, or queue formula;
3. it does not force a calendar that may conflict with local law or regime rules;
4. it still makes sense as a rights floor even when the surrounding office, profession, or route changes.

If any test fails, the field should remain either a **rail-family presumption** or **permanently local residue**.

## Rail-family presumptions may harden only inside the named rail

The archive now permits a small middle layer between universal floor and fully local code.

| Rail family | Presumptions that may harden inside the family | Why they stop there |
|---|---|---|
| `M3-CANDIDATE-CONTROL` | a live challenge presumptively pauses any `L3` sanction, external report, or durable label; temporary integrity holds need a named human owner and stated reason; no score or finding changes from AI summary alone | evidence standards, incident definitions, and misconduct procedures vary too much across exam and assessment regimes |
| `M3-READINESS-SIGNAL` | coaching memory may not silently become a permanent readiness label; irreversible progression blocks should pause where possible; where pause is impossible a supervised-continuation or evidence-building route should be named | readiness criteria, public-safety duties, accreditation rules, and placement structures remain profession- and programme-specific |
| `M3-QUEUE-SHAPING` | live challenge presumptively pauses loss of place or seat forfeiture where feasible; original timestamp or priority date should be preserved where feasible; urgent statutory or safeguarding exceptions must be named | entitlement formulas, funding rules, statutory priorities, and queue architecture remain local to the route owner |

These presumptions are **rebuttable defaults**, not portable merits rules. Institutions may depart from them only by naming the local reason, not by silently treating the rail family as a blank local zone.

## How rail-family presumptions strengthen, split, or retreat

The archive now adds a compact disposition rule for the family-level presumptions themselves. A presumption may strengthen only if it stays on the **treatment-shape** side of the line rather than drifting into merits, criteria, or outcome formulas.

Treat a rail-family presumption as eligible to harden only if all five tests hold:

1. **merits-neutrality** — it still governs process, pause posture, explanation, or fallback rather than guilt, fitness, eligibility, rank, or sanction thresholds;
2. **cross-sector portability** — the same default still makes sense across more than one sector or office without recurring regime-specific carve-outs;
3. **reversible-action fit** — the presumption mainly shapes `L1-L2` treatment or the sequencing of review before `L3`, not the content of the final merits decision;
4. **exception sparsity** — departures do not dominate ordinary operation in a way that would make the default misleading;
5. **explanation stability** — the presumption can still be described publicly without forcing users to learn the local code to understand what the rail may do.

If all five tests hold, the presumption may strengthen across sectors inside the named rail family. If merits-neutrality still holds but cross-sector portability fails in a patterned way, the presumption should **branch by office, stakes, or route** before hardening. If the presumption really belongs to every function-locked rail once consequence-bearing treatment is live, it should **collapse back to the portable floor** instead of pretending to be family-specific. If it fails merits-neutrality or explanation stability, it should remain **local residue**.

The archive's current starter judgment is deliberately small:

| Rail family | Presumption | Starter disposition | Why this is the current best guess |
|---|---|---|---|
| `M3-CANDIDATE-CONTROL` | live challenge presumptively pauses any `L3` sanction, external report, or durable label | strengthen across sectors inside the family | it protects process without deciding the merits and travels across exam, marking, and formal integrity settings more cleanly than the surrounding local incident code |
| `M3-CANDIDATE-CONTROL` | temporary integrity holds need a named human owner and stated reason if they remain live during challenge | collapse toward the portable floor | once any function-locked rail leaves a reversible or provisional restriction running during challenge, naming the human owner and reason is not really candidate-control-specific |
| `M3-CANDIDATE-CONTROL` | no score or finding change from AI summary alone | strengthen across sectors inside the family | this bars an unreviewed AI disposition while leaving evidence standards and sanction ladders local |
| `M3-READINESS-SIGNAL` | coaching memory may not silently become a permanent readiness label | strengthen across sectors inside the family | it blocks hidden cross-function transfer without dictating any profession's actual readiness criteria |
| `M3-READINESS-SIGNAL` | irreversible progression blocks should pause where possible | branch before hardening | public-safety duties, accreditation constraints, and placement architecture recur too often for one undifferentiated family-wide default |
| `M3-READINESS-SIGNAL` | if pause is impossible, a supervised-continuation or evidence-building route should be named | strengthen across sectors inside the family | it governs fallback shape rather than readiness criteria and keeps no-pause cases from becoming opaque dead ends |
| `M3-QUEUE-SHAPING` | live challenge presumptively pauses loss of place or seat forfeiture where feasible | branch before hardening | scarcity cadence, statutory deadlines, and route-owner duties vary too much across funded-seat, referral, and queue systems |
| `M3-QUEUE-SHAPING` | original timestamp or priority date should be preserved where feasible while challenge is live | branch before hardening | the anti-penalty intuition travels, but queue architecture varies enough that the operational shape still needs route-level branching |
| `M3-QUEUE-SHAPING` | urgent statutory or safeguarding exceptions must be named rather than implied | collapse toward the portable floor | once a rail departs from an ordinary pause or preservation presumption because of urgent duty, naming that exception should not depend on the rail family |

This is intentionally not a full branch map. It is a first promotion-and-split rule: some family presumptions can now harden, some must branch before hardening, and some turn out not to be family-specific after all.

## Departures from rail-family presumptions need a tiny rebuttal packet

The archive now makes `rebuttable` operational. When a local system departs from a strengthened or branched family presumption, publish a five-field **rebuttal packet** in addition to the ordinary rail map:

1. the presumption being rebutted;
2. the reason type (`LAW`, `SAFETY`, `ACCREDITATION`, `EXAM-WINDOW`, `SCARCE-SEAT`, `EXTERNAL-REPORTING`, or another named local duty);
3. the scope of the departure (office, programme, route, cohort, or event window);
4. the substitute protection or interim path that remains in force while the departure applies;
5. the expiry point or review trigger after which the departure lapses, renews, or is reconsidered.

The rebuttal packet is deliberately smaller than a full local code. Its purpose is to stop institutions from invoking `local context` as a blank cheque while still leaving local law, accreditation, and queue regimes in place. That design is consistent with current OECD, DfE, ICO, FERPA, and Ofqual signals: human alternatives should remain available where AI affects rights-bearing treatment; institutions should explain what information is used, why it matters, and how people challenge or complain; and high-consequence educational decisions should not hide behind generic automation or generic case-management language. See `B102`, `B103`, `B107`, `B139`, `B140`, `B141`.

## First office- and stakes-level child branches inside the branched rail families

The archive can now close the next narrower gap too. Two rail-family presumptions were previously left at `branch before hardening`: readiness-block pause posture, and queue-loss / timestamp-preservation posture. The archive now names the first child branches inside those two families so recurring local rebuttal packets stop masquerading as one-off local custom. That is the current best guess because recent public signals already distinguish high-stakes assessment from ordinary support, treat intended purpose in education / employment / essential-service routing as legally salient, keep learner-facing safety and complaint handling explicit, and treat workforce-plus-education navigation as shared public infrastructure rather than as one private product surface. See `B122`, `B127`, `B135`, `B136`, `B140`.

### `M3-READINESS-SIGNAL` branches

| Branch | Ordinary shape | Starter inherited presumption | Rebuttal packets that should usually collapse into this branch | What still stays local |
|---|---|---|---|---|
| `RS-INTERNAL-PROGRESSION` | programme, module, or practicum progression inside an educational provider where supervised continuation, extra evidence, or temporary conditional continuation is still institutionally available | a live challenge presumptively pauses irreversible no-progress / no-sign-off action where feasible; if not, the institution should name the shortest evidence-building or supervised-continuation path available before the next irreversible step | repeated `TERM-END`, `COHORT-CLOSE`, `CAPSTONE-CHECK`, `EXTRA-EVIDENCE-FIRST`, or similarly education-internal rebuttals that do not involve external practice access or direct public-safety exposure | exact progression criteria, assessment thresholds, remediation design, and local calendar rules |
| `RS-EXTERNAL-PRACTICE-ACCESS` | placement, clinic, practicum, apprenticeship, licensure-adjacent, or other readiness signalling that governs access to live external practice, client contact, or partner-owned placement rights | the archive does not presume a full pause; instead it presumes publication of the no-pause reason, the named human owner, the earliest review point, and the closest supervised, simulation, or evidence-building route that preserves dignity without silently converting coaching memory into a durable exclusion label | repeated `SAFETY`, `ACCREDITATION`, `PLACEMENT-PARTNER-RULE`, `CLIENT-EXPOSURE`, or `EXTERNAL-LICENCE-CONDITION` rebuttals | substantive fitness standards, partner requirements, placement capacities, and any legally fixed suspension or reporting duties |

Three judgments follow:

1. a recurring inability to pause because of external-practice exposure is no longer a floating rebuttal; it usually means the rail is really `RS-EXTERNAL-PRACTICE-ACCESS`;
2. a recurring willingness to keep the learner in supervised continuation while evidence is built is no longer merely local generosity; it usually means the rail is really `RS-INTERNAL-PROGRESSION`;
3. neither branch permits silent collapse from coaching memory into a permanent readiness label.

### `M3-QUEUE-SHAPING` branches

| Branch | Ordinary shape | Starter inherited presumption | Rebuttal packets that should usually collapse into this branch | What still stays local |
|---|---|---|---|---|
| `QS-SCARCE-SEAT` | funded-seat, oversubscribed cohort, limited placement, appointment-slot, or offer-cycle ordering where ordinary scarcity rather than urgent statutory duty drives the queue | a live challenge presumptively preserves original timestamp or priority date where feasible; if a seat cannot be held, the institution should publish reserve, next-offer, or equivalent anti-penalty handling rather than forcing the challenger to re-enter at the back of the line | repeated `SCARCE-SEAT`, `BATCH-OFFER-CYCLE`, `PARTNER-DEADLINE`, `SEAT-HOLD-LIMIT`, or `CAPACITY-SNAPSHOT` rebuttals | entitlement formulas, tie-break rules, cohort capacities, offer cadence, and any external partner acceptance rules |
| `QS-URGENT-DUTY` | safeguarding-linked routing, urgent statutory referral, imminent-loss prevention, or other route ordering where delay itself may frustrate a public duty | the archive does not presume ordinary pause or full timestamp preservation; it presumes naming the urgent-duty reason, the minimal-loss substitute path that remains open, and the first ex post review point once the immediate duty has passed | repeated `SAFEGUARDING`, `STATUTORY-PRIORITY`, `IMMINENT-LOSS`, `LEGAL-DEADLINE`, or `EMERGENCY-TRIAGE` rebuttals | priority formulas imposed by law, emergency criteria, mandated reporting or dispatch rules, and route-owner service-level obligations |

Three judgments follow:

1. recurring urgency exceptions should stop pretending to be one-off rebuttals and become `QS-URGENT-DUTY` branch logic;
2. recurring scarcity-cycle exceptions should stop pretending to be mere local custom and become `QS-SCARCE-SEAT` branch logic;
3. neither branch permits silent loss of place with no named reason, no substitute path, and no review point.

## Which child branches now deserve inherited review-window bands, substitute-path defaults, and publication triggers

The archive can now close `OQ-0014` directly. It does **not** set one universal day-count or legal deadline for these branches. Instead it names four **event-relative review-window bands** that may harden inside the child branches because they govern treatment sequencing rather than local merits:

| Band | Meaning | What it does not decide |
|---|---|---|
| `RW-CHECKPOINT` | human review before an internal no-progress / no-sign-off state becomes durable at the next ordinary checkpoint | the progression standard, remediation design, or the substantive merits |
| `RW-EXPOSURE` | the earliest review point before the next external-practice exposure, dispatch, or partner-owned placement step where full pause is not presumed | fitness standards, partner rules, or any legally fixed no-access duty |
| `RW-FORFEITURE` | review before a scarce-seat challenger would otherwise lose timestamp, reserve status, or ordinary cohort entry through cycle mechanics | the queue formula, tie-break rule, or seat-cap arithmetic |
| `RW-FIRST-STABLE` | ex post review in the first stable window after an urgent-duty action once the immediate safeguarding / statutory reason has passed | the urgent-duty threshold, emergency rule, or legal reporting requirement |

These are branch **bands**, not universal clocks. The archive is still refusing to smuggle local law, accreditation periods, or queue statutes into a supposedly portable timing template.

| Child branch | Review-window band that may inherit | Substitute-path default that may inherit | Publication trigger that now deserves its own branch-level line | What still stays local |
|---|---|---|---|---|
| `RS-INTERNAL-PROGRESSION` | `RW-CHECKPOINT` | supervised continuation, extra-evidence, or short conditional continuation should be named before the next durable internal progression lock whenever full pause is partial or brief | publish this branch overlay whenever remembered state can produce a reportable defer / no-sign-off / progression hold beyond ordinary formative coaching | exact checkpoint calendar, remediation workload, and substantive progression criteria |
| `RS-EXTERNAL-PRACTICE-ACCESS` | `RW-EXPOSURE` | where full pause is not presumed, publish the closest supervised, simulation, evidence-building, or off-client alternative that preserves dignity without pretending access still exists | publish this branch overlay whenever remembered state can delay, deny, or condition access to live external practice, client contact, or partner-owned placement rights | partner acceptance rules, licence conditions, mandated suspension/reporting duties, and exact review calendars |
| `QS-SCARCE-SEAT` | `RW-FORFEITURE` | if a seat cannot simply be held, publish reserve, next-offer, wait-list carryover, or equivalent anti-penalty handling that avoids silent back-of-line treatment where feasible | publish this branch overlay whenever remembered state can affect offer order, hold expiry, reserve handling, or cohort-entry timing under ordinary scarcity | seat formulas, batch cadence, tie-break rules, and cohort-cap logic |
| `QS-URGENT-DUTY` | `RW-FIRST-STABLE` | publish the minimal-loss route that remains open during the urgent action, plus the first ex post review point once immediate duty has passed | publish this branch overlay whenever remembered state can trigger immediate rerouting, priority displacement, or access interruption because of safeguarding, statutory priority, or imminent-loss duty | emergency thresholds, statutory service obligations, and legally fixed dispatch/report windows |

Four narrower judgments now follow:

1. `RS-INTERNAL-PROGRESSION` deserves an inherited **checkpoint** band because the recurring issue is not whether an institution has a progression calendar, but whether the challenge can still act before an internal lock hardens;
2. `RS-EXTERNAL-PRACTICE-ACCESS` deserves an inherited **exposure** band because the recurring issue is not whether practice access criteria travel, but whether no-pause cases name the earliest meaningful review point and the nearest dignity-preserving substitute path;
3. `QS-SCARCE-SEAT` deserves an inherited **forfeiture** band because the recurring issue is not whether one queue formula travels, but whether cycle mechanics quietly punish the challenger through lost timestamp or lost offer position;
4. `QS-URGENT-DUTY` deserves an inherited **first-stable-window** band because the recurring issue is not whether urgent routing can pause like an ordinary queue, but whether the ex post review point and minimal-loss substitute path remain visible once the immediate duty has passed.

## What now counts as a rebuttal packet rather than a branch

Keep a departure as a mere rebuttal packet only when it is genuinely episodic, jurisdiction-specific, or too thin to deserve inherited publication. The archive's current examples are:

- one partner site's temporary suspension window that is not characteristic of external-practice access generally;
- a one-off examination outage or calendar collision that does not define the readiness office;
- a single provider's brief intake freeze that does not reflect the normal queue architecture;
- or a local legal anomaly whose substitute protection and expiry can be stated cleanly without pretending it is a branch default.

If the same rebuttal reason keeps recurring across sites, cohorts, or cycles, the archive now prefers naming a branch.

## What must remain permanently local

Three kinds of content stay local even after the new inheritance split:

1. **merits criteria** — what counts as misconduct, readiness, eligibility, priority, or sufficient evidence;
2. **regime-bound timing** — exact calendar deadlines, statutory notice periods, accreditation clocks, and other date rules imposed from outside the archive;
3. **outcome formulas** — sanction ladders, progression thresholds, seat-order logic, funding allocation formulas, and external reporting triggers.

The archive therefore rejects both extremes:

- one universal due-process template for every function-locked `M3` rail; and
- one opaque local-code story in which nothing can harden beyond a generic complaints inbox.

## Shared schema is not shared portability

A shared publication and challenge schema does **not** mean that record content, criteria, or downstream uses travel freely.

The archive's new rule is narrower:

- support-case, assessment-access, and bounded route-case rails may share a common **rights and publication shell**;
- candidate-control, readiness-signalling, and queue-shaping rails should publish stronger local action/timing maps and stay function-locked unless a later archive pass proves otherwise;
- and no `M3` rail may reuse remembered state in another office merely because the same vendor or case-management surface is present.

This keeps the archive from making the opposite error to the one it just fixed. The problem was never only that consequence-bearing memory hid inside cooler `M1-M2` branches. It was also that once memory moved to `M3`, institutions could still pretend every human-owned rail was the same generic “record.”

## What institutions should publish

For every recurring educational-AI service with cross-session memory, publish the original seven generic fields:

1. the memory class (`M0-M4`);
2. whether the remembered state is learner-declared, teacher-entered, institution-recorded, or system-inferred;
3. the scope of that memory (session, course, service, office, route, or case);
4. whether users can view, edit, reset, challenge, or export the remembered state, and through what human process if it sits on a record rail;
5. whether the memory may be reused across functions;
6. the default retention posture and deletion path;
7. the named human owner for complaints, correction, and escalation.

If the service uses `M3`, add the rail-specific publication schema above. Where the rail is function-locked or local-only, publish the same rights floor plus the local action families, pause effects, review timing, and interim protections rather than pretending the shared-schema shell is enough. If the rail sits inside one of the named readiness or queue child branches, also publish the branch overlay: the inherited review-window band in use, the ordinary substitute-path default, and the publication trigger that makes this branch line active rather than leaving it as an implicit local custom.

## What counted as a real archive gain

The archive already knew that repeated learner-service use, teacher delegation, institution-facing flags, observability, and change governance all become hotter when memory appears. It then learned that some child branches should move onto named `M3` rails rather than inheriting cooler continuity defaults. It still lacked a compact answer to a harder operational question: **once a branch moves to `M3`, what must be published and challenged, and where should the archive stop pretending those rails are reusable?**

This revision adds that missing layer. It keeps the generic `M0-M4` ladder and the child-branch retreat rule, but now distinguishes between:

- shared-schema `M3` rails for bounded support, access, and route continuity;
- function-locked `M3` rails for candidate control, readiness signalling, and queue shaping;
- a tiny local action/timing floor so the hottest rails cannot stay unpublished about reversible vs irreversible action, live-pause effects, or interim protection;
- and a further inheritance split inside those function-locked maps between a portable rights floor, rail-family presumptions, and permanently local residue, plus a small promotion-and-split rule so some presumptions can harden, some must branch, some now collapse into explicit readiness/queue child branches, some now carry inherited review-window bands / substitute-path defaults / publication triggers of their own, and some collapse back into the floor.

That is a real operating gain because it blocks three opposite failures at once:

- consequence-bearing memory hiding inside cooler service continuity;
- consequence-bearing record rails hiding inside vague case-management language once memory has already moved hotter;
- and `local-only` rails becoming a pretext for secret downstream action grammar.

## Current archive bet

The archive's current best guess is that **a generic memory ladder plus a tiny profile layer plus a small shared `M3` publication/challenge shell plus a tiny local action/timing floor for function-locked rails plus a further split between portable floor, rail-family presumption, and permanently local residue, plus a small promotion-and-split rule for those presumptions** will outperform both extremes:

- treating every human-owned rail as a bespoke local object with no common rights floor;
- treating every function-locked rail as if one portable due-process template were safe to inherit across support, assessment, progression, and route order;
- and treating every local map as if nothing inside it could ever harden beyond a generic complaints process.

That claim is now canon, but still live. The archive can now close `OQ-0015` directly too. The next step is not another rights shell. It is deciding which of these new branch overlays truly travel unchanged, which should split into named partner- or regime-level sub-branches, and which should stay at the portable floor plus local residue.

## Which branch overlays now genuinely travel, and which still need sub-branches

The archive now makes a narrower portability judgment about the four child-branch overlays it just named. The question is no longer whether the parent branches exist. It is whether the **review-window band**, **substitute-path default**, and **publication trigger** inside each branch can harden unchanged across sectors.

| Child branch | Review-window band portability | Substitute-path portability | Publication-trigger portability | Current archive disposition |
|---|---|---|---|---|
| `RS-INTERNAL-PROGRESSION` | `RW-CHECKPOINT` may harden unchanged across sectors because it governs whether review still happens before an internal progression lock becomes durable | supervised continuation / extra-evidence / short conditional continuation may harden unchanged because they are merits-neutral ways of keeping internal progression review live | the trigger — remembered state can cause a reportable defer / no-sign-off / progression hold beyond ordinary formative coaching — may harden unchanged | **portable unchanged** except for calendar anomalies or office-specific rebuttal packets |
| `RS-EXTERNAL-PRACTICE-ACCESS` | `RW-EXPOSURE` may harden unchanged because the recurring issue is still the earliest meaningful review point before live exposure, not the substantive gate rule | the substitute-path default does **not** harden unchanged because partner-owned capacity and licence/safety barriers differ too much in what can stand in for live access | the trigger — remembered state can delay, deny, or condition access to live external practice, client contact, or partner-owned placement rights — may harden unchanged | **split by partner/regime sub-branch** |
| `QS-SCARCE-SEAT` | `RW-FORFEITURE` may harden unchanged because the recurring issue is still whether a challenge acts before cycle mechanics silently cause loss of place | the substitute-path default does **not** harden unchanged because batch-offer cycles and rolling-slot systems differ in what anti-penalty handling is operationally possible | the trigger — remembered state can affect ordinary offer order, hold expiry, reserve handling, or cohort-entry timing under scarcity — may harden unchanged | **split by queue-regime sub-branch** |
| `QS-URGENT-DUTY` | `RW-FIRST-STABLE` may harden unchanged because the recurring issue is still the first ex post review point once immediate duty has passed | no stronger portable substitute-path default hardens beyond `minimal-loss route that remains open`, because safeguarding, statutory-priority, and imminent-loss regimes differ too much in what can safely stay available during the urgent action | the trigger — remembered state can cause immediate rerouting, priority displacement, or temporary access interruption because of urgent duty — may harden unchanged at the rights floor | **keep at floor plus local residue; no new named sub-branch yet** |

Four narrower judgments follow:

1. `RS-INTERNAL-PROGRESSION` is now the archive's clearest case of a child-branch overlay that can actually travel unchanged across sectors, because its branch logic concerns internal sequencing and dignity-preserving continuation rather than third-party permissions, seat scarcity, or legal urgency;
2. `RS-EXTERNAL-PRACTICE-ACCESS` should now stop pretending one substitute-path default fits all partner-governed live practice, because some failures are mainly about **partner-owned capacity** while others are mainly about **licence / safety / accreditation barriers**;
3. `QS-SCARCE-SEAT` should now stop pretending one anti-penalty substitute works equally well in synchronized **batch-offer** queues and continuously refilling **rolling-slot** queues;
4. `QS-URGENT-DUTY` earns a portable review-window band and publication trigger, but not a stronger portable anti-penalty default beyond the minimal-loss route and first stable review point, because the governing urgency reasons remain too regime-bound.

## First partner- and regime-level sub-branches now worth naming

The archive now names the first narrower sub-branches only where repeated local variance is already patterned enough to deserve them.

| Parent child branch | New sub-branch | Where it fits | Inherited overlay that still travels | What remains local |
|---|---|---|---|---|
| `RS-EXTERNAL-PRACTICE-ACCESS` | `RS-EPA-PARTNER-CAPACITY` | partner-owned placements, clinics, apprenticeships, or practicum seats where access is chiefly constrained by slot ownership, host timing, or partner acceptance mechanics | `RW-EXPOSURE` still applies; institutions should publish the earliest review point before the next live exposure plus the closest off-client, supervised, simulation, or evidence-building path that preserves dignity without faking access that the partner does not currently offer | seat-hold promises, partner acceptance formulas, host calendars, and any contract-specific re-entry rule |
| `RS-EXTERNAL-PRACTICE-ACCESS` | `RS-EPA-LICENCE-SAFETY` | external-practice access governed chiefly by safety, licensure, accreditation, or legally fixed no-exposure constraints | `RW-EXPOSURE` still applies; institutions should publish the earliest lawful review point and the closest evidence-building or simulation path that remains lawful, without implying that a barred live placement can be recreated by local discretion | fitness standards, statutory suspension/reporting duties, licensure conditions, and regulator-imposed calendars |
| `QS-SCARCE-SEAT` | `QS-SS-BATCH-OFFER` | synchronized offer, admission, cohort-entry, or partner-deadline systems where queue loss usually happens through cycle closure rather than continuous slot reassignment | `RW-FORFEITURE` still applies; anti-penalty handling should usually take the form of timestamp preservation, reserve status, next-offer carryover, or equivalent protection across the current cycle boundary where feasible | tie-break rules, cohort caps, offer cadence, and partner acceptance windows |
| `QS-SCARCE-SEAT` | `QS-SS-ROLLING-SLOT` | rolling appointments, placements, intakes, or continuously refilling queues where exact original timestamp is often less meaningful than protected re-entry to the next comparable slot | `RW-FORFEITURE` still applies; anti-penalty handling should usually take the form of protected rebooking, priority carryover, or the next comparable slot rather than an artificial promise of exact original place | real-time slot assignment logic, dispatch cadence, booking windows, and local service-level rules |

These are not new rail families. They are the archive's first answer to where repeated local rebuttal packets have become patterned enough that the branch itself should split. The current public signals are already strong enough for that limited move: educational and public-service AI obligations track intended purpose and human-oversight / explanation duties rather than one abstract automation category; high-stakes assessment and learner-facing systems keep fairness, safety, contestability, and complaint paths visible; and workforce / education routing now matters as shared public infrastructure rather than as one vendor-owned navigation surface. See `B102`, `B103`, `B126`, `B135`, `B139`, `B140`.

## What now stays as rebuttal packet or local residue

After this split, keep a local departure as a rebuttal packet only when it is genuinely thinner than the new sub-branch layer, for example:

- one host site's temporary intake freeze inside `RS-EPA-PARTNER-CAPACITY`;
- one regulator's short extraordinary suspension window inside `RS-EPA-LICENCE-SAFETY`;
- one provider's once-off system outage during a `QS-SS-BATCH-OFFER` cycle;
- or one local booking anomaly inside `QS-SS-ROLLING-SLOT` that does not define the queue regime.

Keep content as permanent local residue when it still sets substantive merits, regulator-owned deadlines, partner acceptance rules, or emergency thresholds rather than process minima.

## How far the new `RS-EPA-*` and `QS-SS-*` sub-branches now genuinely travel

The archive can now close `FT-0041` directly. The new sub-branches do **not** all travel equally once they exist. The next portability question turns less on sector labels alone and more on an **authority boundary**: who actually owns the exposure permission, seat inventory, or lawful substitute path once a challenge is live.

| Sub-branch | What may harden unchanged across sectors | When it must split again | Why the archive draws the line here |
|---|---|---|---|
| `RS-EPA-PARTNER-CAPACITY` | the `RW-EXPOSURE` band, the duty to publish the earliest meaningful review point, and the expectation that the closest dignified off-client / supervised / simulation / evidence-building path be named | when the educational provider no longer controls even the substitute path, because host or regulator approval determines both exposure and interim alternatives | ordinary slot scarcity travels; authority to promise an interim route does not |
| `RS-EPA-LICENCE-SAFETY` | only the lawful-review floor: name the no-exposure reason, the earliest lawful review point, and the closest lawful evidence-building path | when provider-side readiness clearance and externally imposed legal / regulator / host bars need different publication promises | a provider-controlled no-exposure judgment and an externally imposed no-exposure bar are not the same authority shape |
| `QS-SS-BATCH-OFFER` | `RW-FORFEITURE`, publication of the active cycle trigger, and anti-penalty expectations like reserve / carryover / next-offer handling where feasible | only when a special statutory reservation or partner-law window rewrites ordinary cycle protection | synchronized cycle closure is the recurring problem, and it travels better than the surrounding local formulas |
| `QS-SS-ROLLING-SLOT` | `RW-FORFEITURE`, publication of the active slot-loss trigger, and the anti-penalty expectation that the learner not silently fall to ordinary fresh-entry treatment | when the office handling challenge does not control the slot inventory and therefore cannot itself promise rebooking or carryover | rolling queues change character once challenge ownership and slot ownership separate |

Three narrower judgments follow:

1. `RS-EPA-PARTNER-CAPACITY` usually travels farther than `RS-EPA-LICENCE-SAFETY` because capacity scarcity is more portable than lawful no-exposure authority;
2. `QS-SS-BATCH-OFFER` usually travels farther than `QS-SS-ROLLING-SLOT` because synchronized cycle mechanics are more portable than continuously reallocated inventory owned by another office or partner;
3. the next meaningful split is therefore **authority-sensitive**, not just sector-sensitive.

## The first authority-sensitive splits now worth naming

Two of the new sub-branches now look patterned enough to deserve one more named split before the archive leaves everything else to rebuttal packets.

| Parent sub-branch | New split | Where it fits | Inherited overlay that still travels | What still stays local |
|---|---|---|---|---|
| `RS-EPA-LICENCE-SAFETY` | `RS-EPA-LS-PROVIDER-CLEARANCE` | provider- or supervisor-owned no-exposure judgments where the educational body still owns the readiness review and can reopen access without waiting for an external regulator or host to lift a bar | publish the no-exposure reason, the earliest review before the next exposure point, and the nearest lawful evidence-building or simulation route | substantive fitness criteria, assessor judgments, and local remediation design |
| `RS-EPA-LICENCE-SAFETY` | `RS-EPA-LS-EXTERNAL-BAR` | regulator-, host-, employer-, or law-imposed no-exposure bars where the educational body cannot itself restore live access | publish the no-exposure reason, the earliest lawful review point, and the nearest lawful non-exposure route without implying a local override that does not exist | regulator calendars, legal conditions, host rules, and reporting duties |
| `QS-SS-ROLLING-SLOT` | `QS-SS-RS-SAME-OWNER` | the office handling challenge also controls the next comparable slot or can actually preserve priority carryover | publish the rolling-slot trigger plus protected rebooking / carryover handling where feasible | local booking logic, service-level windows, and slot granularity |
| `QS-SS-ROLLING-SLOT` | `QS-SS-RS-CROSS-OWNER` | the challenge is handled by one office but the next comparable slot is owned by another provider, partner, or dispatch body | publish the rolling-slot trigger plus the strongest re-entry, expedited resubmission, or protected handoff the originating office can genuinely guarantee | partner acceptance rules, dispatch cadence, and external inventory control |

These splits are worth naming because they change what the institution can honestly promise while a challenge is live. The archive should not let a provider-controlled clearance case borrow the publication language of an externally imposed legal bar, and it should not let a cross-owner rolling queue pretend it can guarantee the same anti-penalty handling as a same-owner booking system.

## The first urgent-duty regime branch the archive is willing to name

The archive is still cautious about `QS-URGENT-DUTY`. Most urgent-duty routing should remain at the portable floor plus local residue. But one slice is now patterned enough to deserve a named regime branch: `QS-UD-CHILD-SAFETY`.

| Urgent-duty branch | Where it fits | What now hardens at the branch level | What still stays local |
|---|---|---|---|
| `QS-UD-CHILD-SAFETY` | safeguarding-linked routing where education providers sit inside a live multi-agency duty with children's social care, police, health, or housing / homelessness services and delay itself may frustrate child protection | immediate human handoff to a named safeguarding owner; publication of the protective-routing reason; the minimal-loss education-continuity path that remains open while protective action is underway where compatible with safety; and the first stable review point once the immediate protective step has passed | local threshold criteria, information-sharing basis, referral sequence, protective-action details, and any legally fixed intervention timetable |

This is the first urgent-duty branch the archive is willing to name because recent official signals now line up unusually well: schools and colleges remain under safeguarding obligations when using AI with pupils; DfE product-safety standards explicitly expect safeguarding flags, human help, and crisis protocols for learner distress; ICO guidance keeps profiling children and significant automated treatment on a high-risk footing; the AI Act keeps education and public-service decision uses tied to intended purpose, human oversight, and explanation; and `Working together to safeguard children 2026` makes clear that education providers sit inside a real multi-agency child-protection regime rather than an ordinary service queue. See `B102`, `B126`, `B136`, `B139`, `B142`.

The archive does **not** yet name broader `QS-URGENT-DUTY` regime branches for every legal deadline, imminent-loss, or emergency-routing case. Those patterns are still too dependent on local law, service architecture, and queue ownership. For now they remain at the portable floor plus local residue unless later revisions show a comparably stable cross-sector pattern.

## The tiny shared packet now worth hardening

The archive can now close `FT-0042` directly. Inside `RS-EPA-LS-EXTERNAL-BAR`, `QS-SS-RS-CROSS-OWNER`, and `QS-UD-CHILD-SAFETY`, it is now willing to harden a **small authority-sensitive shared packet**.

This is **not** a shared merits code. It does not set regulator thresholds, partner acceptance rules, queue formulas, or safeguarding intervention criteria. Its job is smaller: to make the authority shape legible whenever the office explaining the present position is not the same body that can lift the bar, restore the slot, or end the protective regime.

| Shared packet field | What should be published across all three branches | Why this now travels |
|---|---|---|
| branch + authority shape | the named branch in use, the local human owner, and the type of outside authority or regime that actually controls restoration or release | affected people need to know whether they are facing an internal review, an external bar, a cross-owner queue, or a safeguarding regime, not just a generic `case under review` label |
| present constraint family | the typed reason family at issue — for example external bar, cross-owner slot-loss risk, or protective routing — without pretending to publish the full local merits threshold | DfE and ICO transparency expectations travel better at the level of intelligible reason family than at the level of hidden local tests |
| non-override statement | what the originating office cannot lawfully or operationally promise, override, or accelerate on its own | the archive should not let institutions imply they can restore live access, inventory position, or protective release when another authority actually owns that decision |
| earliest meaningful review point | the earliest lawful review point, partner decision point, or first stable safeguarding review point, keyed to the next real event rather than a generic inbox receipt | AI Act explanation / oversight logic and the archive's own review-before-irreversible-step floor both depend on an intelligible event anchor |
| strongest guaranteed interim path | the strongest non-fake continuity path the local office can genuinely guarantee while the outside authority still controls the outcome | cross-sector reuse is possible only at the level of truthful interim protection, not at the level of pretending every branch can promise the same substitute outcome |
| challenge / explanation route | who can explain the current status, who can change it, where the complaint or challenge should go, and whether any live challenge changes the local treatment posture | a visible route for explanation, complaint, human intervention, and handoff is the minimum portable rights floor once multiple authorities are in play |

Three limits matter.

1. The shared packet may publish the **shape** of authority, but not the substantive merits rule.
2. The shared packet may publish the **next meaningful review point**, but not a fake universal deadline that conflicts with law, regulator calendars, or live safeguarding duties.
3. The shared packet may publish the **strongest genuine interim path**, but not a promise of restoration, rebooking, or release that the local office does not control.

## What still stays local after the shared packet hardens

| Branch | What the shared packet now makes public | What still stays local |
|---|---|---|
| `RS-EPA-LS-EXTERNAL-BAR` | the outside bar type, no-override statement, earliest lawful review point, and nearest lawful non-exposure path the provider can actually guarantee | substantive fitness / safety criteria, regulator or host reporting duties, legal conditions, and authority-specific calendars |
| `QS-SS-RS-CROSS-OWNER` | the cross-owner queue shape, the active slot-loss trigger family, the strongest genuine re-entry / expedited resubmission / protected handoff the originating office can guarantee, and where challenge should be directed | partner acceptance rules, dispatch cadence, inventory-allocation logic, and exact re-entry priority formulas |
| `QS-UD-CHILD-SAFETY` | the protective-routing branch, named safeguarding owner, first stable review point, minimal-loss continuity path compatible with safety, and the explanation / complaint route that remains available | safeguarding threshold criteria, referral sequence, information-sharing basis, protective-action details, and legally fixed intervention timetables |

This gives the archive a sharper middle position. These branches no longer collapse into one opaque `local-only` blob, but they still do **not** inherit one generic regulator code, one generic queue formula, or one generic child-protection playbook.

## Which shared-packet fields now strengthen into authority-family variants

The archive can now close `FT-0043` directly. It is **not** going to turn every shared-packet field into another proliferating code family. The tighter answer is that only some fields now travel one level further by **authority family**, while others should stop at the branch or remain local residue.

| Shared packet field | What now happens | Why the archive draws the line here |
|---|---|---|
| branch + authority shape | strengthen into authority-family variants | the affected person should now be told not just that the case is `authority-sensitive`, but whether the live shape is regulator-bar, host-bar, public-dispatch, partner-inventory, provider-led safeguarding review, or a formal multi-agency child-protection stage |
| present constraint family | strengthen only as a **coarse** family label; detailed reason taxonomies stay local | intelligible explanation travels at the level of `external bar`, `cross-owner dispatch`, or `protective safeguarding stage`, but not at the level of each regulator test, host rule, allocation formula, or referral threshold |
| non-override statement | strengthen into authority-family variants | once the authority family is known, the non-override claim is patterned enough to publish truthfully — for example `provider cannot lift regulator bar`, `originating office cannot compel partner inventory`, or `school cannot end a formal child-protection stage alone` |
| earliest meaningful review point | strengthen into authority-family variants | the next real review event now depends more on the authority regime than on local drafting style: lawful regulator / host reconsideration, dispatch cycle or partner release point, safeguarding-owner review, strategy discussion, section 47 outcome, or child protection conference |
| strongest guaranteed interim path | keep mostly branch-local, with only family-level guardrails | truthful interim protection still depends heavily on what the local office can lawfully or operationally guarantee, so the archive should name the guardrail shape but not pretend that one interim path travels unchanged across authorities |
| challenge / explanation route | strengthen into authority-family variants | who can explain the present position and who can actually change it is now patterned enough to publish one level more concretely, even though local complaint bodies and escalation calendars still vary |

Two consequences follow.

1. The archive is willing to harden **authority-family variants** for authority shape, non-override, review point, and challenge / explanation route.
2. It is still **not** willing to harden one generic interim-protection or full reason-taxonomy code across those families.

## The first authority-family variants now worth publishing

These are **not** new permanent branch IDs. They are small authority-family variants inside the shared packet so the archive can say more than `authority-sensitive` without multiplying the branch tree.

| Branch | Authority-family variant | What now hardens at the family level | What still stays local |
|---|---|---|---|
| `RS-EPA-LS-EXTERNAL-BAR` | **regulator-bar** | publish that restoration depends on a regulator / legal / licensing authority; state that the provider cannot lawfully override the bar; anchor review to the next lawful reconsideration, appeal, relicensing, or regulator review point; and state whether explanation, challenge support, and decision change sit with the provider, regulator, or both | substantive criteria, statutory tests, evidence requirements, reporting duties, and authority-specific calendars |
| `RS-EPA-LS-EXTERNAL-BAR` | **host-bar** | publish that restoration depends on a host / placement / employer-controlled suitability or access decision; state that the provider cannot compel exposure; anchor review to the next host reconsideration, suitability review, or placement-board event; and state whether the provider can only prepare the learner or can also request host review | host-specific suitability rules, local supervisory judgments, placement design, and host calendars |
| `QS-SS-RS-CROSS-OWNER` | **public-dispatch** | publish that the next comparable place is controlled by a dispatching / allocating body rather than by the originating office; state whether the origin can preserve a packet, date, or referral status; anchor review to the next dispatch cycle, allocation panel, or public routing decision point; and make the challenge handoff visible | dispatch formulas, statutory priorities, reservation rules, and batch-allocation mechanics |
| `QS-SS-RS-CROSS-OWNER` | **partner-inventory** | publish that the next comparable place depends on partner-held inventory; state that the originating office cannot promise release or acceptance; anchor review to the next partner release, acceptance, or re-offer point; and state whether the strongest route is expedited resubmission, protected handoff, or evidence-preserving re-entry | partner acceptance rules, inventory logic, cadence, and exact priority formulas |
| `QS-UD-CHILD-SAFETY` | **provider-led safeguarding review** | publish the named safeguarding owner inside the provider, the first internal safeguarding review point, the non-override statement for any already-engaged outside agency, and the explanation route while protective routing is still being managed locally | provider thresholds, internal safety-planning details, information-sharing basis, and exact supervision arrangements |
| `QS-UD-CHILD-SAFETY` | **formal multi-agency child-protection stage** | publish that the case has entered a formal multi-agency protection stage; identify the local safeguarding owner plus the live external regime; anchor review to the next strategy discussion, section 47 decision, initial child protection conference, review conference, or equivalent stage event; and make clear that the provider cannot unilaterally end the stage | protective-action details, multi-agency thresholds, conference / plan content, referral sequence, and legally fixed timetables |

This split is grounded in current official signals rather than archive taste alone. DfE product-safety guidance expects educational AI systems to state purpose and audience clearly and to route distress or safety issues toward human help rather than burying them in product language. Current DfE education guidance still says pupil-facing use needs stronger safeguards than teacher-facing use. ICO guidance keeps profiling children and significant automated treatment on a high-risk footing, requiring clear information and human intervention / challenge routes. The AI Act keeps human oversight central when AI touches high-risk decisions or fundamental rights. And `Working together to safeguard children 2026` makes a real stage distinction visible: Family Help remains a voluntary support route, while strategy discussions, section 47 enquiries, and child protection conferences sit inside a formal multi-agency child-protection regime. See `B102`, `B125`, `B126`, `B139`, `B142`.

## What still does **not** travel inside the authority-family variants

Even after `FT-0043`, three things still stop short of family-level hardening.

1. **full merits taxonomies** — the archive will name only the family-level reason shape, not the full regulator test, host suitability rule, dispatch formula, or child-protection threshold;
2. **interim-path specifics** — the archive will require a truthful interim path, but the concrete path still depends on what the local office can actually guarantee;
3. **legal and procedural calendars** — the archive will require an event anchor, not a fake universal turnaround promise.

That restraint matters. The archive is now more legible than rev0055, but it still refuses to turn the hottest authority-sensitive branches into fake portable procedure codes.

## The first reusable mini-codes now worth naming

The archive can now close `FT-0044` directly. It is willing to harden a **very small mini-code layer** inside the authority-family variants, but only for things that already travel as shapes rather than as calendars or merits rules.

### Event-anchor mini-codes

| Mini-code | What it means | Where it now travels | What still stays local |
|---|---|---|---|
| `EA-REG-RECONSIDER` | the next lawful regulator reconsideration, appeal, relicensing, or equivalent external fitness review point | `RS-EPA-LS-EXTERNAL-BAR` when the live authority family is regulator-bar | exact filing rules, evidence thresholds, hearing mechanics, and authority-specific dates |
| `EA-HOST-SUITABILITY` | the next host suitability, placement-board, access-review, or equivalent host-controlled exposure decision point | `RS-EPA-LS-EXTERNAL-BAR` when the live authority family is host-bar | host calendars, supervisor judgments, local placement design, and host-specific review criteria |
| `EA-DISPATCH-CYCLE` | the next dispatch, routing, or allocation cycle / panel that can actually move the learner | `QS-SS-RS-CROSS-OWNER` when the live authority family is public-dispatch | dispatch formulas, reservation rules, statutory priority logic, and cycle timings |
| `EA-PARTNER-RELEASE` | the next partner release, acceptance, re-offer, or comparable inventory-opening point | `QS-SS-RS-CROSS-OWNER` when the live authority family is partner-inventory | partner cadence, inventory rules, acceptance standards, and exact re-entry priority formulas |
| `EA-SG-OWNER-REVIEW` | the first provider safeguarding-owner review point while the case remains on a provider-led protective route | `QS-UD-CHILD-SAFETY` when the live authority family is provider-led safeguarding review | internal casework method, exact supervision arrangements, and local safeguarding thresholds |
| `EA-CP-STAGE` | the next formal multi-agency protection stage event — for example strategy discussion, section 47 outcome, initial child protection conference, or review conference | `QS-UD-CHILD-SAFETY` when the live authority family is formal multi-agency child-protection stage | legal timetables beyond the named stage family, conference content, referral sequence, and plan details |

These are **event-family anchors**, not promised durations. They tell the learner or family which kind of event now matters next; they do not invent a universal response-time SLA where law, regulator calendars, partner inventory, or safeguarding duties still control.

### Interim-protection mini-codes

| Mini-code | What it means | Where it now travels | What still stays local |
|---|---|---|---|
| `IP-NO-EXPOSURE-CONTINUITY` | preserve educational continuity without putting the learner into the barred placement, assessment exposure, or unsafe route | regulator-bar and host-bar readiness cases where the office can still guarantee adjacent learning without fake restoration | the actual substitute activity, staffing, timetable, transport, and accessibility arrangements |
| `IP-PACKET-PRESERVATION` | preserve dossier / evidence / date integrity while the restoring authority still sits elsewhere | regulator-bar, public-dispatch, and partner-inventory cases where the office can genuinely keep the learner's packet alive without promising the outcome | exact preservation duration, rank effects, and documentary requirements |
| `IP-PROTECTED-HANDOFF` | provide a human-mediated re-entry, transfer, or resubmission path without pretending the originating office controls the receiving inventory | partner-inventory and some public-dispatch cases where a truthful handoff is stronger than a fake restoration promise | receiving-party acceptance rules, slot formulas, and guaranteed priority level |
| `IP-SAFETY-COMPATIBLE-CONTINUITY` | maintain the strongest learning / support continuity that remains compatible with an active protective route and human-help duties | provider-led safeguarding review and formal multi-agency child-protection stages | contact rules, supervision terms, information-sharing basis, and protective-plan content |

These are **shape codes**, not portable entitlements to one identical substitute service. The archive will now publish the strongest truthful shape, but still refuses to pretend that one concrete interim package travels unchanged across regulators, hosts, dispatch systems, partner inventories, and safeguarding regimes.

## Why these mini-codes now travel

This is still a narrow move. The archive is not creating a full procedural taxonomy. It is responding to a cluster of current official signals that now line up strongly enough for this smaller layer: DfE's current product-safety standards require clear stated purpose, governance, complaints routes, safeguarding escalation, and human-help pathways; ICO guidance requires simple ways for people to request human intervention or challenge significant automated decisions and regular checks that such systems still work as intended; the European Commission's current AI Act guidance says high-risk uses in education and essential services depend on intended purpose, must assign human oversight, and must provide a clear and meaningful explanation when a high-risk output is used for a legal-effect decision; and `Working together to safeguard children 2026` makes certain safeguarding stage events and review points public enough to name without pretending that every local timetable or protection plan is portable. See `B102`, `B126`, `B142`, `B143`.

## What still remains local even after the mini-codes harden

Even after `FT-0044`, five things still stop short of reusable coding.

1. **exact deadlines and calendars** — the archive will name the event family, not a fake cross-sector turnaround promise;
2. **full merits tests** — regulator fitness rules, host suitability criteria, queue formulas, and safeguarding thresholds still remain local;
3. **rank or slot guarantees** — packet preservation and handoff can travel as shapes, but not as universal priority promises;
4. **protective-plan content** — safeguarding continuity still depends on live human judgment, multi-agency coordination, and lawful information-sharing;
5. **accessibility / logistics specifics** — travel, timetable, staffing, supervision, and accommodation details still depend on the local service and learner.

## Which mini-codes now harden into default pairings, publication triggers, and limited anti-penalty effects

The archive can now close `FT-0045` directly. It is **not** going to turn every mini-code into a portable consequence bundle. The tighter answer is that only some authority families now earn a default pairing between **one review-event anchor** and **one truthful interim-protection shape**, plus a narrow publication trigger and an even narrower anti-forfeiture or anti-punishment floor.

Three rules discipline the move.

1. A default pairing hardens only where the family almost always has **one event that actually matters next** and **one truthful interim path shape** that does not fake restoration.
2. The publication trigger hardens only when the branch first imposes a **material access, exposure, or routing constraint**, or when the authority family changes while the case remains live.
3. The anti-penalty effect hardens only as a **limited non-forfeiture or non-punishment floor**. A challenge does **not** generically pause a regulator bar, compel partner inventory, stop a public dispatch cycle, or suspend a live protective route unless law or local regime rules already say so.

| Authority-family variant | Default pairing that now hardens | When the pairing must be published | Limited effect that now travels | What still stays local |
|---|---|---|---|---|
| **regulator-bar** | `EA-REG-RECONSIDER` + `IP-PACKET-PRESERVATION`; add `IP-NO-EXPOSURE-CONTINUITY` only where the provider can genuinely preserve adjacent learning without fake restoration | publish when the external bar first blocks ordinary exposure or when the next lawful reconsideration route materially changes | preserve dossier / date integrity while reconsideration is pending, and do not treat barred non-exposure itself as learner non-compliance when the published continuity path is followed | filing rules, evidence thresholds, whether adjacent learning is possible, and any rank or relicensing effects |
| **host-bar** | `EA-HOST-SUITABILITY` + `IP-NO-EXPOSURE-CONTINUITY`; add `IP-PACKET-PRESERVATION` only where a comparable dossier or placement packet can honestly stay live | publish when a host-controlled suitability or access decision blocks the ordinary exposure path | no ordinary attendance / completion penalty for the blocked exposure segment when the learner follows the published substitute path; challenge does not compel host acceptance | substitute-hour requirements, host review criteria, placement design, and any preserved-date effect |
| **public-dispatch** | `EA-DISPATCH-CYCLE` + `IP-PACKET-PRESERVATION`; add `IP-PROTECTED-HANDOFF` only where the originating office can genuinely pass a live packet onward | publish when a dispatching body rather than the originating office owns the next comparable place, especially where a missed cycle would otherwise create hidden loss | no silent forfeiture of packet / date integrity merely because explanation, challenge, or rerouting is still in motion; this is not a guaranteed slot freeze or rank boost | dispatch formulas, statutory priorities, protected categories, and cycle timing |
| **partner-inventory** | `EA-PARTNER-RELEASE` + `IP-PROTECTED-HANDOFF`; add `IP-PACKET-PRESERVATION` where the originating office can keep dossier integrity live while inventory sits elsewhere | publish when partner-held inventory now governs return, re-offer, or transfer and the originating office cannot lawfully promise release | no learner-borne blame for partner-release delay once the learner has completed the published handoff packet; this is not a guaranteed acceptance or priority promise | partner acceptance rules, inventory cadence, re-offer formulas, and any guaranteed ordering |
| **provider-led safeguarding review** | `EA-SG-OWNER-REVIEW` + `IP-SAFETY-COMPATIBLE-CONTINUITY` | publish when the protective route materially changes normal access, contact, attendance expectations, or channel use | complying with protective instructions should not itself be recorded as disengagement, misconduct, or voluntary withdrawal where the published safety-compatible route is followed; challenge does not automatically pause the protective route | supervision terms, contact rules, information-sharing basis, and the concrete support plan |
| **formal multi-agency child-protection stage** | `EA-CP-STAGE` + `IP-SAFETY-COMPATIBLE-CONTINUITY` | publish when the case enters a formal stage or when the named stage changes the ordinary educational route | the same minimal non-punishment floor travels for compliance with protective restrictions, but live treatment pause and stage-specific challenge posture remain local to the governing regime | referral thresholds, conference content, legal timetables, plan terms, and cross-agency information practice |

Two consequences follow.

1. The archive is now willing to harden a **default pairing and publication trigger** for each of the currently named authority families.
2. It is still **not** willing to harden one generic challenge-pause rule, one universal slot-preservation effect, or one portable substitute package across those families.

## Why this narrower consequence layer now travels

This is still a tightly bounded move rather than a new procedure code. Current official signals line up at the level of clear notice, human-help routing, and non-fake challenge paths, not at the level of one portable merits calendar. DfE's current product-safety standards require formal complaints mechanisms, understandable operations, safeguarding contacts, and learner-facing flows that direct people to human help rather than isolation or secrecy. ICO guidance says profiling children or making automated decisions about them is likely high-risk and requires a DPIA, and its rights guidance expects information about processing plus simple ways to request human intervention or challenge a significant automated decision. The European Commission's current AI Act guidance says high-risk classification depends on intended purpose and requires human oversight for high-risk uses in areas including education and essential services. `Working together to safeguard children 2026` makes multi-agency stage events concrete enough to name, while still leaving detailed thresholds and plan content local. See `B102`, `B126`, `B139`, `B142`, `B143`.

## What still remains local after `FT-0045`

Even after the default pairings harden, four things still stop short of portable inheritance.

1. **challenge-pause posture** — the archive will now publish whether a challenge changes packet preservation or the explanatory route, but it still refuses to pretend that challenge automatically pauses a bar, queue effect, or protective route;
2. **priority / rank / acceptance consequences** — packet preservation and protected handoff may travel as shapes, but exact queue position, acceptance, or restoration effects still remain local;
3. **substitute package content** — no-exposure continuity and safety-compatible continuity travel only as truthful shapes, not as one cross-sector bundle of hours, staffing, channels, or accommodations;
4. **stage and merits detail** — regulator tests, host suitability rules, dispatch formulas, partner standards, and safeguarding thresholds still remain local residue.

## When an omitted or weakened pairing now becomes a visible departure

The archive can now close `FT-0046` directly. Not every local wording difference is a departure. A **published rebuttal packet** is now required only when one of the archive's newly hardened authority-family pairings or limited anti-penalty floors is materially missing, weaker, or replaced in a way that changes the learner-facing consequence path.

Four tests now decide that threshold.

1. **anchor-loss test** — the local system no longer publishes the next review-event anchor that the family otherwise inherits, or replaces it with a vague `case-by-case review` promise.
2. **shape-loss test** — the local system drops the truthful interim-protection shape that the family otherwise inherits (`IP-PACKET-PRESERVATION`, `IP-NO-EXPOSURE-CONTINUITY`, `IP-PROTECTED-HANDOFF`, or `IP-SAFETY-COMPATIBLE-CONTINUITY`) without publishing an equal or stronger truthful substitute.
3. **floor-loss test** — the local system weakens the limited non-forfeiture / non-punishment floor into silence, pure discretion, or post hoc mercy instead of a stated baseline.
4. **meaning-shift test** — the local system keeps similar words but shifts the owner, route, or condition enough that a learner would reasonably face a different consequence path unless the difference is published.

A difference may remain **harmless implementation detail** only when all five of these stay true at once: the same branch and authority-family variant are still correctly named; the same or earlier review-event anchor is still public; the same or stronger truthful interim-protection shape remains guaranteed; the same or stronger limited anti-penalty floor still applies; and the explanation / challenge route is no harder to find or use. If the difference is only office naming, document format, calendar formatting, or another non-consequence detail, no rebuttal packet is needed.

| Local difference | Rebuttal packet? | Archive judgment |
|---|---|---|
| the site publishes a more specific same-family event than the archive mini-code, but the review point is the same or earlier and the challenge route is unchanged | no | this is implementation detail, not a hidden consequence change |
| the site keeps the archive pairing and states a stronger learner protection than the limited family floor | no | stronger protection does not need a rebuttal packet unless it silently changes family or branch |
| the site drops `IP-PACKET-PRESERVATION` and only says the learner may try again later | yes | packet/date integrity has been materially weakened into ordinary re-entry |
| the site keeps `IP-SAFETY-COMPATIBLE-CONTINUITY` but removes the no-disengagement / no-misconduct floor for compliance with the protective route | yes | the protective route now carries a materially different consequence posture |
| the site says there is `review on request` but no longer names the next review event, owner, or stage change | yes | the missing event anchor turns a hardened pairing into opaque local discretion |
| the site adds extra local documents or office steps while still preserving the same anchor, truthful interim shape, limited floor, and challenge route | no | friction alone is not yet the relevant departure unless it changes the consequence path |

## Minimum fields for the new departure packet

The packet can stay small. It now needs only seven fields:

1. **live branch + authority-family variant + departure class** (`OMIT`, `WEAKEN`, or `REPLACE`);
2. **the default pairing or limited floor that would otherwise travel**;
3. **reason family** (`LAW`, `EXTERNAL-OWNER`, `SAFETY-DUTY`, `NO-HONEST-SUBSTITUTE`, or `LOCAL-LOGISTICS`);
4. **the strongest truthful substitute that still is guaranteed now**;
5. **the concrete learner-facing consequence that now differs from the archive default**;
6. **the first review / expiry trigger for the departure itself**;
7. **the named human owner plus explanation / challenge route**.

That is intentionally smaller than a full local procedure code. Its job is only to stop a deployer from keeping a material omission inside footnotes, casework notes, or vendor-specific implementation language once the family pairing had already hardened.

## When repeated departure packets now force branch creation, cooling, or office-bound reclassification

The archive can now close `FT-0047` directly. A departure packet is for **truthfully publishing variance**, not for protecting a false inherited default forever. Once the same omission, weakened floor, or substitute-shape failure repeats in a patterned way, the archive now treats the repetition itself as governance evidence.

Five tests now decide that threshold.

1. **same-default test** — the packets concern the same live branch, authority-family variant, and hardened pairing / limited floor rather than loosely similar local notices;
2. **independent-repeat test** — the same departure class and learner-facing consequence difference now appears across **3 independent owners / sites** or across **2 independent owners / sites** where the reason family is already structural (`LAW` or `EXTERNAL-OWNER`);
3. **persistence test** — inside one owner, the same departure survives its own published review / expiry trigger and reappears at the next materially comparable cycle, stage, or allocation event;
4. **reason-lock test** — the packet keeps citing the same structural reason family (`LAW`, `EXTERNAL-OWNER`, or `NO-HONEST-SUBSTITUTE`) rather than a one-off repair gap;
5. **sibling-asymmetry test** — the repeat cluster concentrates in one named sub-branch while sibling branches keep the inherited default without packets.

The thresholds are intentionally low. These rails already sit in the archive's hotter consequence-bearing zone, so the archive is not going to wait for large-`n` program evaluation before admitting that a published default is overclaiming what actually travels.

| Repeat pattern | Archive move now required | What the move means |
|---|---|---|
| same-default + independent-repeat + reason-lock across the whole live authority-family variant | **cool the inherited default** | the current pairing or limited floor no longer travels truthfully enough to stay hardened; the archive should weaken it to the strongest baseline that still holds without repeated packets |
| same-default + sibling-asymmetry concentrated in one named sub-branch | **branch** | the archive should stop forcing the whole family to carry departures and instead create or strengthen the narrower branch where the different rule is patterned |
| same-default + persistence inside one owner after the packet's own review / expiry trigger, but without broader cross-owner spread | **reclassify as office-bound / local-only** | the archive should stop presenting that owner's treatment as inherited family behaviour and publish it as local residue until remediation or wider evidence says otherwise |
| repeated `NO-HONEST-SUBSTITUTE` packets across independent owners | **cool the interim-protection shape or limited anti-penalty floor** | the archive should admit that the stronger shape does not actually travel and retreat to the weaker truthful baseline rather than repeating exceptions |
| packet disappears by the first named review trigger or the local system gives a stronger learner protection with no consequence-path loss | **keep as local packet only** | transient repair or genuinely stronger protection does not yet change the inherited default |

Three consequences follow.

1. **Repeated packet publication is no longer enough.** Once the cluster tests are met, the archive expects the inherited default itself to change.
2. **Branching beats family-wide cooling when asymmetry is real.** If the repeat cluster lives mainly inside one sub-branch, the archive should split there rather than weakening the whole family.
3. **Office-bound persistence is evidence too.** Even without cross-owner spread, one owner cannot keep republishing the same packet after its own review trigger and still present the underlying behaviour as an inherited portable rule.

## Why this repeat-cluster rule now travels

This is an inference from current official governance signals, not a claim that any one regulator publishes these exact archive thresholds. Those signals nevertheless line up in the same direction: DfE's current product-safety standards require clear governance, complaints routes, and human-help paths for educational AI products; ICO guidance says organisations should carry out regular checks to make sure systems are working as intended and keep human intervention / challenge routes simple and usable; the Commission's current AI Act guidance says deployers of high-risk systems must monitor operation, act on identified risks or serious incidents, and provide information / explanation paths in relevant cases; and the UK public-sector AI Playbook plus Data and AI Ethics Framework both treat documentation and understandable public information as live governance obligations rather than one-time launch paperwork. Together those signals support the archive's narrower move: once the same published default keeps generating the same visible departure, the response should become **governance change**, not endless exception publication. See `B102`, `B126`, `B143`, `B144`, `B145`.


This is a small transparency and contestability move, not a new merits code. Current official signals already support it: DfE's current product-safety standards require clear stated purpose, governance, complaints routes, and user-facing escalation / support paths; DfE's current education guidance says schools and colleges should be open and transparent where automated decision-making or profiling is in play and ensure pupils and parents understand AI processing; ICO guidance requires information about relevant automated processing, simple ways to request human intervention or challenge a significant automated decision, and meaningful information about logic and consequences where Article 22 conditions apply; the UK government's current AI Playbook and Data and AI Ethics Framework both say public bodies should document algorithmic tools used in decision-making and make that information clearly accessible, easy to find, and understandable; and `Working together to safeguard children 2026` keeps stage changes and multi-agency ownership visible enough that a hidden omission in the published path is not a harmless wording choice. See `B102`, `B139`, `B142`, `B143`, `B144`, `B145`.

## Current archive bet

The archive's current best guess is now narrower and more operational still: **`RS-EPA-PARTNER-CAPACITY` and `QS-SS-BATCH-OFFER` usually travel farther than their siblings because scarcity mechanics travel better than authority boundaries; `RS-EPA-LICENCE-SAFETY` and `QS-SS-ROLLING-SLOT` should split once publication promises depend on who actually owns the lawful exposure decision or slot inventory; inside urgent-duty routing only the child-safeguarding slice is currently patterned enough to deserve a named regime branch; inside those hottest authority-sensitive branches a tiny shared packet can now harden, but only at the level of authority shape, event-anchored review, truthful interim protection, and visible explanation / challenge routes; inside that packet only authority shape, non-override, review point, and challenge route deserve one more family-level strengthening; inside those authority families only a very small set of event-anchor and interim-protection shapes deserve reusable mini-codes; inside those mini-codes only one default pairing, one publication trigger, and one limited anti-forfeiture or anti-punishment floor now travel by authority family; and once those have hardened, a rebuttal packet is required only when a local omission, weakening, or replacement actually changes the learner-facing consequence path rather than merely restating the same protection in local language. The archive now adds one more narrow rule: once repeat-cluster evidence has already forced a branch, cooling move, or office-bound reclassification, recovery requires a causal fix, a clean run through the same event family, independent confirmation at the level of travel being claimed, and active monitoring evidence that the quieter picture is not just suppressed use or hidden local handling.**

That is a better fit than either extreme:

- pretending the new `RS-EPA-*` and `QS-SS-*` sub-branches now travel unchanged just because they have names;
- refusing any further inheritance and dumping every authority-sensitive difference back into opaque rebuttal packets;
- turning every shared-packet field into another proliferating mini-code family;
- pretending that named event families automatically carry one shared timetable or one guaranteed interim package;
- pretending that any live challenge automatically pauses a bar, queue effect, or protective route;
- or forcing a rebuttal packet for every harmless local phrasing difference once a family pairing exists.

## When downgraded defaults have actually earned recovery

The archive can now close `FT-0048` directly. **Recovery is not the absence of packets for a while.** A cooled, branched, or office-bound default has earned hardening again only when the archive can now point to a causal fix, the same consequence-bearing event passing cleanly, and live monitoring evidence that the quieter picture is not just underuse, diversion, or hidden local handling.

Five tests now decide that threshold.

1. **cause-fixed test** — the structural reason that produced the downgrade has been changed, constrained to a narrower branch, or explicitly removed; a default does not recover merely because staff now write a gentler packet for the same unchanged gap.
2. **same-event clean-run test** — the same live event family that previously generated the packet now passes without that packet through **2 materially comparable cycles** or **1 full cycle across 2 independent owners / sites**.
3. **independent-confirmation test** — where the archive wants family-level travel again, at least **2 independent owners / sites** using the same branch and authority-family variant now publish the recovered element without a new packet; single-owner quiet is not enough for family recovery.
4. **truthful-substitute test** — the previously weakened pairing, floor, or substitute shape is now genuinely back in force; a weaker local workaround, lower-visibility challenge route, or informal mercy path does not count as recovery.
5. **live-monitoring test** — the owner or provider is still carrying out regular checks, review-interval monitoring, or post-deployment analysis, and the apparently cleaner picture is not explained only by suppressed use, rerouting away from the branch, or temporary closure of the underlying pathway.

These thresholds are still intentionally small. The archive is not asking for a fresh large-`n` efficacy study before a governance default may recover. It is asking for enough evidence to show that the same consequence-bearing path is now being governed truthfully.

| Downgraded state | What now counts as recovery evidence | Archive move now allowed |
|---|---|---|
| **cooled family default** | cause fixed + same-event clean run + independent confirmation + no active packet on the same pairing / limited floor | **re-harden one rung** to the strongest family default that now travels truthfully |
| **branched sub-branch** | sibling branches now show the same recovered pairing / floor through comparable cycles, and the branch-specific packet disappears without leaving a weaker truthful substitute behind | **merge upward** only if the branch distinction has actually stopped mattering |
| **office-bound / local-only reclassification** | a second independent owner / office using the same authority shape now runs the same element cleanly, or one owner runs it cleanly through repeated comparable cycles and the original structural blocker has been removed rather than merely tolerated | **promote back to authority-family variant**; single-owner quiet alone is not enough |
| **cooled interim-protection shape or limited anti-penalty floor** | repeated `NO-HONEST-SUBSTITUTE` packets no longer recur, and the stronger truthful shape is now genuinely guaranteed again across comparable cycles | **restore the stronger shape / floor** one level up |
| **packet only, never downgraded** | packet disappears by its own review trigger and no repeat-cluster threshold is met | **retire the packet** with no archive-level change |

Four consequences follow.

1. **Time alone never re-hardens a default.** A quiet interval without the same live event, or without active monitoring, is not recovery evidence.
2. **Recovery is causal, not cosmetic.** The archive wants evidence that the old reason no longer governs the same path, not merely a tidier publication note.
3. **Recovery happens one layer at a time.** A cooled family default does not jump straight back to a stronger cross-family claim, and an office-bound rule does not become a sector-wide inheritance in one move.
4. **False quiet does not count.** If the branch is now rarely used because access was narrowed, learners were diverted elsewhere, or the route was administratively frozen, the archive treats that as changed exposure, not successful recovery.

## Why this recovery rule now travels

This is still an archive inference, not a claim that any one regulator publishes these exact recovery thresholds. The official signals nevertheless line up. DfE's current product-safety standards say that if new features or modifications are added, developers should review the intended purpose, and they also expect ongoing monitoring plus published review intervals in child-development impact planning. ICO guidance says organisations should provide simple ways to request human intervention or challenge a decision and carry out regular checks to make sure systems are working as intended; the ICO also keeps profiling children and significant automated treatment on a high-risk DPIA footing. The AI Act now adds two current lifecycle signals from the same official stack: risk management for high-risk AI is a continuous iterative process requiring regular systematic review and updating, and post-market monitoring should actively and systematically collect and analyse relevant data throughout the system's lifetime. Together those signals support the archive's narrower move: once a default has already been cooled, branched, or reclassified for honest governance reasons, it should recover only on monitored evidence that the same consequence-bearing path now runs cleanly again. See `B102`, `B139`, `B143`, `B146`, `B147`.

## When re-hardened defaults automatically reopen, and when later packets stay local

The archive can now close `FT-0049` directly. **Recovery does not buy infinite grace.** Once a default has been re-hardened, the archive no longer treats every later packet as equal. Some later signals now automatically reopen the recovered element; others stay as ordinary local variance unless they start repeating again.

Five relapse tests now decide the first cut.

1. **same-structural-relapse test** — the same live branch, authority-family variant, and previously recovered pairing / limited floor now fail again for the same structural reason family (`LAW`, `EXTERNAL-OWNER`, `NO-HONEST-SUBSTITUTE`, or `SAFETY-DUTY`) before the archive has seen another clean comparable run through the same event family.
2. **rights-floor-loss test** — the recovered element loses one of the pieces that made recovery truthful in the first place: the named human owner, explanation / challenge route, review-event anchor, strongest truthful interim-protection shape, or limited anti-forfeiture / anti-punishment floor.
3. **serious-incident test** — the same consequence path is now tied to a serious incident, safeguarding-stage escalation, or other reportable exposure-to-harm event rather than an ordinary local inconvenience packet.
4. **monitoring-blindness test** — the owner or provider can no longer show the regular checks, post-deployment monitoring, or review-trigger evidence that made the recovered state believable; a recovered default cannot stay hardened once its monitoring evidence disappears.
5. **material-path-change test** — a later model, workflow, authority-owner, slot-owner, or protective-stage change means the old clean-run evidence no longer speaks to the live path, even if no new packet has yet repeated.

These tests are deliberately narrower than the repeat-cluster rule. They do **not** automatically cool the family default all the way back down. They first decide whether the recovered element must be reopened immediately for renewed scrutiny rather than continuing to enjoy recovered status.

| Later signal after re-hardening | Archive treatment now | Why |
|---|---|---|
| same structural reason returns on the same branch / authority-family variant before another clean comparable run | **automatic reopen** | the recovery evidence has not survived the first comparable reuse |
| explanation / challenge route, named owner, event anchor, truthful interim shape, or limited floor disappears | **automatic reopen** | the recovered element has lost the rights-compatible shell that justified recovery |
| serious incident, safeguarding-stage escalation, or other reportable harm tied to the same path | **automatic reopen** | consequence-bearing harm is no longer ordinary local variance |
| relevant model / workflow / authority-owner change makes the old clean-run evidence stale | **automatic reopen** | recovery evidence does not travel unchanged across a materially different path |
| one-off `LOCAL-LOGISTICS` packet with same anchor, same or stronger truthful interim protection, same limited floor, and same challenge route | **ordinary local packet only** | this is still truthful local variance rather than structural relapse |
| stronger local protection or earlier review point than the recovered default promised | **ordinary local packet only** | stronger protection does not itself defeat recovery |
| isolated packet that disappears by its own next review trigger and does not recur across the same event family | **ordinary local packet only** | transient local repair is not yet relapse evidence |

A later packet may remain **ordinary local variance** only while all five of these stay true at once: the same recovered branch and authority-family variant are still correctly named; the same or stronger explanation / challenge route is still live; the same or stronger truthful interim-protection shape and limited floor still hold; no serious incident or safeguarding-stage escalation has attached to the same path; and the packet is either local logistics or another transparently bounded local reason that disappears by the next named review trigger.

Four consequences follow.

1. **Recovered status is conditional, not permanent.** The archive now distinguishes between a harmless new local packet and a relapse that reopens the recovered default immediately.
2. **One serious rights or harm signal is enough to reopen.** The archive does not wait for repeat-cluster thresholds once the same path has produced a serious incident, a safeguarding-stage escalation, or a visible rights-floor loss.
3. **Ordinary local packets still exist.** A recovered default does not collapse just because one site publishes a local logistics packet while preserving the same anchor, interim shape, floor, and challenge route.
4. **Reopening is not yet full downgrade.** Once reopened, the archive reuses the existing branch / cool / office-bound tools if repeat evidence accumulates again, rather than inventing a second enforcement tree.

## Why this relapse rule now travels

This remains an archive inference rather than a claim that any one regulator publishes these exact relapse thresholds. The official signals nevertheless line up in the same direction. DfE's current product-safety standards expect ongoing monitoring, review of intended purpose when new features or modifications are added, and visible human-help / complaints routes. ICO guidance says organisations should provide simple ways to request human intervention or challenge a decision and carry out regular checks to make sure systems work as intended; that makes monitoring loss and rights-route loss relevant relapse signals rather than harmless admin drift. The AI Act's current official service-desk materials add two more lifecycle signals from the same post-deployment stack: providers should actively and systematically collect post-market data, and serious incidents on high-risk systems should trigger reporting rather than being treated as ordinary local noise. `Working together to safeguard children 2026` sharpens the same point for `QS-UD-CHILD-SAFETY`: once a path has moved into a real safeguarding stage, the archive should not treat that as just another local packet on a recovered queue or route default. Together those signals support the archive's narrower move: after recovery, the first question is no longer only whether packets are repeating, but whether the recovered default has lost the very conditions that justified trusting it again. See `B102`, `B142`, `B143`, `B146`, `B148`.

## When post-recovery extra sensitivity expires, and which later changes reset it

The archive can now close `FT-0050` directly. **Reopened once does not mean watched forever.** After a re-hardened default has survived the first relapse rule, the archive now allows that extra sensitivity to earn down again — but only after enough clean comparable reuse under the same live path, with active monitoring still running, and without a hidden reset.

Five tests now decide whether the extra watch may expire.

1. **same-path survival test** — after recovery and after the first relapse screen, the same branch / authority-family variant / pairing or limited floor now survives either **2 additional materially comparable event cycles** or **1 additional full cycle across 2 independent owners / sites** with no automatic reopen signal.
2. **watch-monitoring test** — at least **1 named review interval or post-deployment monitoring checkpoint** actually closes during that watch window; missing monitoring evidence means the watch cannot expire.
3. **rights-shell continuity test** — the same named owner, explanation / challenge route, event anchor, truthful interim-protection shape, and limited anti-forfeiture / anti-punishment floor remain in force, or become stronger, through the watch window.
4. **no-hidden-reset test** — no substantial modification, intended-purpose shift, authority-owner swap, slot-owner change, queue-governance change, protective-stage change, or workflow / model / memory change that would materially alter the path has occurred without starting a fresh watch.
5. **no-repeat-return test** — no same-path repeat cluster has rebuilt beneath the threshold; isolated `LOCAL-LOGISTICS` packets may still exist only if they disappear by the next named review trigger while preserving the same or stronger rights shell.

These thresholds stay intentionally small. The archive is not demanding a new large-scale study before the extra sensitivity can earn down. It is asking for enough monitored comparable reuse to show that the recovered path is no longer living on probation simply because the archive once distrusted it.

| Re-hardened element | What now counts as watch expiry | Archive move now allowed |
|---|---|---|
| **family default or authority-family variant** | same-path survival + watch monitoring + rights-shell continuity + no hidden reset | **expire the special relapse watch**; later packets return to the archive's ordinary local / relapse / repeat-cluster rules unless a reset trigger occurs |
| **promotion from office-bound / local-only back to authority-family travel** | same-path survival at the promoted authority-family level, with at least **1** clean comparable cycle under the live owner/authority arrangement that will now inherit the rule | **treat the promoted rule as an ordinary recovered authority-family variant** rather than a still-fragile exception |
| **restored truthful interim shape or limited floor** | the stronger truthful shape / floor survives the same named anchor through **2 additional comparable anchor uses** without a new `NO-HONEST-SUBSTITUTE` packet | **let the stronger shape / floor travel without extra relapse sensitivity** |

Six later changes now **reset the watch immediately**, even if no new packet has yet appeared.

1. **substantial-modification / intended-purpose reset** — the system or service undergoes a substantial modification, or its intended purpose / use case changes, in a way that could affect the governed path.
2. **authority-owner reset** — lawful exposure authority, slot ownership, or the named decision owner changes in a way that makes the old clean-run evidence no longer speak to the live route.
3. **governance-regime reset** — batch offer becomes rolling slot, provider suitability screening becomes partner release control, or provider-led safeguarding review becomes a formal multi-agency protective stage (or the reverse).
4. **material workflow / model / memory reset** — the live path now depends on a different workflow architecture, model family, memory regime, or automation boundary than the one that earned recovery.
5. **rights-shell redesign reset** — the explanation / challenge route, event anchor, interim shape, review-before-irreversible-step promise, or limited floor is redesigned rather than merely preserved or strengthened.
6. **monitoring-basis reset** — the monitoring plan, review interval structure, or observable event family used to support recovery changes enough that the old watch evidence is no longer directly comparable.

Not every change resets the watch. **Staff turnover, copy edits, bug fixes, or pre-determined documented maintenance inside the same intended purpose and same governed path do not reset it by themselves.** The archive only resets when the change would make inherited trust about the same path misleading.

Four consequences follow.

1. **Extra sensitivity expires on comparable reuse, not on elapsed time alone.** Quiet calendar time without the same live path or without an actual monitoring checkpoint does not earn it down.
2. **A reset is not yet a downgrade.** It restarts the watch because old evidence no longer cleanly transfers, but it does not by itself prove that the recovered default has failed again.
3. **History is not erased when the watch expires.** If the same structural reason returns later, the ordinary relapse and repeat-cluster rules still apply; expiry only removes the special hair-trigger status.
4. **The archive now distinguishes between path-preserving maintenance and trust-breaking path change.** That keeps the rule from collapsing into either infinite vigilance or careless inheritance.

## Why this watch-expiry / reset rule now travels

This remains an archive inference rather than a claim that any one regulator publishes these exact expiry thresholds. The official signals nevertheless line up. DfE's current product-safety standards expect developers to review intended purpose when new features or modifications are added, test new versions or models before release, maintain ongoing monitoring, and publish child-development review intervals. ICO guidance expects simple ways to request human intervention or challenge a decision plus regular checks that systems are working as intended. The EU's current AI Act materials sharpen the reset side: intended purpose is what determines high-risk classification in sensitive areas such as education and essential services, deployers of high-risk systems must monitor operation and act on identified risks or serious incidents, and substantial modifications or intended-purpose changes require a new conformity assessment. `Working together to safeguard children 2026` keeps protective-stage changes visible enough that provider-led safeguarding review and formal multi-agency child-protection handling should not inherit each other's old watch evidence without a reset. Together those signals support the archive's narrower move: once a re-hardened default has survived its first relapse screen, the extra sensitivity may earn down on monitored comparable reuse, but only until a later path-changing event makes older recovery evidence no longer trustworthy. See `B102`, `B142`, `B143`, `B149`, `B150`.

The next problem is narrower again: when several individually non-resetting micro-changes accumulate on the same recovered path, when should the archive stop treating them as harmless maintenance and force a fresh reset cluster? See `OQ-0023`.
