# Interface-affinity contract sheet page — requested NIC, effective NIC, and fallback class interface spec

## Purpose

This page exists because `bind to interface` sounds stronger than it is.
AnonSync should require one first-class **Interface-affinity contract sheet** whenever the operator requests named interface preference, hard cutoff, or runtime-class behavior that can widen interface audience.

The page must keep five truths separate:

1. requested interface identity
2. effective interface identity now
3. whether fall-forward is allowed
4. listener audience class
5. strongest safe sentence

## Object model

### `interface_affinity_contract`

- `interface_affinity_contract_id`
- `scope_ref`
- `runtime_class` (`desktop-user`, `desktop-hidden`, `service-current-user`, `service-local-service`, `service-local-system`, `headless-other`, `unknown`)
- `requested_interface_handle` (friendly name, system handle, MAC if available)
- `requested_interface_presence` (`present`, `missing`, `degraded`, `unknown`)
- `effective_interface_handle`
- `fallback_policy` (`follow-next-active`, `hard-cutoff`, `unspecified`, `unknown`)
- `listener_audience_class` (`one-interface-intended`, `all-active-interfaces`, `unknown`)
- `current_route_witnesses[]`
- `continuity_window` (`current-only`, `windowed`, `none`)
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `related_review_refs[]`
- `related_receipt_refs[]`

## Required sections

### 1) Requested interface

Show:

- chosen interface name and low-level handle
- whether the choice came from explicit operator request, imported config, inherited default, or runtime auto-choice
- whether the interface is currently present

### 2) Effective interface now

Show:

- interface actually carrying the current route witness
- evidence basis such as current tunnel observation, socket/listener witness, or inferred host route
- whether this is only a current observation or a reviewed continuity window

### 3) Fallback and cutoff class

Show exactly one of:

- `next active interface may be used`
- `connections stop if requested interface disappears`
- `cutoff behavior unknown`

### 4) Listener audience

Show whether the current runtime is effectively:

- intended for one interface
- listening on all active interfaces
- unknown / not proven

This section must name runtime-class influence directly.

### 5) Safe sentence

Examples:

- `Requested NIC is present and currently effective, but fall-forward remains allowed.`
- `Requested NIC is missing; no hard cutoff is configured, so current route may use another active interface.`
- `Runtime is service-class and interface audience may be wider than the requested transfer preference.`

## Interaction rules

1. The primary action may not say `Bind` or `Use this NIC` without also showing fallback class.
2. A current effective-interface witness may not be labeled `pinned` unless hard cutoff is also in force or equivalent stronger evidence exists.
3. Dense projections may shorten labels, but must preserve requested/effective/fallback/audience as separate fields.
4. The page must link directly to multi-NIC review and fallback proof when uncertainty remains.

## CLI projection

Examples:

```text
anonsync nic contract show --scope seat:home-nas
anonsync nic contract show --scope subject:ledger --json
```

## Acceptance bar

The page is good enough when a cautious operator can answer all of the following from one view:

- which NIC was requested
- which NIC appears effective now
- whether Sync may silently fall forward
- whether the runtime may be listening more broadly than the chosen data interface suggests
- what stronger sentence the product refused to make
