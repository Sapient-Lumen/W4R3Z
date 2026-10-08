---
id: P-0248
title: CalDAV/CardDAV Interop & Evidence ShipKit — canonical DAV traces + sync scenario runner
status: idea
domains: [interop, calendaring, contacts, webdav, testing, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://datatracker.ietf.org/doc/html/rfc4791
  - https://datatracker.ietf.org/doc/html/rfc6352
  - https://crates.io/crates/libdav
  - https://crates.io/crates/kaldav
  - https://crates.io/crates/fast-dav-rs
---

## What it should provide others

A **portable, replayable interop harness** for CalDAV/CardDAV that makes “works on my client/server” problems debuggable across implementations.

The crate should give users:

- **Canonical DAV trace IR**: normalize PROPFIND/REPORT/PUT/DELETE sequences into a diffable event stream.
- **Scenario runner**: declarative “sync stories” (create/edit/move/merge/ACL/caldav scheduling basics) executed against real servers.
- **Evidence bundles**: `*.davbundle.zip` with redacted HTTP transcripts, parsed iCalendar/vCard payload summaries, and a stable verdict report.
- **Compatibility matrix tooling**: auto-generate “this server supports X, breaks Y” tables from bundles.

## Why this is still missing

There are functional clients/servers in Rust, but interop remains **ad hoc and non-portable**:

- CalDAV is standardized in RFC 4791 and CardDAV in RFC 6352, yet practical support varies widely across deployments.  
- Existing Rust crates (e.g., `libdav`, `kaldav`, `fast-dav-rs`) provide client implementations, but not a shared **interop+evidence layer** for CI and cross-project debugging.

## Design outline

### 1) Canonical trace model

Represent a session as:

- HTTP request/response frames (headers/body hashed or redacted)
- DAV method taxonomy (PROPFIND/REPORT/MKCOL/etc.)
- Parsed higher-level objects:
  - iCalendar components (VEVENT/VTODO) summary
  - vCard property summary
- Deterministic “semantic events” (create, update, delete, move, conflict)

### 2) Scenario DSL

Examples:

- “Create event → update DTSTART → fetch via REPORT calendar-query”
- “Create contact with PHOTO → server rounds/truncates → verify allowed behavior”
- “Move collection → verify href rewriting + ETag semantics”

### 3) Evidence bundle format (`davbundle`)

A bundle is a zip with:

- `manifest.json` (versions, redaction policy, client/server fingerprints)
- `trace.ndjson` (canonical frames)
- `objects/` (normalized iCal/vCard summaries)
- `verdict.json` (pass/fail + explanations)
- `notes.md` (human summary)

### 4) Adapter surface

- HTTP stack: `reqwest` + optional `hyper`
- Auth: basic + bearer; allow caller-provided auth handler
- Storage: optionally emit a local vdir snapshot for offline inspection

## Minimum lovable MVP (4–8 weeks)

1. Trace IR + `davbundle` writer/reader
2. 6–10 core scenarios (create/update/delete + one REPORT each)
3. One “server profile” runner that produces a compatibility report

## De-risk plan

- Start by running against two known servers and diff the IR.
- Implement redaction early (headers/body allowlist + hashing).
- Add “tolerances” (ETag differences, server-specific properties) as profile rules.

## Scorecard (0–5)

- Impact: 4
- Neglectedness: 3
- Feasibility: 4
- Adoptability: 4
- Sustainability: 3
- Differentiation: 5
