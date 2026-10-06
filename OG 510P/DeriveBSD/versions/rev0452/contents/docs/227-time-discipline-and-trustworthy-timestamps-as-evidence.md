# Time discipline + trustworthy timestamps as evidence (NTP/NTS/PTP + receipts)

Time is an invisible dependency.
When it is wrong, everything else becomes harder to reason about:
- receipts and signatures appear “expired”
- rollouts can’t be correlated
- forensics becomes ambiguous (“did this happen before or after the change?”)
- posture/attestation and secret release policies lose teeth

Most OSes treat time sync as:
- a best-effort daemon
- stringy logs
- no durable evidence of *how* time was obtained or *how trustworthy* it is

DeriveBSD should treat clock discipline the same way it treats other operational facts:
**inventory → explicit requirements/plans → snapshots → receipts → typed events → bounded export**.

This doc is about *operational time*. (Deterministic time/entropy for builds/tests lives in `docs/197-time-and-rng-authority.md`.)

Implementation notes (FreeBSD-friendly backends + NTS/Roughtime wiring): `docs/307-time-sources-in-practice-chrony-nts-and-roughtime.md`.

## Lessons worth stealing

### NTP is ubiquitous; securing it matters
NTPv4 is the baseline protocol most deployments rely on.
The important greenfield lesson is to avoid “unauthenticated time by default”.

### NTS (Network Time Security) is the modern “good default”
NTS adds cryptographic protection for client/server NTP.
It’s the obvious baseline for hosts that already care about supply chain integrity.

### PTP is the right answer for certain environments
If you need tight bounds (datacenters, trading, industrial), PTP/IEEE‑1588 exists.
DeriveBSD shouldn’t require PTP, but it should model it as a first-class source type.

### Keep “how time was obtained” separate from “what time is”
You want both:
- a live snapshot of current sync quality
- receipted history of steps/slews/source changes

## DeriveBSD approach

### 1) `time-source-inventory` (what sources exist on this host)
A privacy-safe inventory of time sources the host can use:
- NTP servers (optionally NTS)
- PTP domains/ports (if present)
- hardware RTC
- optional external sources (GPS, Roughtime)

This is used by policy to decide what is allowed.

### 2) `time-requirement` (policy-shaped expectations)
A small gate object describing what “good enough time” means for a workflow.
Examples:
- **before committing** a host generation
- **before requiring attestation** (fresh verifier receipts are time-bounded)
- **before releasing certain secrets**

Typical fields:
- max allowed offset / uncertainty
- max age since last successful sync
- require authenticated sources (NTS/PTP with auth)
- whether large steps are allowed (and their limit)
- explicit degraded-time response (`deny`, `repair-only`, `allow-if-proof-fresh`, `allow-breakglass-only`)

### 3) `time-sync-plan` (how we intend to discipline the clock)
A plan declaring:
- selected sources
- authentication mode (NTS, symmetric key, none)
- step vs slew policy
- guardrails (max step, max slew rate)

This keeps time configuration from being “hidden in `/etc`”.

### 4) `time-sync-snapshot` (current time health)
A compact snapshot that can participate in health gates and incident bundles:
- when a workflow proceeds under `allow-if-proof-fresh`, the snapshot carries `inputs.proof_bundle_digest` for the exact `time-proof-bundle` that justified it
- sync status (synced / degraded / unsynced)
- current estimated offset and uncertainty bounds
- selected reference source and authentication state
- last sync time and recent step events

This is the “askable truth” surface.

### 5) `time-sync-receipt` (evidence of time actions)
Every meaningful action emits a receipt:
- stepped clock by Δ
- slewed for drift
- source changed
- leap-second handling decisions

Receipts should reference:
- the `time-sync-plan` digest (if applicable)
- before/after snapshot digests
- correlated change-set step (when applicable)

### 6) `time-event` (typed event stream)
The structured event journal should carry time milestones:
- `sync-acquired`, `sync-lost`, `source-changed`
- `clock-stepped`, `leap-announced`, `leap-applied`

Time events should reference the relevant snapshot/receipt digests.

## Wiring into the ops spine

- **Health-gated updates**: optional gate input: require a fresh `time-sync-snapshot` meeting policy bounds before commit.
- **Change sets**: add an optional `require-time-sync` step that references `time-requirement`.
- **Incident bundles**: include `time-sync-snapshot` (and recent `time-sync-receipt` digests) by default.
- **Attestation/secrets**: higher-risk workflows can require time requirements to be satisfied before releasing authority.

See also: `docs/112-health-gated-updates.md`, `docs/219-change-sets-and-apply-engine.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/215-structured-event-log-as-evidence.md`.

The official support handoff can now carry `time_sync_receipt_digests` when trustworthy-time actions materially shaped the incident, which keeps exact clock-discipline proof on the typed bundle contract instead of daemon logs or raw protocol transcripts.

## Design notes

### Handle clock steps explicitly
Clock steps are operationally important:
- they can invalidate assumptions in metrics, rate limiters, and event ordering
- they can break time-bounded auth tokens

DeriveBSD should:
- emit a `time-sync-receipt` + `time-event` on steps
- prefer slew-only for normal drift correction
- allow steps only under explicit policy (bootstrapping, severe offset)

### Prefer “trustworthy time” for security-sensitive lanes
For any workflow where “time lies” is a meaningful attack:
- prefer NTS or PTP with authentication
- optionally require a quorum (multiple sources within skew bounds)

This should be policy, not a hard requirement.

Last updated: 2026-03-23r433
