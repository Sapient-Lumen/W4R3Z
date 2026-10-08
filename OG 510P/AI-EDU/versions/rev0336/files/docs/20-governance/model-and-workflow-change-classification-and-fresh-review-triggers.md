# Model and workflow change classification and fresh-review triggers

## Current overlay

A model, prompt, retrieval, memory, tool, vendor-term, or integration change now reopens the
evidence grade and authority ceiling when it changes the claim, affected cohort, data flow, action
power, or proof burden. Treat `EV7` renewal evidence as part of change review, not as an
afterthought.

This document closes the archive's next governance gap about **when a change to an educational-AI
system is small enough to treat as maintenance and when it is large enough to require fresh review,
shadowing, notice, or a temporary freeze rather than a quiet release**.

The archive's current bet is:

> treat model, prompt, tool, memory, cohort, and workflow changes as classifiable governance events
rather than as one undifferentiated stream of “updates,” and publish in advance which classes
trigger sign-off, fresh review, shadowing, notice, or live-window freezes.

The point is to avoid five predictable failures at once:

- **maintenance theatre** — institutions describe every release as a routine update even when the
  system's behaviour, scope, or stakes materially changed;
- **silent scope stretch** — a study helper becomes an adviser, a drafting tool becomes a marker, or
  a queue assistant starts shaping access to seats or services without a fresh governance decision;
- **mid-window drift** — model swaps, tool activation, retrieval changes, or memory changes land
  during exams, active pastoral intervention, readiness cycles, or intake windows and are treated as
  harmless housekeeping;
- **one-size release discipline** — trivial bug fixes and substantial functionality changes are
  handled under the same approval path, which either over-burdens maintenance or under-governs risky
  change;
- **rollback fiction** — when a release harms or confuses users, the institution discovers too late
  that it never defined who signs off, what must be tested, or how a safe substitute path stays
  live.

Current public signals point in the same direction. The UK DfE's current product-safety standards
say educational AI products should clearly state their intended purpose and target demographic,
review intended purpose when features or modifications are added, and sufficiently test new versions
or models before release. The European Commission's current AI Act guidance says providers of
high-risk systems must repeat conformity assessment when the system or its purpose is substantially
modified, while deployers must monitor operation, assign human oversight, and act on identified
risks or serious incidents. The UK NCSC's current secure-AI guidance adds the operational posture:
monitor behaviour and inputs, use a secure-by-design approach to updates, and treat operation and
maintenance as a distinct lifecycle discipline rather than as ad hoc patching. In hot assessment
contexts, Ofqual's current AI-marking principles reinforce why this matters: when human judgment,
fairness, and contestability are central, change control cannot be reduced to a vendor release note.
See `B102`, `B123`, `B126`, `B127`.

## Relationship to the rest of the archive

This document works alongside:

- the deployment ladder in
  [`general-purpose-vs-purpose-built-deployment-ladder.md`](general-purpose-vs-purpose-built-deployment-ladder.md);
- the student-, teacher-, and institution-facing default tables;
- the observability and retention grammar in
  [`minimum-observability-and-retention-without-surveillance.md`](minimum-observability-and-retention-without-surveillance.md);
- the failure ladder and failure-profile overlay in
  [`failure-escalation-safe-degradation-and-manual-fallback.md`](failure-escalation-safe-degradation-and-manual-fallback.md)
  and
  [`sector-and-function-profile-splits-for-failure-defaults.md`](sector-and-function-profile-splits-for-failure-defaults.md);
- the sector-and-function change-profile overlay in
  [`sector-and-function-profile-splits-for-change-defaults.md`](sector-and-function-profile-splits-for-change-defaults.md).

It does **not** replace those tools.

It adds one thing only:

- a **compact change-classification grammar** for deciding when a release remains inside the already
  approved envelope and when it instead requires fresh governance review, shadowing, notice, or a
  live-window freeze.

The archive's rule is simple: **every recurring educational-AI service should have a visible release
owner, a visible change class, and a visible path for rolling back or pausing a bad change**.

## The change ladder (`C0-C4`)

