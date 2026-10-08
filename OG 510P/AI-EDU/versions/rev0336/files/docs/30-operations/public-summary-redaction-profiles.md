# Public-summary redaction profiles

A service record has one canonical `public_summary`, but real communication has several audiences.
This surface prevents two opposite failures: a learner notice that exposes protected or security
facts, and a partner-facing summary that is too vague to support reliance, contestability, or
renewal.

The rule is simple: **the canonical public summary is never published raw.** It is rendered through a
redaction profile that names the audience, allowed fields, suppressed detail categories, mandatory
limit language, freshness requirements, and the human contact route.

## Publication bands

| Code | Meaning | Default action |
|---|---|---|
| `PUB0` | No public summary yet | Do not publish; internal record only. |
| `PUB1` | Learner / family notice | Publish only purpose, non-use, optionality, high-level data, fallback, limits, and contact route. |
| `PUB2` | Teacher / staff operating notice | Add workflow conditions, review burden, stop triggers, and support owner without protected facts. |
| `PUB3` | Partner / receiving-institution notice | Add authority ceiling, evidence freshness, recognition limits, and appeal route. |
| `PUB4` | Vendor / procurement review extract | Add security posture and data-flow questions without exploit details or learner traces. |
| `PUBX` | Suppress or pause | Public summary is withheld because protected, security, or misleading-claim risk is active. |

`PUB3` and `PUB4` are not more public than `PUB1`. They are narrower professional extracts for
people who need more operating detail and have a defined role.

## Required redaction profiles

The archive ships example profiles in `examples/redaction-profiles/`.

| Profile | Audience | Publication band | Primary use |
|---|---|---|---|
| `RDP-LEARNER` | learner | `PUB1` | Short notice for students, adult learners, and public-route users. |
| `RDP-FAMILY` | family / guardian | `PUB1` | Family-facing notice for minors or dependent learners. |
| `RDP-TEACHER` | teacher / staff | `PUB2` | Operating summary for human coverage, review, and fallback. |
| `RDP-PARTNER` | partner institution / recognizer | `PUB3` | Reliance, transfer, or recognition review. |
| `RDP-VENDOR` | vendor / procurement | `PUB4` | Procurement or security-facing extract. |
| `RDP-PUBLIC-ROUTE` | public learner / workforce route user | `PUB1` | Low-barrier public-service notice with cost and appeal emphasis. |

Profiles may be copied locally, but they should keep stable IDs or map back to the closest archive
profile so service-record tests remain comparable.

## Never publish raw details

A redacted summary must not expose:

- diagnosis, disability, accommodation, language-access, immigration, discipline, or hardship facts;
- raw prompts, learner traces, private logs, small subgroup results, or hidden-risk flags;
- prompt-injection strings, retrieval-poisoning examples, exploit paths, API keys, or tool-call
  payloads;
- vendor-confidential details that are not needed for public contestability;
- evidence claims whose expiry clock is `STALE` or `EXPIRED` unless the claim is explicitly removed
  or rephrased as a limit.

Protected facts can still be handled. They route to the protected-route owner named in the service
record, not into public notice text.

## Rendering algorithm

1. Start from the validated service record, not marketing copy.
2. Select the audience profile named in `publication_and_adapters.default_public_summary_redaction_profile`
   or a stricter local profile.
3. Keep only `allowed_public_summary_fields` from the profile.
4. Add every `mandatory_message` that is not already clear in the summary.
5. Remove or narrow any public phrase named in `public_claim_to_remove_if_weak` when its evidence is
   weak, stale, expired, or out of population.
6. Replace protected detail with the profile's protected-route phrase, such as “contact the named
   support office for private support options.”
7. Replace security detail with the profile's security phrase, such as “security testing is reviewed
   through the service owner and is not published as exploit detail.”
8. Publish the review date and human contact route.

## Decision table

| Situation | Default profile | Public posture |
|---|---|---|
| Optional low-stakes tutor | `RDP-LEARNER` | Allow `PUB1`; emphasize limits and independent work. |
| K-12 tool touching minors | `RDP-FAMILY` plus `RDP-LEARNER` | Family notice required; no hidden memory or raw trace. |
| Teacher-facing planning assistant | `RDP-TEACHER` | Add review burden and human sign-off; no learner-risk flags. |
| Higher-ed credit-bearing feedback | `RDP-LEARNER` plus `RDP-TEACHER` | Include syllabus/construct limits and appeal route. |
| Public workforce recognition | `RDP-PUBLIC-ROUTE` plus `RDP-PARTNER` | Include cost, optionality, recognition limits, and appeal. |
| Accessibility or accommodation support | `RDP-LEARNER` or `RDP-FAMILY` with protected-route owner | Do not reveal the protected support fact in public summary. |
| Agentic workflow | `RDP-TEACHER` and, if learner-facing, `RDP-LEARNER` | Name queue/write ceiling and rollback in plain language. |
| Active security incident | `PUBX` | Suppress or replace public summary until safe notice is approved. |

## Validator hook

`tools/check_redaction_profiles.py` verifies that shipped redaction profiles are complete and that
service records reference existing profiles. `tools/check_public_summary_renders.py` then smoke-tests
each candidate render for allowed fields, mandatory messages, forbidden phrases, visible human-contact
routes, and weak/stale claim removal. `tools/check_service_records.py` also fails public service
records that enable publication without at least one redaction profile.

## Current archive bet

Transparency is not a dump of everything the institution knows. It is role-appropriate truth: enough
to understand purpose, limits, record effects, appeal/fallback, and evidence freshness, without
turning protected support, security detail, or learner traces into public metadata.

See
[`machine-readable-service-record-schema-and-validator.md`](machine-readable-service-record-schema-and-validator.md),
[`public-pilot-summary-examples.md`](public-pilot-summary-examples.md),
[`public-summary-render-smoke-tests.md`](public-summary-render-smoke-tests.md),
[`../20-governance/evidence-expiry-and-renewal-clocks.md`](../20-governance/evidence-expiry-and-renewal-clocks.md),
and `AS-0222`.
