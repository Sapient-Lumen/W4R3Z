# Sector and function profile splits for failure defaults

## Current overlay

Failure profiles now include claim failure. If a scaled service does not support its claimed
learning, access, workload, safety, validity, contestability, or security benefit, the failure path
may be demotion, re-pilot, claim relabeling, or retirement rather than ordinary bug repair.

This document closes the archive's next governance gap about **which failure defaults should already
split by sector and function before local evidence accumulates, because one generic `F0-F4` ladder
is too blunt for minors, formal assessment, professional gatekeeping, and public-route services**.

The archive's current bet is:

> keep one generic failure-escalation ladder as the floor, but publish a second tiny starter profile
layer wherever developmental duty, exam-window integrity, supervised-practice safety, or
benefits-linked public routing already makes a uniform brake-and-fallback default misleading.

The point is to avoid five predictable failures at once:

- **slow brakes in hot contexts** — institutions apply the same gradual `F1-F2` posture to minors,
  exam monitoring, public-route allocation, and low-stakes study help even when the hotter contexts
  need a faster stop;
- **mid-window change drift** — model swaps, prompt rewrites, tool activation, or policy edits land
  during exam periods, live placements, or intake windows and are treated as ordinary maintenance;
- **reopen theatre** — a vendor says an issue is fixed and the institution reopens the service
  without checking whether local owners, manual substitutes, and affected cohorts are actually
  ready;
- **discretionary no-penalty timing** — learners lose marks, queue position, attendance credit, or
  route continuity while staff argue about whether the outage or error was serious enough to count;
- **one-service-fits-all incident writing** — generic incident response language hides that some
  educational functions already need stricter default owners, faster freezes, or stronger reopen
  conditions.

Current public signals point in the same direction. The UK DfE's current product-safety standards
say educational AI products should state their intended purpose and target demographic, test new
versions or models before release, and use child-centred design for learner-facing products. The
European Commission's current AI Act guidance says deployers of high-risk systems must monitor
operation, act upon identified risks or serious incidents, assign human oversight, and in some
public-service contexts carry out a fundamental-rights impact assessment before first use. Ofqual's
current AI-marking principles then sharpen the hot end in assessment by centering safety,
transparency/explainability, fairness, accountability/governance, and contestability/redress in a
domain that still depends on trained human judgment. See `B102`, `B124`, `B126`, `B127`.

## Relationship to the generic failure ladder

This document does not replace
[`failure-escalation-safe-degradation-and-manual-fallback.md`](failure-escalation-safe-degradation-and-manual-fallback.md)
or
[`model-and-workflow-change-classification-and-fresh-review-triggers.md`](model-and-workflow-change-classification-and-fresh-review-triggers.md).

It adds one thing only:

- a **starter profile layer** for places where the archive already knows the generic failure
  defaults need a pre-declared split.

The generic failure ladder still answers the first question:

- is the issue small enough to observe,
- serious enough to contain,
- hot enough to cool and narrow,
- severe enough to suspend,
- or systemic enough to roll back and formally pause?

This document answers the second question:

- in this sector or function, does the archive already know that the first brake must be faster, the
  no-penalty rule must attach earlier, or the reopen condition must be stricter?

## The starter profile table

The archive keeps this table intentionally small. These are **starter inherited profiles**, not a
full incident manual.

| Profile | Scope | Ordinary examples | Default hot adjustments | Change-freeze / fresh-review defaults | Reopen floor | Why the split exists |
|---|---|---|---|---|---|---|
| `FP-K12-MINORS` | repeated learner-facing AI for minors, school-managed copilots, welfare-adjacent chat, and school-device AI that can shape attendance, discipline, or support routing | school homework/revision help, school help chat, school copilots, attendance follow-up, wellbeing or support-routing surfaces | treat `H1`, `H3`, and serious `H4` as minimum `F3`; use `F2` for `H6` only if a staffed substitute is already live the same day; attach no-learner-penalty immediately where the approved path shaped homework access, attendance, behaviour follow-up, or welfare support | do not make major model/prompt/tool/memory changes during active pastoral interventions or formal school assessment windows without fresh local review plus a visible fallback; child-facing expansion to a younger cohort always counts as fresh governance review | named service owner plus safeguarding lead review, checked communication path for affected learners/families/staff, and a brief live smoke test with real school scenarios before reopening at scale | minors create a faster duty of care and a lower tolerance for “monitor for now,” but that duty should still route through visible adults rather than into ambient surveillance or informal teacher heroics |
| `FP-FORMAL-ASSESS` | controlled assessments, proctoring, exam-support workflows, marking support, and assessment-critical AI use where validity or candidate treatment is at stake | remote or in-lab proctoring, AI-assisted marking support, assessment workflow triage, controlled practical assessments, cheating-monitoring tools | treat `H2`, `H5`, and serious `H6` as minimum `F3`; treat `H4` affecting candidate traces, marks, or security as `F4` unless clearly local and reversible; no candidate penalty, late mark, or integrity inference should ride through unresolved `F2-F4` events | freeze major model, prompt, policy, or workflow changes for the live assessment window unless a fresh review explicitly approves them; any substantial change to cheating-monitoring, marking support, or controlled-assessment tooling counts as a fresh governance review, not maintenance | accountable assessment owner confirms manual or previously approved substitute workflow, centres/candidates get a visible handling rule, and affected cases can be rechecked by trained humans before full reopen | assessment-critical AI sits closest to qualification validity and public trust, so the archive rejects casual mid-window drift and weak reopen discipline |
| `FP-PRO-PRACTICE` | professional-practice education where AI touches supervised readiness, simulation, remediation, or progression toward live client/patient-facing work | clinical simulation debrief, practicum support, readiness remediation, apprenticeship coaching, progression review in safety-critical programmes | treat `H5` and safety-relevant `H3/H6` as minimum `F3`; use `F4` when the issue could distort readiness-to-practice or client/patient safety decisions; no adverse readiness or progression action should rely on a function currently sitting at `F2-F4` | do not change models, tools, or key prompt/workflow logic mid-cycle in a readiness, remediation, or placement-decision workflow without supervisor review and a visible human-only substitute path; expansions from coaching into gatekeeping always count as fresh governance review | programme lead plus supervising practitioner confirm that affected judgments can be re-performed or checked by accountable humans, and that any reopened tool is again clearly subordinate to direct human supervision | professional-practice contexts already mix educational support with safety-bearing human judgment, so they need hotter brakes before AI drift can quietly influence gatekeeping or remediation |
| `FP-PUBLIC-ROUTE` | adult basic education, workforce, library, and public-service learning routes where AI can influence intake, queue order, referral, funded-seat access, or linked-service movement | intake chat, route triage, multilingual help, seat allocation support, referral support, benefits-adjacent learning navigation | treat `H3`, `H5`, and queue/routing `H6` as minimum `F3`; treat cross-agency or record-boundary `H4` as minimum `F4`; preserve queue position, provisional place, or route continuity until a human alternative is available | do not make substantial model/workflow changes during active intake, enrollment, or mandated-participation windows without a parallel human route and public notice; any expansion from optional help into eligibility, referral, or allocation support counts as a fresh governance review | named office owner confirms explanation and contestability are again live, affected learners retain a human path while the tool is reintroduced, and any public-facing notices or standing instructions are updated before reopen | public-route systems can look clerical from the inside while materially shaping access to scarce seats, funded support, or linked public services, so outage or drift should not be absorbed as ordinary learner friction |

