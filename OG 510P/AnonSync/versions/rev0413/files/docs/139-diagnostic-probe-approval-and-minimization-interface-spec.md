# Diagnostic probe approval, activation, and minimization interface spec

## Purpose

The archive already has:

- convergence windows
- wait-vs-intervene decision sheets
- convergence evidence bundles
- bounded intervention attempts with after-action recompute

What still remained under-specified was the boundary between `ordinary evidence refresh` and `heavier diagnostic capture`.
Sometimes the product genuinely needs more than a status refresh:

- a timed debug-log window
- a transfer sample
- a route snapshot
- a watcher/scan-health recompute
- crash-artifact capture
- an external path-measurement step

That is exactly where products drift back into support folklore.
Someone flips a persistent debug toggle, restarts the runtime, collects too much, forgets when it should stop, and later cannot say whether the extra capture was justified, how long it stayed on, or what residue remained after the probe ended.

This document defines the interface contract for one first-class **diagnostic probe approval** surface, one explicit **activation/deactivation receipt** boundary, and one **minimization plan**.

## Core rule

Any diagnostic action that meaningfully increases collection depth, retention scope, performance cost, or disclosure risk must be reviewed as a named probe plan before it starts.

The plan must state:

1. which uncertainty justifies the probe
2. which evidence classes the probe will collect
3. which classes are explicitly excluded
4. how the probe is activated
5. how long the probe may run
6. how the probe stops or is turned back down
7. what local cost or privacy cost it introduces
8. whether the result stays local-only or becomes exportable material

The product must not hide this behind one vague toggle like `Enable debug logging`.

## Why this needs its own spec

Current Resilio material is useful but still teaches the operator through procedural support steps:

- enable debug logging in settings or through hidden alternate gestures
- restart to ensure the deeper collection mode actually took effect
- reproduce the issue and let logs run for a while
- maybe enlarge log size first
- maybe gather crash material
- maybe run a separate iperf3 test with Sync shut down
- maybe send the output elsewhere afterward

That is valid support guidance.
It is not the interaction contract AnonSync wants.
AnonSync should force each deeper probe to declare its trigger, activation path, cost, scope, stop condition, lingering residue, and disclosure posture before capture starts.

## Public objects

### Diagnostic probe plan

A durable plan object for one proposed diagnostic capture step.

Suggested fields:

- `diagnostic_probe_plan_id`
- `diagnostic_incident_ref`
- `convergence_evidence_bundle_ref` nullable
- `triggering_uncertainty`
- `probe_kind` (`debug-log-window`, `transfer-sample`, `route-snapshot`, `watcher-health-refresh`, `resource-snapshot`, `crash-artifact-capture`, `external-path-measurement`)
- `intrusiveness` (`low`, `moderate`, `high`, `external-tooling`)
- `activation_kind` (`in-product-switch`, `runtime-restart-required`, `external-binary`, `os-surface`, `mixed`)
- `expected_decision_value`
- `approval_state` (`draft`, `reviewed`, `approved`, `running`, `finished`, `expired`, `canceled`)
- `local_only_default` bool
- `auto_stop_at`
- `created_at`

### Probe evidence class row

One evidence class that the probe would include or exclude.

Suggested fields:

- `probe_evidence_class_row_id`
- `class_kind` (`recent-logs`, `trace-logs`, `transfer-samples`, `route-state`, `resource-health`, `watcher-health`, `crash-artifacts`, `external-tool-output`, `config-summary`)
- `inclusion_state` (`included`, `excluded`, `optional`, `blocked-unless-escalated`)
- `reason`
- `estimated_size`
- `estimated_sensitivity`

### Minimization guard row

One explicit boundary that keeps probe scope honest.

Suggested fields:

- `minimization_guard_row_id`
- `guard_kind` (`time-boxed`, `subject-bounded`, `member-bounded`, `secret-scan-before-seal`, `paths-tokenized`, `addresses-tokenized`, `no-live-export`, `auto-stop-required`, `external-binary-confirmed`, `stop-receipt-required`, `residue-disclosed`)
- `state` (`satisfied`, `missing`, `blocked`, `not-applicable`)
- `summary`

### Probe activation / deactivation receipt

A durable record that proves deeper capture actually started, actually stopped, and what local residue remained.

Suggested fields:

- `probe_activation_receipt_id`
- `diagnostic_probe_plan_ref`
- `phase` (`activated`, `stopped`, `expired`, `canceled`)
- `activation_kind`
- `runtime_restart_happened` bool
- `residue_after_stop` (`none`, `recent-logs-retained`, `trace-files-retained-unsealed`, `manual-cleanup-needed`, `unknown`)
- `recorded_at`

