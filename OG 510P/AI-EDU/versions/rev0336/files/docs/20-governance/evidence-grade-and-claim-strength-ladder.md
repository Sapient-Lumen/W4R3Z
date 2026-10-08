# Evidence-grade and claim-strength ladder

The archive now has procurement intake, rollout gates, service-BOM fields, action authority,
cognitive-effort budgets, companion safeguards, and workflow security. It still needs one smaller
discipline:

> Do not let a claim travel farther than its evidence.

AI-in-education conversations often collapse very different claims into one confident sentence:
students liked it, teachers saved time, output quality improved, learning improved, retention held,
access improved, bias stayed bounded, security was tested, and legal duties were met. Those are not
the same claim. This surface gives the archive a portable evidence ladder so procurement, pilots,
scale decisions, assessment redesign, and public-route recognition do not launder weak evidence into
strong authority.


## Current overlay

Use [`claim-family-evidence-matrix.md`](claim-family-evidence-matrix.md) when applying this ladder to a real service. The ladder names evidence strength; the matrix names which claim family the evidence actually supports.

## Evidence ladder

| Code | Evidence posture | What it can support | What it cannot support |
|---|---|---|---|
| `EV0-ASSERTION` | plausible theory, vendor claim, expert belief, or local intuition | exploration, curriculum discussion, risk imagination | procurement approval, scale, high-stakes use, learner-record effects |
| `EV1-DEMO` | product demo, sandbox test, or staff tryout with no representative learners | usability screening, early service-BOM questions, red-team prompt collection | claims about learning, equity, accessibility, teacher workload, or safety in use |
| `EV2-LOCAL-PILOT` | bounded pilot with named cohort, baseline, human fallback, and exit rule | limited continuation, local design learning, clearer risk register | broad scale, cross-sector portability, official learning-gain claim |
| `EV3-COMPARATIVE-PILOT` | pilot with comparison condition, pre/post evidence, subgroup monitoring, and workload accounting | cautious local promotion, function-specific improvement claim | high-stakes automation, permanent adoption, claim that effects will travel unchanged |
| `EV4-EXTERNAL-STUDY` | credible external study in a similar function/age/stakes setting | stronger prior for adoption or replication | bypassing local context, accessibility, security, construct, and workload checks |
| `EV5-REPLICATED-OR-META` | multiple credible studies or syntheses showing durable benefit under relevant conditions | cross-site default, stronger procurement preference, curricular investment | unrestricted use across constructs, ages, languages, or protected routes |
| `EV6-STANDARD-OR-LAW` | statutory duty, official assessment rule, recognized standard, regulator guidance, or contractual control | mandatory floor, compliance gate, non-negotiable exclusion or minimum practice | evidence of learning benefit by itself |
| `EV7-OPERATIONAL-AUDIT` | live monitoring, incident review, appeals, security tests, accessibility checks, and workload data after launch | renewal, narrowing, rollback, or retirement decisions | original approval if the service never passed a prior evidence gate |

A claim may carry more than one code. For example, an accessibility routing tool may have `EV6` for
web-accessibility duties, `EV2` for local usability, and `EV1` for learning outcomes. That
combination is not weak; it is honest.

## Claim families

Every recurring AI service should separate at least these claims.

| Claim family | Question | Minimum evidence before scale |
|---|---|---|
| `learning_gain` | Did learners understand, retain, transfer, or self-regulate better? | `EV3` local or `EV4` external plus local replication plan |
| `performance_gain` | Did outputs or task completion improve? | `EV2`, but must not be described as learning without `learning_gain` evidence |
| `teacher_capacity` | Did the service reduce net workload without hidden review, correction, or escalation burden? | `EV2` with workload accounting; `EV3` before institution-wide labor claims |
| `access_equity` | Did the service improve access for learners who were previously blocked or underserved? | `EV2` with subgroup/accessibility review; `EV6` where a legal floor applies |
| `assessment_validity` | Does the proof still measure the intended construct under AI access? | construct map plus `EV3` or official assessment rule where stakes are high |
| `safety_wellbeing` | Did the system avoid emotional dependency, crisis substitution, or youth-safeguarding failures? | safeguarding review plus incident/appeal route; companion-like services need `EV7` renewal |
| `privacy_security` | Were data flow, retrieval, prompt injection, tool use, and record contamination risks tested? | service-BOM plus red-team evidence before recurring use; `EV7` after launch |
| `contestability` | Can affected people understand, challenge, correct, or route around the system? | tested appeal/correction path before any `AA3-AA5` authority |
| `compliance` | Does the service satisfy applicable law, policy, contract, or assessment rule? | `EV6`; never replace local legal/procurement review with archive language |

## Claim-strength rule

