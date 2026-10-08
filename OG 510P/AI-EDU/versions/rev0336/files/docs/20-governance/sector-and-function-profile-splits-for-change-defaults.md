# Sector and function profile splits for change defaults

## Current overlay

Change profiles now reopen evidence and authority when a release changes the claim family, cohort,
construct, memory, retrieval corpus, tool authority, protected route, or security boundary. A
technically small change can be governance-major if it changes what the system can cause or what
evidence users rely on.

This document closes the archive's next governance gap about **which change defaults should already
split by sector and function before local evidence accumulates, because one generic `C0-C4` ladder
is too blunt for minors, formal assessment, professional gatekeeping, and public-route services**.

The archive's current bet is:

> keep one generic change ladder as the floor, but publish a second tiny starter profile layer
wherever developmental duty, exam-window integrity, supervised-practice safety, or benefits-linked
public routing already makes a uniform release-governance default misleading.

The point is to avoid five predictable failures at once:

- **cool maintenance labels in hot contexts** — institutions treat the same model swap, retrieval
  change, memory expansion, or workflow rewrite as ordinary `C1-C2` maintenance in minors, formal
  assessment, public-route routing, and low-stakes study help even when the hotter contexts need a
  hotter default class;
- **younger-cohort drift** — a service expands to a younger age band or more vulnerable group but
  inherits the same release posture it had with older or lower-stakes users;
- **mid-window scope stretch** — new prompt logic, new handoff rules, or new tools land during exam
  windows, active pastoral intervention, readiness cycles, or intake periods and are treated as
  harmless housekeeping;
- **backend convenience theatre** — cross-function memory, new data feeds, or queue-shaping outputs
  are described as technical improvement even when they materially alter learner treatment;
- **notice-free reopen** — services reappear after change with no visible update to the approved
  purpose, oversight path, or handling instructions for the people affected.

Current public signals point in the same direction. The UK DfE's current product-safety standards
say educational AI products should state their intended purpose and target demographic, review
intended purpose when features or modifications are added, and sufficiently test new versions or
models before release. The DfE's current school-and-college support materials also point
institutions toward planned audits, safety review, and explicit implementation support rather than
casual workflow drift. The European Commission's current AI Act guidance says conformity assessment
for high-risk systems has to be repeated when the system or its purpose is substantially modified,
while deployers must monitor operation, assign human oversight, and in some public-service contexts
carry out a fundamental-rights impact assessment before first use. Ofqual's current AI-marking
principles then sharpen the hot end in assessment by centering safety, transparency/explainability,
fairness, accountability/governance, and contestability/redress in a domain that still depends on
trained human judgment. See `B102`, `B117`, `B126`, `B127`.

## Relationship to the generic change ladder

This document does not replace
[`model-and-workflow-change-classification-and-fresh-review-triggers.md`](model-and-workflow-change-classification-and-fresh-review-triggers.md)
or
[`sector-and-function-profile-splits-for-failure-defaults.md`](sector-and-function-profile-splits-for-failure-defaults.md).

It adds one thing only:

- a **starter profile layer** for places where the archive already knows the generic change defaults
  need a pre-declared split.

The generic change ladder still answers the first question:

- is this clerical change,
- bounded maintenance,
- a behaviour-affecting in-envelope update,
- scope or cohort stretch,
- or a governance-reset / substantial modification?

This document answers the second question:

- in this sector or function, does the archive already know that some apparently bounded releases
  should start one class hotter, carry a stricter freeze window, or require stronger pre-release
  review before local evidence accumulates?

## The starter profile table

The archive keeps this table intentionally small. These are **starter inherited profiles**, not a
full release-management manual.

