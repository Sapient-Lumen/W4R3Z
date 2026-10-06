# Change sets + apply engine (unifying config, state, and service transitions)

As the archive grows, a pattern emerges:

- configuration has explicit plans + receipts (`config-plan`, `config-receipt`)
- persistent state has explicit migration plans + receipts (`state-migration-plan`, `state-migration-receipt`)
- service supervision has explicit state + events (`svc.snapshot`, `svc.event`)
- resource governance has explicit policy + receipts (`resource-policy`, `resource-receipt`)
- boot/update decisions are health-gated (`boot.health.report`)

If we ship these as separate tools, operators will glue them together with ad-hoc scripts.
That reintroduces the exact failure modes we’re trying to eliminate: partial changes, unclear ordering,
poor auditability, and “what changed?” being a forensic exercise.

DeriveBSD should add one *thin* orchestration layer:

**A change set is an explicit, verifiable plan for a multi-step transition.**

The apply engine executes the plan, emits receipts, and integrates with health gating.

## What problem this solves

- Avoid “restart this, then edit that, then run migration X” shell scripts.
- Make ordering explicit (apply config → run migrations → restart services → health gate → commit).
- Make rollback explicit (pre-snapshots + holds; config candidate roots; BE fallback).
- Make cross-system automation consistent (local CLI and fleet control planes share the same objects).

## Evidence artifacts (new)

- `change-set`: a signed bundle referencing the component plans and required checks.
- `change-receipt`: emitted by the apply engine, referencing the per-step receipts + event pointers.

Both should be **small** (metadata + digests), with payloads referenced by store paths or bundles.

## DeriveBSD direction

### 1) Change sets are *composed*, not invented

A `change-set` primarily references existing evidence objects:

- `config-plan` (if config changes)
- one or more `state-migration-plan` objects (if persistent state changes)
- optional `fw-update-plan` (if firmware changes)
- optional `storage-scrub-plan` (if storage integrity verification is required as part of maintenance)
- optional `svcdb` / service action intents (reload/restart constraints)
- optional `incident.bundle` request template (collect context on failure)
- the **health gate policy** identifier + required checks

### 2) Apply engine ordering (default)

A simple default ordering works for most hosts:

1) **Snapshot**: emit `config-snapshot` + `state-snapshot` and create ZFS holds/snapshots as required.
2) **Apply config**: apply `config-plan` into candidate roots; validate; activate; (optionally) start confirm window.
3) **Time gate (optional)**: `require-time-sync` against a `time-requirement` before any steps that depend on trustworthy time.
4) **Posture gate (optional)**: `require-attestation` against an `attestation-requirement` before secret release or commit (when policy requires).
5) **Apply secrets (optional)**: validate/unseal/fetch required secrets for this generation and emit `secret-receipt` evidence.
6) **Apply PKI (optional)**: validate trust bundle(s), ensure/renew identities per `pki-issue-plan`, and emit `pki-issue-receipt` evidence.
7) **Apply resource policy (optional)**: apply `resource-policy` budgets/caps before service reconciliation.
8) **Run migrations**: execute `state-migration-plan` steps in declared order; emit per-volume receipts.
9) **Apply firmware (optional)**: execute `fw-update-plan` steps (staged for next-boot if required) and emit a `fw-update-receipt`.
10) **Run storage scrub (optional)**: execute a `storage-scrub-plan` (possibly within a maintenance window / best-effort throttling) and emit a `storage-scrub-receipt`.
11) **Service reconciliation**: reconcile to desired `svcdb` state (reload/restart where required) and emit `svc.event`.
12) **Health gate**: run minimal policy-governed probes; emit/attach `boot.health.report` or equivalent host probe.
13) **Commit**: if health passes and confirm is satisfied, commit the generation; else rollback.


### 3) Commit-confirmed as a *change-level* safety valve

Even if only part of a change is “risky” (network/auth), it’s useful to treat confirmation as a change-level latch.

- `change-set.confirm` can require confirmation within a time window.
- confirmation is capability-gated (only holders of a confirm authority can finalize).
- lack of confirmation triggers rollback and a `change-receipt` explaining why.

### 4) Failure mode design

Failures should not be “silent partial state.” Instead:

- always emit a `change-receipt` (success/failure)
- on failure, optionally emit an `incident.bundle` (bounded context)
- on failure (or in CI), optionally trigger a record/replay capture hook and reference the resulting `debug.replay.capsule` digest in the receipt (see `docs/220-operational-time-travel-debugging.md`)
- record a high-level failure in the structured journal (`event.record`) so operators can query:
  - “what changes failed in the last 24h?”
  - “show me all hosts that rolled back due to migration timeout”

## Integration points

- **Health-gated updates**: can treat “apply change-set + receipt success” as a first-class prerequisite (`docs/112-health-gated-updates.md`).
- **Event journal**: change execution milestones should be expressed as `event.record` (`docs/215-structured-event-log-as-evidence.md`).
- **Incident bundles**: failures can trigger a bundle collection policy (`docs/216-incident-snapshots-and-support-bundles.md`).
- **Config + state lanes**: change sets are the glue, not a replacement (`docs/218-...`, `docs/217-...`).

## Open questions

- Do we allow multi-host change sets (fleet rollouts), or keep `change-set` host-local and let the fleet orchestrator compose at a higher level?
- How do we represent “soft failures” (warnings) vs “hard failures” for partial progress?
- Should the apply engine be a dedicated service under supervision (recommended) or a CLI-only mode?


## Time gating

Change sets may include a `require-time-sync` step that references a `time-requirement` object.
This makes time assumptions explicit for workflows that depend on trusted timestamps (commit, secret release, posture verification).
See `docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md`.

## Posture gating

Change sets may include a `require-attestation` step that references an `attestation-requirement` object.
This makes posture gates explicit and auditable in multi-step transitions.
See `docs/226-platform-posture-and-attestation-results-as-evidence.md`.

Last updated: 2026-02-24

