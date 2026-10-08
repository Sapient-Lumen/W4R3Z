# Sector adapters for the service-record schema

The service-record schema should stay cross-sector. Sector differences should appear as **adapters**:
small overlays that say which fields, owners, public-summary profiles, evidence clocks, and stop
triggers become mandatory in a given setting.

Adapters do not replace local law, policy, collective agreements, accessibility duties, or academic
rules. They prevent the archive from pretending that a generic record means the same thing in a
middle-school classroom, credit-bearing university course, workforce-recognition office, and
protected accommodation route.

## Adapter principle

A valid adapter must answer five questions.

| Question | Why it matters |
|---|---|
| Who is the learner and who can speak for or with them? | Minors, adult learners, dependent students, and public-route users need different notice and support paths. |
| What consequence can the service affect? | Credit, eligibility, disability support, public benefit, discipline, and recognition require different ceilings. |
| Who owns the record? | Classroom, registrar, support office, workforce agency, and partner-recognition records cannot be casually merged. |
| Which public profile is safe? | The same summary can under-inform a partner and overexpose a learner. |
| What stops or shrinks the service? | Sector triggers need to include construct drift, access failures, cost burden, appeal failures, and protected-route leakage. |

## Shipped adapters

Example adapters live in `examples/sector-adapters/`.

| Adapter | Applies when | Hard default |
|---|---|---|
| `ADAPT-K12-MINORS` | K-12, secondary, primary, or minor-facing service | Family notice, teacher/safeguarding owner, no hidden memory, and tighter action ceilings. |
| `ADAPT-HIGHER-ED-CREDIT` | Higher-ed or credit-bearing course service | Syllabus/construct alignment, academic-integrity route, record owner, appeal, and accessible alternative. |
| `ADAPT-PUBLIC-WORKFORCE-RECOGNITION` | Public workforce, recognition, eligibility, or benefit-adjacent service | Cost/fee clarity, recognition limits, public appeal, partner portability, and no-charge fallback. |
| `ADAPT-ACCESSIBILITY-PROTECTED` | Accessibility, accommodation, language access, or protected support | Protected-route owner, public redaction, no-penalty fallback, non-misuse boundary, and separated records. |

A service can carry several adapters. A higher-ed advising service that touches credit and public aid
should normally carry both `ADAPT-HIGHER-ED-CREDIT` and `ADAPT-PUBLIC-WORKFORCE-RECOGNITION`. A
secondary accessibility service should carry both `ADAPT-K12-MINORS` and
`ADAPT-ACCESSIBILITY-PROTECTED`.

## Adapter trigger rules

| Trigger in service record | Required adapter |
|---|---|
| `age_bands` includes `primary`, `secondary`, `minor`, or `k12` | `ADAPT-K12-MINORS` |
| `sector` includes `higher_ed` or `highest_stakes_touched` includes `course_credit` | `ADAPT-HIGHER-ED-CREDIT` |
| `sector` includes `public_workforce` or stakes include `public_benefit`, `eligibility`, or `recognition` | `ADAPT-PUBLIC-WORKFORCE-RECOGNITION` |
| stakes include `accessibility`, memory is `M3`, or protected support owner is named as more than `none` | `ADAPT-ACCESSIBILITY-PROTECTED` |

These are minimum triggers. Local teams may apply stricter adapters.

## Adapter field contract

Each adapter JSON includes:

- `adapter_id` and `sector_family`;
- `trigger_terms` used by validators and local importers;
- `required_owner_fields` and any special owner notes;
- `minimum_action_ceiling` and `maximum_default_memory`;
- `required_public_redaction_profiles` and `default_redaction_profile`;
- `extra_public_notice_requirements`;
- `hard_stop_conditions`;
- `renewal_or_evidence_overrides`;
- `record_separation_rules`.

The adapter does not approve the service. It tells reviewers what cannot be missing.

## Sector defaults

| Sector | Default posture |
|---|---|
| K-12 / minors | Prefer `AA0-AA2`, `M0-M1`, teacher-owned classroom use, family notice where material, and no learner-risk file. |
| Higher-ed credit | Permit AI support only through construct-aware syllabus grammar, appeal routes, and record-owner review for credit effects. |
| Public workforce recognition | Treat navigation and recognition as entitlement-adjacent: cost, portability, appeal, and accessible alternatives must be visible. |
| Accessibility / accommodation | Keep support facts off public summaries; do not let proof, detection, or advising systems infer disability or accommodation status. |

## Validator hook

`tools/check_sector_adapters.py` verifies that adapter examples are complete and that service records
carry required adapters when trigger terms appear. `tools/check_service_records.py` checks that every
referenced adapter exists.

## Current archive bet

Adapters are safer than schema forks. They let one service-record format stay comparable while still
making sector-specific obligations visible at the point of review.

See
[`machine-readable-service-record-schema-and-validator.md`](machine-readable-service-record-schema-and-validator.md),
[`public-summary-redaction-profiles.md`](public-summary-redaction-profiles.md),
[`../20-governance/action-authority-ceiling-backfill-for-high-risk-functions.md`](../20-governance/action-authority-ceiling-backfill-for-high-risk-functions.md),
and `AS-0223`.
