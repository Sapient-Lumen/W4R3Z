# Evidence collection posture by profile

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt  

DeriveBSD already has event logs, inspect-style diagnostics, flight recorders, and incident bundles.
What this doc decides is narrower and more important for coherence:
**what evidence should exist by default in each product shape, and when does richer capture or external sharing require an explicit lane?**

This is intentionally **not** a full backend spec for the archivist, journal store, or tracing substrate.
It is a product-default decision.

See also:
- ADR: `adrs/ADR-0067-evidence-collection-posture-by-profile.md`
- evidence spine overview: `docs/229-evidence-spine-overview.md`
- structured event log: `docs/215-structured-event-log-as-evidence.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- diagnostics trees: `docs/302-structured-diagnostics-inspect-trees.md`
- flight recorders: `docs/303-flight-recorder-tracing-and-budgeted-diagnostics.md`
- product profiles: `docs/411-product-profiles-as-compilation-target.md`

## Why this needs a hard decision

The archive already says evidence should be typed, bounded, redaction-aware, and export-mediated.
Without a profile-shaped default, those principles still drift in practice:

- fleet hosts either collect too little to explain incidents or collect too much without a clear budget story,
- workstation support quietly becomes ambient telemetry or background uploads,
- general-purpose installs inherit hidden collector/support-agent assumptions,
- and factory/regulatory images claim redacted bundle discipline while still depending on live diagnostic streaming.

Evidence posture is too foundational to leave as implied local custom.
The archive needs a stable default for **when evidence is always on, when it stays local, and when bundles are the contract**.

## Scope of this knob

`evidence` covers the default handling of:

- structured event-log retention and whether bounded local evidence is expected
- inspect-tree and flight-recorder availability as normal local evidence
- whether richer capture or external sharing is ambient vs explicit
- whether incident/support bundles are the primary operational handoff contract
- whether the timeline-first support handoff remains available as the default human orientation surface

It does **not** decide every backend detail of event storage, archivist APIs, or trace encoding.

## Product-shape defaults

| Profile | `evidence` default | Practical meaning |
|---|---|---|
| A (`fleet_host`) | `always-on` | Bounded local evidence collection is normal: structured logs, inspect snapshots, and small flight recorders should exist by default; richer retention or export scope changes remain policy- and receipt-shaped. |
| B (`workstation`) | `exportable` | Local evidence should be useful and user-exportable, but richer capture or external sharing must stay trusted-UI-visible rather than ambient telemetry or background support uploads. |
| C (`general_os`) | `local-retained-explicit-export` | Useful local evidence is retained by default; external sharing, remote collectors, and richer tracing remain explicit choices rather than hidden prerequisites. |
| D (`appliance_factory`) | `bundled-and-redacted` | Production evidence is bundle-oriented and redacted by default; deterministic incident/support bundles are the normal handoff surface, not ambient live streams. |

These values live in `spec/examples/product.profiles.json` and are guarded by `tools/check_product_profiles.py`.

## Cross-profile invariants

Regardless of profile:

- evidence collection must stay **bounded** and attributable
- access to diagnostics remains an authority surface, not an ambient side effect
- richer capture and wider export need explicit policy, leases, or approvals rather than silent escalation
- packet capture, when used, must stay a bounded `packet.capture.session` lane with `packet.capture.summary` as the normal review/export surface rather than ambient `.pcap` folklore (`docs/507-packet-capture-session-and-summary-first-export-boundary.md`, `docs/508-packet-capture-summary-review-surface-boundary.md`)
- redaction/export transforms remain deterministic and receipted
- incident/support bundles should be explainable artifacts, not mystery tarballs
- the official support handoff should remain timeline-first (`incident.timeline` + `incident.bundle` + `bundle.plan` + `bundle.payload.manifest` + `bundle.build.receipt`)

## What this fixes by profile

### A) Secure fleet host (`fleet_host`)

Default: `always-on`

- Fleet operability should not depend on remembering to enable tracing after the failure.
- The default is bounded local evidence that already exists when health gates, rollbacks, or incidents need it.
- The safety valve is not "collect nothing"; it is budgets, leases, and explicit receipts for richer capture or wider export.

### B) Secure workstation (`workstation`)

Default: `exportable`

- The user should be able to gather and share useful evidence without ambient root shells or support agents.
- Workstation support/export flows should remain recipient-visible and redaction-aware in the trusted UI.
- Richer capture is allowed, but it must feel like a conscious maintenance/support action, not ambient telemetry.

### C) General-purpose OS (`general_os`)

Default: `local-retained-explicit-export`

- General-purpose viability requires useful local evidence without assuming a vendor support backend or always-on collector.
- Local retention remains the baseline; remote collectors, richer tracing, and support agents stay optional and killable.
- This keeps C practical without redefining A/B/D posture.

### D) Appliance factory / regulatory (`appliance_factory`)

Default: `bundled-and-redacted`

- Production and regulatory environments need deterministic, reviewable evidence handoff more than they need live debugging streams.
- Minimal/redacted bundles match the archive’s existing export and offline-maintenance posture.
- Ambient vendor telemetry or long-lived live streams would undercut the production story, so they stay out of bounds by default.

## What this does **not** decide yet

This doc does **not** freeze:

- the exact inspect-tree producer API
- the exact flight-recorder backend or trace file format
- the exact retention sizes or sampling defaults
- the exact redaction taxonomy
- the exact journal-vs-snapshot store split

Those remain implementation details or future RFC/ADR material.

## Why this is worth locking now

This decision collapses a recurring ambiguity without inventing a new subsystem:

- A gets bounded always-on local evidence,
- B explicitly resists ambient support telemetry,
- C keeps local operability without remote-collector dependency,
- D gets a real bundle-oriented production evidence baseline.

That is enough to guide future specs and coding while keeping the archivist, tracing substrate, and bundle builders replaceable.

## Design cue from current systems

A few ecosystem lessons are stable:

- ETW is useful because bounded in-memory sessions make high-signal evidence available before the postmortem begins
- journald is useful because structured, indexed local logs beat grep-only folklore
- Fuchsia diagnostics is useful because logs and inspect trees are attributed and queried through one archivist surface
- OpenTelemetry is useful only when sensitive-data handling and export boundaries are treated as first-class concerns
- support-bundle tools are useful when the bundle is bounded and explainable, not an unreviewed root script

DeriveBSD should steal those lessons while keeping collection budgets, export lanes, and storage backends explicit.

Last updated: 2026-03-08r237
