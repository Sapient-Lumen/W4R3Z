# Tracing and observability as evidence (trace sessions)

DeriveBSD already treats **audit logs** and **structured events** as evidence.
The next step is making *dynamic tracing* a first-class, policy-bound workflow: when you need more runtime visibility, you create a **trace session artifact**, run it under a lease, and capture outputs as evidence.

This bakes in the best lesson from DTrace: powerful observability can be production-safe and low overhead when probes are disabled.
Packet capture is a different stronger lane and should remain on the separate `packet.capture.session` + `packet.capture.summary` contract rather than quietly substituting for tracing (`docs/507-packet-capture-session-and-summary-first-export-boundary.md`, `docs/508-packet-capture-summary-review-surface-boundary.md`).

## Why this deserves groundfloor support

### 1) Debug authority is one of the most dangerous authorities
“Let me run tracing” is often equivalent to “let me exfiltrate secrets.”
So we treat tracing like any other privilege:

- it is **leased** (timeboxed)
- it is **scoped** (service/contract/jail/host)
- it is **receipted** (who, what, when)
- outputs are **structured and redacted deterministically**

This composes with `docs/192-observability-as-capability.md` and breakglass (`docs/236-breakglass-and-recovery-mode.md`).

### 2) Explanations need more than logs
Sometimes you need to answer questions like:

- “Which syscall pattern preceded the crash?”
- “Which lock or allocator path is hot?”
- “Why did this service restart loop?”

DTrace provides a generic interface to dynamic tracing and is designed to allow administrators/developers to ask arbitrary questions about system and program behavior.

## DeriveBSD model

### 1) Trace sessions are typed artifacts
A `trace.session` describes:

- scope (host vs service instance vs contract handle)
- tool/provider (DTrace, BPF, ktrace, audit)
- program/script digest (the query)
- sampling/retention constraints
- redaction profile

See: `spec/trace.session.schema.json`.

### 2) Start/stop produces receipts
Running a session yields a `trace.receipt` with:

- session digest
- start/stop timestamps
- actual privileges used (debug grant id)
- outputs produced (digests)

See: `spec/trace.receipt.schema.json`.

### 3) Outputs are evidence objects
`trace.output` is metadata for produced artifacts:

- format (`dtrace-agg`, `dtrace-text`, `bpftrace-json`, …)
- compression/encryption
- redaction transform digest (if applied)

See: `spec/trace.output.schema.json`.

### 4) Causality graphs can point at traces
A trace output digest is just another node in the `causality.graph`.
This lets an incident bundle carry *minimal* traces that actually explain the failure, without dumping gigabytes.

## Recommended “safe defaults”

- Prefer *aggregation* outputs (counts, latency histograms) over per-event streams.
- Default to short sessions (e.g., 30–120s) unless explicitly extended.
- Treat all trace output as sensitive by default; require explicit redaction profiles for export.

## Implementation notes (BSD-native)

- FreeBSD ships DTrace, and its handbook documents use for diagnosing performance problems and debugging unexpected behavior in kernel and userland.
- DeriveBSD can provide a small `derive trace` CLI that:
  - takes a `trace.session` spec
  - requests a debug lease (or breakglass)
  - runs tracing in a *confined* helper (jail/microVM)
  - stores outputs and emits receipts

Related:
- `docs/120-observability-explainability-dtrace.md`
- `docs/215-structured-event-log-as-evidence.md`
- RFC-0180


## References

- FreeBSD dtrace(1): https://man.freebsd.org/cgi/man.cgi?query=dtrace&sektion=1
- FreeBSD Handbook: DTrace: https://docs.freebsd.org/en/books/handbook/dtrace/
- Solaris Dynamic Tracing Guide: https://docs.oracle.com/cd/E19253-01/817-6223/index.html


Last updated: 2026-03-08r237
