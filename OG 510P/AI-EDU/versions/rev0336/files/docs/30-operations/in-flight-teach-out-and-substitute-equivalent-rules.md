# In-flight teach-out and substitute-equivalent rules

This document closes the archive's live gap around **in-flight reliance**.

The archive already had:

- a packet and recognition rail;
- sector defaults for recognition strength;
- standing-list governance, publication, recency, exception, maintenance, public-history, and
  partner-consumption rules.

What it still lacked was a sharper answer to the hardest middle case:

> **when a learner has already relied on a standing rule, but the receiving decision is not yet
settled, what protection is owed if that rule narrows, expires, or is suspended?**

The archive's answer is:

> **default to continuity by the nearest safe path. Prefer teach-out, successor substitution,
challenge access, or construct-close equivalents over hard restart whenever integrity, legality, and
construct fit still permit it.**

This move is grounded in a converging public pattern. HLC now requires teach-out agreements to be
fair and equitable, to provide reasonable opportunities to complete a program of study, to state the
applicable time period, to identify covered students and programs, and to disclose in advance the
credits the receiving institution is willing to accept, tuition/fees, records retention, and
communication plans. HLC's current toolkit also says closing and receiving institutions should
establish specific transitional processes for students' academic, emotional, financial, and
logistical transitions, and it recommends multiple transfer options plus teach-out planning by
programme. SACSCOC's current substantive-change policy centers minimal disruption and additional
cost, requires reasonable completion options for all students regardless of progress, and explicitly
allows receiving institutions to seek exceptions to ordinary institutional-credit rules to
accommodate students near the end of a programme. U.S. Department of Education closure guidance says
a comparable continuation should preserve minimal interruption, delay, and loss of credits, and
current FAQ guidance makes the practical stakes visible by tying comparable-program continuation to
discharge eligibility and record access. Public catalog-rights and appeal practices add a
non-retroactivity and substitution signal: students ordinarily retain an established requirement
baseline while institutions still use faculty-governed substitutions and appeals when local fit
needs judgment. See `B74`, `B75`, `B76`, `B77`, and `B78`.

## Core rule

The archive now distinguishes three possible responses for an in-flight learner when a standing
entry changes midstream:

- **preserve the pathway** — keep the learner on a path that is as close as possible to the
  relied-upon route;
- **preserve the outcome, alter the path** — require a successor entry, a construct-close
  equivalent, or a challenge/review route, but do not force the learner to restart duplicate basics;
- **graceful restart** — only when integrity, legal validity, or authority failure makes even
  substitute-equivalent protection unsafe.

The archive rejects two bad extremes:

- **full grandfathering for every in-flight case**, which can freeze obviously stale or unsafe
  rules;
- **hard restart by default**, which externalizes system maintenance risk onto the learner.

The default bias is: **when the learner relied in good faith, move them sideways before moving them
backward.**

## What counts as in-flight reliance

The archive now names four reliance classes. For the evidence anchors (`E0`-`E4`) and burden bands
(`B0`-`B3`) that determine when these classes trigger stronger protection, see
[`documented-reliance-and-burden-thresholds.md`](documented-reliance-and-burden-thresholds.md).

### `I0 inquiry_only`

The learner has asked questions or browsed options, but there is no documented plan, submission, or
advised pathway.

Default protection:

- no special teach-out right;
- ordinary updated rules apply;
- still provide clear reasons and next steps.

### `I1 advised_path`

An advisor, navigator, or institutionally recognized public node has documented that a specific
standing entry or route was recommended for a named learner.

Default protection:

- preserve queue position;
- offer successor substitution where available;
- avoid duplicate intake or duplicate basic modules if the construct still fits.

### `I2 submitted_or_routed`

The learner has submitted materials, entered a referral workflow, started a recognition review, or
been routed into a receiving-node process under the prior standing rule.

Default protection:

- manual review before denial;
- successor substitution or construct-close equivalent by default;
- challenge/portfolio/review access if automatic standing use is paused.

### `I3 committed_progress`

The learner has already started the recognized offering, has nearly completed it, has incurred
meaningful cost, or has structured time/sequence commitments in reliance on the old route.

Default protection:

