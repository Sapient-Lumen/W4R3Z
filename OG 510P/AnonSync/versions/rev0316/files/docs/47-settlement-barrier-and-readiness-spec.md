# Settlement barrier and readiness spec

## Purpose

The archive already had convergence reports and a few flows proving that ordinary `idle` state is not enough for cutover, backup, relocate, restore, or maintenance decisions.
What it still lacked was a sharper public contract for another operator question:

> what exact evidence lets the product say “settled enough for *this* action”, how long does that answer remain trustworthy, and what receipt proves the action was taken against that evidence rather than against wishful status? 

Resilio's current docs are useful precisely because they show why this cannot stay fuzzy.
They still tell operators to combine `X of Y peers`, status warnings, sync history, per-peer queues, time-skew warnings, watcher-exhaustion warnings, and “ghost file” conditions by hand. Some warnings can be hidden or worked around, some imply future recovery when sources return, and some degrade change detection without making the share look obviously busy.
That is practical troubleshooting, but it is not a settlement contract.

This document turns that lesson into an AnonSync requirement:

- target intent
- witness or source requirements
- freshness budget for evidence
- quiet-window expectations
- degraded detection rules
- missing-source tolerance
- proof of the answer used at apply time

must be inspectable through one shared readiness grammar.

## Core stance

1. **Convergence is evidence, not the final verdict.**  
   A convergence report is one input. The product still needs a public object that says whether that evidence is good enough for a named action.

2. **Intent changes the bar.**  
   `status`, `backup`, `cutover`, `restore`, `relocate`, and `maintenance-drain` should not silently share the same readiness threshold.

3. **A readiness answer expires.**  
   “Safe enough” is only true for some evidence age and some quiet window. Old proof must go stale visibly.

4. **Witness sets must be explicit.**  
   The product should never leave operators guessing whether “all reachable peers”, “all writable peers”, “one steward plus one replica”, or “this exact required set” was the settlement standard.

5. **Apply should cite the proof it relied on.**  
   High-signal actions should emit receipts that name the barrier or readiness answer used, not merely that the action succeeded.

6. **Readiness is not only a wait loop.**  
   A caller should be able to preview the bar, see which clause failed, and decide whether to narrow scope or relax policy deliberately.

## Relationship to convergence

A good mental model is:

- the **convergence report** answers what the daemon currently knows about transfer completion, source reachability, watcher/scan health, clock confidence, and background work
- the **settlement policy** answers what level of evidence is required for a named intent
- the **settlement barrier** combines those two for one target and waits, refreshes, or blocks accordingly
- the **settlement receipt** proves which answer was accepted when a risky action crossed the line

That keeps “are we syncing?”, “are we settled enough?”, and “what proof backed the action?” from collapsing into one vague status line.

## Public objects

### Settlement policy

A durable policy object describing what evidence is required before an operation may claim the target is settled enough.

Fields:

- `settlement_policy_id`
- `name`
- `intent` (`status`, `cutover`, `backup`, `relocate`, `restore`, `maintenance-drain`, `custom`)
- `required_confidence` (`high`, `medium`, `low`)
- `required_state` (`converged`, `degraded-converged`)
- `required_source_mode` (`all-reachable`, `all-required`, `all-writable`, `witness-set`, `minimum-count`)
- `required_source_refs[]` nullable
- `minimum_source_count` nullable
- `require_continuous_detection` boolean
- `allow_periodic_rescan` boolean
- `allow_background_work` (`none`, `safe-read-only`, `non-mutating`, `any`)
- `allow_clock_warnings` boolean
- `max_report_age`
- `quiet_window`
- `stale_after`
- `created_by`
- `created_at`
- `provenance_ref` nullable

Notes:

- `quiet_window` means “how long must the report stay good without contradiction before we claim readiness for this policy?”
- `stale_after` exists so a once-valid readiness answer does not remain ambient authority forever
- `allow_background_work` exists because some actions tolerate non-mutating hashing while others should not

