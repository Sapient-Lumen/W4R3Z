# Pilot-to-scale evidence and rollout gates

This document closes the archive's next governance gap about **what should count as scale-worthy evidence after a promising educational-AI pilot succeeds, because pilot permission and default deployment are not the same institutional act**.

The archive's current bet is:

> keep pilot permission relatively cheap, keep ordinary default deployment expensive, and make most educational AI pass through a visible limited-rollout gate before it becomes routine infrastructure.

The point is to avoid seven predictable failures at once:

- **pilot-glow extrapolation** — a charismatic local pilot is mistaken for broad readiness;
- **satisfaction proxy drift** — teacher or student liking stands in for learning, access, or safety evidence;
- **hero-operator dependence** — the tool works only with unusually strong local champions, tutors, or support staff;
- **funding-cliff rollout** — a grant-funded pilot is scaled without durable operating money or staffing;
- **professional-learning omission** — institutions treat rollout as procurement rather than as an instructional change that needs training and support;
- **version-drift amnesia** — the pilot was run on one tool, prompt, memory layer, or workflow, but scale quietly ships another;
- **predictive overreach** — a tool that classifies or flags risk is scaled on accuracy language alone even when the intervention path, false-positive burden, or contestability story is weak.

Current public signals point in the same direction. OECD's 2025 paper on AI adoption in education and its 2026 Digital Education Outlook framing both push toward guided educational use and policy roadmaps rather than casual scale. IES's new GenAI R&D centers are also instructive because they are still framed around exploratory studies, longitudinal surveys, and theory refinement rather than instant district-wide defaulting. Digital Promise's 2026 scan of state guidance then makes the maturity problem explicit: most states are still in exploratory or piloting stages, and only a smaller share have moved toward systematic evidentiary evaluation. Stanford's Tutor CoPilot result shows what stronger evidence looks like in contrast: a real-world randomized trial, a concrete pedagogical mechanism, gains in topic mastery, especially for lower-rated tutors, and a cost profile that matters for scale. Finally, IES's 2026 school-turnaround synthesis is useful precisely because it is mixed: student-facing tutoring tools show the strongest evidence, some predictive/early-warning uses remain ambiguous, and teacher-support uses still need more evidence tied to student learning. SETDA's 2025 state trends then add the operational warning that AI is now the top state edtech priority while durable funding plans and professional learning still lag. See `B11`, `B12`, `B13`, `B130`, `B131`, `B132`.

## Relationship to the archive's existing evidence rule

This document does not replace [`evidence-and-procurement.md`](evidence-and-procurement.md).

It adds one thing only:

- a **rollout-gate grammar** for deciding when a tool may move from pilot to limited expansion, from limited expansion to broad use, and from broad use to default infrastructure.

The archive already had stake-based evidence packages. It still lacked a compact answer to the narrower operational question:

- **what happens after the pilot goes well?**

This document answers that question without pretending every good pilot should scale. Read it together with [`sector-and-function-profile-splits-for-rollout-gates.md`](sector-and-function-profile-splits-for-rollout-gates.md), which says where the generic ladder already needs a hotter burden or lower ceiling before local evidence accumulates, how those inherited starter profiles should harden, branch, stay provisional, or remain capped below `RG4` rather than hardening by drift, and where the first support-versus-consequence child branches now deserve their own inherited rollout overlays.

## The rollout-gate ladder (`RG0-RG4`)

| Gate | Name | Ordinary meaning | What is true at this stage |
|---|---|---|---|
| `RG0` | exploration | sandboxing, procurement review, and theory-of-change drafting | the institution may test or compare tools, but makes no readiness claim beyond bounded exploration |
| `RG1` | bounded pilot | a time-limited, explicitly governed local pilot | the institution has a named claim, baseline or comparison plan, training path, fallback path, and stop conditions |
| `RG2` | limited monitored rollout | expansion beyond a single pilot site or cohort, but still under active review | the claim has survived more than one local context or term, subgroup/access review has begun, and change control is tighter |
| `RG3` | scale approval | the institution may use the tool broadly for the approved function | the claim is supported strongly enough for routine use, the operating model is funded, and rollback/governance are live |
| `RG4` | default infrastructure | the tool or workflow is treated as a normal institutional rail rather than a special initiative | the institution can keep the service legible, governable, affordable, and reviewable through vendor, version, and staffing change |

The ladder is about **deployment maturity**, not tool quality in the abstract. A powerful system may still belong at `RG1`, while a modest tool with stable evidence, clear funding, and good fallback may legitimately reach `RG3`.

## Read the ladder together with the claim type

The archive now makes four claim families explicit.

| Claim family | Example claim | What scale-worthy evidence must show |
|---|---|---|
| workflow claim | saves staff time, reduces friction, improves material preparation | real-world time or workload gains under ordinary conditions, plus no clear quality collapse, rights failure, or accessibility backslide |
| teaching/tutoring quality claim | improves questioning, feedback, explanation, or instructional moves | observable pedagogical improvement in authentic use, and at least some learner-outcome or practice-quality evidence rather than satisfaction alone |
| learner-outcome claim | improves understanding, mastery, transfer, persistence, or progression | direct evidence on learner outcomes in the target population and subject, ideally against a comparison condition or strong baseline |
| predictive/allocation claim | identifies risk, prioritizes support, routes cases, or informs interventions | not just prediction quality, but actionability, false-positive/false-negative review, contestability, and evidence that the intervention path outperforms current practice |

The same pilot may support one claim family without supporting another. A lesson-planning copilot might earn a workflow claim without yet earning a learner-outcome claim. A risk flagger might predict well enough to study further while still failing the archive's bar for broad routinized use.

## Minimum passage rules between gates

### Moving from `RG0` to `RG1`

