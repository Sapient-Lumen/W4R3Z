# Failure escalation, safe degradation, and manual fallback

## Current overlay

Failure handling now includes security, evidence, and authority failure, not only outages. If a
service exceeds its approved `AA` ceiling, loses construct validity, exposes protected data, fails
red-team checks, or creates hidden workload, the safe fallback may be human-only operation, narrowed
use, re-pilot, or retirement rather than a technical retry.

This document closes the archive's next implementation gap about **what educational institutions
should do when a deployed AI service starts drifting, failing, harming, or becoming ungovernable in
live use**.

The archive's current bet is:

> treat model failure, harmful drift, and silent capability change as governance events rather than
as ordinary product maintenance; cool, narrow, suspend, or roll back the service before learners are
asked to absorb the risk.

The point is to avoid four predictable failures at once:

- **silent update drift** — a vendor or institutional team swaps models, prompts, memory settings,
  or tools and the educational function changes before anyone re-governs it;
- **harm without a brake** — the system produces unsafe, biased, manipulative, or rights-sensitive
  outputs but staff have no published threshold for cooling or stopping it;
- **service collapse as learner burden** — a tutoring, advising, or proof workflow fails and
  learners are still penalized for missed deadlines, blocked access, or lost continuity;
- **incident theatre** — institutions say humans remain accountable, but no owner, fallback path, or
  reopen condition has actually been specified.

Current public signals point in the same direction. The UK DfE's current product-safety standards
say educational AI products should state their intended purpose and target demographic, review that
purpose when features change, maintain robust monitoring and reporting, test new versions or models
before release, and publish a mental-health crisis protocol for learner-facing systems. The DfE's
current AI-in-education guidance also says safety should be the top priority and that risk
assessments should include plans for unauthorised use cases. The European Commission's educator
guidance continues to frame AI use as a context-based ethical and legal decision rather than an
improvisation. The EU AI Act then sharpens the lifecycle floor for higher-risk systems: continuous
risk management, post-market monitoring, serious-incident reporting, and deployer duties to inform
providers and authorities when serious incidents occur. The UK NCSC's secure-AI guidance adds the
operational posture: monitor behaviour and inputs, use secure-by-design update practice, and
maintain defined incident procedures and lessons-learned loops. See `B102`, `B105`, `B123`, `B124`,
`B125`.

## Relationship to the rest of the archive

This document works alongside:

- the deployment ladder in
  [`general-purpose-vs-purpose-built-deployment-ladder.md`](general-purpose-vs-purpose-built-deployment-ladder.md);
- the student-, teacher-, and institution-facing default tables;
- the observability/retention grammar in
  [`minimum-observability-and-retention-without-surveillance.md`](minimum-observability-and-retention-without-surveillance.md);
- the starter failure-profile layer in
  [`sector-and-function-profile-splits-for-failure-defaults.md`](sector-and-function-profile-splits-for-failure-defaults.md);
- the change-governance grammar in
  [`model-and-workflow-change-classification-and-fresh-review-triggers.md`](model-and-workflow-change-classification-and-fresh-review-triggers.md);
- and the public-route continuity surfaces in `../30-operations/`.

It does **not** replace those tools.

It adds one thing only:

- a **cross-cutting failure, escalation, and fallback grammar** for deciding when a live
  educational-AI service may continue under observation, when it must narrow or cool, and when it
  must suspend or roll back before further use.

The archive's rule is simple: **every recurring educational-AI service should have a visible human
owner, a visible brake, and a visible non-punitive fallback path**.

## The escalation ladder (`F0-F4`)

| Level | Name | Ordinary meaning | Default posture |
|---|---|---|---|
| `F0` | observe in place | small anomaly, low-stakes mismatch, or one-off quality defect with no rights or safety consequence | continue temporarily with local observation and quick correction |
| `F1` | contain and notify | repeated low-stakes failure or a localized issue affecting one class, one workflow, or one service cohort | keep use narrow, notify the named owner, and stop spread while checking whether the issue is local or systemic |
| `F2` | cool and narrow | drift, update regression, suspicious pattern, or rights-sensitive ambiguity that does not yet justify full shutdown | disable risky features, require stronger human confirmation, restrict to safer cohorts/tasks, or switch to a cooler substitute workflow |
| `F3` | suspend the affected function | the current function is no longer safe, fair, explainable, or reliable enough for live use | stop the affected function and route learners/staff to a manual or non-AI substitute path |
| `F4` | roll back and formally pause | serious incident, systemic rights or safety risk, or inability to explain or contain the failure | roll back or disable the system/service, open formal review, and do not reopen until named conditions are met |

The archive prefers the coolest sufficient response, but it rejects the opposite mistake: leaving a
service live because escalation would be inconvenient.

## Trigger families (`H1-H7`)

These are starter trigger families, not a full incident manual.

### `H1` — safeguarding, self-harm, or manipulative response

The system produces, escalates, or mishandles harmful, coercive, isolating, or crisis-adjacent
interaction in a learner-facing context.

Minimum response: `F3`, and `F4` if the issue is systemic or tied to a release/update.

### `H2` — silent capability change or unexplained regression

A model swap, prompt/workflow change, new tool connection, memory setting, or vendor update changes
behaviour enough that the existing governance classification may no longer fit.

Minimum response: `F2` until the service is re-checked; `F3` when the affected function is
high-stakes, repeated, or rights-bearing.

