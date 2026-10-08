# Public maintenance history and trust-signal profile

This document closes the disclosure gap left open by the archive's standing-recognition maintenance work.

The archive already has:

- a typed public handoff packet;
- sector defaults for what outside AI-learning should mean;
- governance rules for standing-equivalency lists;
- a tiny publication profile with family-specific recency windows;
- a bounded exception grammar for partial equivalencies and local overrides;
- and a privacy-light maintenance rule for learning from appeals, disagreement, and false matches.

What it still lacked was a compact answer to a narrow operational question:

> **what maintenance history should public systems publish so partner systems and learners can trust standing entries without exposing raw counts, trigger thresholds, or learner-level cases?**

The archive's answer is:

> **publish state, date, scope, reason family, and impact hint. Do not publish raw counts, small-cell operational metrics, or case traces.**

This move is grounded in a converging set of public signals. Credential Engine's approval-list and prior-learning-recognition work supports publishing lifecycle status, membership periods, jurisdictional scope, policies, evidence, and outcomes as interoperable data rather than as hidden local practice. W3C's VC ecosystem treats credential status as a publishable, privacy-sensitive layer and explicitly uses grouped status lists to preserve privacy rather than exposing fine-grained histories. Europass verification surfaces public checks like validity, revocation, and accreditation status instead of operational case logs. 1EdTech's current credential requirements make revocation, expiration, evidence, and versioning ordinary metadata concerns. ALA's privacy guidance and vendor guidance require minimization, retention review, restricted disclosure, and user-facing clarity. FERPA keeps correction/amendment and disclosure-control rights live once educational records and public-facing status systems start to interact. See `B41`, `B43`, `B57`, `B61`, `B64`, `B65`, `B66`, `B67`, `B68`, and `B69`.

## Core rule

The archive now distinguishes three layers:

- **public maintenance history** — what any learner or partner system can see;
- **partner-consumable status/profile fields** — structured fields that software can ingest;
- **local maintenance evidence** — counts, thresholds, sampled cases, and case files that remain local.

The archive rejects two bad extremes:

- **opaque standing recognition**, where partner systems cannot tell whether an entry is still trustworthy or why it changed;
- **overexposed maintenance telemetry**, where public trust is pursued by publishing raw counts, thresholds, node-by-node disagreement statistics, or learner-adjacent dispute traces.

The archive's bias is: **publish effects, not numerators; rule history, not learner history.**

## What the public layer is for

The public layer should answer only the questions a learner, advisor, or partner system actually needs to know:

- Is the entry active, expiring, narrowed, suspended, superseded, expired, or retired?
- Since when?
- Why, at a short category level?
- What scope does the change affect?
- What should a receiving node do next?
- Where does a learner go if they think the standing entry was applied wrongly?

If a field does not help answer one of those questions, it usually belongs in the local maintenance layer instead.

## Minimum public history card

Every standing entry should publish a short human-readable history card.

### Identity fields

- `entry_id`
- `entry_version`
- `publisher_list_id`
- `publisher_authority`
- `published_on`
- `last_updated`

### Standing state fields

- `entry_status` — use the existing publication vocabulary (`provisional`, `active`, `expiring`, `expired`, `retired`)
- `maintenance_status` — one of `stable`, `watch`, `under_review`, `narrowed`, `suspended`, `superseded`
- `effective_from`
- `effective_until` when applicable
- `supersedes_entry_id` when applicable
- `superseded_by_entry_id` when applicable

### Public explanation fields

- `change_kind`
- `reason_family`
- `public_revision_note`
- `scope_impact`
- `action_hint`
- `appeal_route_ref`
- `next_review_by`

The human-readable note should be brief. The archive prefers **short, coded transparency** over miniature policy manuals.

## Change kinds

The archive's starter vocabulary for `change_kind` is:

- `admitted` — first publication of a standing rule;
- `clarified` — language, metadata, or human-readable guidance changed without changing the recognition ceiling;
- `narrowed_scope` — fewer requirement families, sectors, or versions are now covered;
- `raised_ceiling` — the default recognition outcome became stronger;
- `lowered_ceiling` — the default recognition outcome became weaker;
- `split_entry` — one entry became multiple more precise entries;
- `suspended` — automatic reliance should pause while review continues;
- `superseded` — a newer rule replaces the old one;
- `expired` — the review window elapsed and the rule is no longer pre-cleared;
- `retired` — the rule should no longer be used as a standing shortcut.

This keeps the public history focused on **what changed in the rule**.

## Reason families

The archive does not want long public debate logs. It does want short, repeatable reason families.

The starter vocabulary for `reason_family` is:

- `version_drift`
- `construct_mismatch`
- `quality_assurance_change`
- `authority_change`
- `scope_clarification`
- `recency_failure`
- `privacy_or_legal_change`
- `editorial_correction`
- `published_exception_promoted`

The public note may add one or two plain-language sentences, but the code should do most of the work.

## Scope impact

Every public change should say **what the change touches**.

The archive's preferred `scope_impact` values are:

- `metadata_only`
- `future_uses_only`
- `specific_versions_only`
- `specific_requirement_families_only`
- `specific_sectors_only`
- `all_future_automatic_uses`