## Reading the profiles correctly

These profiles are **overlays**, not replacements.

The generic failure ladder still answers the first question:

- is the institution observing, containing, cooling, suspending, or rolling back?

This document answers the second question:

- in this sector or function, does the archive already know that the first ordinary brake must start
  hotter, faster, or with a stronger freeze window?

That means the same underlying model can inherit different failure defaults in different settings:

- an optional study helper in ordinary higher education may still begin under the generic failure
  ladder;
- the same model used in a school-managed learner-facing system for minors belongs under
  `FP-K12-MINORS`;
- a similar system used for controlled assessment belongs under `FP-FORMAL-ASSESS`, where mid-window
  change tolerance is much lower;
- and the same family of tool used for public intake, referral, or funded-route support belongs
  under `FP-PUBLIC-ROUTE`, where queue position and explanation duties matter immediately.

## Timing rules the archive now treats as knowable in advance

Local incident data still matters, but the archive now treats five timing rules as knowable
**before** local evidence accumulates.

### 1. In hot contexts, `F2` is not an ordinary resting state

Where minors, live assessment, supervised-practice gatekeeping, or public-route allocation are
involved, `F2` should usually be brief and transitional. If the institution cannot name the
substitute path, the accountable owner, and the review window, the service should not stay at `F2`
indefinitely.

### 2. Front-end no-penalty should attach early, not after blame sorting

If an institution-approved path fails in one of these hotter contexts, the learner should not wait
for backend fault attribution before deadlines, queue position, or progression protection activates.

### 3. Live windows narrow the meaning of “maintenance”

A substantial model, prompt, tool, memory, or workflow change during an exam period, active pastoral
intervention, readiness cycle, or intake window should be presumed governance-relevant even if the
vendor labels it a routine update.

### 4. Reopen needs local operational readiness, not just a vendor fix

A reopened educational service still needs a named owner, a functioning fallback, an explanation
path where rights or stakes require it, and a local check that the service again behaves within the
approved boundary.

### 5. Human-only substitute paths should already exist for the hottest functions

In assessment-critical, readiness-critical, and public-route allocation contexts, the archive now
treats the existence of a human substitute path as part of the deployment floor, not as a bonus
contingency to be invented after failure.

## What institutions should publish

Where a local failure rule inherits one of these profiles, publish one extra line with only six
additions beyond the generic failure fields:

1. profile identifier (`FP-K12-MINORS` through `FP-PUBLIC-ROUTE` or local equivalent);
2. which trigger families are treated as minimum `F3` or `F4` under that profile;
3. when the no-learner-penalty rule attaches by default;
4. which live windows carry change-freeze or fresh-review expectations;
5. who must sign off on reopen in addition to the ordinary local owner;
6. whether affected learners retain queue position, deadline protection, or provisional continuity
   during the pause.

This keeps the public layer small while blocking the common failure where an institution publishes
one generic incident rule but never says that minors, formal assessment, professional gatekeeping,
and public-route services already require different first-response expectations.

## What counted as a real archive gain

The archive previously knew that recurring educational-AI services need visible brakes, visible
owners, and non-punitive fallback paths. It still lacked a compact answer to a harder operational
question: **where do we already know the generic brake is too slow, the generic reopen condition is
too weak, or the generic “maintenance” label is too forgiving?**

This document answers that with a bounded starter layer. It keeps the generic `F0-F4` grammar, but
it now makes the archive more deployable across schools, assessment systems, professional education,
and public-route coordination without pretending those contexts share one default tolerance for
drift or outage.

## Current archive bet

The archive's current best guess is that a **generic failure ladder plus a tiny sector-and-function
profile layer** will outperform both extremes:

- one universal incident rule for all educational-AI services;
- and bespoke service-by-service incident writing with no inherited defaults.

That claim is now canon, but still live. The next problem is narrower: which of these starter
failure profiles are stable enough to harden, where they should branch further by office, stakes, or
modality, and when model or workflow changes should force an even hotter review path rather than a
routine freeze exemption. See `OQ-0010`.
