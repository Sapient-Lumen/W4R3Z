# ADR 0291: Add authenticated content-free diagnostics

- Status: accepted and implemented
- Date: 2026-09-01

## Context

IoTox has detailed disposable runtime projections and purpose-built retained experiment evidence, but
neither is an appropriate support artifact. Copying runtime trees or logs can disclose peer identity,
terminal content, filenames, topology, credentials, and local paths. A crash-local ring that is not
authenticated can be silently edited. Conversely, putting a stable device signature in a shareable
bundle creates a long-lived correlator and conflicts with the accepted identity-free export.

## Decision

Add one bounded canonical `diagnostics-flight-v1` store. Every fixed-size record uses only closed
event/phase/network/status fields, a closed flag mask, a structural redacted-configuration
commitment, and ten content-free counters. The whole state is stable-device-signed and crash-
atomically replaced. Opening an existing store verifies its expected device, canonical bytes,
permissions, size, contiguous sequence, and tail accounting. Default retention is 128 records with a
reviewed 16..256 range. Startup commits `security-ready` fail-closed; later write failures are
best-effort and explicitly counted.

Add empty-payload same-user local-control v1.49 operation 108. The Agent returns a strictly parsed
redacted projection, not the signed store. `diagnostics-export PATH` validates that response, wraps
it with version/revision and a domain-separated payload digest, validates again, and creates a new
mode-0600 no-follow/no-clobber file. `diagnostics-inspect PATH` performs the same canonical and digest
validation offline.

When a maximum 256-record local tail with full-width counters cannot fit the 48 KiB redacted-control
ceiling, export retains the newest fitting suffix and binds an explicit `export-omitted-records`
count. It never mutates or silently shrinks the signed local store.

Exclude identities, addresses, friend numbers, content, terminal bytes, commands, filenames,
namespace names, paths, endpoints, credentials, keys, signatures, ledger records, raw configuration,
and time. Commit only a closed path/key/endpoint-free structural policy projection. Keep timestamps
out rather than pretending that removing payload makes a detailed chronology anonymous.

The exported digest is integrity framing, not authenticity. The shareable artifact intentionally
cannot be verified back to a device. The signed local store has no independent rollback witness and
does not resist replay of an older valid copy. Dedicated namespace health and normalized host-
capability aggregation remain later joins rather than reasons to ingest arbitrary current logs.

## Consequences

An operator can obtain a bounded, inspect-before-share support record without granting a diagnostic
collector filesystem access or copying payload. A corrupted or foreign local ring prevents Agent
startup; an operational post-start recorder failure is visible without taking the remote-control
plane down. The ring adds one crash-atomic signed write per retained transition and is therefore for
sparse state changes, not high-rate telemetry. Ratox, sync, authority, and peer framing are unchanged.

Two owned registry checks freeze store signing/bounding/tamper refusal and export privacy/bundle
canonicality. The one-binary process gate crosses live Agent export, offline inspection, private
mode, size, redaction, and destination no-clobber behavior.