This helps prevent a common failure mode where a visible update exists, but nobody can tell whether it matters for their context.

## Action hints

The public layer should also tell partner systems and human advisors what kind of follow-up is prudent.

The archive's starter `action_hint` vocabulary is:

- `continue_as_published`
- `read_note_then_continue`
- `recheck_before_next_use`
- `route_to_manual_review`
- `pause_automatic_acceptance`
- `use_successor_entry`

These are deliberately **hints**, not a complete automation contract. The archive wants the public layer to carry enough meaning for trust and triage before it tries to solve cross-system auto-consumption perfectly. The default partner-consumption and grandfathering rules that now close that gap live in [`partner-consumption-and-grandfathering-rules.md`](partner-consumption-and-grandfathering-rules.md).

## What should stay out of the public layer

Do **not** publish the following by default:

- raw appeal counts;
- upheld-rate percentages;
- node-by-node disagreement tables;
- false-match counts when volume is small enough to invite inference;
- trigger thresholds;
- reviewer identities;
- local faculty or evaluator notes;
- learner narratives;
- support/accommodation-channel information;
- chat logs, telemetry, or behavior traces.

The archive's view is that these fields either leak too much, invite gaming, or create false confidence in numbers that are too context-sensitive to travel well.

## Partner-consumable profile

The machine-readable partner layer should be only slightly richer than the public history card.

The archive's starter partner fields are:

- all identity, state, reason, scope, and action fields from the public card;
- `change_sequence_number`
- `changed_field_set`
- `review_window_class`
- `entry_family`
- `recognition_ceiling`
- `manual_review_trigger_ref` when already public under the exception profile.

That is enough for another system to notice that something changed, update its local cache, and decide whether to keep relying on the standing entry, pause, or ask a human.

## Local-only maintenance evidence

The following may still exist locally for governance, audit, and correction:

- aggregate maintenance counts and bands;
- internal thresholds for review triggers;
- sampled local cases;
- faculty or evaluator deliberation notes;
- advisory discussion of whether a change is over- or under-reactive;
- learner-specific appeal materials;
- protected support-channel records.

These materials should stay local, time-limited, and governed by ordinary privacy, records, and institutional-retention rules.

## Publication cadence

The archive now prefers a simple cadence rule.

Publish a public history update whenever there is a substantive change to:

- status;
- recognition ceiling;
- covered versions;
- covered sectors or requirement families;
- successor entry;
- appeal route;
- or next review date.

Do **not** publish a new public history event for every local case or every internal review conversation.

## Retention and display posture

The public layer should be durable enough to show recent rule history, but not so detailed that it becomes an operational dossier.

The archive's starter posture is:

- always show current status;
- show the current version plus a short rolling history of substantive prior changes;
- keep supersession links and effective dates durable;
- suppress raw counts entirely from the public layer;
- and avoid tiny change logs for purely editorial events unless they alter meaning.

In other words: **make the current rule legible, and make consequential changes discoverable.**

## Example patterns

### Example 1. Narrowed because tool-specific training drifted

Good public history:

- `change_kind = narrowed_scope`
- `reason_family = version_drift`
- `scope_impact = specific_versions_only`
- `action_hint = recheck_before_next_use`
- short note: “Earlier product versions remain covered; newer interface/workflow changes require review before automatic use.”

Bad public history:

- raw false-match counts by campus;
- internal threshold values;
- reviewer comments about specific learners or advisors.

### Example 2. Temporary suspension during quality concern

Good public history:

- `change_kind = suspended`
- `reason_family = quality_assurance_change`
- `scope_impact = all_future_automatic_uses`
- `action_hint = pause_automatic_acceptance`
- short note: “Automatic standing use is paused pending review of updated provider assessment controls.”

Bad public history:

- speculation about specific disputed cases;
- publication of case-level evidence.

### Example 3. Clarification only

Good public history:

- `change_kind = clarified`
- `reason_family = scope_clarification`
- `scope_impact = metadata_only`
- `action_hint = read_note_then_continue`

This prevents needless panic when a public note changes but the recognition ceiling does not.

## Failure modes this document is trying to prevent

- **black-box standing rules** — the entry changes, but outsiders cannot tell what happened;
- **dashboard maximalism** — trust is pursued through raw operational statistics that do not travel well and may expose sensitive patterns;
- **silent scope drift** — entries narrow or split without a durable public trace;
- **panic updates** — minor clarifications look like major policy reversals because no change vocabulary exists;
- **privacy spillover** — maintenance transparency becomes a back door for case-level disclosure;
- **automation theater** — systems pretend the public feed fully settles local action when the action hint is only advisory.

## Current archive bet

The archive's current best guess is that **a thin public history layer built from statuses, dates, reason families, scope impact, and action hints** will travel better than either no public maintenance history or metrics-heavy publication.

That remains a bounded claim. The next live problem is narrower still: which of these public maintenance signals partner systems should consume automatically, which should trigger local confirmation, and when prior uses should be grandfathered rather than reopened. See `OQ-0008` and `FT-0014`.
