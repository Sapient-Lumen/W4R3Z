# RFC-0159: Crash artifacts and symbolication as evidence (crash-report / crash-event)

Status: draft  
Last updated: 2026-02-24

## Problem
Crashes are inevitable. What fails ecosystems is that crash handling becomes:
- opaque (strings in logs)
- unsafe (core dumps leak secrets)
- irreproducible (symbolication depends on whatever symbols happen to exist)
- hard to correlate (no ids tying crashes to changes, services, faults)

DeriveBSD’s “ops evidence spine” should treat crashes as first-class evidence.

## Goals
- Emit a **metadata-first** `crash-report` evidence object for crashes across domains (service/kernel/hypervisor/VM).
- Emit a typed `crash-event` into the structured event journal.
- Make symbolication reproducible:
  - artifacts embed build-ids
  - debug symbols are distributable as store outputs
  - symbolication emits a receipt-like trace (sources used, build-ids resolved)
- Make the safe path the default:
  - crash reports are shareable metadata
  - dumps are policy-gated and explicitly requested

## Non-goals
- Mandating a single crash backend (minidump vs full core vs kernel dump). The report points to whatever was captured.
- Replacing full observability tooling (DTrace/audit). Crashes are one high-signal lane.

## Artifacts

### `crash-report` (evidence)
A stable object representing “a crash happened”, with:
- identity: crash_id, timestamp, host generation
- subject: service_id / pid / vm_id / kernel
- crash signature: signal/exception code, optional stack hash
- artifact pointers: digests for core/minidump/kernel-dump (optional)
- correlation: change_id, fault_id, event ids (optional)
- privacy flags and redaction receipts (optional)

Schema: `spec/crash.report.schema.json`.

### `crash-event` (typed event)
A structured event for journal queries and correlation.

Schema: `spec/crash.event.schema.json`.

## Symbolication model (build-id first)
- Every executable and shared object should expose a stable build-id.
- Debug info should be publishable and fetchable by build-id (debuginfod-like ergonomics).
- Symbolication should record:
  - which symbol sources were consulted
  - what was resolved
  - what was missing

(Exact “receipt” schema is deferred; the initial version stores this in `crash-report.artifacts.symbolication`.)

## Integration points
- Service supervisor emits crash reports and crash events.
- Fault manager can classify “crash loop” and attach crash ids to diagnosis.
- Incident bundles include crash reports by default; dump payloads only when explicitly enabled.
- Change sets can reference crash spikes as gate signals (future work).

## Open questions
- Do we want a dedicated `crash-policy` object, or fold dump capture policy into the existing config/policy engine?
- Preferred dump format(s) for each domain:
  - userland: minidump vs ELF core
  - kernel: minidump vs full dump
  - VM: guest dump vs host-side capture
- How far should the OS go in automatic symbolication vs exporting data for external pipelines?