| Class | Name | Ordinary meaning | Default treatment |
|---|---|---|---|
| `C0` | clerical or presentational | copy edits, link fixes, non-behavioural visual polish, internal documentation fixes, or operational maintenance that does not reasonably change user treatment or system outputs | record locally; no fresh governance review |
| `C1` | bounded maintenance | bug fixes, latency improvements, permission cleanup, harmless UI flow changes, or other small adjustments that keep the same function, same cohort, same modality, and same decision footprint | local owner sign-off plus smoke test and rollback check |
| `C2` | behaviour-affecting in-envelope update | prompt or policy retuning, moderation-threshold change, retrieval-corpus change, memory-default change, tool-parameter change, model-version update inside the already approved function, or other changes likely to alter outputs while staying within the same declared purpose | bounded pre-release evaluation, named sign-off, rollback readiness, and no release during frozen windows unless an exception path is explicitly approved |
| `C3` | scope stretch or cohort stretch | new user cohort, younger age band, new modality, new external tool, new persistence layer, new handoff rule, new data source, new office owner, or expansion from one approved function into another | fresh governance review against the deployment ladder and default tables, limited rollout or shadow period, and updated public/service documentation before scale |
| `C4` | governance-reset or substantial modification | new model family or fine-tune, new scoring or recommendation logic that can shape marks/access/progression, cross-function data reuse, expansion into high-risk or rights-sensitive educational use, or a change that materially alters the system's purpose | treat as a new governed deployment: re-approve, re-test, and re-publish before use at scale |

The archive keeps the table intentionally small. It is a **release-governance floor**, not a full
software-delivery manual.

## How to classify a change

Ask the questions in order. The first “yes” sets the minimum class.

1. **Does the change alter the system's declared purpose or the kind of educational treatment it can
   shape?** If yes, start at `C3` and often `C4`.
2. **Does it add a new cohort, especially minors or a younger age band, or move the tool into a
   hotter setting such as formal assessment, professional gatekeeping, or public-route allocation?**
   If yes, start at `C3`.
3. **Does it add or materially change memory, persistence, retrieval sources, cross-system data
   flow, or external actions?** If yes, start at `C3`.
4. **Does it materially change outputs while staying inside the same approved purpose?** If yes,
   start at `C2`.
5. **Is it only clerical or bounded maintenance with no plausible effect on user treatment or
   outputs?** If yes, it may remain at `C0-C1`.

When in doubt, classify hotter rather than cooler. The archive prefers one unnecessary fresh review
over a hidden shift in learner treatment.

## Automatic bump triggers

The archive now treats seven triggers as reasons to bump a change **at least one class hotter** than
it first appears.

### 1. New age band or vulnerability profile

A change that expands to younger learners, minors, SEND-heavy cohorts, or welfare-adjacent contexts
should not inherit the cooler class it had with an older or lower-stakes group.

### 2. New modality or capture surface

Moving from text-only interaction to audio, image, screen, biometric, or environmental capture
should usually bump the release because observability, safety, and rights expectations changed.

### 3. New persistence or memory behaviour

Even if the visible function looks the same, longer memory, new retrieval stores, or cross-session
user state can change both outputs and governance obligations.

### 4. New external tools or actions

A system that can now email, schedule, file, grade, flag, or update records is not merely a faster
version of the same assistant.

### 5. New cross-function data reuse

Using tutoring traces for advising, study activity for risk flags, or staff drafting history for
performance management is a governance reset, not a backend convenience.

### 6. New consequence-bearing output

If the release adds marks, recommendations, warnings, queue order, pathway steering, or readiness
judgments that can materially shape treatment, the class rises immediately.

### 7. Release during a protected live window

A change that might be `C2` in an ordinary week should often be treated like `C3` during active exam
windows, readiness cycles, live placements, active pastoral cases, or intake/enrolment periods.

## Default treatment by class