- strongest teach-out or substitute-equivalent presumption short of full grandfathering;
- preserve progress wherever possible;
- consider exceptions to ordinary residency / institutional-credit / sequence rules when public
  policy already allows that sort of accommodation.

`I3` is the archive's clearest teach-out class.

## Protection vocabulary

The archive now uses a small protection vocabulary for in-flight cases.

- `T0 updated_rule_only` — ordinary updated rule applies; no special protection beyond explanation.
- `T1 preserve_queue_and_review` — hold the learner in process and require manual review before
  denial.
- `T2 successor_substitution` — map the learner to a successor standing entry without restarting
  intake.
- `T3 substitute_equivalent_path` — route the learner to a construct-close equivalent, bridge, or
  updated requirement that preserves as much prior progress as possible.
- `T4 challenge_or_portfolio_access` — give the learner an alternative way to prove competence
  without repeating the full underlying learning.
- `T5 teach_out_commitment` — preserve completion through the old route or an approved equivalent
  path, typically for near-completion or high-reliance cases.

The archive treats `T5` as the strongest ordinary in-flight protection and reserves full reopening /
invalidation logic for the exceptional failure family already named in
[`partner-consumption-and-grandfathering-rules.md`](partner-consumption-and-grandfathering-rules.md).

## Default mapping by change family

### 1. Editorial clarification or metadata correction

Typical pattern:

- `change_kind = clarified`
- `reason_family = editorial_correction`
- no real change to recognition ceiling or construct fit

Default protection:

- `I0` → `T0`
- `I1`-`I3` → `T1` or `T2`

Rationale:

These cases should almost never push a learner backward.

### 2. Successor publication or version rollover with preserved construct fit

Typical pattern:

- `change_kind = superseded`
- successor entry exists;
- the construct and recognition ceiling are materially continuous

Default protection:

- `I0` → updated route only
- `I1`-`I3` → `T2 successor_substitution`

Rationale:

If the system knows the successor, it should move the learner there without making them rediscover
the path.

### 3. Recency expiry or version drift

Typical pattern:

- `reason_family = version_drift` or `recency_failure`
- old standing trust is stale, but not discredited

Default protection:

- `I1` → `T1`
- `I2` → `T3` or `T4`
- `I3` → `T3` or `T5` when the learner is near completion or cost exposure is already meaningful

Rationale:

The system no longer wants to pre-clear fresh entrants under the old rule, but in-flight learners
should usually get either an updated equivalent or a way to prove what they know.

### 4. Narrowed scope or lowered ceiling

Typical pattern:

- `change_kind = narrowed_scope` or `lowered_ceiling`
- prior standing shortcut was too broad

Default protection:

- `I1` → `T1`
- `I2` → `T3` or `T4`
- `I3` → `T3`, `T4`, or limited `T5` if the learner is at the end of the path and the remaining
  mismatch is small enough to govern explicitly

Rationale:

A narrowed rule usually calls for a more exact route, not automatic erasure of prior reliance.

### 5. Suspension during review

Typical pattern:

- `maintenance_status = suspended`
- no final adverse integrity finding yet

Default protection:

- `I0` → updated route only
- `I1`-`I2` → `T1` or `T4`
- `I3` → `T4` or conditional `T5` with explicit human approval

Rationale:

Suspension should stop fresh automation but still preserve a governed path forward for learners
already in motion.

### 6. Authority failure, fraud, or legal invalidity

Typical pattern:

- issuer authorization disappears or was falsified;
- fraud or claimant-specific misrepresentation is evidenced;
- legal/privacy findings invalidate the underlying use itself

Default protection:

- `I0`-`I2` → `T0` or `T4` only if alternate evidence is possible
- `I3` → `T4` where the learner can independently prove competence; otherwise graceful restart

Rationale:

This is the main family where the archive permits a true break in continuity because the problem is
not drift; it is invalidity of the underlying authority or claim.

## Sector defaults for in-flight protection

### Libraries and low-barrier civic entry points

Default bias:

- preserve navigation continuity;
- never make the learner restart intake from scratch merely because a standing entry changed;
- route quickly to a human navigator plus successor or equivalent options.

Typical tools:

- `T1`, `T2`, `T3`

### Workforce systems and bridge / noncredit routes

Default bias:

- preserve forward motion toward employability or next-step training;
- when standing trust narrows, offer bridge modules, successor pathways, or challenge access before
  requiring full re-enrollment.

Typical tools:

- `T2`, `T3`, `T4`

### Community colleges, VET, and open-access credit-bearing bridge nodes

Default bias:

- avoid duplicate basics;
- use credit-for-prior-learning, challenge, portfolio, or substitution where policy already supports
  those moves;
- reserve hard restart for construct failure or integrity failure.

Typical tools:

- `T3`, `T4`, selective `T5`

### Universities and highly sequenced credit-bearing programmes

Default bias:

- protect reliance, but do not smuggle major construct mismatches into formal credit silently;
- preserve place in line, use faculty-governed equivalency review, and consider teach-out or
  exception requests for near-completion learners when the remaining difference is narrow.

Typical tools:

- `T1`, `T3`, `T4`, rare `T5`

## Minimum in-flight protection floor

Whenever a learner qualifies for `I1`-`I3`, the archive now expects a minimum floor.

### 1. Preserve legibility

The learner should be told:

- what changed,
- which prior entry or route they relied on,
- what this means for their case,
- and what the next concrete path is.

### 2. Preserve place in line

A standing-rule change should not usually force a learner to restart referral, queueing, or advisor
triage from zero.

### 3. Preserve records access

Do not create continuity rules without transcript, verification, and packet availability. Release
holds and record-access barriers when closure or route change would otherwise strand the learner.
See `B75`, `B77`.

### 4. Preserve non-duplication when construct fit survives

If the system believes the learner still has a plausible path to the same or a close enough outcome,
use substitute-equivalent routes or challenge pathways before requiring repetition of
already-covered basics.

### 5. Keep support routing private

Accommodation, disability, translation, and other protected support channels do not become public
portability metadata just because a learner needs teach-out or substitute-equivalent protection.

## Near-completion rule

The archive now makes one sharper claim:

> **the closer a learner is to completion, the stronger the presumption for teach-out, successor
substitution, or a narrow policy exception rather than restart.**

This does **not** mean automatic credit for anything already done. It means the system should
actively search for the least-disruptive lawful path, especially when public policy already
recognizes exceptions for near-completion teach-out students.

## Cost and delay posture

The archive does not yet set a universal numeric cap for added cost or delay. It does set a design
posture:

- small administrative changes should not create extra cost;
- successor substitution should normally preserve timetable and fee expectations as much as
  possible;
- if the only path forward adds substantial delay or cost, the system owes a stronger justification
  and should look first for bridge, challenge, or exception routes.

The archive keeps exact caps as live followthrough work rather than pretending one number fits every
sector.

## What the archive refuses

The archive refuses the following patterns:

- **silent hard restart** because a standing entry disappeared from a list;
- **denial by omission** where “not currently listed” is treated as “must repeat everything”;
- **retroactive bait-and-switch** where a learner is advised into a route and then told that
  midstream maintenance risk is entirely their problem;
- **public exposure of support-channel details** in the name of proving reliance;
- **full equivalency by sentiment** where institutions ignore genuine construct or legal failures.

## Practical publication consequence

A public maintenance signal is not enough on its own for in-flight fairness. The consuming
institution or public node also needs to know whether the case should receive:

- ordinary updated treatment,
- successor substitution,
- substitute-equivalent routing,
- challenge/portfolio access,
- or teach-out protection.

That means future publication work may need a tiny additional field or local rule reference for
**in-flight protection class**, but the archive deliberately keeps that question open until it is
clearer how much should be shared publicly versus held in local governed policy.

## Relation to the rest of the archive

This document sits downstream from the standing-entry maintenance stack.

- [`public-maintenance-history-and-trust-signals.md`](public-maintenance-history-and-trust-signals.md)
  says what gets published.
- [`partner-consumption-and-grandfathering-rules.md`](partner-consumption-and-grandfathering-rules.md)
  says what a partner should do by timing class.
- **This document** says what meaningful protection looks like inside the hardest timing class: the
  learner already relied, but the receiving outcome is not yet final.

The archive's current answer is intentionally modest: **protect motion, preserve evidence, minimize
duplication, and escalate to stronger teach-out or substitute-equivalent measures as reliance
deepens.**