### Settlement barrier

A named, refreshable readiness gate for one target and one intended action.

Fields:

- `settlement_barrier_id`
- `target_type` (`share`, `mount`, `device`, `system`, `plan`)
- `target_id`
- `intent` (`status`, `cutover`, `backup`, `relocate`, `restore`, `maintenance-drain`, `custom`)
- `policy_ref`
- `current_convergence_report_ref`
- `current_state` (`pending`, `satisfied`, `degraded-satisfied`, `blocked`, `stale`, `expired`, `canceled`)
- `evidence_age`
- `quiet_window_elapsed`
- `required_sources[]`
- `present_sources[]`
- `missing_sources[]`
- `failed_clauses[]`
- `next_safe_actions[]`
- `created_by`
- `created_at`
- `last_evaluated_at`
- `satisfied_at` nullable
- `expires_at` nullable

Rules:

- `degraded-satisfied` is only valid if the selected policy explicitly allows degraded convergence
- `failed_clauses[]` should be stable enough for CLI, API, and workbench use without free-text scraping
- barriers should be refreshable without mutating the underlying target

### Settlement receipt

A durable receipt proving that an action crossed a named readiness bar using specific evidence.

Fields:

- `settlement_receipt_id`
- `subject_type` (`plan`, `cutover`, `backup`, `restore`, `relocate`, `delete`, `maintenance-freeze`, `custom`)
- `subject_id`
- `target_refs[]`
- `intent`
- `policy_ref`
- `barrier_ref` nullable
- `accepted_convergence_report_ref`
- `accepted_state` (`satisfied`, `degraded-satisfied`)
- `accepted_confidence`
- `accepted_sources[]`
- `accepted_missing_sources[]`
- `accepted_detection_mode`
- `accepted_background_work`
- `accepted_clock_health`
- `accepted_at`
- `expires_at` nullable
- `operator_ref`
- `notes` nullable
- `provenance_ref` nullable

Rules:

- receipts should be emitted automatically for high-signal plan apply, cutover, restore-to-share, destructive share action, and profile/root transitions that required settlement
- a later audit should be able to show not only *that* an action happened, but whether it happened under strict or relaxed readiness criteria

## Clause vocabulary

`failed_clauses[]` should come from a stable vocabulary such as:

- `SOURCE_MISSING_REQUIRED`
- `SOURCE_COUNT_BELOW_MINIMUM`
- `REPORT_TOO_OLD`
- `QUIET_WINDOW_NOT_MET`
- `WATCHER_DEGRADED_NOT_ALLOWED`
- `PERIODIC_RESCAN_NOT_ALLOWED`
- `CLOCK_WARNING_NOT_ALLOWED`
- `CLOCK_BLOCKED`
- `BACKGROUND_WORK_NOT_ALLOWED`
- `CONFIDENCE_BELOW_REQUIRED`
- `STATE_BELOW_REQUIRED`
- `MANUAL_REVIEW_REQUIRED`

The product can still render helpful prose, but the stable clause codes are the contract.

## Readiness classes

The workbench and CLI should be able to summarize a barrier in compact form:

- `Ready` — policy satisfied with non-stale evidence
- `Ready (guarded)` — policy satisfied only because degraded convergence is explicitly allowed
- `Waiting` — no fatal contradiction yet, but quiet window, source arrival, or refresh is still pending
- `Blocked` — at least one clause currently fails and operator action is required
- `Stale` — previously satisfied answer is too old to reuse safely

These are intentionally not raw daemon internals.
They are operator-facing classes that summarize the barrier honestly.

## Rendering rules

### Good examples

- `Cutover readiness: Ready after 2m quiet window. All writable sources present. Evidence age 11s.`
- `Backup readiness: Ready (guarded). Missing cold replica is allowed by policy; continuous detection still healthy.`
- `Restore readiness: Blocked. Clock warning not allowed and remote steward unreachable.`

