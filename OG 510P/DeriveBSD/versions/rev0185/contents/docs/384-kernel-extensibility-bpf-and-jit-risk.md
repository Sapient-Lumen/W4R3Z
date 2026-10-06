# Kernel extensibility: BPF/JITs and in-kernel programmability are authority

Most modern OSes have converged on “programmable kernel hooks” (BPF/eBPF, kprobes, tracepoints, packet filters, JITed rule engines).
This is a **productivity superpower** and a **security liability**: it turns “load a program” into “run untrusted code in the kernel”,
and the verifier/JIT become a giant, high-severity bug magnet.

DeriveBSD can keep the utility while making the risk **explicit, lease-gated, and reviewable**.

## The stance

- **Default:** no in-kernel programmable runtime for normal workloads.
  - No `bpf` device exposure in service jails/microVMs by default (already implied by devfs ruleset defaults).
  - Tracing/network capture happens via **mediated services** (portals/brokers), not raw kernel devices.

- **Optional lane:** if we support BPF/eBPF-like programmability, treat it as:
  1) a **UAPI surface** (registered/diffed),
  2) a **parser surface** (registered/diffed), and
  3) an **authority lease** (grant/receipt),
  with a clear “JIT off unless policy says otherwise” rule.

## Why this matters (greenfield advantage)

### 1) Verifiers are huge and historically fragile
Even when the verifier is correct, *proving* it is hard; and the failure mode is kernel compromise.
Greenfield advantage: we can require **stronger gates** and keep the lane optional.

### 2) “Observability” and “packet capture” are often the Trojan horse
Many systems accidentally treat kernel tracing/capture as “debug tooling”.
In practice, it is **cross-process visibility** and sometimes **cross-tenant** visibility.
Greenfield advantage: treat it as a portal with consent, retention limits, and audit receipts.

## Design: BPF is a leased, brokered capability

### Components
- **Tracing broker** (privileged compartment): owns the kernel interfaces.
- **Clients**: request actions via contracts (attach probe, capture packets, read counters).
- **Permission Center**: shows grants, expirations, and “why allowed”.

### Grants
A BPF-like grant must be explicit about:
- what hooks may be attached (which subsystem/tracepoint/probe family)
- whether read-only or state-mutating helpers are allowed
- allowed data egress and redaction constraints
- time/volume budgets (e.g., max events/sec, max bytes)
- whether JIT is permitted

### Receipts
Every attach/load produces a receipt linking:
- the requesting component id
- the contract surface digest
- the UAPI ids touched
- the parser ids involved (program format)
- whether JIT was used
- the budget + retention constraints

## Registry wiring (make drift reviewable)

If a BPF lane exists, it must appear in the existing drift surfaces:

- **UAPI registry/diff:** register kernel entrypoints used for program load/attach/query.
  - See: `docs/362-uapi-surface-registry-and-compat-gates.md`

- **Parser registry/diff:** register the program format(s) that are parsed/verified.
  - See: `docs/376-parser-surface-registry-and-fuzz-gates.md`

- **Authority diff:** a new “can load/attach kernel programs” edge must show up.
  - See: `docs/366-capability-graphs-and-authority-diff-surfaces.md`

- **Trust boundary graph/diff:** adding a “kernel programmable runtime” boundary should be visible.
  - See: `docs/380-trust-boundary-graphs-and-threat-diff.md`

## Product ergonomics (keep the good parts)

- Provide a **safe default UX**:
  - “capture packets” and “trace syscall latency” should be portal flows that don’t require hand-exposing `/dev/bpf`.

- Prefer **precompiled, reviewed probes** for common tasks.
  - Treat probe bundles as artifacts with attestations.

- Keep the “escape hatch” explicit:
  - Allow a privileged operator lane to load custom programs, but only via lease + receipts, with JIT off by default.

## Non-goals

- Treating in-kernel programmable runtimes as “normal app features”.
- Shipping a new bespoke verifier stack.

## References

- Linux Foundation: *eBPF Security Threat Model*:
  - https://www.linuxfoundation.org/hubfs/eBPF/ControlPlane%20%E2%80%94%20eBPF%20Security%20Threat%20Model.pdf
- “Verifying the Verifier” (CAV’23):
  - https://people.cs.rutgers.edu/~sn624/papers/agni-cav23.pdf
- SoK: *Challenges and Paths Toward Memory Safety for eBPF* (Oakland’25):
  - https://nebelwelt.net/files/25Oakland.pdf
- FreeBSD devfs advisory (illustrates why `bpf` devices are sensitive in jails):
  - https://www.freebsd.org/security/advisories/FreeBSD-SA-05%3A17.devfs.asc

Last updated: 2026-02-27r109
