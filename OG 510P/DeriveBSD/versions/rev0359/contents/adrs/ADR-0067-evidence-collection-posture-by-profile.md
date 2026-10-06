# ADR-0067: Evidence collection posture by profile

Date: 2026-03-06
Status: Accepted

## Context

DeriveBSD already has the ingredients for a coherent evidence and diagnostics story:
`docs/229-evidence-spine-overview.md`, `docs/215-structured-event-log-as-evidence.md`,
`docs/216-incident-snapshots-and-support-bundles.md`, `docs/302-structured-diagnostics-inspect-trees.md`,
and `docs/303-flight-recorder-tracing-and-budgeted-diagnostics.md` define typed event logs, bounded support bundles,
structured diagnostics trees, and budgeted flight recorders.

What the archive still lacked was a **product-default boundary** for when evidence collection is normal,
when it must stay local and user-mediated, and when bundles are the contract instead of live streams.
Without that boundary, the same evidence vocabulary drifts into contradictory defaults:

- fleet hosts either under-collect and become miserable to debug or over-collect without a budget story,
- workstation support quietly turns into ambient telemetry or background uploads,
- general-purpose installs inherit hidden collector/support-agent dependencies they never asked for,
- and factory/regulatory images claim redaction discipline while still assuming live diagnostic streaming.

## Decision

DeriveBSD will treat **evidence collection posture** as a first-class, profile-shaped default captured in
`spec/examples/product.profiles.json` under `evidence` and guarded by `tools/check_product_profiles.py`.

This posture covers the default handling of:

- structured event-log retention and whether bounded local collection is expected,
- inspect-style diagnostics and flight-recorder availability as normal local evidence,
- whether richer capture or external sharing is ambient vs explicit,
- and whether incident/support bundles are the primary evidence handoff contract.

The default values are:

- **A / `fleet_host`**: `always-on`
- **B / `workstation`**: `exportable`
- **C / `general_os`**: `local-retained-explicit-export`
- **D / `appliance_factory`**: `bundled-and-redacted`

## Meaning by profile

### A) Secure fleet host (`fleet_host`)

- Bounded local evidence collection is normal: structured event logs, inspect snapshots, and small flight recorders should exist by default.
- Richer retention or export scope changes remain policy-shaped and receipted.
- Fleet operability should not depend on turning on ad-hoc tracing after the incident has already happened.

### B) Secure workstation (`workstation`)

- Local evidence should be useful and user-exportable by default.
- Richer capture, external sharing, or long-lived support upload paths must stay trusted-UI-visible rather than ambient.
- The workstation should not quietly degrade into background telemetry or invisible support-agent folklore.

### C) General-purpose OS (`general_os`)

- Useful local evidence is retained by default.
- External sharing, remote collectors, and richer tracing remain explicit choices rather than hidden prerequisites for viability.
- C keeps compatibility real by refusing to require always-on vendor support plumbing as the price of operability.

### D) Appliance factory / regulatory (`appliance_factory`)

- Production evidence is bundle-oriented and redacted by default.
- Deterministic incident/support bundles are the normal handoff surface, not ambient live streams.
- Live diagnostic streaming or open-ended telemetry remains absent from production posture unless explicitly approved.

## Consequences

### Positive

- The archive now has a stable answer to "what evidence is present by default?" across A–D.
- Workstation posture explicitly resists ambient telemetry drift while still preserving humane support/export flows.
- Factory/regulatory posture now matches the archive’s existing redaction/minimal-export claims instead of undermining them.

### Negative / trade-offs

- This adds one more stable profile knob that must remain small and guardrailed.
- Exact diagnostics APIs, retention sizes, and storage backends remain open implementation work.
- Fleet always-on posture still requires budget discipline so operability does not become surveillance-by-accident.

## Non-goals

This ADR does **not** decide:

- the exact inspect-tree API for every language,
- the exact flight-recorder backend (custom rings vs DTrace vs ktrace hybrids),
- the exact redaction taxonomy,
- or the exact storage split between journal segments, snapshot stores, and bundle payload blobs.

Those remain implementation work or future RFC/ADR material.

## Why this shape

The coherence win is not "always collect everything" and it is not "collect only when support asks."
It is deciding that:

- A defaults to always-on bounded local evidence,
- B defaults to user-exportable local evidence with trusted-UI-visible expansion,
- C defaults to local retention with explicit export/collector choice,
- D defaults to redacted bundle-oriented production evidence.

That is enough to guide future specs and coding without prematurely freezing the archivist, exporter, or tracing substrate.
