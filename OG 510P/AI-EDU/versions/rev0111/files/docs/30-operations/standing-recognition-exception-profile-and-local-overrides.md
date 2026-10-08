# Standing-recognition exception profile and local-override grammar

This document closes the exception-logic gap left open by the archive's standing-list publication work.

The archive already has:

- a typed public handoff packet;
- sector defaults for what outside AI-learning should mean;
- governance rules for standing-equivalency lists;
- and a tiny machine-readable publication profile with family-specific recency windows.

What it still lacked was a compact answer to a narrow but important question:

> **how should a standing rule express partial equivalency, local override, and construct-sensitive exception logic without collapsing back into hidden local discretion or into a giant shared policy language?**

The archive's answer is:

> **publish a base standing rule plus, when needed, a tiny exception profile that carries only repeated public constraints, recognition caps, and manual-review triggers. Keep everything else local.**

This move is grounded in a converging set of public signals. Credential Engine's prior-learning-recognition work treats policies, evidence, methods, and outcomes as publishable data rather than invisible casework. CUNY's CPL policy and Transfer Explorer surfaces show the real shape of the problem: credit can transfer, yet applicability still varies by degree requirement, residency, grade thresholds, and even combinations of courses. 1EdTech's CASE standard shows that outcome, rubric, and criterion references can travel as structured associations rather than only prose. W3C's verifiable-credential work reinforces that portable claims can be updated and checked over time, but should not silently drag private or overly detailed institutional logic into the portable layer. See `B41`, `B43`, `B53`, `B60`.

## Core rule

The shared publication layer should carry **only the exception logic that changes the public meaning of a standing rule across repeated cases**.

That means the interoperable layer may carry:

- narrow scope limits;
- repeated eligibility conditions;
- recognition ceilings;
- partial-equivalency statements;
- and named manual-review triggers.

It should **not** carry:

- private learner support information;
- advisor case notes;
- staffing/capacity contingencies;
- instructor-by-instructor discretion;
- dense programme-handbook prose;
- or full local decision trees.

## The archive's two-part publication pattern

A standing entry now has two separable parts.

### Part 1. Base standing rule

This is the ordinary public entry described in [`standing-list-publication-profile-and-recency-windows.md`](standing-list-publication-profile-and-recency-windows.md):

- what outside learning is being recognized;
- where;
- with what default outcome;
- under what dates;
- and with what default manual-review route.

### Part 2. Optional exception profile

This is only published when repeated public exceptions are common enough to deserve reuse.

A list maintainer should **not** publish an exception profile merely because one programme once made an unusual judgment. The threshold is repetition, public legibility, and likely reuse.

## Minimal exception profile

The archive's preferred exception profile is intentionally small.

### A. Profile identity

- `exception_profile_id` — stable identifier for the exception block;
- `entry_id` — base standing entry to which it belongs;
- `profile_status` — `active`, `expiring`, `expired`, or `retired`;
- `effective_from` — when the exception profile became active;
- `review_by` — when the exception profile must be checked again.

### B. Narrow scope selectors

These fields say **where the base rule stops or narrows**.

- `applies_to` — specific receiving scope, programme family, requirement family, or node subset;
- `does_not_apply_to` — excluded programme families or requirement families;
- `requirement_scope` — whether the rule applies to general education, gateway basics, bridge completion, elective credit, placement, or other named requirement families.

The archive prefers **broad requirement families** over one-off course numbers whenever possible.

### C. Repeated eligibility conditions

These fields say what recurring public condition must hold for the standing rule to fire.

- `conditions` — one or more compact conditions such as:
  - minimum grade or score;
  - required combination of courses/modules;
  - tighter-than-default recency;
  - supervised-assessment requirement;
  - co-requisite or prior-foundation requirement;
- `condition_note` — one short human-readable note when the condition needs clarification.

The archive prefers **a short controlled vocabulary plus one short note** over full policy prose.

### D. Recognition cap or partial-equivalency action

These fields say how recognition changes when the entry is narrower than its family default.

- `recognition_cap` — the highest permitted outcome under this exception profile (`R1`-`R4` or local equivalent);
- `partial_action` — e.g. `waive_duplicate_basics_only`, `counts_as_elective_only`, `placement_or_challenge_only`, `entry_requirement_only`, `manual_review_before_credit`;
- `construct_fit_ref` — optional link to outcomes, rubric criteria, or framework items when partial fit depends on named constructs rather than a provider title alone.

This is how the archive handles **partial equivalency** without pretending that every outside completion is either full credit or nothing.

### E. Manual-review triggers

These fields say when the public rule stops and a human must decide.

- `manual_review_triggers` — one or more named triggers such as:
  - licensure or external-accreditor programme;
  - construct-sensitive major/core requirement;
  - version mismatch or stale evidence;
  - unclear course combination;
  - local curriculum change;
