# MicroVM lifecycle plans and receipts (making `derive-vmmd` spec-able)

**Tier:** A (Core)
**Profiles:** A, B, C, D
**Pillars:** isolation, operability, supply-chain
**Patterns:** Plan→Apply→Receipt, Broker→Lease→Receipt

DeriveBSD’s microVM posture is only coherent if runtime actions are as evidence-rich as builds.
A microVM lifecycle operation must be:

1) **verify** (digests + signatures)
2) **enforce** (least authority + bounded interop)
3) **receipted** (typed, queryable evidence)

This doc defines four small, digest-bound artifacts that make the `derive-vmmd` boundary implementable without inventing a distributed system.

## Why this exists

Without typed contracts, “launch/stop a VM” drifts into:

- ad-hoc flags
- mutable host-local state
- log-only forensics
- hidden policy decisions

A minimal Plan + Receipt pair forces a stable join key:

- *what was requested?* (plan)
- *what policy authorized it?* (policy digest)
- *what actually happened?* (receipt)

## The artifacts

### `microvm.launch.plan`

A request to realize a compiled runtime contract on a host.

Schema: `spec/microvm.launch.plan.schema.json`
Example: `spec/examples/microvm.launch.plan.json`

Conventions:
- The plan must include a **stable** `instance.instance_id` so receipts are idempotent and human-queryable.
- `plan_id` is a request/workflow id; `plan_digest` is the content identity (`sha256` of JCS-canonical JSON; see `docs/80-canonical-json-hashing-jcs.md`; `adrs/ADR-0043-microvm-plan-digest-sha256.md`).
- Do **not** embed secrets; reference lease ids and let brokers emit their own receipts.
- Launch idempotency semantics are fixed by `adrs/ADR-0041-microvm-instance-idempotency.md`.

### `microvm.launch.receipt`

A typed receipt emitted by `derive-vmmd` after verification + enforcement.

Schema: `spec/microvm.launch.receipt.schema.json`
Example: `spec/examples/microvm.launch.receipt.json`

Conventions:
- Always bind the receipt to `plan_id` + `plan_digest` (plan→result join key).
- `plan_digest` is `sha256` of the JCS-canonicalized plan JSON (see `docs/80-canonical-json-hashing-jcs.md`).
- Include `host.generation_digest` so fleet operators can correlate “this ran under which host generation?”
- When launch uses leased capabilities (secrets, device grants, trace grants), point at the corresponding `lease.use.receipt` digests.
- Record attached host↔guest IO channels under `assigned.io_channels` (vsock, virtio-console, nmdm, stdio) so incidents can reconstruct what crossings existed (see `adrs/ADR-0044-microvm-io-channels-in-receipts.md`). Treat endpoints (e.g. vsock `cid:port`) as **ephemeral evidence**, not stable identity.
- For `outcome: denied` or `failed`, include a non-empty `reasons[]` list with stable reason codes (see `adrs/ADR-0045-microvm-receipt-reason-codes.md`; registry: `docs/456-microvm-receipt-reason-code-registry.md`).

### `microvm.stop.plan`

A request to stop a running microVM instance on a host.

Schema: `spec/microvm.stop.plan.schema.json`
Example: `spec/examples/microvm.stop.plan.json`

Conventions:
- Stop is authorized by policy just like launch (it is a privileged, destructive operation).
- `requested.mode` is intentionally small:
  - `graceful` (default): attempt an orderly in-guest shutdown if supported, bounded by `timeout_ms`.
  - `force`: terminate/destroy the backend instance (may risk data integrity).
- If you want a safety guard, set `expect_running_plan_digest` to prevent accidentally stopping an instance that has been explicitly replaced.

See: `adrs/ADR-0042-microvm-stop-semantics.md`.

### `microvm.stop.receipt`

A typed receipt emitted by `derive-vmmd` after authorization + stop attempt.

Schema: `spec/microvm.stop.receipt.schema.json`
Example: `spec/examples/microvm.stop.receipt.json`

Conventions:
- Always bind the receipt to `plan_id` + `plan_digest` (plan→result join key).
- Record what was observed at evaluation time when possible (`observed.running_at_start`, `observed.running_plan_digest`).
- Use `outcome: already-stopped` when the instance is not running (idempotent stop).
- Use `outcome: timeout` when a graceful stop was attempted but bounded time elapsed.
- For `outcome: denied`, `failed`, or `timeout`, include a non-empty `reasons[]` list with stable reason codes (see `adrs/ADR-0045-microvm-receipt-reason-codes.md`; registry: `docs/456-microvm-receipt-reason-code-registry.md`).


## Instance identity and idempotency (v0)

This is the smallest safe rule set that keeps A–D coherent without forking behavior.

### Launch idempotency (strict)

- `plan_id` is a *request id* (useful for tracing workflows); it is **not** the content identity.
- `plan_digest` is the content identity: sha256 of the UTF-8 bytes of the **JCS-canonicalized** `microvm.launch.plan` JSON (see `docs/80-canonical-json-hashing-jcs.md`).
- `instance.instance_id` is a stable, namespaced identity string (recommended: `svc:<service_id>/<instance_id>` where `<instance_id>` defaults to `default`).

On a given host, `derive-vmmd` is strict-idempotent by `(instance_id, plan_digest)`:

- if the instance is already running *with the same* `plan_digest`, do **not** restart; emit `outcome: already-running`
- if the instance is running but the `plan_digest` differs, deny with `outcome: denied` and reason `instance-id-collision`

See: `adrs/ADR-0041-microvm-instance-idempotency.md`.

### Stop idempotency (safe)

On a given host:

- if the instance is not running, emit `outcome: already-stopped`
- if `expect_running_plan_digest` is provided and the running plan digest differs, deny with a reason such as `plan-digest-mismatch`

See: `adrs/ADR-0042-microvm-stop-semantics.md`.

### Replacement/upgrades remain explicit

DeriveBSD does not standardize an implicit “replace” operation in v0.
To change what is running, callers must:

- stop + launch under a new `instance_id`, OR
- wait for a future lifecycle spec (replace plans + receipts) that makes replacement explicit and reviewable.

## Wiring

### `derive-vmmd` responsibilities (host-local authority boundary)

At launch/stop time `derive-vmmd` must:

- verify signatures + digests for referenced artifacts/manifests (launch)
- evaluate policy (deny-by-default on authority expansion; deny dangerous stop requests unless authorized)
- realize backend calls (bhyve + helpers), preferably with jail/capsicum hardening
- emit receipts **even on denial/failure/timeout** (denial is evidence)

See also:
- `docs/29-vm-control-plane.md`
- `adrs/ADR-0040-microvm-orchestration-host-local.md`

### Evidence spine

Treat microVM lifecycle plans/receipts as first-class runtime evidence:

- include receipts in bounded incident bundles when the instance is in scope
- allow exports via `export.policy` (redaction-aware)

See: `docs/229-evidence-spine-overview.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/251-export-policies-and-support-bundle-portal.md`.

### Adapter lanes (fleet orchestration lives outside the OS)

Fleet systems should submit digest-bound `microvm.*.plan` objects to hosts (over a killable adapter lane) and treat host receipts as the source of truth.

See: `docs/402-adapter-lanes-and-strangler-discipline.md`, `adrs/ADR-0040-microvm-orchestration-host-local.md`.

Last updated: 2026-03-04r184
