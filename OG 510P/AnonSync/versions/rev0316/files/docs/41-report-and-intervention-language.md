## Revision addendum — report family after rev0275: re-entry reports for stale-return honesty

The report grammar now needs one more family.

### 27) Re-entry-case report

Answers what exactly came back after dormancy and how trustworthy that return currently is.
It should always say:

- dormancy interval
- return class
- roster visibility state
- chronology confidence
- source-reality verdict

### 28) Dormancy-timeline report

Answers what happened between the last good witness and the current return.
It should always say:

- last good witness
- dormancy anchors
- hide / expiry / warning events
- return events
- current interpretation

### 29) Stale-return review report

Answers what makes the return risky or safe.
It should always say:

- dominant chronology risk
- source/announcement reality
- safest next action
- strongest safe sentence
- stronger forbidden sentence

### 30) Re-entry receipt

Answers what safe return judgment was issued and what would reopen it.
It should always say:

- return class
- chronology confidence
- safe current sentence
- stronger rejected sentence
- reopen conditions

## Revision addendum — report family after rev0274: next-opportunity reports for honest delay language

The report grammar now needs one more family.

### 23) Next-observation-opportunity report

Answers when a seat is next honestly expected to notice, publish, or fetch a change.
It should always say:

- duty class
- next opportunity type
- unmet prerequisites
- due-time basis
- lateness gate

### 24) Late-claim review report

Answers whether the relevant opportunity actually passed and what delay sentence is safe.
It should always say:

- claim under test
- opportunity-passed proof class
- surviving alternative explanations
- strongest safe sentence
- stronger forbidden sentence

### 25) Duty-cycle timeline report

Answers when the seat was actually duty-capable across the disputed interval.
It should always say:

- covered interval
- duty-state segments
- real opportunity windows
- gate changes
- current claim status

### 26) Observation-opportunity receipt

Answers what due judgment was issued and what would reopen it.
It should always say:

- duty basis
- due verdict
- strongest allowed sentence
- stronger rejected sentence
- reopen conditions

## Revision addendum — report family after rev0269: measurement reports for capacity-isolation truth

The report grammar now needs one more family.

### 19) Measurement-plan report

Answers what performance question is being isolated and under what comparison contract.
It should always say:

- question class
- baseline Sync observation
- participant pair and direction scope
- required quiescence level
- strongest allowed later conclusion

### 20) Sidecar-benchmark-run report

Answers what benchmark rows actually ran and whether the experiment is trustworthy.
It should always say:

- participant roles
- quiescence verdict
- row coverage
- strongest valid output summary
- anomaly / invalidity notes

### 21) Performance-hypothesis review report

Answers which intervention is actually justified after the experiment.
It should always say:

- dominant bottleneck hypothesis
- evidence basis
- best supported intervention
- main cost class
- revert trigger

### 22) Measurement receipt

Answers what the experiment proved, what it did not prove, and what should happen next.
It should always say:

- baseline-versus-benchmark summary
- supported bottleneck statement
- approved next safe step
- stronger forbidden claim
- reopen boundary

## Revision addendum — report family after rev0266: recipient-ask reports for follow-up truth

The report grammar now needs one more family.

### 15) Recipient-ask report

Answers what a later requester is actually asking for and how that ask binds to the case.
It should always say:

- requester lane and audience class
- ask clauses
- required vs optional posture
- binding token or reply-chain requirement
- current satisfiability posture

### 16) Ask-fulfillment review report

Answers whether the prepared return satisfies the ask without oversharing.
It should always say:

- clause coverage
- missing members
- extra-disclosure warnings
- strongest supported satisfaction sentence
- smallest honest next move

### 17) Return-lane review report

Answers whether the chosen lane can actually carry the reviewed packet.
It should always say:

- lane type
- binding token used
- size/format fit
- current-surface feasibility
- required pre-step if blocked

### 18) Ask-fulfillment receipt

Answers what ask version was actually answered and what remains open afterward.
It should always say:

- ask version
- returned members
- binding proof
- satisfaction class
- reopen boundary

## Revision addendum — report family after rev0265: companion-case reports for split-audience truth

The report grammar now needs one more family.

### 11) Companion-case report

Answers whether one incident currently has a public-safe artifact, a private artifact, or both, and how they relate.
It should always say:

- public artifact state
- private artifact state
- audience class for each side
- withheld-detail boundary
- linkage basis and confidence
- next continuation lane

