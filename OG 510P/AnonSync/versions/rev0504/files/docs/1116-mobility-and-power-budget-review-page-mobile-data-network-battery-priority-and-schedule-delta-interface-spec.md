# Mobility and power budget review page: mobile data, network, battery, priority, schedule, and delay delta interface spec

## Purpose

This review appears whenever an operator changes a transfer-affecting budget rather than a direct content policy.
It exists to answer one ordinary question before commit:

> what transfer lanes become eligible or ineligible under which networks, power states, schedule windows, runtime-priority conditions, and timing modifiers?

## When this review must appear

Trigger this review for changes such as:

- allow / forbid mobile data
- Wi‑Fi-only or custom-network rules
- battery-saver thresholds
- charging-only wake cadence
- scheduler pause or speed windows
- background-priority-sensitive runtime posture
- file-class publication delay
- queue priority defaults

## Fixed page order

1. change summary header
2. budget delta matrix
3. context examples
4. wake / resume forecast
5. approval footer

### 1) Change summary header

Show:

- subject / seat / runtime
- current budget
- proposed budget
- strongest safe sentence after apply
- stronger rejected sentence after apply

### 2) Budget delta matrix

Render rows for contexts such as:

- on approved Wi‑Fi
- on cellular only
- below battery threshold
- charging above threshold
- during scheduled zero window
- in lowered background priority
- for delayed file classes
- for lower-priority queued downloads

Columns:

- payload upload
- payload download
- deletion publication
- local detection
- peer visibility
- automatic wake behavior
- expected immediacy

### 3) Context examples

Provide concrete examples in plain language:

- `At 9% battery this runtime will stop rather than sleep.`
- `On cellular, payload transfer remains blocked even if the share itself is otherwise eligible.`
- `During the zero-speed window, indexing continues but payload lanes do not.`
- `Office files may remain eligible but held for an extra publish delay.`
- `Newer files may jump ahead of older ones without changing the underlying eligibility of the older files.`

### 4) Wake / resume forecast

Show:

- what event restores full eligibility
- whether the product can forecast a next wake
- what remains unknown
- whether the operator is about to create a state that looks paused but is actually context-gated or delay-shaped

### 5) Approval footer

Require acknowledgement whenever the change creates a non-obvious mixed state such as:

- `transfer blocked, detection active`
- `sleeping with periodic wake`
- `payload stopped but deletion publication still possible`
- `eligible but delayed`
- `queued but currently deprioritized`

## Rules

### Rule 1 — review the contexts, not just the setting names

`Use mobile data = off` is too abstract by itself.

### Rule 2 — the operator must see mixed states before apply

The review must not hide that some lanes remain alive.

### Rule 3 — schedule, battery, delay, and priority are budgets or modifiers, not mere toggles

They shape movement over time and must be previewed that way.
