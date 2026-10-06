# RFC-0130: Deterministic redaction transforms (privacy filtering as evidence)

Status: **draft**

## Motivation

Telemetry and debugging artifacts often contain sensitive data.
Most systems rely on:

- ad-hoc scrubbing scripts
- best-effort denylist filters
- “don’t export logs” as the only privacy control

DeriveBSD wants artifacts that are shareable and verifiable.
That requires redaction to be:

- deterministic
- versioned
- auditable

## Goals

- Define a signed, digestable representation of a redaction profile.
- Define a receipt that proves which redaction was applied.
- Allow reuse across observability, crash artifacts, and replay capsules.
- Support both declarative rules and sandboxed modules.

## Non-goals

- Designing a full data-loss-prevention system.
- Guaranteeing perfect secret detection.
- Replacing upstream application-side scrubbing.

## Proposal

### 1) Evidence object: `redaction.transform`

Schema: `spec/redaction.transform.schema.json`

Represents a redaction profile as a signed artifact.
Two common forms:

- **declarative**: allowlists + basic masking rules
- **module**: a sandboxed transform (Wasm) with a tiny ABI

Transforms SHOULD be compiled from human policy sources (HuJSON → canonical JSON → artifact).

### 2) Evidence object: `redaction.receipt`

Schema: `spec/redaction.receipt.schema.json`

Binds:

- `input_digest`
- `output_digest`
- `transform_digest`

Optionally includes small summary counters (fields removed, spans dropped), but heavy data is referenced by digest.

### 3) Integration points

- `trace.stream.grant.constraints.redaction_profile_digest`
- `trace.capsule.redaction`
- `debug.record.grant.constraints.redaction_profile_digest`
- `debug.replay.capsule.redaction`

### 4) Operational invariants

- Prefer allowlist-first transforms.
- Redaction transforms are reviewed like any other policy artifact.
- Forensics mode requires explicit grants and should generate additional receipts.

## References

- OpenTelemetry guidance: handling sensitive data (processors, filtering): https://opentelemetry.io/docs/security/handling-sensitive-data/
- Redaction processor reference: https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/processor/redactionprocessor/README.md
