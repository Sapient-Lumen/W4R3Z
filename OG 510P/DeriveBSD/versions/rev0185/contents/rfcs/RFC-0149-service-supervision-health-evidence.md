# RFC-0149: Service supervision + health evidence (`svcdb`, `svc.snapshot`, `svc.event`)

Status: Draft

## Summary

Define a stable, inspectable **service supervision data model** for DeriveBSD:

- `svcdb` — compiled service database derived from the Plan
- `svc.snapshot` — runtime service state snapshot
- `svc.event` — append-only supervision events (transitions, restarts, crashes)

Keep the runtime executor BSD-native (rc.d/service jails/microVM runners), but require backends to speak these artifacts.

Keep `svc-event` aligned with the shared event envelope (`event.record`) so events can be stored/query/exported uniformly (see RFC-0150).


## Motivation

DeriveBSD’s “evidence objects” and “health-gated updates” require stable answers to:
- What services exist for this generation?
- What do they depend on and where do they run?
- Which services are healthy right now, and why not?
- Are we in a restart loop / maintenance condition?

Without this, rollouts degenerate into unstructured logs and bespoke status scripts.

Inspirations:
- illumos/Solaris SMF service objects + state model (`smf(7)`; LISA’05 paper): https://smartos.org/man/7/smf , https://www.usenix.org/event/lisa05/tech/full_papers/adams/adams.pdf
- s6-rc compiled DB + bundles: https://skarnet.org/software/s6-rc/overview.html
- FreeBSD service jails (“automatic jailing of rc.d services”): https://www.freebsd.org/status/report-2024-04-2024-06/service-jails/
- process contracts (`process(5)`): https://smartos.org/man/5/process

## Goals

- Make service intent and dependencies **diffable** and **reviewable**.
- Make runtime supervision status available via a **stable schema**, not ad hoc logs.
- Enable health gating and promotion policy to reference service health deterministically.
- Allow multiple activation/supervision backends without changing the meaning of “service”.

## Non-goals (v0)

- Reproducing the full SMF repository and tooling surface.
- A “universal init replacement”.
- Forcing a specific executor (rc.d remains acceptable).

## Artifacts

### `svcdb` (compiled service database)

Produced during planning/activation output.

Minimum fields (v0):
- `generation_digest`
- `services[]`:
  - `id`
  - `placement` (host/jail/microvm)
  - `dependencies`
  - `restart_policy`
  - `resources` (optional)
  - `capsets/grants` (optional pointers)
- `bundles{ name: [service_id...] }`

Schema: `spec/svcdb.schema.json`

### `svc.snapshot`

Produced at runtime by the restarter/supervision layer.

Minimum fields (v0):
- `generation_digest`
- `services[]`:
  - `id`
  - `desired` (enabled/disabled)
  - `state` (`online/offline/degraded/maintenance/uninitialized/disabled`)
  - `since`
  - `restarts_window`
  - `message` (optional)
  - `evidence[]` (optional digests)

Schema: `spec/svc.snapshot.schema.json`

### `svc.event`

Produced at runtime as an append-only event stream (journal file, ring buffer, or broker endpoint).

Minimum fields (v0):
- `generation_digest`
- `service_id`
- `event_type` (`state-transition`, `restart-attempt`, `crash`, `maintenance-enter`, `maintenance-exit`, `note`)
- `at`
- `from_state` / `to_state` (when applicable)
- `reason` (optional)
- `evidence[]` (optional digests)

Schema: `spec/svc.event.schema.json`

## State model

Adopt the SMF vocabulary for operator legibility:

- `uninitialized` — not yet evaluated by a restarter
- `offline` — enabled but not currently running/available
- `online` — running/available
- `degraded` — running/available with reduced capacity
- `maintenance` — requires operator action / repeated failure
- `disabled` — explicitly disabled

Optionally:
- `legacy-run` — started outside supervision; discouraged for DeriveBSD-managed services

Backends may map these states from native mechanics (rc.d return codes, jail status, microVM guest agent signals) but must preserve semantics.

## Supervision behavior (v0)

- Each service has a **restart policy**:
  - `never`, `on-failure`, `always`
  - max restarts in a rolling window, with exponential backoff
- After threshold exceedance, enter `maintenance` and emit:
  - `svc.event` with `maintenance-enter`
  - optional `fault.event` (`svc.restart-loop`) via fault management lane

## Health gating integration

`boot.health.report` should include a check (policy-controlled) like:
- required bundles are `online` (or allowed `degraded`)
- no required services are `maintenance`
- restart storm limits not exceeded

The check should reference evidence digests:
- `svc.snapshot` digest
- key `svc.event` digests (optional)
- any related `fault.snapshot` digest

See: `docs/112-health-gated-updates.md`, `docs/213-fault-management-architecture.md`.

## Open questions

- Best minimal process ownership mechanism on BSD (contract analog vs. jail boundary vs. supervisor pid tracking).
- Where `svc.event` lives (journal file, ring buffer, RPC endpoint) and retention policy.
- Bundle semantics vs. targets (boot milestones) vs. “goal services”.