### `H3` — rights-sensitive or bias-bearing differential treatment

The service appears to generate materially different treatment by disability status, language
status, demographic group, or protected-support pathway, or it pushes learners into opportunity,
intervention, or proof burdens that comparable peers do not face.

Minimum response: `F3` for the affected function, with `F4` where the pattern appears systemic.

### `H4` — observability or data-boundary breach

Logging, retention, cross-function reuse, third-party access, or training use crosses the published
boundary, or the institution cannot state who now has access to which learner or teacher data.

Minimum response: `F2` for low-stakes/local issues; `F3-F4` where protected data, minors, formal
assessment, or public-route records are involved.

### `H5` — high-stakes use without real human control

A grading, pathway, selection, safeguarding, accommodation, or official-record workflow is being
materially shaped by AI output that the accountable human cannot explain, correct, or genuinely
override.

Minimum response: `F3`.

### `H6` — reliability or availability failure in a time-sensitive context

The service becomes unavailable, erratic, too slow, or too inconsistent for a deadline-bearing,
attendance-bearing, or continuity-bearing educational task.

Minimum response: `F2` if a cooler path is immediately available; otherwise `F3` with manual
fallback and no learner penalty.

### `H7` — owner incapacity

The named local owner cannot interpret the alerts, review the outputs, or manage the service at the
speed the context requires.

Minimum response: `F2` while narrowing scope; `F3` when the human-accountability layer has clearly
become performative rather than real.

## Minimum crosswalk for recurring functions

| Context | Ordinary minimum when a trigger fires | First substitute path |
|---|---|---|
| optional student study help or low-stakes practice | `F1-F2` | static materials, teacher-curated practice, office hours, or ordinary search/library support |
| recurring tutoring, advising, accessibility routing, or well-being support | `F2-F3` | named human support path, bounded static guidance, or staffed office workflow |
| teacher planning and materials drafting | `F1-F2` | teacher-authored templates, prior materials, or non-generative tooling |
| teacher feedback assistance or marking support | `F2-F3` | manual marking/comment path or a previously approved rubric-only workflow |
| institution-facing queueing, flags, or decision support | `F2-F4` | manual triage, queue freeze, or human-only review of affected cases |
| assessment-critical or public-route continuity functions | `F3-F4` | manual continuity rule, extension, challenge/bridge substitute, or protected human review |

The archive's current posture is conservative in one specific way: **the hotter the function, the
less room there is for “monitor for now” as the first response**.

## No-learner-penalty default for system-caused failure

When an institution-approved AI path moves to `F2-F4`, the learner should not be made the buffer for
institutional indecision.

The default front-end rule is:

- pause or extend deadlines that depended on the failing service;
- provide a manual or lower-tech substitute path where one exists;
- do not convert loss of access into attendance, participation, integrity, or punctuality penalties;
- route any resulting continuity burden through the archive's no-fault transition and public-route
  protections where recognition or progression is affected.

This is not a blank cheque for every missed task. It is a narrow rule for **system-caused
interruption of an approved path**.

## What counts as a governance change rather than ordinary maintenance

The archive now treats the following as presumptively governance-relevant changes for recurring
services:

1. switching the underlying model or major model family;
2. enabling memory, tool use, browsing, agentic steps, or new integrations;
3. expanding to a new user group, age band, office, or stakes context;
4. changing observability, retention, or data-sharing behaviour;
5. changing the default fallback, escalation owner, or reopen condition;
6. making a once-optional tool the ordinary required path for a course, office, or public service.

These changes do not always require full re-procurement. But they do require a **fresh local
governance check**.

## What institutions should publish

For each recurring educational-AI service, publish six small fields in addition to the
deployment/default tables:

1. the named local owner;
2. the highest ordinary escalation level the service may reach before leadership review is
   mandatory;
3. the first substitute or manual fallback path;
4. whether the no-learner-penalty default applies and in which contexts;
5. what kinds of change count as governance-relevant updates rather than ordinary maintenance;
6. the minimum reopen condition after `F3` or `F4`.

This is usually enough to stop the common failure where an institution says a human remains
accountable but never states who pauses the tool, who informs learners or staff, what happens to
deadlines or case queues, or what evidence is needed before reopening.

## What counted as a real archive gain

The archive previously knew how to classify AI functions, how much observability they should carry,
and where human handoff or sign-off begins. It still lacked a compact answer to a simpler
operational question: **what happens when the service goes wrong on a Tuesday afternoon while
learners, teachers, or advisors still need the work to continue?**

This document adds that missing brake. It makes failure handling part of educational governance
instead of leaving it to vendor status pages, informal teacher heroics, or learner self-absorption
of the loss.

## Current archive bet

The archive's current best guess is that a tiny failure-escalation ladder plus a visible manual
fallback rule will outperform both extremes:

- silent continuation under drift, because nobody wants to trigger a pause;
- and blanket risk aversion, where institutions avoid useful AI support because they never specified
  how to narrow, cool, or stop it responsibly.

That claim is now canon, but now sits alongside a starter profile layer for hotter contexts. The
next problem is narrower: which of those starter failure profiles are stable enough to harden, where
they should branch further by office, stakes, or modality, and when model or workflow changes should
force an even hotter review path rather than a routine freeze exemption. See `OQ-0010`.
