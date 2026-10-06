# Time sources in practice (chrony NTS + Roughtime quorum)

DeriveBSD already models secure time as an evidence-bearing lane (`docs/200-secure-time-bootstrapping.md`, `docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md`, `docs/283-trustworthy-time-nts-roughtime-and-lkgt.md`).

This doc is the **“how do we actually do it on BSD hosts?”** companion:
- what daemons/backends exist today
- what to prefer by default
- how to wire them into DeriveBSD’s `system.time` broker + evidence objects

## The key goal

We want a host to be able to answer:
- **what sources did you consult?**
- **were they authenticated?**
- **did they agree within policy bounds?**
- **what time did you pick and why?**

…without relying on stringy logs.

## Practical backends

### 1) `chronyd` (recommended default for NTS)

`chrony` supports **Network Time Security (NTS)** and is widely deployed.
In most ecosystems the configuration is as simple as adding the `nts` option to a server or pool line.

Why it fits DeriveBSD:
- supports authenticated time without bespoke plumbing
- good “VM reality” behavior (handles unstable clocks well)

Implementation hint:
- DeriveBSD can run `chronyd` inside a tight sandbox and treat it as an untrusted *measurement producer*.
- `system.time` consumes `chronyd` status + performs policy evaluation + emits receipts.

Refs:
- NTS overview (RFC 8915): https://www.rfc-editor.org/info/rfc8915
- chrony config manual (`server ... nts` option): https://chrony-project.org/doc/4.8/chrony.conf.html
- chrony comparison (NTS support + isolated-network behavior): https://chrony-project.org/comparison.html

### 2) `ntpsec` (viable NTS alternative)

`ntpsec` supports NTS and has explicit configuration controls.

Why it fits:
- compatible with NTP operator expectations
- can be used as an alternate backend in a “backend diversity” posture

Refs:
- NTPsec NTS Quick Start: https://docs.ntpsec.org/latest/NTS-QuickStart.html

### 3) `ntpd-rs` (optional memory-safe lane)

A modern Rust implementation that explicitly targets NTP+NTS.
DeriveBSD can treat this as an optional “smaller TCB / memory-safe backend” lane.

Ref:
- ntpd-rs repository: https://github.com/pendulum-project/ntpd-rs

### 4) Roughtime clients (fast quorum sanity + misbehavior evidence)

Roughtime is designed to be quorum-friendly and to allow clients to retain cryptographic proof of server inconsistency.

DeriveBSD does **not** need to replace NTP/NTS with Roughtime.
Instead, it can use Roughtime as:
- a cheap *sanity oracle* (“is our time wildly wrong?”)
- an optional quorum participant (especially during bootstrap)

Refs:
- IETF Roughtime draft: https://datatracker.ietf.org/doc/draft-ietf-ntp-roughtime/
- Cloudflare Roughtime overview: https://developers.cloudflare.com/time-services/roughtime/

## DeriveBSD wiring (broker + evidence)

The existing evidence objects are sufficient:

- `time-source-policy` (signed): `spec/time.source.policy.schema.json`
  - chooses sources (NTS/Roughtime endpoints)
  - defines quorum and max skew
  - defines bootstrap guardrails (RTC allowance, max jump)

- `time-proof-bundle`: `spec/time.proof.bundle.schema.json`
  - records per-source observations (reported time + uncertainty)
  - records agreement result + selected time
  - stores only transcript digests by default (privacy-safe)

- `time-sync-plan` / `time-sync-snapshot` / `time-sync-receipt`
  - make “clock discipline actions” durable and explainable
  - support handoff can stay on `time_source_inventory_digest` + `time_sync_snapshot_digest` + `time_sync_receipt_digests` instead of daemon-private status text

- `time-proof-bundle` stays a richer side-evidence lane for transcript/agreement analysis; it is not the routine support-handoff truth surface.

### Recommended flow

1) Collect observations
- query NTS sources (chrony/ntpsec/ntpd-rs backend)
- optionally query one or more Roughtime sources

2) Build a `time-proof-bundle`
- store digests of protocol transcripts
- compute agreement (median / bounded skew)

3) Decide time state
- if quorum met: `synced`
- if partial: `degraded` (still emit proof bundle, mark `in_quorum=false`)
- if none: `unsynced`

4) Emit a `time-sync-snapshot`
- include `lkgt_time` if LKGT enforcement is enabled

5) Emit `time-event`s for important transitions


## Product-shape defaults now fixed

The backend choice is still open, but the product-default posture is no longer vague:

- **A** requires authenticated time with quorum/LKGT posture for expiry-sensitive gates.
- **B** keeps degraded time visible in trusted UX and gates sensitive actions instead of silently trusting weak time.
- **C** keeps authenticated time preferred, with explicit compatibility fallback.
- **D** supports bounded offline/bootstrap authority through signed time or authenticated quorum instead of “ignore time because airgap”.

See: `docs/468-trustworthy-time-posture-by-profile.md`.

## Failure modes to design for

- **No NTS sources available:** prefer “degraded + explicit receipts” over silently falling back to unauthenticated NTP.
- **Quorum disagreement:** treat as an incident-worthy signal; emit an event and avoid expiry-sensitive operations.
- **Bootstrap RTC drift:** allow RTC only within a tight policy window; once secure time is obtained, advance LKGT and refuse backward jumps.

Last updated: 2026-03-21r364
