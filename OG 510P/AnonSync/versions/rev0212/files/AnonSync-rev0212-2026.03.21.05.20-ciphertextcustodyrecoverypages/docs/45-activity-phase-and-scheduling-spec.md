# Activity phase and scheduling spec

## Purpose

The archive already had temporary override leases and route leases.
What it still lacked was a sharper answer to a quieter but important interface question:

> when an operator says “pause”, what exact parts of the system do they think should stop, and what exact parts should still continue?

Resilio's current docs are useful precisely because they show why this cannot stay fuzzy.
They describe global pause, per-folder pause, and a weekly scheduler, but they also say that paused or scheduled-paused peers can still propagate deletes, still rescan and index new files, and may still need a separate `rate_limit_local_peers` setting if the operator expected LAN throttling too.
That is real utility, but it is not yet a public phase model.

This document turns that lesson into an AnonSync requirement:

- transfer suppression
- scan/index activity
- delete propagation
- discovery / dialing posture
- recurring windows
- one-shot maintenance overrides

must be inspectable through one shared activity grammar.

## Core stance

1. **No naked `Paused` truth claim.**  
   The product may use the word in prose, but never as the complete model. It must also say which phases are suspended, which remain active, and why.

2. **Recurring windows and one-shot overrides share one grammar.**  
   A weekly schedule should not become a separate mini-product. It should compile to the same phase/effective-state model used by ad hoc overrides.

3. **Transfer is not the whole runtime.**  
   Upload, download, scan/index, delete handling, and route/discovery posture are related but separate.

4. **Route exceptions stay separate from activity control.**  
   A direct-speed lease is still a route lease, not a hidden side effect of a throttle or pause control.

5. **The effective answer must be rendered directly.**  
   Operators should not have to mentally combine baseline policy, active override, recurring schedule, and LAN-vs-Internet caveats.

## Activity phases

The interface should expose at least these runtime phases:

- `scan-index`
- `ingress-bytes`
- `egress-bytes`
- `delete-propagation`
- `announce-discovery`
- `dial-attempts`

These are not implementation threads.
They are operator-meaningful slices of behavior.

A single target may therefore truthfully be in a state like:

- downloads suspended
- uploads draining
- scans active
- delete propagation still active
- announcement unchanged

That is a better answer than the single word `Paused`.

## Effective activity state

### Activity phase state

A first-class read object describing one phase of one subject after baseline policy, overrides, and recurring windows have been combined.

Fields:

- `activity_phase_state_id`
- `subject_type` (`system`, `device`, `share`, `mount`, `policy`)
- `subject_id` nullable
- `phase` (`scan-index`, `ingress-bytes`, `egress-bytes`, `delete-propagation`, `announce-discovery`, `dial-attempts`)
- `effective_mode` (`active`, `throttled`, `suspended`, `draining`, `degraded`, `blocked-pending-review`)
- `rate_caps` nullable
- `route_class_scope` (`all`, `internet`, `lan`, `overlay`, `clearnet-direct`)
- `baseline_ref` nullable
- `active_override_refs[]`
- `active_schedule_refs[]`
- `current_answer`
- `generated_at`

Rules:

- `current_answer` should be legible enough to render directly in CLI and workbench summaries
- rate caps should say what path classes they affect, so LAN-only versus Internet-only behavior is never hidden in a side toggle
- if a phase is `degraded`, the object should point at the relevant health/report surface rather than pretending the control window is the whole story

### Schedule window

A recurring time-bounded policy object that activates phase controls without silently rewriting the durable baseline.

Fields:

- `schedule_window_id`
- `target_type` (`system`, `device`, `share`, `mount`, `policy`)
- `target_id` nullable
- `preset` (`transfer-quiesce`, `egress-drain`, `metered-link`, `maintenance-freeze`, `custom`)
- `phase_controls[]`
- `route_class_scope` (`all`, `internet`, `lan`, `overlay`, `clearnet-direct`)
- `timezone`
- `recurrence_rule`
- `enabled`
- `created_by`
- `created_at`
- `next_activation_at` nullable
- `last_activation_at` nullable
- `provenance_ref` nullable

Notes:

- recurring windows should be inspectable even when currently inactive
- each window should be able to say what effective override objects it would activate right now if the time matched
- `route_class_scope` exists so operators do not have to discover later that a bandwidth cap only affected Internet paths

## Phase-control presets

