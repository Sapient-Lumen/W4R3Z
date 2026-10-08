# Standing-list publication profile and recency windows

This document closes the archive's next standing-recognition gap.

The archive already has a packet rail, sector defaults, and governance rules for standing equivalency. What it still needed was a **small publication profile**: a way for public systems to publish standing rules in a form that is easy for humans to read, easy for other systems to ingest, and honest about freshness.

The archive's answer is:

> **publish standing-equivalency entries twice: once as a short human-readable table, and once as a tiny machine-readable profile with unique IDs, dates, scope, and review windows tied to the family of learning being recognized.**

This move is grounded in a converging set of public signals. Credential Engine's 2025-2026 prior-learning-recognition work makes policies, accepted evidence, evaluation methods, and outcomes publishable data rather than invisible local discretion. CTIDs provide stable identifiers for credential-related resources. 1EdTech's Open Badges and CLR standards, together with W3C Verifiable Credentials, show that achievements can travel with structured metadata about issuer, criteria, evidence, and expiry. Europass's achievement template shows how public credentials can publish title, awarding body, linked learning outcomes, volume, learning setting, and qualification context. ACE and NCCRS keep the archive honest that standing recognition must remain versioned and dated: materially changed offerings and expired review windows are not the same thing as the older approved version. And the current AI-literacy guidance context matters too: California Community Colleges and DOL both now describe AI capability frameworks as evolving and requiring ongoing updates rather than one-time publication. See `B31`, `B35`, `B41`, `B42`, `B43`, `B48`, `B51`, `B52`, `B56`, `B57`, `B58`, `B59`.

## Core rule

Standing lists are **policy publications**, not learner records.

That means the machine-readable layer should describe:

- what outside learning or assessment is being recognized;
- by whom;
- under what scope;
- to what ceiling;
- with what dates;
- and with what fallback route when the standing rule does not fit.

It should **not** publish learner-specific evidence, protected support information, chat histories, or raw portfolio materials. Exception logic that affects only rare local cases should also stay out of the base entry and route to manual review instead.

## Publication shape

Each standing-list maintainer should publish two synchronized surfaces:

1. a short public table or catalogue that ordinary staff and learners can read;
2. a machine-readable feed (`CSV`, `JSON`, `JSON-LD`, or equivalent) using the same entry IDs and dates.

The archive's preference is **simple, boring publication** over bespoke wallet-only protocols. The rule should be legible even if a receiving node never builds a sophisticated exchange service.

## Minimal machine-readable profile

The archive's minimum profile is intentionally small.

### A. Publisher and list identity

Every published feed should include:

- `profile_version` — the schema/profile version used by the publisher;
- `publisher_id` — the maintaining authority;
- `list_id` — the identifier for the standing list itself;
- `published_at` — publication timestamp;
- `default_manual_review_route` — where edge cases go if no specific entry route is given.

### B. Entry identity

Every entry should include:

- `entry_id` — stable local identifier for the standing rule;
- `entry_status` — `provisional`, `active`, `expiring`, `expired`, or `retired`;
- `source_resource_id` — CTID, official URL, local registry ID, or other stable identifier for the outside learning or assessment;
- `source_title` — title of the course, badge, assessment, bridge completion, or credential;
- `source_version` — version label, review period, or dated edition;
- `issuer_id` — identifiable issuing body;
- `issuer_verification_basis` — how the publisher knows the issuer is real and in good standing.

### C. Learning and assurance description

Every entry should include:

- `family_code` — the learning family used for recency defaults;
- `admission_path` — the path by which it entered standing status (`P1`-`P4` from the governance doc);
- `claim_family` — portable claim strength (`A0`-`A3` or local equivalent);
- `assessment_basis` — e.g. supervised exam, evaluated course, bridge completion, portfolio-backed demonstration;
- `learning_outcomes_ref` — framework link, outcome list, or public learning-outcome summary;
- `evidence_basis` — ACE, NCCRS, public articulation, challenge exam, accredited issuer, or equivalent.

### D. Recognition action

Every entry should include:

- `receiving_scope` — receiving sector, programme family, or node to which the standing rule applies;
- `recognition_outcome` — default recognition result (`R1`-`R4` or local equivalent);
- `recognition_ceiling` — highest allowed outcome under this standing rule;
- `affected_requirement` — what duplicated-basic area, module, placement, waiver, or review trigger is affected;
- `construct_fit_note` — one short statement of why the match is narrow enough to stand;
- `manual_review_route` — entry-specific exception path when the rule only partly fits;
- `not_listed_rule` — explicit statement that omission triggers review rather than categorical denial.

### E. Freshness and succession

Every entry may also optionally point to a bounded exception profile when repeated public constraints, partial-equivalency logic, or manual-review triggers need to travel across systems. See [`standing-recognition-exception-profile-and-local-overrides.md`](standing-recognition-exception-profile-and-local-overrides.md).

Every entry should include:

- `effective_from` — when the rule became active;
- `review_by` — the next mandatory review date;
- `expires_on` — hard expiry if not reaffirmed;
- `supersedes` — prior entry ID(s) when the new rule replaces an older version;
- `change_trigger` — what kinds of changes force early review;
- `exception_profile_ref` — optional pointer to a bounded exception profile when repeated public constraints need to travel with the base standing rule.

## What should never be in the standing-list profile

The archive's standing publication profile must not carry:

- learner names or identifiers;
- raw artifact bundles;
- accessibility/accommodation records;
- detailed chat logs or telemetry traces;
- internal case notes;
- or full portfolio evidence.

Those belong in local support or review systems, not in the shared publication layer.

## Family-specific recency windows

The archive now rejects one universal expiry rule for all AI-learning recognitions. Different families age at different speeds.

The windows below are the archive's current default bias, not a metaphysical truth. They are justified by the combination of version-sensitive ACE/NCCRS review logic and the unusually rapid change rate of AI tools, risks, and literacy expectations.

| Family | Typical examples | Default `review_by` | Default `expires_on` | Archive rationale |
|---|---|---:|---:|---|
| `F1` Public foundational AI-literacy completion | public or public-partner module with named outcomes aligned to a framework | 12 months | 24 months | fundamentals may persist, but capabilities, risks, and governance expectations shift quickly enough that published basics should be refreshed at least annually |
| `F2` Standardized or supervised assessment | challenge exam, proctored assessment, supervised demonstration with published rubric | 12 months | 24 months | assessment constructs are more stable than tool tutorials, but AI-linked rubrics, security assumptions, and task design still drift |
| `F3` Externally evaluated offering | ACE-reviewed, NCCRS-reviewed, or similarly quality-reviewed course/exam | 12 months local check, plus external cycle | external end date or 36 months, whichever is sooner | strong outside review helps, but local standing should still inherit dates and close when the external review expires or the version changes |
| `F4` Articulated bridge completion | local public-stack bridge module, community-college/workforce/library bridge, system-specific onboarding route | each term or 12 months max | 18 months | these entries are tightly coupled to local curricula, funding rules, and pathway architecture, so they should age with programme change rather than sit indefinitely |
| `F5` Tool/model/vendor-specific workflow badge | prompt or workflow badge tied to a named platform, model family, or product surface | 6 months | 12 months | tool surfaces, capabilities, and safety expectations churn quickly; standing recognition should stay narrow, provisional, and short-lived |

## Form is not family

A useful clean-up follows from the profile work:

> **being a digital credential is not itself a standing-recognition family.**

A badge, CLR assertion, verifiable credential, or Europass-issued record can be an excellent **container** for a claim, but its shelf life and recognition ceiling should be determined by the underlying learning family, assurance path, and construct fit—not by the fact that it sits in a wallet or can be cryptographically checked.

This lets the archive keep authenticity and equivalency separate:

- issuer verification matters;
- machine readability matters;
- but neither one substitutes for curricular fit, freshness, or bounded publication of repeated exceptions.

## Default early-review triggers

Publishers should not wait for `review_by` when any of the following occurs:

- the issuing body materially changes the curriculum, assessment, or model/tool target;
- the underlying framework or public guidance is superseded;
- the receiving requirement changes enough to break construct fit;
- the external evaluation body issues a new date, end date, or changed recommendation;
- or a repeated pattern of appeals shows the published rule is too broad or too narrow.

## Publication posture by receiving node

The archive's preferred posture is asymmetric.

- libraries and civic first-contact points can publish very simple continuity / non-duplication feeds;
- workforce systems should publish routing and duplicated-basic waiver rules, not improvised academic-credit promises;
- bridge and noncredit public providers should publish the richest practical standing tables;
- credit-bearing programmes should publish narrower feeds tied to faculty-governed CPL, challenge, or articulation rules;
- universities should publish where review becomes available and where repeated basics may be waived, while remaining cautious about direct credit publication.

## Failure modes this document is trying to prevent

- **one-size-fits-all expiry** — slow and fast learning families get the same shelf life even though they drift differently;
- **human-readable only governance** — good rules exist, but cannot travel or be compared across systems;
- **wallet confusion** — cryptographic verifiability gets mistaken for curricular equivalency;
- **stale AI badge trust** — product-specific completions linger on standing lists long after the platform changed;
- **private-data spillover** — publication feeds start carrying learner traces, support records, or sensitive review materials.

## Current archive bet

The archive's current bet is that **a tiny machine-readable publication profile plus family-specific recency windows** will keep public AI-learning recognition both fresher and more interoperable than either giant learner-record systems or static human-readable PDFs alone.

That remains a bounded claim. The archive has since answered the structure question with a separate bounded exception profile, answered the maintenance question with a privacy-light appeal-feedback rule, and answered the disclosure question with a thin public history/profile for state, date, scope, reason family, and action hint. The next live question is narrower: which of those public maintenance signals partner systems should consume automatically, which should trigger local confirmation, and when prior uses should be grandfathered rather than reopened.
