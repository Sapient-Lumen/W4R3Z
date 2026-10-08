# Outside-action follow-through coverage and fix-claim boundary interface spec

## Purpose

The archive already had intervention attempts, outside-blocker handoffs, return-proof rows, post-action recompute, and frozen guidance basis.
What it still lacked was one stronger contract for a common and expensive lie:

> one outside step was requested or even observed, therefore the product starts speaking as if the whole blocker is fixed.

That is too coarse.
A firewall change can be requested without being applied.
A service restart can be observed without restoring listener reachability.
A browser trust exception can be accepted while the underlying endpoint identity has already changed.
A shell-side fix can touch one source object while other required follow-through remains.

## Core decision

Any repair or unblock path that leaves the current product surface, or that can stop at a partial outside step, should create one first-class **follow-through coverage** object.

That object must keep five truths separate:

1. **what was asked for**
2. **what source-side execution was actually observed**
3. **what product-side effect was actually re-observed**
4. **what named follow-through remains**
5. **what current fix claim is now honest**

The product must not let `asked`, `started`, `executed`, `effect observed`, and `claim-ready` collapse into one green state.

## Why this matters

Real operator detours repeatedly create partial wins that are easy to overstate:

- a host service restarted, but the control listener still is not reachable from this seat
- a trust dialog was accepted, but the certificate or endpoint basis has changed since the handoff began
- a permission was granted, but the blocked bind or subject still has not been reread successfully
- a support or admin request was answered, but the product still has not seen local confirming evidence
- one sub-step was machine-fixed, but later cleanup, policy review, or verification remains manual

AnonSync already had the pieces to open the handoff and later recompute.
What it lacked was one explicit bridge that keeps partial completion honest in between.

## Public objects

### Follow-through case

A durable object describing one blocked or recently repaired lane whose resolution may require several distinct outside or cross-surface steps.

Suggested fields:

- `followthrough_case_id`
- `source_object_ref`
- `related_handoff_ref` nullable
- `promised_outcome_summary`
- `coverage_state` (`requested-only`, `in-flight`, `source-step-observed`, `effect-observed-partial`, `claim-ready`, `contradicted`, `superseded`, `abandoned`)
- `current_fix_claim` (`no-fix-claim`, `request-issued`, `source-change-observed`, `partial-effect-observed`, `blocker-cleared-for-now`, `unknown`)
- `next_honest_action`
- `created_at`

### Requested step row

One step that was asked for or declared necessary.

Suggested fields:

- `requested_step_row_id`
- `case_ref`
- `step_kind` (`change-setting`, `restart-runtime`, `approve-trust`, `grant-permission`, `run-command`, `collect-artifact`, `ask-admin`, `review-followup`, `cleanup-residue`, `other`)
- `owner_lane` (`product`, `browser`, `os-dialog`, `shell`, `service-manager`, `admin-console`, `vendor`, `other`)
- `required_for_claim` (`yes`, `optional`, `followup-only`)
- `state` (`declared`, `requested`, `started`, `skipped`, `not-needed`, `unknown`)
- `summary`

### Source-execution row

One observed fact that a source-side step actually ran or changed.

Suggested fields:

- `source_execution_row_id`
- `case_ref`
- `step_ref` nullable
- `evidence_kind` (`receipt-imported`, `runtime-state-change`, `config-reread`, `browser-observed`, `operator-attested`, `external-response-linked`, `unknown`)
- `state` (`present`, `missing`, `stale`, `contradictory`, `weak-only`)
- `summary`
- `observed_at` nullable

### Effect-observation row

One product-side reread proving whether the source-side step actually changed the blocked product truth.

Suggested fields:

- `effect_observation_row_id`
- `case_ref`
- `effect_kind` (`listener-reachable`, `bind-now-valid`, `route-restored`, `trust-now-current`, `policy-now-satisfied`, `capture-now-stopped`, `residue-cleared`, `other`)
- `state` (`observed`, `not-observed`, `partial`, `stale`, `contradictory`, `not-yet-reread`)
- `summary`
- `observed_at` nullable

### Fix-claim boundary row

A compact statement of what the product may honestly say now.

Suggested fields:

- `fix_claim_boundary_row_id`
- `case_ref`
- `claim_strength` (`none`, `request-only`, `source-only`, `partial-effect`, `current-blocker-cleared`, `unknown`)
- `remaining_required_steps[]`
- `remaining_review_required` (`yes`, `no`, `unknown`)
- `warnings[]`

### Follow-through receipt

A durable record that the coverage state changed.

Suggested fields:

- `followthrough_receipt_id`
- `case_ref`
- `transition` (`open`, `request-recorded`, `source-step-observed`, `effect-reread`, `claim-updated`, `supersede`, `abandon`)
- `recorded_at`

## Fixed inspection order

Every follow-through coverage surface should preserve this order:

1. **Promised outcome and current coverage state**
2. **Requested steps**
3. **Observed source-side execution**
4. **Observed product-side effect**
5. **Current fix-claim boundary**
6. **What still remains**

### 1) Promised outcome and current coverage state

This section should say:

- what the operator was trying to clear
- what coverage state the case is in now
- whether the current story is `request-only`, `source change observed`, `partial effect`, or `claim-ready`

### 2) Requested steps

This section should show the full declared ladder.
Examples:

- `approve current browser trust exception`
- `restart user-session daemon`
- `return to local web and refresh listener probe`
- `review cleanup residue after capture stop`

### 3) Observed source-side execution

This section should answer:

- what actually ran, changed, or was confirmed outside the current surface
- which evidence is strong versus weak
- whether the source-side observation is already stale or contradictory

### 4) Observed product-side effect

This section should answer the harder question:

- what changed in product truth after reread
- whether the original blocker actually moved
- whether only one effect was observed while other required effects remain missing

### 5) Current fix-claim boundary

This section is mandatory.
Examples:

- `request issued only; no fix claim yet`
- `daemon restart observed; listener recovery not yet observed`
- `permission grant observed; one blocked subject still unreadable`
- `current blocker cleared for this seat; residue review still remains`

### 6) What still remains

This section should name the next honest move.
Examples:

- `refresh bridge and keep case open`
- `open post-action recompute`
- `review remaining cleanup step`
- `mark contradictory and reopen stronger escalation`

## Public rules

### Rule 1 — requested is not executed

A declared or issued outside step must not count as observed execution.

### Rule 2 — executed is not effect-observed

A service restart, setting edit, or browser acceptance must not by itself count as blocker resolution.

### Rule 3 — one observed effect may still be only partial coverage

If the promised outcome named several required consequences, the product must preserve partial coverage honestly.

### Rule 4 — source-only fixes must stay source-only

A change observed in one source surface must not silently upgrade to `fixed` while product reread still fails or has not happened.

### Rule 5 — weaker evidence may support continuity, not stronger claim

Operator attestation or third-party reply may keep the case legible, but stronger claims should prefer local reread, linked receipts, or direct product observation.

### Rule 6 — follow-through coverage should survive recompute and supersession

If a later recompute or later handoff supersedes the case, the older coverage receipts should remain inspectable rather than being rewritten into the newer story.

## Dense row contract

A dense follow-through row should preserve these labels in this order:

- `Outcome`
- `Coverage`
- `Requested`
- `Observed source`
- `Observed effect`
- `Claim boundary`
- `Next`

## Relationship to nearby specs

This spec sharpens the seam between:

- `138-intervention-attempt-receipt-and-post-action-recompute-interface-spec.md`
- `232-diagnostic-export-log-redaction-and-self-serve-support-boundary-interface-spec.md`
- `245-external-blocker-handoff-followup-and-return-proof-interface-spec.md`
- `249-external-guidance-source-boundary-fetch-snapshot-and-frozen-review-basis-interface-spec.md`

Those documents already cover chosen actions, outward handoffs, packet/basis discipline, and recompute.
This one prevents partial outside progress from being laundered into a whole-fix claim in the middle.

## Acceptance test

This surface is good enough when a cautious operator can answer all of the following from one case:

- what outcome was promised
- which steps were merely requested versus actually observed
- what product-side effect has or has not been re-observed
- whether the current story is request-only, source-only, partial-effect, or claim-ready
- what named follow-through still remains before the product may speak more strongly
