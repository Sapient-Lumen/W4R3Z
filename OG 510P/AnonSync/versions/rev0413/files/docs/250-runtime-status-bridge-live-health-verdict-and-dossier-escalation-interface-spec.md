# Runtime status bridge, live health verdict, and dossier-escalation interface spec

## Purpose

The archive already had system status, system health, work-phase ledgers, incident opening, convergence reports, and full evidence-bundle/export lanes.
What it still lacked was one operator-facing contract for a much more everyday question:

> from the current seat and current surface, is AnonSync ready, not ready, unavailable, skipped for a known reason, or actually unhealthy right now — and when does that lightweight answer need escalation into a fuller incident dossier?

That seam matters because current Linux/service reality often splits the truth across human-oriented status commands, session state, unit state, listener reachability, and later support capture.
A cautious operator should not need all of those just to answer `is the current lane basically okay?`

## Core decision

AnonSync should expose one first-class **runtime status bridge**.

The bridge is a lightweight but machine-readable proof surface that joins:

- current seat/session readiness
- current daemon/service/runtime posture
- current control-entry / listener reachability
- strongest known blocker class
- the exact escalation boundary where the bridge stops and a richer incident / dossier lane begins

The bridge must be strong enough for ordinary operator questions.
It must also be honest enough to say when it cannot support a stronger claim.

## Why this matters

Current Linux-native operations repeatedly blur several different truths:

- the session is ready, but the owned runtime is stopped
- the runtime is intentionally skipped because a condition failed
- the runtime is alive, but the listener/control surface is unreachable here
- the runtime is healthy enough for ordinary use, but a richer dossier is still needed for a harder incident
- the current seat simply cannot inspect a required subsystem and therefore cannot say `healthy`

AnonSync already has the heavier objects needed after escalation.
What was missing was the lighter bridge that says which everyday truth has already been proven before the operator is pushed into raw host archaeology or a full incident packet.

## Public objects

### Runtime status bridge

A compact, durable projection over the current seat and current product/runtime lane.

Suggested fields:

- `runtime_status_bridge_id`
- `seat_ref`
- `surface_class` (`local-web`, `desktop`, `headless-cli`, `remote-workbench`, `mobile`, `other`)
- `runtime_owner_kind` (`user-session-daemon`, `system-service`, `foreground-process`, `unknown`, `not-applicable`)
- `bridge_verdict` (`ready`, `not-ready`, `unavailable`, `skipped-cleanly`, `degraded`, `error`, `unknown`)
- `freshness_state` (`fresh`, `aging`, `stale`, `unreadable`)
- `strongest_blocker_class` (`none`, `session`, `service`, `listener`, `identity-root`, `filesystem`, `transport`, `policy`, `resource`, `external-blocker`, `unknown`)
- `current_claim_boundary`
- `next_honest_action`
- `generated_at`

### Bridge probe row

One machine-readable fact family that contributed to the bridge verdict.

Suggested fields:

- `bridge_probe_row_id`
- `bridge_ref`
- `probe_kind` (`session-readiness`, `runtime-health`, `listener-reachability`, `control-auth`, `identity-root`, `work-phase`, `transport-health`, `resource-pressure`, `other`)
- `probe_source_kind` (`local-measurement`, `daemon-self-report`, `service-manager`, `session-manager`, `config-derived`, `operator-attested`, `unknown`)
- `state` (`passing`, `failing`, `skipped`, `unsupported`, `unreadable`, `stale`)
- `summary`
- `observed_at` nullable

### Bridge escalation boundary

A compact statement of where the bridge stops being enough.

Suggested fields:

- `bridge_escalation_boundary_id`
- `bridge_ref`
- `strong_enough_for` (`everyday-status`, `safe-retry`, `surface-repair`, `routing-check`, `incident-open`, `no-strong-claim`)
- `not_strong_enough_for` (`support-export`, `deep-diagnosis`, `destructive-repair`, `trust-rotation`, `high-risk-apply`, `unknown`)
- `recommended_escalation_object_kind` (`incident`, `convergence-bundle`, `external-blocker-handoff`, `guidance-intake`, `repair-review`, `none-yet`)
- `reason_summary`

### Bridge receipt

A durable record that one bridge verdict was rendered and, when relevant, superseded or escalated.

Suggested fields:

- `bridge_receipt_id`
- `bridge_ref`
- `transition` (`render`, `refresh`, `escalate`, `supersede`, `expire`)
- `recorded_at`
- `successor_ref` nullable

