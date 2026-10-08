# Exception expiry, renewal, promotion, and baseline-rejoin proof interface spec

## Purpose

Once sanctioned durable difference becomes a first-class **baseline exception request**, another seam appears immediately:

- how does the product decide whether the exception should continue?
- when should a repeated exception be promoted into baseline instead?
- if the exception is supposed to end, what proves the target really rejoined baseline?
- how does the operator know whether some shadowing override still blocks inheritance?

This document defines the interface contract for **exception expiry review**, **renewal**, **promotion-to-baseline**, and **baseline-rejoin proof**.

## Core rule

Every approved baseline exception must eventually reach one reviewed outcome:

1. **renewed exception**
2. **promoted into standing baseline**
3. **closed with proved baseline rejoin**
4. **closed as unresolved because rejoin could not yet be proved**

The product must not let a durable exception survive indefinitely as an unexamined remembered special case.

## Why this needs its own spec

Current official Resilio docs sharpen the need for this boundary.

They currently document many ways to create or preserve difference:

- linked-device modes and default folder paths
- manual custom placement through `Disconnected` and later `Connect`
- per-folder `Folder Preferences`
- host-level power-user defaults
- configuration-mode launch parameters applied across machines
- reconnect flows that can yield different effective paths or duplicate folders

Those controls are real and sometimes necessary.
What they still do not provide as one product-native lifecycle object is the answer to:

- does this target still need to stay different?
- should this pattern now become the new baseline?
- if we remove the exception, what exact overrides must clear?
- after clearing them, did the target actually inherit baseline again?
- if not, what shadowing override or stale condition still prevents rejoin?

AnonSync should therefore insist on one more first-class answer surface:

- an **exception expiry, renewal, promotion, and baseline-rejoin proof** for `does this exception continue, become baseline, or end now, and what evidence proves whether baseline inheritance resumed?`

## Public objects

### Exception lifecycle review

The durable object opened when an exception reaches review time or a rejoin trigger fires.

Suggested fields:

- `exception_lifecycle_review_id`
- `baseline_exception_ref`
- `review_started_at`
- `review_state` (`draft`, `reviewed`, `approved`, `closed`, `superseded`)
- `current_outcome_candidate` (`renew`, `promote-to-baseline`, `attempt-rejoin`, `defer-insufficient-evidence`)
- `strongest_reason`
- `rejoin_proof_ref` nullable
- `promotion_draft_ref` nullable

### Rejoin prerequisite row

One thing that must be cleared or restored before baseline can apply again.

Suggested fields:

- `rejoin_prerequisite_row_id`
- `prerequisite_kind` (`manual-path-override-cleared`, `folder-preference-cleared`, `host-default-restored`, `config-overlay-removed`, `member-mode-aligned`, `capacity-restored`, `network-constraint-cleared`, `platform-capability-confirmed`)
- `prerequisite_summary`
- `state` (`pending`, `satisfied`, `blocked`, `inconclusive`)
- `evidence_ref` nullable

### Renewal rationale row

One reason why the exception should continue.

Suggested fields:

- `renewal_rationale_row_id`
- `reason_summary`
- `still-supported-by-evidence` bool
- `what-changed-since-last-review`
- `next-review-trigger`

### Promotion signal row

One sign that the exception pattern should become baseline instead of staying exceptional.

Suggested fields:

- `promotion_signal_row_id`
- `signal_kind` (`repeated-exception-pattern`, `majority-of-cohort-different`, `baseline-friction`, `platform-reality`, `policy-change`, `safety-improvement`)
- `signal_summary`
- `strength`
- `recommended_rollout_scope`

### Baseline rejoin proof

The durable summary shown after the product attempts to end the exception and re-observe effective state.

Suggested fields:

- `baseline_rejoin_proof_id`
- `baseline_exception_ref`
- `target_ref`
- `rejoin_attempted_at`
- `rejoin_verdict` (`proved-rejoined`, `partially-rejoined`, `shadowed-override-remains`, `could-not-prove-rejoined`)
- `remaining_shadow_summary`
- `future_inheritance_now_active_summary`
- `followup_ref` nullable

## Fixed inspection order

Every exception-lifecycle surface should preserve this order:

1. **Why the exception exists now**
2. **Whether the reason still holds**
3. **What would need to change for baseline to apply again**
4. **Whether the better answer is renew, promote, or rejoin**
5. **What the product observed after attempted rejoin**
6. **Whether baseline inheritance was actually restored**

### 1) Why the exception exists now

The surface should restate the current exception plainly.
Examples:

- `host H remains excepted from baseline download priority because network share latency made default ordering unsafe`
- `member M remains excepted from default arrival path during migration phase`
- `subject class Finance remains excepted from publication baseline pending custody review`

### 2) Whether the reason still holds

The product should compare last approval with fresh evidence.
Examples:

- `storage budget restored since prior review`
- `platform still lacks folder-preference surface`
- `migration milestone completed`
- `network segmentation evidence no longer present`

### 3) What would need to change for baseline to apply again

The operator should see a prerequisite checklist like:

- clear manual path override
- restore member mode to baseline posture
- remove folder-specific predefined hosts
- remove config overlay or host-level default
- verify baseline path is available and writable
- re-run future simulation and effective-state observation

### 4) Whether the better answer is renew, promote, or rejoin

This section should force a real decision:

- `renew because reason still holds and scope remains narrow`
- `promote because this pattern now fits most of cohort C`
- `attempt rejoin because triggering condition is satisfied`
- `defer only because evidence is missing, not because no one wants to decide`

### 5) What the product observed after attempted rejoin

This section should present evidence, not intent:

- `manual path override removed`
- `folder preference still shadowing baseline priority`
- `future-arrival simulation now matches cohort baseline`
- `member still receives manual placement because lower-level exception remains`

### 6) Whether baseline inheritance was actually restored

The verdict should be explicit:

- `proved rejoined`
- `partially rejoined`
- `shadowed override remains`
- `could not prove rejoined because target not freshly observed`

## Public rules

### Rule 1 — every exception must come back for lifecycle review

No approved exception may remain permanently active without renewed justification or an explicit indefinite-review posture.

### Rule 2 — removal intent is not rejoin proof

Saying `the exception was cleared` is not enough.
The product must still observe whether baseline behavior actually resumed.

### Rule 3 — shadowing overrides must be named

If rejoin fails, the interface should state which lower-level or parallel override still blocks baseline inheritance.

### Rule 4 — repeated renewals should challenge the baseline

If the same exception keeps getting renewed across targets or review windows, the product should suggest promotion into standing baseline.

### Rule 5 — defer only for evidence gaps, not discomfort

`Need more evidence` is valid only when the product can point to a missing observation or blocked prerequisite.

### Rule 6 — promotion opens a rollout draft, not a silent rewrite

When the exception pattern should become normal, the product must open a standing rollout draft rather than mutating baseline in place.

## Dense row contract

A dense lifecycle row should preserve these labels in this order:

- `Exception`
- `Reason still holds`
- `Prerequisites to rejoin`
- `Best next outcome`
- `Rejoin verdict`
- `Future inheritance now`
- `State`

## Example prompts

- `Does this exception still need to exist?`
- `Should this special case become the new baseline instead?`
- `What must clear before this target can rejoin baseline?`
- `Did baseline inheritance really resume after we ended the exception?`
- `What shadowing override is still blocking rejoin?`

## Anti-goals

- do not let durable exceptions live forever as remembered folklore
- do not treat removal of one override as proof that all shadowing overrides are gone
- do not let repeated exception patterns avoid baseline review forever
- do not close an exception without saying whether future inheritance is now active again