| Class | Minimum approval path | Testing posture | Notice / documentation posture | Fallback expectation |
|---|---|---|---|---|
| `C0` | local record only | ordinary regression or clerical check | optional internal release note | no special fallback change |
| `C1` | named local owner | smoke test with rollback confirmation | update internal operator notes if relevant | existing fallback remains enough |
| `C2` | local owner plus responsible governance contact for the service | bounded pre-release evaluation on representative tasks, harms, and edge cases; rollback path checked before release | update service record and any staff instructions that affect handling | no release unless substitute path still works if rollback is required |
| `C3` | fresh review using the deployment ladder, function defaults, observability rule, and failure rule | limited rollout, shadow period, or parallel run where feasible; check that human handoff and contestability still work | update public/service-facing documentation before scale; refresh any local notices or classroom/service instructions | substitute path must be named and live before broad release |
| `C4` | full re-approval as if the service were newly governed | re-test the approved use case, rights-sensitive edges, and rollback/withdrawal path; where relevant, repeat pilot or trial steps | re-publish service description, owner, oversight, and handling rules before use at scale | human or previously approved substitute path must carry the function until the new version is approved |

## Freeze windows the archive now treats as knowable in advance

The archive now makes five freeze expectations explicit.

### 1. Formal assessment windows

Do not release `C2-C4` changes into live assessment, proctoring, marking-support, or
cheating-monitoring workflows unless a named accountable owner has approved the exception and a safe
substitute path is already live.

### 2. Active pastoral or safeguarding intervention windows

Do not release `C2-C4` changes into school-managed minor-facing systems involved in welfare,
behaviour follow-up, attendance escalation, or safeguarding support without fresh local review.

### 3. Readiness-to-practice or placement-decision windows

Do not release `C2-C4` changes into professional-practice remediation, readiness, or
placement-adjacent systems without supervisor review and a human-only fallback.

### 4. Intake, enrolment, and public-route allocation windows

Do not release `C2-C4` changes into systems shaping route triage, funded-seat access, referral
order, or public-service learning coordination without a parallel human path and public handling
instructions.

### 5. Protected-support routing changes

Changes that alter how accessibility, accommodation, translation, or other protected-support routing
works should not be released as routine maintenance. They need fresh review even if the visible user
interface barely changed.

## What counts as a fresh governance review

A fresh governance review does not mean rewriting the whole archive. It means re-checking the
service against the smallest relevant set of canon surfaces:

- the deployment ladder;
- the relevant function-family default table;
- any applicable sector-and-age or sector-and-function profile layer;
- the observability and retention rule;
- the failure and fallback rule;
- and, where relevant, the proof-of-learning and accessibility / protected-support rules.

The archive's aim is not bureaucratic maximalism. It is to stop the common institutional pattern
where a system changed enough to require a new educational judgment, but only the technical release
process noticed.

## What institutions should publish

For every recurring educational-AI service, publish only seven change-governance fields:

1. the release owner;
2. the local change ladder (`C0-C4` or equivalent);
3. which classes require fresh governance review before scale;
4. which live windows carry freeze or exception rules;
5. whether `C3-C4` changes require shadowing, limited rollout, or parallel run;
6. who signs off on reopening or rollback if the release causes harm or confusion;
7. where users can find the currently approved purpose, cohort, and handling rule.

This is enough to block the most predictable failure: the institution that says it governs AI, but
has no public rule for deciding when an update stopped being maintenance.

## What counted as a real archive gain

The archive already knew that recurring educational-AI services need visible owners, visible brakes,
manual fallback, tighter rules in hotter sectors, and a separate memory / personalisation grammar
for deciding what kinds of persistence are acceptable at all. It still lacked a compact rule for
**what to do before failure** when a release changes the service itself.

This document adds that missing layer. It lets the archive say not only “publish a brake if the
service drifts,” but also “publish which kinds of changes are allowed to ship as maintenance, which
require shadowing or notice, and which count as a fresh governed deployment.”

## Current archive bet

The archive's current best guess is that a **generic change ladder plus the existing failure and
function tables** will outperform both extremes:

- treating all releases as one undifferentiated software-maintenance stream;
- and writing a bespoke release-governance manual for every single educational-AI service.

That claim is now canon, but still live. The next problem is narrower: which of the starter
sector-and-function change profiles are stable enough to harden, where they should branch further by
office, stakes, or modality, and when a seemingly bounded `C2-C3` change should instead be presumed
fresh deployment because the function already sits inside a hotter context. See
[`sector-and-function-profile-splits-for-change-defaults.md`](sector-and-function-profile-splits-for-change-defaults.md)
and `OQ-0011`.