### Bad examples

- `Settled`
- `Looks good`
- `Safe`

Those are too context-free.

## CLI surface

The archive already has `anonsync converge ...`.
This document adds a settlement/readiness layer above it.

### Policy management

```text
anonsync settle policy list
anonsync settle policy show cutover-strict
anonsync settle policy create   --name cutover-strict   --intent cutover   --confidence high   --required-sources all-writable   --require-continuous-detection   --max-report-age 30s   --quiet-window 2m
```

### Barrier creation and inspection

```text
anonsync settle barrier create --share workdocs --intent cutover --policy cutover-strict
anonsync settle barrier show stb_01J...
anonsync settle barrier wait stb_01J... --timeout 10m
anonsync settle barrier refresh stb_01J...
anonsync settle barrier cancel stb_01J...
```

Output should say at least:

- the policy in force
- the current convergence report being evaluated
- which clauses currently fail or remain pending
- evidence age and quiet-window progress
- whether the answer can be reused for apply right now

### Receipt inspection

```text
anonsync settle receipt list --subject cutover
anonsync settle receipt show str_01J...
```

### Intent-aware shortcuts

High-signal commands may inline readiness without inventing a second hidden heuristic.
Examples:

```text
anonsync cutover plan --share workdocs --require-settlement cutover-strict
anonsync mount relocate --share workdocs --require-settlement relocate-safe --plan
anonsync restore apply --share workdocs --require-settlement restore-safe --plan
```

## API expectations

The daemon API should expose at least:

```text
GET    /v1/settlement/policies
POST   /v1/settlement/policies
GET    /v1/settlement/policies/{settlement_policy_id}
GET    /v1/settlement/barriers
POST   /v1/settlement/barriers
GET    /v1/settlement/barriers/{settlement_barrier_id}
POST   /v1/settlement/barriers/{settlement_barrier_id}/refresh
POST   /v1/settlement/barriers/{settlement_barrier_id}/wait
POST   /v1/settlement/barriers/{settlement_barrier_id}/cancel
GET    /v1/settlement/receipts
GET    /v1/settlement/receipts/{settlement_receipt_id}
```

These resources should expose both structured clause results and human-readable summaries.
They should also let a caller ask the same question two ways:

- give me the latest barrier state
- tell me why the current state is not sufficient for the chosen policy

## Workbench expectations

### Home lane behavior

Home should be able to surface:

- `Cutover blocked by stale settlement evidence`
- `Backup barrier waiting on quiet window`
- `Maintenance freeze ready under guarded policy`

### Share page

The settlement card on a share page should show:

- the currently selected readiness intent
- the active or most recent barrier
- whether any later edit or transfer invalidated the answer
- quick links to barrier detail and settlement receipts

### Plan/apply drawer

If a plan depends on settlement, the apply drawer should show:

- the required policy
- the accepted barrier state
- expiry or stale deadline
- whether apply will refresh proof first or use the existing answer

## Interaction with other specs

- `41-report-and-intervention-language.md` remains the common report envelope for the underlying convergence and health findings
- `45-activity-phase-and-scheduling-spec.md` can influence readiness through phase states such as `scan-index` degraded or delete propagation intentionally suspended
- `43-mount-binding-repair-and-preservation-spec.md` and `44-file-intent-deviation-and-restore-spec.md` may require settlement before risky apply
- `46-namespace-projection-and-placeholder-spec.md` may require settlement barriers before claiming late-tightening effects are complete

## Non-goals

This document does **not** claim that settlement is mathematically absolute.
It claims something narrower and more useful:

- the daemon should state what evidence it has
- policy should state what evidence is required
- barriers should state whether that requirement is currently met
- receipts should prove what standard was accepted when high-signal actions happened

That is enough to replace peer-count folklore with a supported product contract.
