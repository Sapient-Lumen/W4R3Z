# Appeal feedback and privacy-light standing-list maintenance

This document closes the maintenance gap left open by the archive's standing-recognition work.

The archive already has:

- a typed public handoff packet;
- sector defaults for what outside AI-learning should mean;
- governance rules for standing-equivalency lists;
- a tiny publication profile with family-specific recency windows;
- and a bounded exception grammar for partial equivalencies, local overrides, and named manual-review triggers.

What it still lacked was a compact answer to a narrow operational question:

> **how should appeals, disagreement, and repeated false matches update standing rules over time without turning public AI-learning recognition into centralized learner-level surveillance?**

The archive's answer is:

> **maintain standing rules with aggregate signals, bounded trigger thresholds, and sampled human review. Keep learner-level case files local, time-limited, and off the interoperable rail.**

This move is grounded in a converging set of public signals. CUNY transfer and CPL practice shows that reevaluation and appeal already depend on human review of syllabi, evaluator judgment, and faculty/department escalation rather than a purely automatic equivalency engine; CCNY requires syllabus/course-description review by academic departments for appeals, Hostos routes reevaluation through evaluators and academic chairs, and Baruch makes transfer-credit appeal a real right with campus review and a further CUNY OAA appeal path. DOE's student-privacy guidance keeps correction and inspection rights explicit. DOL's monitoring and quality guidance treats performance data as something that should be analyzed and acted on for corrective action and continuous improvement, and requires inaccurate reports to be corrected. ALA's updated privacy interpretation says data collected for analysis should be anonymous or aggregated, not linked to personal information, and should follow purpose limitation, storage limitation, and data minimization. UNESCO's rights framing keeps privacy and governance inside the educational question rather than outside it. See `B20`, `B53`, `B61`, `B62`, `B63`, `B64`.

## Core rule

The archive now distinguishes **case handling** from **rule maintenance**.

- **Case handling** happens locally and may require detailed evidence.
- **Rule maintenance** happens at the standing-entry level and should rely on aggregate signals, bounded review triggers, and short human-readable revision reasons.

The archive rejects two bad extremes:

- **memoryless recognition**, where each bad match is handled locally but never improves the standing rule;
- **surveillance-heavy maintenance**, where every appeal or false match produces a durable centralized dossier about individual learners, support use, or tool traces.

## Three maintenance layers

### Layer 1. Local case handling

Receiving nodes may still need:

- syllabi;
- sample work or supervised assessment results where already permitted;
- faculty or department review;
- and local notes about why a one-off case was affirmed, narrowed, or denied.

Those materials belong in the local review channel, under ordinary privacy/records rules. They do **not** belong in the shared packet, standing-list feed, or public exception profile.

### Layer 2. Entry-level maintenance signals

Each standing entry should maintain a small, privacy-light maintenance record.

The archive's preferred signal families are:

- **use volume** — whether the entry is actually being used often enough to justify maintenance effort;
- **manual-review pressure** — how often the published default is not enough;
- **mismatch pressure** — how often the entry is later narrowed, reversed, or found too broad;
- **under-recognition pressure** — how often appeals or reviews conclude the published ceiling was too weak;
- **staleness pressure** — whether version drift, curriculum change, or recency failure keeps appearing.

These signals should be stored as **counts, rates, or bands tied to the entry**, not as learner narratives.

### Layer 3. Scheduled human review

Aggregate signals do not rewrite standing rules on their own.

They trigger scheduled review by the body already responsible for standing-list governance. That body may:

- keep the entry unchanged;
- tighten scope;
- shorten the review window;
- add or retire an exception profile;
- lower the recognition ceiling;
- split the entry by version, sector, or programme family;
- or retire the standing rule and send future cases to manual review.

The archive prefers **reviewable maintenance decisions** over hidden drift.

## Minimal maintenance profile

The maintenance layer should stay smaller than the publication profile and much smaller than local case files.

### Identity and cadence

- `entry_id`
- `maintenance_window`
- `last_substantive_review`
- `next_review_by`
- `maintainer_authority`

### Aggregate signal fields

The archive's starter fields are:

- `uses_count_band`
- `manual_review_rate_band`
- `affirmed_as_published_rate_band`
- `downward_revision_count`
- `upward_exception_count`
- `false_match_reversal_count`
- `receiving_node_disagreement_count`
- `staleness_flag_count`
- `appeal_count_band`
- `appeal_upheld_rate_band`

The point is not statistical beauty. The point is to let maintainers see whether the entry is **stable**, **too broad**, **too narrow**, or **aging out**.

### Action fields

- `current_maintenance_state` — `stable`, `watch`, `targeted_review`, `tighten_scope`, `split_entry`, `lower_ceiling`, `retire_to_manual_review`
- `last_action_reason`
- `revision_note_public`

The archive wants every substantive maintenance action to have a short public reason, even when the supporting case material remains local.

## What counts as a false match

A false match is not just a denied appeal.

The archive treats a case as a **false match** when the standing rule itself appears to have been wrong for the requirement family, version, or receiving scope at issue.

Typical patterns:

- the entry repeatedly looked equivalent but failed construct fit on review;
- the entry kept getting used for a requirement family that the publisher never intended;
- version drift made older mappings misleading;
- a provider or assessment changed enough that the standing rule is no longer trustworthy;
- or the same outside learning is repeatedly over-claimed beyond the published ceiling.

False matches are entry-maintenance events, not learner moral faults.

## Trigger rules

The archive does not prescribe one numeric threshold for all systems. It does prescribe trigger types.

### Trigger A. Repeated downward correction

If an entry is repeatedly narrowed, reversed, or found overbroad, the maintainer should do one of the following:

