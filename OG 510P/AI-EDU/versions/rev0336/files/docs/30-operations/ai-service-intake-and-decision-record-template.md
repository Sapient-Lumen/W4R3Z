# AI service intake and decision-record template

## Current overlay

For new decisions, add two fields to the template before signoff: `claim_family` and
`evidence_grade`. Use
[`../20-governance/evidence-grade-and-claim-strength-ladder.md`](../20-governance/evidence-grade-and-claim-strength-ladder.md)
for `EV0-EV7`, and use
[`ai-implementation-review-cycle-and-stop-rules.md`](ai-implementation-review-cycle-and-stop-rules.md)
for stage, stop rule, and renewal cadence.

Use this template when a team proposes a recurring AI service, integration, pilot, procurement,
renewal, or scale decision. Keep the record short enough to update. Attach long evidence, contracts,
or security reports elsewhere.

This is a working record, not a public marketing page. A public summary can be generated from it
only after protected support evidence, security details, and learner-level traces are removed.

## 1. Service identity

| Field | Entry |
|---|---|
| Service name |  |
| Vendor / provider |  |
| Institutional owner |  |
| Educational owner |  |
| Technical owner |  |
| Support / escalation owner |  |
| Contract / renewal date |  |
| Current intake status (`BOM0-BOMX`) |  |
| Current rollout gate (`RG0-RG4`) |  |
| Review date |  |

## 2. Use case and non-use case

| Field | Entry |
|---|---|
| Learner / teacher / institution problem |  |
| Intended users and age bands |  |
| Sector / route |  |
| Intended tasks |  |
| Explicit non-use cases |  |
| Highest stakes touched |  |
| Required human owner |  |

## 3. Model, system, and data map

| Field | Entry |
|---|---|
| Model / service family where known |  |
| Wrapper, extension, LMS/SIS integration, or agent tools |  |
| RAG / retrieval corpus |  |
| Input data |  |
| Generated outputs |  |
| Logs / telemetry |  |
| Subprocessors / storage region |  |
| Retention / deletion route |  |
| Data export / continuity route |  |

## 4. Authority and memory

| Field | Entry |
|---|---|
| Highest action authority (`AA0-AA6`) |  |
| Direct write permissions |  |
| Indirect queue / flag / notification effects |  |
| Record-bearing effects |  |
| Memory class (`M0-M3`) |  |
| Learner inspection / correction route |  |
| Protected local record route |  |
| Cross-function reuse prohibited? |  |

## 5. Construct, effort, and proof

| Field | Entry |
|---|---|
| Educational construct or support duty |  |
| AI-compatible task modes |  |
| Required unaided segment |  |
| Cognitive-effort budget (`CE0-CE5`) |  |
| Disclosure rule |  |
| Proof-of-learning bundle |  |
| Authentication / checkpoint route |  |
| Contest or reconsideration route |  |

## 6. Accessibility, equity, and protected support

| Field | Entry |
|---|---|
| Accessibility features verified |  |
| Disability / language / device / connectivity risks |  |
| Protected support route |  |
| No-penalty fallback |  |
| Bias / subgroup analysis |  |
| Learner notice and opt-out / alternative |  |

## 7. Security and adversarial-use review

| Field | Entry |
|---|---|
| Prompt-injection exposure |  |
| Retrieved / uploaded content risk |  |
| Tool or action misuse risk |  |
| Insecure output-handling risk |  |
| Data-exfiltration path checked |  |
| Red-team / abuse test date |  |
| Incident reconstruction without surveillance |  |
| Safe degradation and manual fallback |  |

## 8. Evidence and workload

| Field | Entry |
|---|---|
| Evidence source |  |
| Outcome measured |  |
| Comparison condition |  |
| Duration and population |  |
| Retention / transfer evidence |  |
| Teacher review burden |  |
| Support-staff burden |  |
| Known failure modes |  |

## 9. Decision

| Field | Entry |
|---|---|
| Decision | pilot / scale / narrow / pause / retreat / retire |
| Conditions |  |
| Maximum allowed authority |  |
| Maximum allowed memory |  |
| Required human coverage |  |
| Required proof or audit |  |
| Stop / pause triggers |  |
| Learner-safe continuity plan |  |
| Next review date |  |

## 10. Public summary fields

Publish only the fields needed for affected learners, teachers, families, public-route users, or
partner institutions to understand the service without exposing sensitive records.

| Public field | Entry |
|---|---|
| What the service does |  |
| What it does not do |  |
| Whether use is required or optional |  |
| What data is used at a high level |  |
| Whether AI output affects records or decisions |  |
| Human contact / appeal route |  |
| Accessibility and alternative path |  |
| Last reviewed |  |

## Completion rule

The record is incomplete if any of these are blank: owner, use case, non-use case, data map, memory
class, action authority, construct / effort budget, accessibility route, security review, human
fallback, evidence claim, and stop rule.

If the service touches official records, protected supports, high-stakes assessment, discipline,
eligibility, or child-facing companion-like interaction, the record must also include a named human
reviewer and a no-penalty manual alternative before launch.

## Rev0214 schema-backed record overlay

The Markdown template remains the human-friendly intake surface. For recurring pilots, renewals,
agentic workflows, protected-route services, or public-facing pilots, also keep a compact JSON
record that validates against
[`machine-readable-service-record-schema-and-validator.md`](machine-readable-service-record-schema-and-validator.md).

Add these fields to the working packet when the service is more than a one-off staff exploration.

| Field | Why it is now explicit |
|---|---|
| `schema_record_id` | lets a service record be checked, renewed, and summarized without copying the whole packet |
| `evidence_expiry_date` | prevents old evidence from carrying fresh public claims |
| `early_expiry_triggers` | catches model, prompt, workflow, owner, population, and policy drift |
| `public_claim_to_remove_if_weak` | makes renewal shrink overclaims, not only continue or stop tools |
| `maximum_allowed_authority` | keeps the decision ceiling aligned with the action-authority map |
| `red_team_or_abuse_test_date` | ties agentic and retrieval workflows to a dated security posture |
| `public_summary_allowed` | separates internal review records from public notices |

The JSON record is incomplete if it passes schema shape but fails local owner review. The schema is a
floor, not approval.
## Rev0215 publication and adapter addendum

Every recurring service record should now include a `publication_and_adapters` block before public
notice or renewal. The block names source status, source confidence, sector adapters, public-summary
redaction profiles, the default public profile, normalization notes, and real-record import status.

Do not publish `public_summary` raw. Render it through the audience profile, then remove weak,
stale, expired, protected, or security-sensitive claims before release.
