# RFC-0175: Service contract handles and membership evidence

Status: Draft  
Last updated: 2026-02-25

## Problem

Service supervision that relies on pidfiles and process scraping is:
- unreliable (orphaned subprocesses, ambiguous ownership)
- hard to audit (no stable handle that ties events/receipts together)
- hard to make safe (kill semantics are fuzzy)

DeriveBSD’s supervision-as-evidence posture benefits from a first-class “ownership handle” for each service instance.

## Goals

- Introduce a standardized **service contract handle** abstraction.
- Make it usable across backends:
  - jail-backed services
  - microVM-backed services
  - classic host-process services
- Wire the handle into `svc.snapshot` and `svc.event` so it becomes part of the evidence spine.

## Non-goals

- Implementing kernel-native process contracts in this RFC.
- Mandating a single backend for all services.

## Proposal

### 1) New evidence object: `svc-contract-handle`

Add `spec/svc.contract.handle.schema.json` and an example.

A handle binds:
- `service_id` + optional `instance_id`
- `backend` enum: `jail`, `microvm`, `procgroup`
- backend identifiers (`jail_id`, `vm_id`, `pgid`, etc) in a backend-specific object

### 2) Reference from supervision outputs

- Add optional `contract_handle_digest` to:
  - `svc.snapshot.services[*]`
  - `svc.event` (especially for crashes/restarts and `event_type="contract-event"`)

### 3) Backend semantics

#### Jail backend

- The contract handle maps to the jail boundary.
- Membership events are inferred from jail process lifecycle.

#### MicroVM backend

- The contract handle maps to the VM instance.
- The supervisor treats VM lifecycle as service lifecycle.

#### Procgroup backend

- The contract handle maps to a supervisor-created process group/session.
- Membership tracking is best-effort but standardized:
  - track fork/exec boundaries
  - record the root pid and the pgid/session id

## Data contract changes

- Add `spec/svc.contract.handle.schema.json` (+ example).
- Update `spec/svc.snapshot.schema.json` and `spec/svc.event.schema.json` to allow `contract_handle_digest`.
- Update `spec/examples/svc.snapshot.json` and `spec/examples/svc.event.json` accordingly.

## Rollout plan

1) Add schema + examples.
2) Update the primary restarter to emit a contract handle digest when it can.
3) Encourage new services to use jail or microVM boundaries where possible.

## Risks / tradeoffs

- For procgroup backend, membership correctness depends on kernel visibility into process parentage and exec; treat as best-effort and prefer stronger boundaries.
- Handles could leak internal identifiers; incident bundle export must apply redaction policy.

## Related

- `docs/243-service-contract-handles-and-membership.md`
- `docs/235-process-contracts-and-service-ownership.md`
- `docs/239-service-lifecycle-restarters-and-repo.md`
- `docs/214-service-supervision-health-as-evidence.md`