### 12) Public-summary review report

Answers whether a case statement is safe and still useful for a broader audience.
It should always say:

- public-safe claim
- redaction decisions
- utility verdict after redaction
- stronger forbidden sentence
- whether a private companion packet is required

### 13) Private-companion linkage report

Answers whether a private packet is durably attached to the right companion case.
It should always say:

- referenced companion artifact
- packet purpose
- private-only scope
- continuity verdict
- future continuation lane

### 14) Companion-case receipt

Answers what split-audience artifacts actually exist after publication/send.
It should always say:

- posted/drafted/withheld public state
- sent/saved/withheld private state
- linkage proof
- withheld-detail record
- continuation or reopen boundary

# Report and intervention language

## Purpose

The archive already had proof-bearing objects such as `preflight`, `comparison`, `preservation`, `convergence`, `exposure`, and `plan-drift`.
This revision adds settlement-barrier and settlement-receipt objects above convergence so action-time readiness is inspectable and auditable too.
What it still lacked was a stronger answer to a practical operator question:

> when a risky, degraded, or blocked condition appears, what should the warning actually look like, and how should the next action be presented?

This document answers that question.
It exists so AnonSync does not recreate the same failure mode visible in other sync products, where the real state is spread across badges, hidden files, support articles, stale warnings, and platform-specific rescue steps.

## Core rule

Every actionable finding should collapse into a report with one shared operator grammar.

That means:

- a report may summarize many low-level facts
- it may not hide the scope of the decision
- it may recommend a next action
- it may not smuggle the action in as an automatic side effect
- it may be rendered differently by CLI, TUI, GUI, or local web workbench
- it may not mean something different on those surfaces

## What a report is

A report is a durable or refreshable answer to one concrete operator question.

Examples:

- `Can I link this device safely?`
- `Is this share settled enough for cutover?`
- `What survives if I delete this file from the share?`
- `Can I adopt this visible share into this non-empty path?`
- `What exposure changes if I enable this lease?`
- `Why did this plan stop being safe to apply?`

A report should be referenceable by stable ID and should remain intelligible when viewed later in audit, event, plan, or review contexts.

## Common report envelope

Every report type should expose at least:

- `report_id`
- `report_type`
- `subject_ref`
- `subject_version_ref` or equivalent freshness anchor
- `generated_at`
- `freshness_state` (`fresh`, `aging`, `stale`, `drifted`, `superseded`)
- `severity` (`info`, `watch`, `guarded`, `high-risk`, `blocked`)
- `intent` where applicable (`status`, `cutover`, `delete`, `adopt`, `replace`, `publish`, `grant`)
- `scope_summary`
- `current_answer`
- `recommended_next_action` nullable
- `dangerous_actions[]`
- `unresolved_after_apply[]`
- `evidence_refs[]`

The envelope matters because the operator should not have to learn a different visual grammar for every report family.

## Minimum body structure

A rendered report should always answer six things in the same order:

1. **What is true right now?**
2. **What scope does that truth touch?**
3. **Why is the system saying this?**
4. **What is the safest next action?**
5. **What still remains unresolved afterward?**
6. **How fresh is this answer?**

In richer surfaces this may be presented as cards or drawers.
In textual surfaces it may be rendered as a compact structured block.
The order should stay stable.

## Severity language

Severity should mean operator urgency, not implementation drama.

- `info` — useful fact, no intervention implied
- `watch` — something merits awareness or later review
- `guarded` — action is possible, but should normally be previewed or confirmed
- `high-risk` — action is possible only with strong proof and explicit acknowledgement
- `blocked` — requested action should not proceed under current facts

This language should be shared by CLI, workbench cards, API payloads, and audit rendering.

## Freshness language

Freshness should answer whether the report is still decision-grade.

- `fresh` — safe to rely on for the intended action
- `aging` — still likely usable, but close to review threshold
- `stale` — should be refreshed before use
- `drifted` — referenced objects changed in a meaningful way
- `superseded` — a newer report or plan already replaced this one

A stale report may still be educational.
It should not silently remain apply-grade.

## Required report families

### 1) Preflight report

Answers whether a proposed link, grant, adopt, replace, or claim can be performed safely.
It should always say:

- blockers
- warnings
- downgrade consequences
- authority changes
- capability mismatches
- whether a plan is required before apply

### 2) Comparison report

Answers whether a bind, adopt, or relocate target is empty, already bound, harmlessly matching, or collision-prone.
It should always say:

- identical content count
- local-only count
- remote-only count
- collision classes
- suggested policy or manual follow-up

### 3) Filesystem compatibility report

Answers whether a target path can preserve the semantics the share expects.
It should always say:

- support tier
- blocking mismatches
- warning mismatches
- likely downgrade classes
- which future action may legally reference this report

### 4) Preservation report

Answers what rollback or survival posture remains after a destructive action.
It should always say:

- remaining plaintext coverage
- encrypted-only coverage
- history/version coverage
- weakest surviving recovery path
- whether the action should be allowed, guarded, or blocked

### 5) Convergence report

Answers whether a share is merely quiet or actually settled for a named intent.
It should always say:

- intent
- current confidence
- missing or unreachable sources
- watcher / scan health
- background work still relevant
- explicit blocker reasons for settlement
- evidence age, quiet-window progress, and whether the answer can still be reused safely

### 5b) Settlement barrier

Answers whether the chosen readiness rule is currently satisfied, waiting, stale, or blocked for one intended action.
It should always say:

- the policy being applied
- current barrier state
- failed clauses, if any
- required versus present sources
- expiry or stale deadline
- safest next action

### 6) Exposure report

Answers what infrastructure or peers can currently learn reachability, and why.
It should always say:

- durable baseline policy
- active override leases
- publication posture
- dialing posture
- winning route
- rejected route classes and why they lost

### 7) Authority-delta report

Answers what trust, delegation, stewardship, or successor scope would change.
It should always say:

- subject gaining authority
- authority being removed or narrowed
- future approvals affected
- delegation bounds changed
- follow-on review that remains necessary

### 8) Plan-drift report

Answers why a previously reviewed plan is no longer safe to apply as originally previewed.
It should always say:

- what changed
- whether the change widened, narrowed, or invalidated scope
- whether the plan can be refreshed automatically
- whether operator review must restart

### 9) State-transition report

Answers whether a state root attach/move/import/profile-switch or identity-root replacement is actually touching the intended control universe.
It should always say:

- source and target state roots
- source and target service profiles
- identity continuity expectations
- quiesce / restart boundary
- rollback credibility
- post-transition verification that will still be required

### 10) Activity-effect report

Answers what a pause/drain/throttle/freeze or recurring schedule actually changes right now.
It should always say:

- target subject and current scope
- phase matrix (`scan-index`, `ingress`, `egress`, `delete-propagation`, `announce`, `dial`)
- which phases differ from baseline
- active override and schedule refs
- route-class scope for caps or suppression
- expiry or next activation time

### 10b) Override-effect report

Answers what a temporary exception changes relative to durable baseline, and what will happen when it ends.
It should always say:

- override family and target
- baseline posture
- active temporary effect
- expiry or exhaustion condition
- overlapping active leases if relevant
- safest next action (`renew`, `cancel`, `accept-no-expiry`, `convert-to-durable-policy`)

### 11) Projection-effect report

Answers what a projection or placeholder-policy change means for a concrete path or selector.
It should always say:

- share namespace before/after
- peer-announcement posture before/after
- local-view posture before/after on affected mounts
- local-byte consequences if relevant
- indexed / materialized history already in play
- whether follow-up is `none`, `review`, `safe-evict`, `settlement-barrier`, or `blocked`
- whether an apply will emit a projection receipt

### 12) Rollback/conflict report

Answers what prior state exists for a path and how a restore or conflict-resolution action would treat it.
It should always say:

- candidate provenance (peer, cause, capture time, confidence)
- retention horizon and any history gaps
- conflict class and candidate winner/loser set where relevant
- whether the next safe move is local-only, device-local, or share-plan scope
- whether settlement or preservation proof is still required before apply
- whether an apply will emit a rollback receipt

### 13) Space-pressure report

Answers why a device, state root, share, or mount is under storage pressure and what reclaim actions are safe.
It should always say:

- subject scope and active budget policy
- dominant byte classes and recent growth if known
- whether the current state is watch, guarded, high, or blocked
- which safe-first reclaim actions affect local bytes only
- whether any candidate action would weaken retention, rollback, or preservation posture
- whether an apply will emit a reclaim receipt

- policy origin / precedence / surface-gap

### 12b) Exit/residue report

Answers what an exit action would stop, what it intentionally preserves, and what residue still remains after apply.
It should always say:

- subject being exited and exit-intent class
- authority, visibility, byte-state, and continuity deltas
- what stays intentionally versus what could not yet be cleared
- which residue findings are time-bound, peer-bound, or operator-clearable
- whether a later receipt proves full clearance or only partial exit with acknowledged residue

## Intervention grammar

Reports should not only explain.
They should also structure the next safe move.

Each report may offer up to four intervention slots:

1. **Explain** — open or expand the report without mutation
2. **Refresh** — regenerate findings against current state
3. **Prepare** — create a plan, claim, or draft mutation from the report
4. **Apply** — perform the reviewed mutation if still valid

Dangerous actions should never appear before their associated `Explain` or `Prepare` step is legible.

## Action hierarchy rules

A rendered report should normally expose:

- one primary safe next step
- optional secondary expert steps
- separated dangerous steps

Examples:

- blocked cutover: primary is `Explain blockers`, not `Force sync`
- risky delete: primary is `Preview preservation`, not `Delete from share`
- path collision: primary is `Compare target`, not `Bind anyway`
- drifted replacement plan: primary is `Refresh report`, not `Apply old plan`

## Review-lane integration

The workbench home surface should treat review cards as report-backed summaries.
A review card may compress a report, but it must still show:

- report type
- severity
- freshness
- current answer
- next-safe action

Opening the card should land on the full report, not on an unrelated generic object page that forces the operator to reconstruct the actual issue.


## Attention and delivery integration

Reports remain the semantic source of truth.
Attention events are a durable projection over reports and review items that make lane placement, delivery-channel outcomes, and acknowledgement posture inspectable.

That means:

- a report may back zero, one, or many attention events over time
- attention policy decides lane and delivery, but does not rewrite report meaning
- acknowledgements and snoozes should emit attention receipts that explicitly say whether only presentation changed
- delivery failure should become visible attention state instead of disappearing into daemon logs or browser consoles

## Diagnostics and evidence integration

Reports remain the semantic source of truth for why an incident exists.
Diagnostic incidents and evidence bundles should therefore point back to reports instead of creating a second hidden troubleshooting world.

The report language should support at least these additional families:

- `diagnostic-scope` — what would be collected and why
- `redaction-gap` — what still requires review or blocking before seal/export
- `event-gap` — when event continuity or log coverage is too thin for a strong diagnostic claim

Those reports should make clear:

- whether evidence collection is broad enough for the current question
- whether sensitive material is still present and under what policy
- whether a later bundle export would be blocked, guarded, or ready to seal

## Batch rules for reports

Batch operations are allowed only when the reports agree enough that the operator is not being tricked by compression.

Safe examples:

- refresh several stale convergence reports
- snooze several low-risk watch-level findings
- dismiss several superseded informational reports

Guarded examples:

- adopt several incoming shares only if all comparison and preflight reports are equivalent in class and none are blocked

Disallowed examples:

- mix preservation-guarded deletes with simple informational dismissals under one apply
- mix successor continuity changes with unrelated path-binding repairs

## CLI rendering contract

Textual surfaces should be able to render the same operator truth without GUI-only semantics.

A minimal CLI shape:

```text
anonsync report show rpt_01J...
```

Should be able to print, in order:

- subject and intent
- current answer
- severity and freshness
- scope summary
- top findings
- recommended next action
- unresolved aftermath
- related proof / plan / event references

Other useful commands:

```text
anonsync report refresh rpt_01J...
anonsync report explain rpt_01J...
anonsync report list --type convergence --severity guarded
```

These commands do not create a new model.
They are shared read/projection surfaces over existing report-bearing objects.

## Workbench rendering contract

The workbench should have a dedicated report shelf or filterable report board, even if many reports are usually reached through Home, share pages, or peer pages.

That shelf should support:

- filter by type
- filter by severity
- filter by freshness
- filter by subject kind
- show superseded vs active
- jump from report to underlying object
- jump from object to most relevant active report

## Design tests

The report language is probably not ready if any of the following remains true:

- a user has to read a support article to know whether a warning is still safe to ignore
- two surfaces disagree on whether an action is guarded or blocked
- a stale report can still be applied without an explicit freshness check
- a dangerous action is easier to click than its proof is to inspect
- a review card cannot tell the operator what remains unresolved afterward
- the CLI cannot explain a condition that the GUI can

## Outcome

A mature AnonSync interface should let an operator move from `problem noticed` to `proof inspected` to `safe next step chosen` without ever leaving the shared public model.
That is what this document is trying to lock in.
