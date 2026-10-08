# ADR 0001: Adopt ADRs + change control for a paranoid spec pack

- Status: **Accepted**
- Date: **2026-02-21**

## Context

This spec pack is large and security-sensitive. Unstructured changes risk silent drift, inconsistent claims, and unverifiable “evidence.”

## Decision

Adopt an ADR process and a maintainer change protocol:

- `../docs/150-maintainer-bootstrap-and-change-protocol.md`
- `../docs/152-adr-process-claims-and-evidence.md`

## Consequences

- Major decisions become reviewable and linkable.
- Regressions and drift are easier to detect.

## Follow-ups

- Add a claim/evidence matrix artifact.
- Add an external sources lockfile with sha256 pins.
