# RFC-0151: Incident snapshots and support bundles (`incident.bundle`)

Status: Draft

## Summary

Define an incident/support bundle as a first-class DeriveBSD artifact:

- `incident.bundle` (evidence object) — describes what was captured, why, and how it is packaged
- bundle payload blob — a bounded archive referenced by digest (optionally encrypted)

Integrate with existing evidence lanes (`svc.snapshot`, `fault.snapshot`, `event.segment`, policy decisions) and deterministic redaction transforms.

## Motivation

Operational reality:
- support asks for logs and configs
- engineers ask for “what changed” and “what happened”
- crash reports are useful but often leak secrets

Most ecosystems solve this late via ad-hoc tools (`sosreport`, Apport, ABRT).
DeriveBSD can do better by making “incident context”:

- structured
- bounded
- verifiable
- capability/policy governed

## Design

### 1) Evidence object: `incident.bundle`

Schema: `spec/incident.bundle.schema.json`.

Minimum required fields:
- `kind`, `bundle_version`, `created_at`
- `host.host_id`, `host.generation_digest`
- `payload.format`, `payload.file_digest`

Recommended fields:
- `trigger` (manual / fault / crash / health-gate rollback)
- `scope` (time bounds, inclusion toggles, size limits)
- `includes` (digests for snapshots + event segments + decisions)
- `redaction.transform_digest` (when exporting)

### 2) Payload format

Default payload format: `tar.zst`.

Payload contents should be opinionated:
- prefer embedding **evidence objects** (JSON) and **references** (digests)
- include raw bytes (coredumps, traces) only when explicitly enabled

### 3) Privacy + policy

- Core dumps/memory captures MUST be off by default.
- Policy MAY require:
  - encryption-for-recipient
  - mandatory redaction receipts for exports
  - caps on size and time range

### 4) Collection compartment

The collector should run as a supervised service (service jail) with:
- capability-gated read access to the event journal and snapshots
- no ambient filesystem traversal

## Compatibility

This RFC does not require adopting systemd or Linux crash tooling.
It only standardizes the DeriveBSD evidence surface.

## Open questions

- Preferred encryption modes (`age` vs CMS/PKCS7 vs PGP) for “encrypt-for-support”.
- Where to store large coredumps (store vs state dataset) and how to GC.
- Whether to add a separate `incident.bundle.request` capability flow.