The product may offer presets, but they should compile to explicit controls.

### `transfer-quiesce`

Intended meaning:

- stop new uploads and downloads
- leave scans/indexing active unless explicitly changed
- leave delete propagation explicit rather than implied

Use when the operator mainly wants to stop byte movement without pretending the share became inert.

### `egress-drain`

Intended meaning:

- allow in-flight or queued uploads to finish
- stop new downloads
- keep durable trust and discovery policy untouched

Use for shutdown preparation or weak-uplink exit.

### `metered-link`

Intended meaning:

- throttle chosen route classes only
- preserve explicit truth about what remains unthrottled

Use when the operator wants a recurring commute / hotspot / travel posture.

### `maintenance-freeze`

Intended meaning:

- stop new transfer work
- usually stop delete propagation too
- keep the stronger freeze legible enough that the operator knows they are choosing divergence risk intentionally

This should normally require stronger warning or plan/apply semantics than a simple throttling change.

## Rendering rules

### Share and device answer strips

Good examples:

- `Uploads draining for 38m more; downloads suspended; scans still active; delete propagation unchanged.`
- `Internet transfers capped to 2 MiB/s by weekday metered window; LAN remains unrestricted.`
- `Maintenance freeze active: byte transfer and delete propagation suspended until 18:00.`

Bad examples:

- `Paused`
- `Limited`
- `Scheduler active`

### Chips and summary rows

Short chips are allowed, but the detail row must expand them honestly.
Examples:

- chip: `Drain`
- expansion: `Uploads draining, downloads suspended, scans active, baseline route policy unchanged`

- chip: `Metered`
- expansion: `Internet only; LAN unaffected; expires 18:00`

## CLI surface

The archive already has `anonsync override ...`.
This document adds a clearer read and recurring-window surface around it.

### Read effective activity state

```text
anonsync activity show --share vault
anonsync activity show --device laptop-ember --effective
anonsync activity explain --share vault
```

Output should say at least:

- current phase matrix
- active overrides contributing to the result
- active or upcoming schedule windows
- route-class scope for caps or suppression
- the plain-language current answer

### Recurring windows

```text
anonsync schedule create   --target device:laptop-ember   --preset metered-link   --route-class internet   --down 2MiB/s   --up 512KiB/s   --rrule 'FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=8,9,10,11,12,13,14,15,16,17'

anonsync schedule list
anonsync schedule show swn_01J...
anonsync schedule disable swn_01J...
anonsync schedule enable swn_01J...
```

### Manual overrides remain valid

```text
anonsync override create --target share:media --mode pause-transfer --ttl 2h --reason "metered hotspot"
anonsync override create --target device:laptop-ember --mode drain-egress --ttl 45m --reason "shutdown maintenance"
```

But `status`, `activity show`, and workbench cards should translate those overrides back into the public phase model instead of echoing only the raw mode name.

## API expectations

The daemon API should expose at least:

```text
GET    /v1/activity-state
GET    /v1/activity-state/{subject_type}/{subject_id}
GET    /v1/schedules
POST   /v1/schedules
GET    /v1/schedules/{schedule_window_id}
PATCH  /v1/schedules/{schedule_window_id}
DELETE /v1/schedules/{schedule_window_id}
```

`GET /v1/activity-state/...` should be cheap enough to render by default whenever an override or recurring window is active.

## Workbench expectations

The workbench should gain one stable card or tab: **Activity & windows**.

That card should show:

- current phase matrix
- active one-shot overrides
- active recurring windows
- next scheduled activation if relevant
- which route classes are capped or unaffected
- whether delete propagation is still active

The home surface should also be able to surface:

- a recurring window about to activate
- an override nearing expiry
- a maintenance freeze that could surprise another operator later

## Safety thresholds

1. Recurring windows that suspend delete propagation or announcement should normally require stronger review than ordinary throttling.
2. A no-expiry manual override should require explicit acknowledgement.
3. The effective answer should always distinguish durable baseline from active windowed behavior.
4. A route lease should never be silently created as a side effect of an activity window.

## Why this matters

Resilio's current docs are honest enough to teach the lesson clearly:

- pause and scheduler still allow more activity than the label suggests
- LAN throttling can depend on an extra power-user switch
- global pause, per-folder pause, and scheduler are related but not one public phase model

AnonSync should keep the useful operator power while making the runtime truth inspectable in one place.