- `manual_review_route` — where that review goes.

The archive's preference is to publish the **reason category** for review, not the whole local judgement script.

## What belongs in the shared layer

The shared layer is for **stable, public, repeated constraints**.

Good candidates for publication:

- a grade floor used across many programmes;
- a known combination rule (`course A` plus `course B`);
- an explicit cap such as “waives duplicate basics only”;
- a rule that licensure-track programmes must route to review;
- a requirement-family scope such as `general-education-only` or `entry-requirement-only`.

## What stays local

The local layer is for **volatile, private, or overly detailed logic**.

Keep local:

- staff-capacity decisions;
- current seat availability;
- evolving pilot exceptions not yet stable enough for publication;
- disability/accommodation records;
- detailed faculty deliberation notes;
- behavioural telemetry or vendor-generated learner profiles;
- and long course-by-course special cases that almost never repeat.

## The archive's publication bias

When in doubt, the archive prefers the following order:

1. publish the base standing rule;
2. publish a tiny exception profile only for repeated public constraints;
3. send everything else to named manual review.

This bias prevents two equal and opposite failures:

- **underpublication**, where important exceptions vanish into hidden local discretion;
- **overpublication**, where the shared layer turns into brittle policy code that no ordinary public provider can maintain.

## Default condition vocabulary

The archive's starter vocabulary is intentionally tiny.

- `grade_floor`
- `score_floor`
- `combination_required`
- `recency_tighter_than_family_default`
- `supervised_assessment_required`
- `co_requisite_required`
- `prior_foundation_required`

Publishers may extend this list, but only when a new condition is both durable and reused.

## Default partial-action vocabulary

The archive's starter partial-action vocabulary is:

- `waive_duplicate_basics_only`
- `counts_as_elective_only`
- `placement_or_challenge_only`
- `entry_requirement_only`
- `manual_review_before_credit`

This vocabulary is deliberately plainer than full transfer-code systems. It is meant to preserve learner legibility.

## Default manual-review vocabulary

The archive's starter manual-review reasons are:

- `licensure_or_external_accreditor`
- `construct_sensitive_major_or_core`
- `version_or_date_mismatch`
- `unclear_combination_match`
- `local_curriculum_change`
- `evidence_strength_below_required_ceiling`

The publication layer should say **why** review is needed, not hide review behind an unexplained stop sign.

## Why construct references matter

Exception logic often becomes opaque when it relies on titles alone.

A better pattern is:

- publish the title and issuer for human recognition;
- publish the claim family and recognition ceiling for decision routing;
- and, where partial fit matters, attach a lightweight `construct_fit_ref` to named outcomes, rubric criteria, or framework items.

This is the archive's preferred use of CASE-like alignment work: not giant outcome warehouses, but just enough reference stability to explain why a standing rule covers gateway basics, elective credit, or placement while stopping short of major-core substitution.

## Example patterns

### Example 1. Public foundational AI-literacy module

A library/community-college bridge module may carry a standing rule of `R2` for duplicated introductory AI-literacy content.

Its exception profile may say:

- `does_not_apply_to = [licensure_track_programmes]`
- `partial_action = waive_duplicate_basics_only`
- `manual_review_triggers = [licensure_or_external_accreditor]`

This preserves public value without falsely promising direct major credit in externally constrained programmes.

### Example 2. Course combination requirement

A receiving system may know that one outside module only maps when paired with another foundation module or supervised practical.

Its exception profile may say:

- `conditions = [combination_required]`
- `condition_note = requires both foundational literacy and supervised verification practical`
- `partial_action = placement_or_challenge_only`

This mirrors the real world better than either blanket denial or automatic equivalence.

### Example 3. Programme applicability without silent denial

A standing rule may transfer as general elective or duplicated-basic waiver across a system, yet still not satisfy every major requirement because some programmes impose residency, GPA, or construct-specific major rules.

The archive's answer is not to hide this locally. It is to publish:

- broad requirement-family scope;
- any repeated cap;
- and a named manual-review trigger for construct-sensitive or externally constrained programmes.

## Failure modes the profile is meant to prevent

- **Provider-brand trust disguised as policy** — issuer verification alone does not settle equivalence.
- **One giant policy language** — if every local edge case must be encoded, publication will fail.
- **Silent under-recognition** — omission or unexplained denials become more likely when exceptions stay hidden.
- **False precision** — titles, badges, or platform labels stand in for construct fit.
- **Privacy creep** — support and advising traces leak into the shared layer.

## Compact operating rule

The archive's operational rule is now:

> **publish the base rule; publish only bounded repeated exceptions; route the rest to named human review.**

That is the archive's current best answer to how standing recognition can stay interoperable without pretending that all local educational judgment can or should be flattened into shared code.