| Profile | Scope | Ordinary examples | Default hot adjustments | Freeze / review defaults | Notice / reopening floor | Why the split exists |
|---|---|---|---|---|---|---|
| `CP-K12-MINORS` | repeated learner-facing or school-managed AI for minors, including school copilots, welfare-adjacent chat, attendance/behaviour follow-up, and accessibility-routing surfaces | school homework/revision help, school help chat, attendance nudges, wellbeing or support-routing tools, family-facing school AI | treat any younger-cohort expansion, new persistence or memory layer, new external action, or new modality beyond text as minimum `C3`; treat cross-function data reuse, new consequence-bearing recommendation, or a shift into behaviour/attendance/support routing as minimum `C4` | do not release `C2-C4` changes during active school assessment windows or live pastoral/safeguarding interventions without fresh local review plus a visible fallback; child-facing expansion to a younger cohort always counts as fresh governance review | named service owner plus safeguarding or pastoral owner sign-off, refreshed staff and family handling instructions where relevant, and a brief live check with real school scenarios before full reopen | minors create a faster duty of care and a lower tolerance for quiet behavioural drift, but that duty should still route through visible adults rather than ambient capture or hidden escalation |
| `CP-FORMAL-ASSESS` | controlled assessments, proctoring, marking-support workflows, exam-security tools, and assessment-critical AI where candidate treatment or validity is at stake | remote or in-lab proctoring, AI-assisted marking support, cheating-monitoring tools, controlled practical assessment workflows | treat model-version changes, prompt/policy changes, retrieval changes, or workflow edits affecting candidate traces, cheating flags, marking support, or candidate handling as minimum `C3`; treat new scoring/recommendation logic, new candidate-data reuse, or new consequence-bearing outputs as `C4` | freeze `C2-C4` changes for the live assessment window unless a fresh review explicitly approves the exception; any substantial change to cheating-monitoring, marking support, or controlled-assessment tooling counts as fresh governance review, not routine maintenance | accountable assessment owner confirms the manual or previously approved substitute path, updated candidate/centre handling instructions exist where relevant, and affected cases can be rechecked by trained humans before broad reopen | assessment-critical AI sits closest to qualification validity and public trust, so the archive rejects casual mid-window release discipline or silent candidate-treatment drift |
| `CP-PRO-PRACTICE` | professional-practice education where AI touches supervised readiness, simulation, remediation, placement support, or progression toward live client/patient-facing work | clinical simulation debrief, practicum support, readiness remediation, apprenticeship coaching, progression review in safety-critical programmes | treat new tools, new memory, new data feeds, or new handoff rules in readiness/remediation workflows as minimum `C3`; treat expansions from coaching into readiness judgment, progression signaling, or placement recommendation as minimum `C4` | do not release `C2-C4` changes mid-cycle in readiness, remediation, or placement-decision workflows without supervisor review and a visible human-only substitute path; expansions from support into gatekeeping always count as fresh governance review | programme lead plus supervising practitioner confirm that affected judgments can be re-performed or checked by accountable humans and that reopened tooling remains clearly subordinate to direct supervision | professional-practice contexts already mix educational support with safety-bearing human judgment, so seemingly bounded updates can quietly become gatekeeping changes if release discipline stays generic |
| `CP-PUBLIC-ROUTE` | adult basic education, workforce, library, and public-service learning routes where AI can influence intake, queue order, referral, funded-seat access, or linked-service movement | intake chat, route triage, multilingual help, seat allocation support, referral support, benefits-adjacent learning navigation | treat new intake questions, new data-sharing edges, new external actions, or revised handoff/queue logic as minimum `C3`; treat new eligibility shaping, funded-seat prioritization, cross-agency data reuse, or route recommendation that can materially alter treatment as `C4` | do not release `C2-C4` changes during active intake, enrollment, or mandated-participation windows without a parallel human route and updated public handling instructions; any expansion from optional help into eligibility, referral, or allocation support counts as fresh governance review | named office owner confirms explanation and contestability are live, affected learners retain a human path while the tool is reintroduced, and any public notices or standing instructions are updated before scale | public-route systems can look clerical from the inside while materially shaping access to scarce seats, funded support, or linked public services, so change control should not be absorbed as ordinary administrative friction |

