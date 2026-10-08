# Service NIC-audience review page — all-NIC listener class and exposure delta interface spec

## Purpose

This page exists because a runtime-class change can widen network audience even when the operator thinks they only changed startup behavior.
AnonSync should require a **Service NIC-audience review** whenever service/headless activation, privilege change, or host-run-class migration can change which interfaces may listen or answer.

## Key doctrine

- runtime class is not a cosmetic label
- listener audience is not the same as transfer preference
- `starts before login` is weaker than `same network audience`
- `service can reach the folder` is weaker than `service listens on the same interface set`

## Object model

### `nic_audience_review`

- `nic_audience_review_id`
- `scope_ref`
- `prior_runtime_class`
- `target_runtime_class`
- `prior_listener_audience_class`
- `target_listener_audience_class`
- `expected_exposure_delta` (`none`, `narrower`, `wider`, `unknown`)
- `interface_candidates[]`
- `service_specific_notes[]`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`

## Required sections

### 1) Runtime-class delta

Show exactly what is changing:

- user app to service
- one service principal to another
- service to user app
- unknown / imported configuration

### 2) Listener audience delta

Show whether the target runtime may:

- keep same intended interface audience
- widen to all active interfaces
- become uncertain

### 3) Exposure delta

This section must explicitly answer:

- who could newly reach this runtime if the wider audience becomes real
- which prior assumptions are no longer safe
- whether interface-affinity preference survives, weakens, or becomes observational only

### 4) Safer alternatives

Examples:

- keep user runtime and explicit interface affinity
- move to service but review all-NIC audience first
- add hard cutoff proof before relying on interface naming

## Interaction rules

1. The product must not let `Run as service` or equivalent ship without audience review when interface truth matters.
2. Do not compress `wider listener audience` into a vague security warning.
3. The review should preserve pre/post audience class side by side.

## Acceptance bar

The page is good enough when a cautious operator can answer:

- whether the runtime-class change widens network audience
- whether their existing interface preference survives as policy, witness, or not at all
- what exposure delta the product is asking them to accept