Require only seven things:

1. a named educational problem;
2. a theory of change;
3. the stake level and claim family;
4. a local owner;
5. a privacy/accessibility check;
6. a baseline or comparison plan;
7. a stop-and-fallback rule.

This keeps early exploration possible without letting curiosity masquerade as rollout readiness.

### Moving from `RG1` to `RG2`

Require all of the following:

- evidence from authentic use rather than demos or synthetic tasks;
- at least one comparison to current practice, prior cohorts, or a clearly defined baseline;
- teacher, learner, and where relevant family or advisor feedback;
- first-pass subgroup and accessibility review;
- a documented decision on memory, observability, failure fallback, and change handling for the approved function;
- enough staffing and training to support expansion beyond the original champions;
- and a version boundary so the institution knows whether the expanded rollout is still the same service that was piloted.

The archive treats `RG2` as the most important gate because it blocks the common jump from “the pilot felt promising” to “make it available everywhere.”

### Moving from `RG2` to `RG3`

Require all of the following:

- repeated evidence across more than one site, cohort, or term, or else strong external evidence plus convincing local fit;
- no unresolved accessibility, subgroup, or dependency red flags;
- named durable funding and support capacity beyond a one-off pilot grant;
- professional learning that ordinary staff, not just early enthusiasts, can realistically complete;
- publication of the approved function, accountable owner, handoff path, fallback path, and review date;
- and a change-governance rule stating what future model, prompt, memory, tool, or workflow changes would reopen review.

For learner-outcome claims, the archive prefers direct outcome evidence in the real target context. For workflow-only claims, the archive still requires evidence that time savings do not merely shift burden elsewhere or degrade instructional quality.

### Moving from `RG3` to `RG4`

Require all of the following:

- the service survives routine use without leaning on exceptional local heroics;
- review continues through ordinary procurement, incident, and maintenance cycles;
- the institution can absorb or replace the function without learner penalty if the vendor, model, or workflow changes;
- public or institutional documentation stays current enough that staff and learners can still tell what is approved and why;
- and the function is one the archive can tolerate as ordinary infrastructure rather than a permanent special experiment.

Not every approved service should become `RG4`. Many educational-AI tools should remain governed `RG2-RG3` services rather than disappearing into invisible background infrastructure.

## What does **not** count as scale-worthy evidence

The archive is intentionally blunt here. The following do **not** justify broad rollout by themselves:

- vendor case studies;
- usage growth;
- chatbot eloquence;
- teacher or student enthusiasm without outcome or workload evidence;
- benchmark scores detached from classroom use;
- prediction accuracy without a better intervention path;
- a single charismatic site;
- short-term gains measured before the new support, staffing, or subsidy conditions normalize;
- or a successful pilot run on one model/version followed by scale on another.

## Automatic no-scale or re-open triggers

The archive treats six triggers as reasons to halt scale, remain local, or reopen review.

### 1. The claim outruns the evidence

If the pilot shows time savings but the rollout pitch promises learning gains, the scale claim must shrink or the evidence must grow.

### 2. Effects depend on exceptional implementers

If the apparent success relied on unusually strong tutors, teachers, coordinators, or researchers, the institution has not yet shown ordinary-operating readiness.

### 3. Subgroup or accessibility performance is materially worse

A tool that widens opportunity gaps, increases false flags for some groups, or raises disability barriers should not scale while those failures remain unresolved.

### 4. Funding or staffing collapses after the pilot

If the service only works while extra pilot staff, pilot money, or extraordinary vendor support remain in place, the archive treats broad rollout as premature.

### 5. The approved service materially changed

A new model, new prompt layer, new persistence rule, new modality, or new consequence-bearing output can force the institution back down the ladder.

### 6. The function drifts toward hotter consequences

A study helper that turns into advising, a tutoring tool that begins shaping progression, or a risk model that starts allocating cases belongs under fresh review rather than under pilot nostalgia.

## What institutions should publish before moving up a gate

For every move from `RG1` upward, publish only nine fields:

1. the approved function;
2. the current rollout gate (`RG1-RG4`);
3. the claim family;
4. the evidence summary in one paragraph;
5. the target population and excluded contexts;
6. the subgroup/accessibility findings or known limits;
7. the named funding/support horizon;
8. the model/version/workflow boundary for which the approval holds;
9. the next review date plus the human owner for rollback or complaints.

This is enough to block the familiar institutional failure where leaders say a pilot “worked,” but nobody can later recover **what** worked, **for whom**, **under what version**, **with what support**, or **for how long**.

## How this changes the archive's rollout logic

The archive already knew that evidence should rise with stakes.

It still lacked a compact answer to the narrower implementation question of **how adoption should ratchet after early success**. This document adds that missing ratchet.

It keeps three judgments separate:

- permission to explore;
- permission to run a bounded pilot;
- and permission to make a tool ordinary.

That is a real archive gain because many of the worst AI-in-education failures happen precisely in the gap between those three acts.

## Current archive bet

The archive's current best guess is that a **stake-based evidence package plus a rollout-gate ladder** will outperform both extremes:

- a world where every promising pilot is treated as scale-ready;
- and a world where institutions avoid any ratcheted rollout logic and stay trapped in endless pilotism.

That claim is now canon, but still live. The archive now has a separate starter profile layer for hotter rollout contexts, a compact disposition rule for when those profiles harden, branch, stay local, or remain capped below `RG4`, and a first pair of child branches inside each hotter parent. The next problem has moved sideways: which institution-facing starter profiles are stable enough to harden, where they should branch further by office or context, and where they should retreat back toward human-only handling. See [`sector-and-function-profile-splits-for-rollout-gates.md`](sector-and-function-profile-splits-for-rollout-gates.md) and `OQ-0007`.