## Reading the profiles correctly

These profiles are **overlays**, not replacements.

The generic change ladder still answers the first question:

- what kind of release event is this?

This document answers the second question:

- in this sector or function, does the archive already know that some release events must begin
  hotter, freeze earlier, or require stronger notice and review?

That means the same underlying model can inherit different change defaults in different settings:

- an optional study helper in ordinary higher education may still begin under the generic change
  ladder;
- the same model used in a school-managed learner-facing system for minors belongs under
  `CP-K12-MINORS`;
- a similar system used for controlled assessment belongs under `CP-FORMAL-ASSESS`, where even
  apparently bounded release events start hotter;
- and the same family of tool used for intake, referral, or funded-route support belongs under
  `CP-PUBLIC-ROUTE`, where queue logic, explanation duties, and cross-agency boundaries matter
  immediately.

## What the archive now treats as knowable in advance

Local release evidence still matters, but the archive now treats five change facts as knowable
**before** local implementation evidence accumulates.

### 1. In hot contexts, some `C2` events should start as `C3`

If the release touches learner treatment, candidate handling, readiness judgment, queue order, or
public-route movement in one of these hotter profiles, the archive prefers a hotter default class
rather than waiting for harm to prove the point.

### 2. New cohort or younger-cohort expansion is never ordinary maintenance

For minor-facing systems especially, a change that expands to a younger age band or a more
vulnerable group should not inherit the cooler release posture it had elsewhere.

### 3. Live windows narrow the meaning of “in-envelope”

A release that might be `C2` in an ordinary week should often be treated like `C3` in a live
assessment window, active pastoral intervention, readiness cycle, or intake period.

### 4. Consequence-bearing outputs reset the release posture

If the change adds marks, warnings, readiness signals, queue order, route steering, or other outputs
that can materially shape treatment, the archive prefers `C4` treatment rather than calling the
change a bounded enhancement.

### 5. Reopening still requires updated local instructions

A changed service should not quietly return to scale because a vendor says the release is complete.
Local owners still need an updated handling rule, a functioning substitute path where required, and
any refreshed public or classroom/service-facing instructions.

## What institutions should publish

Where a local change rule inherits one of these profiles, publish one extra line with only six
additions beyond the generic change fields:

1. profile identifier (`CP-K12-MINORS` through `CP-PUBLIC-ROUTE` or local equivalent);
2. which change families are presumed at least `C3` under that profile;
3. which changes are presumed `C4` or fresh deployment under that profile;
4. which live windows carry freeze or exception-review expectations;
5. who must sign off on release or reopen in addition to the ordinary local owner;
6. where users can find the updated handling instructions or human alternative during the frozen
   window.

This keeps the public layer small while blocking the common failure where an institution publishes
one generic release rule but never says that minors, formal assessment, professional gatekeeping,
and public-route services already require different default classes or stronger freeze discipline.

## What counted as a real archive gain

The archive previously knew that recurring educational-AI services need visible release owners,
visible change classes, visible freeze windows, and rollback paths. It still lacked a compact answer
to a harder operational question: **where do we already know the generic change ladder is too cool,
the generic freeze window is too weak, or the generic “maintenance” label is too forgiving?**

This document answers that with a bounded starter layer. It keeps the generic `C0-C4` grammar, but
it now makes the archive more deployable across schools, assessment systems, professional education,
and public-route coordination without pretending those contexts share one default tolerance for
release drift.

## Current archive bet

The archive's current best guess is that a **generic change ladder plus a tiny sector-and-function
profile layer** will outperform both extremes:

- one universal release-governance rule for all educational-AI services;
- and bespoke service-by-service release writing with no inherited defaults.

That claim is now canon, but still live. The next problem is narrower: which of these starter change
profiles are stable enough to harden, where they should branch further by office, stakes, or
modality, and when apparently bounded updates should be presumed fresh deployment rather than a
hot-but-still-local release event. See `OQ-0011`.
