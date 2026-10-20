# ADR 0051 — system.summary is coarse typed telemetry

Status: accepted  
Date: 2026-08-14

## Decision

`system.summary` is registered as command operation 2 and advertised bit 1. It is read-only,
restart-safe, and requires the signed `read_telemetry` authority capability. Its successful body is
exactly 40 bytes (`ISS1`, schema version 1): health, validity flags, uptime in whole minutes, total
and available memory in 64 MiB buckets, one-minute load in tenths, and process count. Twelve trailing
bytes are reserved and must be zero.

The schema contains no host name, user, address, machine identifier, mount, process name, command
line, kernel version, or free-form provider text. Linux collection uses `sysinfo(2)` behind a narrow
typed function. The deterministic command executor receives an immutable optional summary and has
no transport, filesystem, journal, or host-inspection handle.

## Rationale

Useful health telemetry need not reveal the identifiers and inventory commonly emitted by generic
system-information libraries. Fixed units, conservative bounds, reserved-byte validation, and exact
result lengths make the privacy and parser contracts reviewable. Reusing `read_telemetry` keeps both
harmless read operations separate from every mutation capability without expanding the signed
authority wire format.

## Consequences

- Tests inject exact summaries and do not depend on the CI host's values.
- Production values intentionally lose precision and are unsuitable for billing or forensics.
- Collection failure produces `internal_error`; it never falls back to a verbose host dump.
- Generic outbound issuance commits before transport, restart recovery reuses exact bytes, and the
  disposable command tree publishes both the canonical frame and typed result text.
