# Packet capture local-artifact metadata and retention boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Bundles  

`docs/507-packet-capture-session-and-summary-first-export-boundary.md` already made capture lease-shaped,
`docs/508-packet-capture-summary-review-surface-boundary.md` made summary the normal review/export surface,
and `docs/509-packet-capture-selector-compiler-boundary.md` kept capture intent typed.
This doc fixes the next quiet place packet-capture folklore comes back:
**the local raw capture artifact itself.**

See also:
- ADR: `adrs/ADR-0100-packet-capture-local-artifact-metadata-and-retention-boundary.md`
- stronger raw-packet authority lane: `docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md`
- packet-capture session/export contract: `docs/507-packet-capture-session-and-summary-first-export-boundary.md`
- packet-capture summary surface: `docs/508-packet-capture-summary-review-surface-boundary.md`
- packet-capture selector/compiler boundary: `docs/509-packet-capture-selector-compiler-boundary.md`
- support/export lane: `docs/251-export-policies-and-support-bundle-portal.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- session schema: `spec/packet.capture.session.schema.json`
- summary schema: `spec/packet.capture.summary.schema.json`

## Why this needs a hard decision

It is easy to say "summary-first export" and still lose the boundary in practice.
The usual failure mode is simple:

- a local `.pcap` or `.pcapng` file becomes the *real* object people keep,
- tool-specific filenames become the retention policy,
- capture-file comments or sideband metadata start carrying the explanation instead of typed evidence,
- and a file format capable of carrying decryption material quietly turns a support artifact into a secret bundle.

DeriveBSD needs a narrower answer:
**local raw capture files are allowed only as bounded opaque evidence, not as the place where meaning, naming, or decryption state lives.**

## Accepted boundary

Across all profiles:

- `packet.capture.session` remains the authoritative pre-capture review object,
- `packet.capture.summary` remains the normal compact review/export object,
- local raw capture files are referenced by digest only rather than by path or filename,
- session policy must carry a retention budget through `retention.max_local_retention_seconds`,
- each local raw artifact reference must say both `metadata_posture` and `retention_until`,
- and Derive-generated artifacts default to `metadata_posture = packet-records-only`.

That keeps packet files from quietly becoming the archive's real metadata surface.

## Canonical typed additions

`packet.capture.session.retention` now carries:

- `local_storage` — where the local raw artifact may live
- `max_local_retention_seconds` — the maximum allowed lifetime for Derive-managed local raw artifacts after capture ends

`packet.capture.summary.artifacts.local_capture_artifacts[]` now carries:

- `digest`
- `format`
- `storage`
- `metadata_posture`
- `retention_until`

This is intentionally enough to review the boundary without making filename or local directory layout authoritative.

## Metadata posture vocabulary

### `packet-records-only`

The artifact carries packet records and minimal file framing only.
It does **not** carry sideband comments, name-resolution blocks, or embedded decryption material.
This is the normal Derive-generated posture.

### `sideband-metadata-present`

The artifact contains extra capture-file metadata beyond packet records.
That is stronger than the normal Derive-generated posture because it can smuggle explanation, identities, or other sideband context outside the typed `packet.capture.summary` surface.

### `decryption-material-present`

The artifact embeds packet-decryption material or equivalent secrets.
That is a stronger lane still.
Such artifacts must not quietly flow through ordinary incident/support handoff paths.

### Stronger compatibility/import states

`sideband-metadata-present` and `decryption-material-present` are **compatibility / imported-artifact states**, not the normal Derive-generated posture.
The official handling boundary for them is `docs/511-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md`, which keeps them on a typed safe-open import lane and normalizes before ordinary promotion.

## Product-shape defaults

| Profile | Default local-artifact posture | Practical meaning |
|---|---|---|
| **A fleet_host** | `sealed-local + packet-records-only + short bounded retention` | Oncall capture can exist briefly, but the handoff object stays the summary and the raw artifact expires on schedule. |
| **B workstation** | `trusted-host-local + packet-records-only + user-visible retention` | Local troubleshooting stays viable without normalizing stealthy packet-file hoarding or sideband metadata drift. |
| **C general_os** | `explicit-local-admin compatibility allowed, derived workflows stay packet-records-only` | Legacy tools remain viable, but the Derive-managed lane still has one strict default. |
| **D appliance_factory** | `sealed-local-or-none + packet-records-only + shortest practical retention` | Production/regulatory images keep raw artifacts tightly bounded and do not turn packet files into support bundles by accident. |

## Review guidance

When reviewing a packet-capture change that mentions local raw artifacts, ask:

1. Is the authoritative meaning still in `packet.capture.session` and `packet.capture.summary`, rather than in filename or capture-file comments?
2. Does every retained raw artifact have an explicit `retention_until` bounded by the session's `max_local_retention_seconds`?
3. Is `metadata_posture` still `packet-records-only`, or is the proposal widening into a stronger compatibility/import lane?
4. If sideband metadata or embedded decryption material appears, is it called out as a stronger review/export risk instead of a casual implementation detail?
5. Does the target profile still get the packet-capture posture it claims under incident pressure?

## Why this is worth locking now

This is not a new subsystem.
It is a small entropy cut that keeps the already-accepted packet-capture lane honest:

- A keeps incident capture without turning packet files into ambient support artifacts,
- B keeps trusted-host troubleshooting visible and bounded,
- C preserves compatibility without weakening the strict default,
- D keeps the appliance/regulatory story credible.

That is enough to move the archive closer to implementation without prematurely standardizing every storage backend detail.

Last updated: 2026-03-09r240
