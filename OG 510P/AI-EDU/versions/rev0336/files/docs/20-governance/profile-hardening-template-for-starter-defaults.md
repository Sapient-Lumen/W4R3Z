# Profile hardening template for starter defaults

The live queue still contains several starter-profile questions with the same
shape: proof, student-facing, teacher-facing, institution-facing, observability,
failure, change, and coverage defaults all ask when a starter row should harden,
split, cool, retreat, or stay local.

This surface gives one reusable decision grammar so those questions do not each
become a long narrative shell.

## Starter-profile decision states

| Code | State | Meaning |
|---|---|---|
| `PH0-STARTER` | starter only | useful inherited default, but not decision-grade beyond its named context |
| `PH1-HARDEN` | harden | enough evidence and operational stability to treat the row as a stronger local or portable default |
| `PH2-SPLIT` | split | row hides material variation by age, stakes, office, modality, construct, authority, memory, or proof |
| `PH3-COOL` | cool | row remains usable, but only at lower stakes, narrower authority, weaker claim, or lighter proof burden |
| `PH4-RETREAT` | retreat | row should move to human-only, protected-owner-only, local-only, or no-default status |
| `PH5-QUARANTINE` | quarantine | row is unsafe to reuse until incident, evidence, legal, security, or validity issue is resolved |
| `PH6-RETIRE` | retire | row should leave active starter grammar because it misleads more than it helps |

## Minimum evidence before hardening

A profile should not move to `PH1-HARDEN` unless it has answers to all nine
claim-family checks.

| Check | Minimum question |
|---|---|
| learning / educational value | what construct, access, support, or service quality improved? |
| task performance | what immediate task got easier, faster, or more accurate? |
| workload | whose total labor changed, including review, correction, IT, security, and appeals? |
| access | which subgroup or protected route benefited, was chilled, or was excluded? |
| validity | did the row preserve the construct or service truth it claims to support? |
| safety | what dependency, bias, wellbeing, discipline, or record harm appeared? |
| security | what prompt, retrieval, tool, output-handling, or data path was tested? |
| contestability | can affected people inspect, correct, appeal, or reach a human owner? |
| compliance | what law, assessment rule, contract, or local policy floor applies? |

If a claim family is irrelevant, say why. Do not leave it blank.

## Split triggers

A starter row should usually move to `PH2-SPLIT` when any of these differences
change the decision:

- minors versus adult learners;
- ordinary practice versus credit, gateway, discipline, eligibility, or public-benefit stakes;
- human advice versus queue, record, message, score, route, or write authority;
- session support versus persistent memory, protected records, or predictive profile;
- ordinary classroom proof versus official assessment or certification proof;
- teacher-owned use versus office-owned use;
- optional use versus required use;
- general-purpose tool versus purpose-built or route-native tool;
- online-only proof versus live, supervised, oral, or protected proof;
- after-hours delayed fallback versus same-cycle consequence-bearing coverage;
- read-only workflow versus agentic tool use;
- local language / accessibility / device conditions that change access burden.

## Cooling and retreat triggers

A row should move to `PH3-COOL`, `PH4-RETREAT`, or `PH5-QUARANTINE` when:

- performance improves but independent learning, transfer, or construct proof does not;
- teacher convenience creates hidden review, correction, or appeal labor;
- protected support facts leak into ordinary learner metadata;
- a general-purpose product cannot satisfy the service-BOM, security, or fallback record;
- the row depends on AI-only detection, scoring, ranking, or risk labeling;
- action authority expands without owner signoff;
- model, prompt, retrieval, tool, policy, or assessment context changes materially;
- the row repeatedly needs local exceptions to stay safe;
- affected learners cannot understand or challenge the consequence;
- external law or assessment-body policy conflicts with the row.

## Decision row template

Use this row when a future surface wants to harden or split a starter profile.

```text
Starter row:
Profile family:
Current state: PH0 / PH1 / PH2 / PH3 / PH4 / PH5 / PH6
Actor / age / sector:
Stakes:
Function:
Authority ceiling:
Memory ceiling:
Construct / CE posture:
Proof or service-truth surface:
Claim-family evidence:
Security posture:
Accessibility / protected route:
Human fallback:
Contestability route:
Decision:
Why this decision is not broader:
Renewal / reopen trigger:
```

The line **Why this decision is not broader** is mandatory. It is the profile
version of the evidence-laundering brake.

## Family-specific starter questions

| Profile family | First hardening question | Common split trigger | Common retreat trigger |
|---|---|---|---|
| proof-intensity | does the proof preserve the construct without excessive burden? | subject family, age, gateway stakes, protected route | proof becomes surveillance or detector-led suspicion |
| student-facing | does support improve learning/access without dependence or hidden consequence? | minors, required use, memory, companion-like framing | answer engine, wellbeing adjacency, no human route |
| teacher-facing | does AI assist preparation without delegating official judgment? | grading, parent communication, discipline, accommodation, workload | review burden or hidden official action |
| institution-facing | does navigation/support improve service without record or eligibility opacity? | office role, public benefit, cross-agency dependency | route-changing advice without appeal owner |
| observability | does capture support safety/proof without becoming ambient surveillance? | modality, office, protected records, incident reconstruction | full trace collection as routine default |
| failure | does fallback preserve learner standing and service truth? | timing window, consequence window, owner scarcity | learner fault or orphaned queue after system failure |
| change | does update remain bounded or become fresh deployment? | model, prompt, RAG corpus, tool, authority, legal context | “minor” update changes educational or record effect |
| coverage | does service window match consequence timing? | after-hours posture, cohort peak, scarce office route | always-on promise without owner capacity |

## Consolidation rule

When several queued starter-profile questions share this template, prefer one
profile-hardening table over many prose surfaces. Write a new prose surface only
when the profile family has a genuinely new actor, stakes, authority, proof,
memory, owner, jurisdictional, or implementation-evidence pattern.

The first applied table now lives in
[`profile-hardening-application-rows.md`](profile-hardening-application-rows.md).
Those rows close the initial proof, student-facing, teacher-facing,
institution-facing, observability, failure, change, coverage, and applied
profile-hardening followthrough items without creating eight more branch shells.

## Current archive bet

The profile queues were real, but the first closeout now uses applied rows
rather than copied branch prose. Future rows should stay short unless actual
implementation evidence exposes a new actor, owner, proof, memory, authority, or
legal pattern.

See
[`profile-hardening-application-rows.md`](profile-hardening-application-rows.md),
[`claim-family-evidence-matrix.md`](claim-family-evidence-matrix.md),
[`ai-action-authority-register-and-delegation-ceilings.md`](ai-action-authority-register-and-delegation-ceilings.md),
[`cognitive-effort-budget-and-construct-preservation-defaults.md`](cognitive-effort-budget-and-construct-preservation-defaults.md),
[`minimum-observability-and-retention-without-surveillance.md`](minimum-observability-and-retention-without-surveillance.md),
[`failure-escalation-safe-degradation-and-manual-fallback.md`](failure-escalation-safe-degradation-and-manual-fallback.md),
[`model-and-workflow-change-classification-and-fresh-review-triggers.md`](model-and-workflow-change-classification-and-fresh-review-triggers.md),
[`sector-and-function-profile-splits-for-coverage-defaults.md`](sector-and-function-profile-splits-for-coverage-defaults.md),
and `FT-0022`, `FT-0025`, `FT-0026`, `FT-0027`, `FT-0029`, `FT-0030`, `FT-0032`, `FT-0058`.