## Fixed inspection order

Every runtime-status bridge surface should preserve this order:

1. **Current seat and ownership posture**
2. **Bridge verdict now**
3. **Probe rows and strongest blocker**
4. **What the bridge does not claim**
5. **Escalate, repair here, or wait**

### 1) Current seat and ownership posture

This section should say:

- which seat and surface produced the bridge
- whether the runtime appears owned by a foreground process, user service, system service, or no durable runtime at all
- whether this seat is expected to answer the question directly or only partially

Examples:

- `local-web seat talking to user-session daemon`
- `headless CLI attached to system-service runtime`
- `remote workbench can inspect status but cannot prove local browser-entry health`

### 2) Bridge verdict now

This section should answer the everyday question directly.
Examples:

- `Ready — runtime healthy and listener reachable from this seat`
- `Skipped cleanly — runtime did not start because session precondition failed`
- `Unavailable — current seat cannot inspect the needed service-manager lane`
- `Degraded — daemon running, but listener/auth control entry is failing`
- `Error — identity-root unreadable and control lane cannot continue`

### 3) Probe rows and strongest blocker

This section should show:

- the few probe families that justified the verdict
- which ones passed, failed, were skipped, or were unreadable
- the strongest blocker class now
- the freshest observation time that still matters

The operator must be able to answer:

> which small set of facts made the bridge say this?`

### 4) What the bridge does not claim

This section is mandatory.
It should say what stronger claims remain out of scope.
Examples:

- `does not yet prove route health for any specific subject`
- `does not yet prove convergence after yesterday's repair`
- `does not replace a support packet for this incident`
- `does not prove this remote seat can perform local browser trust bootstrap`

### 5) Escalate, repair here, or wait

This section should offer the next honest move.
Examples:

- `Open incident with current bridge attached`
- `Inspect work-phase ledger`
- `Refresh bridge after returning from firewall consent`
- `Wait for session readiness; no heavier dossier needed yet`

## Main surface

Every seat should expose one compact bridge row such as:

- `Ready · user-session daemon healthy · listener reachable here`
- `Skipped cleanly · session not ready · no runtime crash claimed`
- `Unavailable · cannot inspect service-manager lane from this seat`
- `Degraded · runtime alive but control entry failing · incident open recommended`

## CLI parity

Minimum commands:

- `anonsync status bridge`
- `anonsync status bridge --subject <subject-id>`
- `anonsync status bridge explain`
- `anonsync status bridge refresh`

## Public rules

### Rule 1 — bridge and dossier are different scales

The runtime-status bridge is a lightweight proof surface.
It must not pretend to be a full incident dossier.

### Rule 2 — unreadable is not healthy

If the current seat cannot inspect a needed fact family, the bridge must say `unavailable`, `unknown`, or `unreadable` rather than silently promoting hope into health.

### Rule 3 — skipped-cleanly is not crash truth

A reviewed condition miss or session-not-ready skip must stay distinct from `failed`, `degraded`, or `error`.

### Rule 4 — human-oriented status text is not the canonical machine lane

The bridge may quote nearby human status output for convenience, but the canonical object should be machine-readable probe rows and verdict fields.

### Rule 5 — the bridge must publish its own claim boundary

A lightweight answer is only honest when it also says what it does not yet prove.

### Rule 6 — escalation should preserve continuity

Opening a richer incident, evidence bundle, or repair review from the bridge should keep the bridge receipt linked so the operator does not lose the everyday status story when moving into heavier capture.

## Relationship to nearby specs

This spec is the everyday-status companion to:

- `47-settlement-barrier-and-readiness-spec.md`
- `59-diagnostic-evidence-and-support-bundle-spec.md`
- `197-hidden-work-phase-ledger-and-honest-progress-interface-spec.md`
- `202-identity-root-health-folder-list-salvage-and-relink-ladder-interface-spec.md`
- `232-diagnostic-export-log-redaction-and-self-serve-support-boundary-interface-spec.md`

Those documents already cover full reports, incidents, export packets, and recovery ladders.
This one fixes the lighter status bridge that should exist before escalation.

## Acceptance test

This surface is good enough when a cautious operator can answer all of the following without opening a full dossier first:

- is the current seat/runtime basically ready, cleanly skipped, unavailable, degraded, or broken
- which small set of probe facts justified that answer
- what the strongest blocker class is right now
- what stronger claim the bridge does **not** yet support
- whether the next honest move is wait, local repair, or heavier escalation
