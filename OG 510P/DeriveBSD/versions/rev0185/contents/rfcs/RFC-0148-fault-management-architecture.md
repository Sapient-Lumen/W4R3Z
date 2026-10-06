# RFC-0148: Fault management as evidence + self-healing (FMA lessons)

Status: **Draft**  
Last updated: 2026-02-24

## Problem

DeriveBSD has strong primitives for:
- reproducible artifacts
- explicit authority
- health-gated activation and rollouts

…but it currently lacks a first-class model for **hardware/service faults**.
Without this, we risk:
- “log archaeology” as the default workflow
- health probes that miss important failure modes
- ad-hoc automation with unclear audit trails

## Proposal

Add an optional subsystem, `derive-fmd` (name placeholder), inspired by Solaris/illumos FMA:

1) **Detectors** emit structured events (kernel, ZFS, SMART, service probes)
2) `derive-fmd` normalizes them into signed evidence objects (`fault.event`)
3) Pluggable diagnosis engines emit `fault.diagnosis` objects (“suspect lists”)
4) A tamper-evident **fault ledger** persists events/diagnoses and supports export
5) Policy-controlled response agents can emit receipts for actions taken

## Evidence objects (v0)

- `fault.event` (signed)
- `fault.diagnosis` (signed; references event digests/ids)
- `fault.snapshot` (signed summary for health gating)

Schemas:
- `spec/fault.event.schema.json`
- `spec/fault.diagnosis.schema.json`
- `spec/fault.snapshot.schema.json`

## Policy and gating

- Policy may classify fault types into:
  - ignore / warn / block-commit / block-boot (extreme)
- `boot.health.report` should include a check that references a `fault.snapshot` digest.
- Fleet rollouts may also gate promotions based on fault state.

## Implementation sketch (non-normative)

- Event ingestion:
  - `devd` → normalized events
  - ZFS zevents → normalized events
  - optional: BMC/IPMI telemetry as a detector (carefully scoped)
- Storage:
  - ZFS dataset storing canonical JSON objects + a signed checkpoint chain
- Diagnosis:
  - small rules (match on event class + thresholds) → diagnosis objects
  - optional “knowledge base” linkouts, but keep core logic local and auditable

## Non-goals (v0)

- predictive ML maintenance
- replacing existing monitoring stacks
- automated repairs that require complex, non-auditable logic

## References

- Solaris fault management overview: https://docs.oracle.com/cd/E36784_01/html/E48546/gliqg.html
- Joyent RFD (FMA background): https://github.com/joyent/rfd/blob/master/rfd/0006/README.md
- OpenZFS event docs: https://openzfs.github.io/openzfs-docs/man/v2.0/5/zfs-events.5.html
- Oxide RFD 26 (illumos FMA notes): https://26.rfd.oxide.computer/

