# Disclosure lineage receipt page — carriers, visible facts, and blocked stronger sentences interface spec

## Purpose

This receipt exists so later audits can answer one simple but usually forgotten question:

> for this actual issuance / open / route / telemetry event, who could learn what at the time, through which carrier, and what stronger privacy sentence did the system explicitly refuse to claim?

## Core decision

Every serious disclosure-affecting action must emit a **Disclosure lineage receipt**.

The receipt is the durable companion to disclosure reviews and proof pages.

## Page layout

The receipt renders the same order:

1. action and carrier summary
2. observer roster
3. fact-visibility summary
4. strongest safe sentence
5. blocked stronger sentence
6. stale-after / reopen triggers

### 1) Action and carrier summary

Show:

- action ID
- action family
- subject / artifact ref if applicable
- carriers actually used
- time completed

### 2) Observer roster

Show only observer classes relevant to the event, each tagged with a compact visibility class:

- `local only`
- `peer-visible`
- `browser-visible`
- `service-visible`
- `tracker-visible`
- `relay-ciphertext path`
- `telemetry-visible`
- `unknown / unproven`

### 3) Fact-visibility summary

List the concrete fact families that mattered for this event.
Examples:

- subject label
- approximate size
- artifact family
- temporary capability token
- route facts
- OS/version metrics
- payload bytes

Each fact row must say which observer classes could learn it and at what proof grade.

### 4) Strongest safe sentence

Examples:

- `payload bytes were unreadable to relay, but relay path participation was real`
- `artifact details after # stayed local to the browser/device in this open flow`
- `telemetry export exposed runtime posture metrics but not payload bytes`

### 5) Blocked stronger sentence

Examples:

- `reject saying “nothing left the device”`
- `reject saying “no third party could learn anything”`
- `reject saying “browser mediation had zero disclosure consequence”`

### 6) Stale-after / reopen triggers

The receipt must say when its disclosure sentence might stop being current.
Examples:

- handler registration changed
- telemetry policy changed
- helper / route policy changed
- carrier family changed
- artifact was reissued with different preview fields

## Minimal object fields

- `disclosure_lineage_receipt_id`
- `action_ref`
- `subject_ref` nullable
- `artifact_ref` nullable
- `carrier_refs[]`
- `observer_classes[]`
- `fact_visibility_rows[]`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `proof_basis_refs[]`
- `completed_at`
- `stale_after_refs[]`

## Result

AnonSync should preserve disclosure truth with the same seriousness as mutation truth.
A later operator should not need FAQ archaeology to know whether an action was direct-peer only, browser-mediated, tracker-visible, relay-carried, or telemetry-exporting at the time.