### Probe outcome hint

A prediction row that tells the operator what the probe might change.

Suggested fields:

- `probe_outcome_hint_id`
- `probe_plan_ref`
- `may_strengthen_hypotheses[]`
- `may_weaken_hypotheses[]`
- `cannot_prove[]`
- `likely_next_step_if_positive`
- `likely_next_step_if_negative`

## Fixed inspection order

Every probe approval surface should preserve this order:

1. **Why ordinary evidence refresh is no longer enough**
2. **Chosen probe and expected value**
3. **Included and excluded evidence classes**
4. **Activation, cost, duration, and auto-stop behavior**
5. **Minimization guards**
6. **What this probe still cannot prove**
7. **Run locally, hold locally, escalate later, or cancel**

### 1) Why ordinary evidence refresh is no longer enough

This section should explain what uncertainty remains after the current evidence bundle.
Examples:

- `route view and source view remain contradictory after fresh refreshes`
- `local resource stall is plausible but ordinary resource snapshots are too coarse`
- `peer path is suspected to be the bottleneck and external measurement is now justified`

### 2) Chosen probe and expected value

The surface should say plainly what is being proposed and why now.
Examples:

- `Collect 10-minute elevated debug-log window`
- `Capture transfer samples for one subject/member cell`
- `Run external path measurement between these two peers`

### 3) Included and excluded evidence classes

This section is mandatory.
It must show both what the probe will gather and what it is intentionally not allowed to gather.
Examples of explicit exclusions:

- `no full config export`
- `no unrelated subject logs`
- `no crash dumps unless crash recurs during this window`
- `no peer-address disclosure outside tokenized form`

### 4) Activation, cost, duration, and auto-stop behavior

Examples:

- increased local disk churn
- higher CPU usage for trace logging
- temporary larger evidence staging footprint
- Sync pause requirement before external measurement
- restart required before the deeper collector is active
- capture expires automatically after 10 minutes or one reproduced event, whichever comes first
- stopping the probe leaves only reviewed retained logs, not ambient deep capture

### 5) Minimization guards

This section should state the least-invasive controls that make the probe acceptable.
Examples:

- time-boxed capture
- subject/member bounded filtering
- automatic tokenization before sealing
- local-only staging until explicit export review
- explicit confirmation when external tooling is involved
- stop receipt required before the incident can claim deeper capture ended

### 6) What this probe still cannot prove

Examples:

- debug logs may show retries without proving remote human intent
- transfer samples may show slow throughput without proving root-cause ownership
- external path measurement may show capacity limits without proving Sync-level scheduling decisions
- watcher-health refresh may explain delayed discovery without proving byte settlement

### 7) Run locally, hold locally, escalate later, or cancel

Examples:

- `Approve and run locally`
- `Approve, but keep results sealed and non-exportable by default`
- `Escalation required before this high-intrusion probe may run`
- `Cancel and return to evidence bundle`

## Public rules

### Rule 1 — deeper probes require a reason stronger than curiosity

A probe plan must name the unresolved uncertainty that justifies its extra cost or extra sensitivity.

### Rule 2 — heavy capture is always time-boxed

Any probe that raises logging depth or collects high-volume diagnostics must auto-stop.

### Rule 3 — inclusion and exclusion are equally important

The interface must show not only what will be captured, but also what is intentionally left out.

### Rule 4 — activation and shutdown are first-class facts

If the probe depends on a runtime restart, a persistent collector, or an external binary, the product must say so plainly and leave start/stop receipts.

### Rule 5 — external tooling is a separate escalation class

If the proposed step requires shutting down Sync, invoking a third-party binary, or moving outside AnonSync’s own runtime surface, the product must say so plainly.

### Rule 6 — probe plans do not silently imply export

Collecting more evidence locally does not mean it is approved to leave the machine.

### Rule 7 — the product must prefer the lightest clarifying probe

If a lower-cost evidence refresh could answer the same uncertainty, the heavier probe should be blocked or downgraded.

## Dense row contract

A dense probe-plan row should preserve these labels in this order:

- `Uncertainty`
- `Probe`
- `Included`
- `Excluded`
- `Activation`
- `Auto-stop`
- `Cannot prove`

## Acceptance test

This surface is good enough when a cautious operator can answer all of the following before and after starting a probe:

- why this deeper capture is justified now
- what exactly it will and will not collect
- how the deeper collector becomes active
- how long it can run before stopping automatically
- what residue remains after it stops
- what local or privacy costs it introduces
- whether the result stays local by default
- what uncertainty it may reduce and what it still cannot prove