- lower the recognition ceiling;
- add a manual-review trigger;
- tighten the receiving scope or requirement family;
- shorten the recency window;
- or retire the entry to manual review.

### Trigger B. Repeated stronger-than-published outcomes

If the same entry is repeatedly granted stronger outcomes through manual review, the maintainer should not let silent shadow precedent accumulate.

Instead, they should:

- add a bounded exception profile;
- split the entry by sector or programme family;
- or publish a stronger standing rule where formal authority exists.

### Trigger C. Cross-node disagreement

When different receiving nodes keep making different judgments about the same outside learning, the answer is usually not endless arbitration.

The better pattern is to ask whether the entry should be:

- split by receiving sector;
- split by programme family;
- capped more weakly at the cross-system layer;
- or routed to review for construct-sensitive contexts.

### Trigger D. Version drift or stale evidence

When appeals repeatedly surface outdated versions, changed vendor surfaces, or expired evaluated learning, the entry should expire, split by version/date, or move to manual review.

### Trigger E. Repeated procedural confusion

If appeals repeatedly arise because learners or advisors misunderstand what an entry means, the public fix may be editorial rather than substantive:

- improve the human-readable note;
- clarify the requirement-family scope;
- publish the manual-review reason;
- or tighten the status language.

## Appeal posture

The archive now prefers a **rights-preserving but policy-light** appeal structure.

1. The learner should be able to see the published standing rule and public revision note.
2. The learner should have a local route to request reevaluation.
3. That route may require local evidence and department/programme review.
4. Negative local decisions should route through whatever formal system-level appeal path already exists.
5. Appeal outcomes should improve the entry **only when they indicate repeated rule failure**, not merely because a single unusual case was decided differently.

This posture is deliberately consistent with public-system examples where advisors, evaluators, departments, and final central academic review each play distinct roles. See `B62`, `B64`.

## What should never enter the maintenance layer

Do not put the following into the standing-maintenance profile:

- names or stable identifiers for learners;
- protected accommodation/support-channel information;
- raw chat logs or tool telemetry;
- full faculty deliberation notes;
- detailed case narratives when a short coded reason is enough;
- biometric or behavior-tracking signals;
- or anything that would let partner systems reconstruct an individual learner's path through appeals or support channels.

The archive's bias is: **retain locally only what is needed to adjudicate and audit; publish cross-system only what is needed to maintain the rule.**

## Preferred evidence posture for maintenance

The archive now favors three forms of evidence for standing-entry maintenance:

- **aggregate counters or bands** tied to the entry;
- **scheduled sample review** of a small number of local cases by the authorized maintainer;
- and **short public revision notes** that explain what changed and why.

This is enough for corrective action and continuous improvement without pretending that the shared layer needs a full case-management system. See `B61`, `B63`.

## Example patterns

### Example 1. Tool-specific badge keeps overreaching

A vendor-specific workflow badge is published at `R1`/`R2`, but multiple receiving nodes keep trying to treat it as major-core substitution.

Good maintenance response:

- keep the low ceiling;
- add a clearer public note;
- publish a manual-review trigger for construct-sensitive major/core requirements;
- and shorten the review window if the product surface is changing quickly.

### Example 2. Public foundational module keeps winning stronger review outcomes

A library/community-college foundational AI-literacy module is published for duplicate-basics waiver only, but repeated reviews in bridge/noncredit routes keep granting stronger entry outcomes.

Good maintenance response:

- publish a bounded stronger rule for that programme family or sector;
- do not rely on repeated quiet exceptions;
- and do not raise the ceiling everywhere if the stronger fit is local rather than general.

### Example 3. Same entry keeps generating mixed treatment across sectors

A standing rule works in workforce intake but fails repeatedly in licensure-constrained academic programmes.

Good maintenance response:

- split the entry by receiving scope;
- keep the wider continuity rule where it still works;
- and add manual-review routing for the constrained sector rather than retiring the whole entry.

## Failure modes this document is trying to prevent

- **silent shadow precedent** — repeated appeal outcomes change practice without changing publication;
- **appeal theater** — learners can appeal, but nothing ever improves system rules;
- **surveillance creep** — every dispute becomes durable cross-system case tracking;
- **false certainty** — a standing rule remains published even after repeated mismatch signals;
- **overreaction** — one unusual case collapses a standing rule that still works broadly;
- **privacy spillover** — support-channel or telemetry data becomes recognition-maintenance infrastructure.

## Current archive bet

The archive's current best guess is that **aggregate entry-level maintenance signals plus bounded human review** will outperform both ad hoc memory and centralized case tracking.

That means:

- keep case files local;
- let appeals and reevaluations exist as real rights-preserving pathways;
- convert repeated failure or repeated stronger-fit patterns into standing-rule maintenance;
- publish short revision reasons and status changes;
- and collect only the smallest analysis data needed to know whether a rule is stable, too broad, too narrow, or stale.

This closes the archive's old maintenance gap. The archive now answers the disclosure boundary with a separate thin public history/profile for state, date, scope, reason family, and action hint without raw counts. The next live question is narrower still: which continuity-reserve or public-entitlement triggers, proof minima, claiming windows, and publication fields truly travel across sectors, and when repeated `K2` / `K3` burdens should stay as predeclared reserves rather than harden into learner-facing entitlement floors. See [`public-maintenance-history-and-trust-signals.md`](public-maintenance-history-and-trust-signals.md), [`no-fault-transition-cost-absorption-and-fee-waiver-rules.md`](no-fault-transition-cost-absorption-and-fee-waiver-rules.md), `OQ-0008`, and `FT-0034`.
