# ADR-0041: MicroVM instance identity and strict launch idempotency

- Status: **accepted**
- Date: 2026-03-04

## Context

`microvm.launch.plan` + `microvm.launch.receipt` make the `derive-vmmd` boundary spec-able.
But “launch a VM” still has a dangerous ambiguity:

- What happens if a plan is submitted twice?
- What happens if a plan changes but reuses the same `instance_id`?
- Do we implicitly restart/replace, or do we force explicit lifecycle actions?

If this is left unspecified, different product shapes will fork behavior:

- Fleet hosts (A) may want strict safety (no surprise restarts) and a stable join key for receipts.
- Workstations (B) may want convenience (click twice and it “just works”).
- Appliances/regulatory (D) need auditability and explicitness.

DeriveBSD’s pillars push toward a conservative default:

- receipts must remain a stable, queryable evidence surface
- runtime operations must be least-surprise and least-authority
- upgrades/replacements must be explicit (or at least reviewable)

## Decision

### 1) `instance.instance_id` is a stable, namespaced identity string

`instance_id` is the operator-queryable identity used to correlate:

- receipts
- policy decisions
- backend instance handles
- evidence bundles

Recommended convention (not a schema rule):

- `svc:<service_id>/<instance_id>` (where `<instance_id>` defaults to `default`)
- `appvm:<app>/<user>/<instance_id>`
- `job:<pipeline>/<run_id>`

### 2) Launch is **strict-idempotent** by `(instance_id, plan_digest)`

On a given host:

- If no active instance exists for `instance_id`, `derive-vmmd` may launch and emits `outcome: launched`.
- If an active instance exists for `instance_id` and its active plan digest equals the submitted `plan_digest`:
  - `derive-vmmd` MUST NOT restart or replace the instance.
  - It emits `outcome: already-running` (optionally with a reason like `idempotent-replay`).
- If an active instance exists for `instance_id` but the submitted `plan_digest` differs:
  - `derive-vmmd` MUST deny with `outcome: denied`.
  - The denial reason code should be `instance-id-collision`.

This keeps “submit the same plan twice” safe, but prevents implicit replacement.

### 3) Replacement/upgrades are explicit

In v0, DeriveBSD does not standardize an implicit “replace” operation.
To change what is running, callers must:

- use a new `instance_id`, OR
- wait for a future lifecycle spec (stop/replace plans + receipts) that makes replacement explicit and receipted.

## Consequences

- Safe defaults across product shapes (A–D): no surprise restarts.
- Fleet orchestrators remain external but can still be robust:
  - they can re-submit plans without fear of restarts
  - they must treat upgrades as explicit identity transitions
- The “VM lifecycle surface” becomes an explicit future decision (and should be specified as Plan→Receipt when accepted).

See: `docs/455-microvm-launch-plans-and-receipts.md`, `docs/29-vm-control-plane.md`, `docs/80-canonical-json-hashing-jcs.md`.
