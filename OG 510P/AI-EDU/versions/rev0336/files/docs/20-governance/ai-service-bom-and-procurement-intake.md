# AI service bill of materials and procurement intake

## Current overlay

The service-BOM now has to name claim strength, not only service shape. Use
[`evidence-grade-and-claim-strength-ladder.md`](evidence-grade-and-claim-strength-ladder.md) to
record which claims are `EV0-EV7`, and use
[`../30-operations/ai-implementation-review-cycle-and-stop-rules.md`](../30-operations/ai-implementation-review-cycle-and-stop-rules.md)
to decide whether the service is still at intake, sandbox, pilot, local recurring use, scale, or
renewal.

The archive has enough policy language. It now needs a small object that an institution can actually
fill out before an AI service moves from idea to pilot, pilot to scale, or scale to default
infrastructure.

This surface resolves `FT-0164` by adding an **AI service bill of materials** plus a **minimum
intake decision record**. It is deliberately not a vendor questionnaire alone. A vendor can answer
some fields, but the institution must own the educational construct, action authority, proof burden,
memory posture, human coverage, and stop rule.

The default rule is simple:

> No recurring AI service should be piloted, scaled, integrated, or renewed unless a named owner can
produce a current intake record that identifies the service's model, data flow, memory, action
authority, security boundary, accessibility route, evidence claim, human fallback, and retirement
trigger.

## Intake status ladder

| Code | Name | Meaning | Allowed posture |
|---|---|---|---|
| `BOM0` | Not an institutional service | Ad hoc individual use with no institutional data, account integration, record effect, or official recommendation | May be covered by course grammar or acceptable-use guidance, but not procured or promoted |
| `BOM1` | Exploration record | A team is comparing services, drafting use cases, or sandboxing with synthetic / non-sensitive data | No learner records, no production integration, no official learner-facing promise |
| `BOM2` | Pilot-ready record | The service has a named owner, narrow use case, data map, construct map, authority ceiling, risk controls, and fallback | Time-bounded pilot only; no default deployment |
| `BOM3` | Scale-review record | Pilot evidence, accessibility evidence, security review, workload review, and failure logs are available | Expansion may be proposed, but only with updated risk and stop rules |
| `BOM4` | Default-service record | The service is part of ordinary institutional operations | Requires live owner, review cycle, change gates, incident path, and retirement path |
| `BOMX` | Blocked / withdrawn | The service lacks a required field, exceeds authority, fails construct fit, or cannot provide safe fallback | Do not deploy; preserve transition support if already in use |

A service may not jump from `BOM1` to `BOM4`. If the proposed use is record-bearing, child-facing,
assessment-adjacent, protected-support-related, or action-taking, the default ceiling is `BOM2`
until the missing higher-stakes evidence exists.

## Minimum AI service bill of materials

Every recurring service record should include the following fields.