Do not promote a service, pattern, or rule by averaging across claim families. Strong usability
evidence does not repair weak learning evidence. A legal duty does not prove a product is
pedagogically effective. A learning study does not prove the deployment is secure. A successful
pilot for adults does not prove safety for minors.

Use the weakest relevant claim family as the gate when the weaker family is a blocker. For example:

- a tutoring tool with strong learning evidence but untested student data flows remains blocked for
  recurring deployment until privacy and security are reviewed;
- a marking-support tool with promising output-quality evidence remains capped at draft-for-review
  if assessment validity, bias, transparency, and human accountability are not proven;
- a companion-like study coach with high satisfaction remains hotter than ordinary tutoring until
  dependency, emotional disclosure, memory, and human handoff are tested;
- an administrative chatbot with good navigation accuracy remains capped below route-changing
  authority until contestability and human fallback are live.

## Evidence laundering patterns

The archive treats these as red flags.

| Pattern | Why it fails |
|---|---|
| `demo-to-scale` | a polished sandbox demo is treated as representative learner evidence |
| `task-performance-to-learning` | higher-quality AI-assisted output is treated as durable understanding |
| `teacher-time-to-learner-value` | apparent staff efficiency is counted as educational benefit without learning or access evidence |
| `pilot-winner-to-all-ages` | one cohort's success becomes a cross-age or cross-sector default |
| `satisfaction-to-safety` | positive user sentiment hides dependency, privacy, or safeguarding risk |
| `external-study-to-local-approval` | a study elsewhere bypasses local access, language, curriculum, and workflow review |
| `law-to-product` | a legal duty to provide access becomes approval for a specific vendor design |
| `security-checklist-to-security` | paperwork replaces red-team testing of actual prompts, retrieval, tools, and outputs |

## Minimum promotion gates

| Move | Evidence gate |
|---|---|
| sandbox to limited pilot | service-BOM, `AA` ceiling, `CE` posture where student-facing, initial `SEC` review, and `EV1` usability evidence |
| limited pilot to recurring local service | `EV2`, human fallback, stop rule, workload accounting, privacy/security review, and affected-user notice |
| local service to broad institutional scale | `EV3` for the claimed benefit, subgroup review, accessibility check, contestability test, and change/failure plan |
| broad scale to portable sector default | `EV4-EV5`, construct/stakes match, and explicit non-transfer boundaries |
| any `AA5` authority | `EV6` where required, plus human signoff, appeal, audit, and `EV7` renewal after launch |
| any companion-like minor-facing service above `CD1` | safeguarding review, memory limit, human route, incident handling, and renewal evidence before expansion |

## Review cadence

Every recurring service should publish a renewal posture:

| Cadence | Use |
|---|---|
| `R0-ONE-OFF` | no recurring service; no renewal beyond ordinary classroom/procurement record |
| `R1-TERM` | renew after a course term, grading window, or assessment cycle |
| `R2-QUARTERLY` | use for early pilots, student-facing services, or `AA3` workflows |
| `R3-ANNUAL` | use for stable low-risk services with no protected, high-stakes, or agentic authority |
| `R4-EVENT-TRIGGERED` | immediate review after incident, model/tool change, new data flow, complaint pattern, or material policy change |

The cadence does not replace event-triggered review. A stable annual service still reopens if the
model, retrieval corpus, prompt stack, tool authority, memory behavior, target population, or
legal/assessment context changes materially.

## Crosswalk to existing surfaces

- Use [`ai-service-bom-and-procurement-intake.md`](ai-service-bom-and-procurement-intake.md) to name
  the service and its claims.
- Use
  [`ai-action-authority-register-and-delegation-ceilings.md`](ai-action-authority-register-and-delegation-ceilings.md)
  to cap what the service may cause.
- Use
  [`cognitive-effort-budget-and-construct-preservation-defaults.md`](cognitive-effort-budget-and-construct-preservation-defaults.md)
  to avoid converting task help into learning loss.
- Use
  [`ai-service-security-red-team-and-agentic-tool-boundaries.md`](ai-service-security-red-team-and-agentic-tool-boundaries.md)
  before any workflow can retrieve, write, submit, message, label, or route.
- Use [`pilot-to-scale-evidence-and-rollout-gates.md`](pilot-to-scale-evidence-and-rollout-gates.md)
  for the existing rollout posture.
- Use
  [`docs/30-operations/ai-implementation-review-cycle-and-stop-rules.md`](../30-operations/ai-implementation-review-cycle-and-stop-rules.md)
  when the evidence ladder needs a practical review cycle.

See `B08`, `B11`, `B13`, `B17`, `B24`, `B26`, `B275`, `B276`, `B279`, `B280`, and `B281`.