| Field family | Minimum fields | Why the archive needs it |
|---|---|---|
| Service identity | service name, vendor / provider, version or release channel, contract owner, institutional owner, renewal date | prevents invisible drift and orphaned services |
| Educational purpose | learner problem, teacher problem, institutional problem, affected course / route, intended non-use cases | keeps procurement from becoming feature shopping |
| Model and system components | model family where known, hosted service, local wrapper, RAG corpus, plugins/tools, browser extension, LMS/SIS integration, analytics layer | exposes where the service can see, write, retrieve, or act |
| Data flow | input data, learner records, staff records, generated outputs, logs, telemetry, subprocessors, storage region, retention period, deletion path | separates privacy claims from actual routes |
| Memory posture | `M0-M3` memory class, learner-controlled preferences, course memory, protected records, predictive profile, cross-function reuse | prevents personalization from becoming hidden learner modeling |
| Action authority | `AA0-AA6` level, write permissions, queue effects, notification effects, grading effects, eligibility effects, reversible / irreversible actions | names what the AI or workflow can actually cause |
| Construct and effort | assessed construct, allowed `CE0-CE5` help, required disclosure, proof shift, unaided segment, oral / live transfer trigger | keeps AI help from replacing the thing being learned |
| Human coverage | named human owner, fallback path, response window, escalation path, no-orphan handoff rule, after-hours truth claim | prevents fake oversight and unsupported learners |
| Accessibility and protected support | assistive-use path, disability / language / access support route, protected evidence handling, override triggers | prevents access supports from being treated as misconduct signals |
| Security and misuse | prompt-injection exposure, RAG corpus control, tool permission boundary, output handling, data exfiltration risk, abuse reporting, red-team log | makes adversarial behavior a design input, not a surprise |
| Evidence claim | evidence type, comparison condition, measured outcome, equity analysis, teacher workload effect, known failure modes, recheck date | distinguishes learning evidence from adoption enthusiasm |
| Change gate | model update channel, prompt/tool/corpus change process, material-change definition, freeze/rollback owner | blocks silent product drift from changing educational treatment |
| Exit and continuity | stop rule, teach-out path, data export / deletion, substitute service, fee / cost absorption, learner notice | makes withdrawal survivable |

## Non-negotiable decision fields

A procurement or pilot record is incomplete unless it answers these twelve questions in ordinary
language.

1. What educational construct or support duty is this service meant to protect?
2. What learner, teacher, or public-route problem would remain if the AI service were unavailable?
3. What data does the service receive that it would not receive in ordinary classroom practice?
4. What does the service remember, and who can inspect, correct, minimize, or delete that memory?
5. What can the service cause directly or indirectly under the `AA0-AA6` authority ladder?
6. Which `CE0-CE5` effort budget applies to each learner-facing use?
7. What proof of learning, support delivery, or decision quality is owed if the service is used?
8. What human owner is reachable when the service fails, overreaches, or produces a contested
   output?
9. What security and adversarial-use testing has been done against the actual integrated workflow?
10. What accessibility and protected-support route exists that does not expose sensitive support
    evidence as ordinary authorship metadata?
11. What evidence would make the service scale, stay narrow, pause, retreat, or retire?
12. What happens to learners, staff workload, records, and money if the service is withdrawn
    midstream?

If any answer is “the vendor handles that” without a named institutional owner, the service cannot
move beyond `BOM1`.

## Procurement gates by authority and memory

| Highest authority / memory in the service | Minimum gate before pilot | Minimum gate before ordinary default |
|---|---|---|
| `AA1` read-only advice, `M0-M1` memory | `BOM2` with construct and data map | `BOM3` with evidence and fallback |
| `AA2` draft-for-review, `M1-M2` memory | `BOM2` with human signoff and output-handling rule | `BOM3` with workload, equity, and change evidence |
| `AA3` queue / flag / recommendation, any protected support path | `BOM2` plus contestability and no-penalty fallback | `BOM4` only after audit evidence and owner capacity are proven |
| `AA4` reversible low-stakes action | `BOM2` plus rollback test and learner notice | `BOM4` only with monitoring, audit, and manual alternative |
| `AA5` record-bearing or consequence-bearing action | exceptional `BOM2`, human-owned decision, and legal / policy review | ordinary default normally prohibited; keep human-owned route |
| `AA6` prohibited or human-only | no pilot | no default |
| `M3` human-owned record rail or predictive profile | `BOM2` plus inspection / correction / minimization route | `BOM4` only with role-specific owner, audit, and function lock |

The archive should treat `AA3+M2`, `AA3+protected support`, `AA4`, `AA5`, `M3`, and child-facing
companion-like use as **hot combinations**. Hot combinations require narrower pilots, earlier human
ownership, stronger stop rules, and clearer public-facing explanation than ordinary advice or draft
support.

## Security and adversarial-use intake

The security section must cover the integrated educational workflow, not just the base model.

Minimum questions:

- Can an external prompt, uploaded file, webpage, email, LMS page, or retrieved document override
  system instructions?
- Can the service read or write records, send messages, create assignments, alter grades, move
  learners in queues, or trigger support paths?
- What happens if the service receives malicious instructions embedded in student work, teacher
  resources, web pages, PDFs, images, code, or feedback comments?
- Are generated outputs treated as executable instructions by downstream systems?
- Are RAG sources curated, permissioned, versioned, and auditable?
- Are logs sufficient for incident reconstruction without becoming permanent learner surveillance?
- Has the system been tested against prompt injection, data exfiltration, insecure output handling,
  tool misuse, hallucinated policy, and denial-of-service or cost-amplification scenarios?
- Does the service degrade safely when a tool, model, network route, or vendor system is
  unavailable?

Security failure is not just a technical risk in education. It can become a grading error,
support-route exposure, disciplinary false positive, disability disclosure, public-route exclusion,
or official-record fault.

## Evidence intake

Evidence should be attached to the claim being made.

| Claim | Minimum evidence shape |
|---|---|
| “Students learn more” | learning outcome, comparison condition, duration, population, construct, and retention / transfer check where possible |
| “Teachers save time” | measured staff time, review burden, error correction, after-hours spillover, and workload distribution |
| “Feedback improves” | quality rubric, teacher validation, student uptake, learning effect, and bias / language analysis |
| “Assessment remains valid” | construct map, unaided segment, proof bundle, authentication route, and contested-case handling |
| “Support is more accessible” | disability / language / device / connectivity analysis, protected support route, and no-penalty fallback |
| “The service is safe” | security test, incident path, model/tool-change gate, privacy review, and failure drill |

A vendor study can support a vendor claim. It cannot by itself prove local learning gain, equity,
workload, or construct validity.

## Stop, pause, and rollback triggers

A service should pause or retreat when any of these occur:

- the actual authority exceeds the recorded `AA` level;
- the service begins retaining or reusing data beyond the recorded memory posture;
- a model, prompt, tool, RAG corpus, or workflow change alters learner treatment;
- staff review burden exceeds the claimed savings;
- protected support evidence appears in ordinary disclosure, analytics, or misconduct channels;
- false positives, hallucinated policy, or biased routing cause contested educational consequences;
- the vendor cannot explain, export, delete, or minimize records required for continuity or
  withdrawal;
- the human fallback is unreachable in the published service window;
- security testing finds a path from user content to record change, data exposure, or hidden
  downstream action.

Rollback must include learner-safe continuity. The archive should not punish learners for
institutional overdeployment.

## Relation to existing surfaces

This surface sits between procurement principle and implementation record:

- use [`evidence-and-procurement.md`](evidence-and-procurement.md) for evidence posture and
  procurement ethics;
- use
  [`ai-action-authority-register-and-delegation-ceilings.md`](ai-action-authority-register-and-delegation-ceilings.md)
  to name what the service can cause;
- use
  [`cognitive-effort-budget-and-construct-preservation-defaults.md`](cognitive-effort-budget-and-construct-preservation-defaults.md)
  to protect the learning construct;
- use
  [`persistent-memory-personalization-and-learner-model-boundaries.md`](persistent-memory-personalization-and-learner-model-boundaries.md)
  to classify memory;
- use
  [`model-and-workflow-change-classification-and-fresh-review-triggers.md`](model-and-workflow-change-classification-and-fresh-review-triggers.md)
  to decide when updates require fresh review;
- use
  [`human-coverage-bands-and-no-orphan-handoffs.md`](../30-operations/human-coverage-bands-and-no-orphan-handoffs.md)
  to prevent fake oversight;
- use
  [`ai-service-intake-and-decision-record-template.md`](../30-operations/ai-service-intake-and-decision-record-template.md)
  to produce the working record.

See `B275`, `B276`, `B280`, and `B281`.
