# ADR 0155: Separate Ratox render timing from live queue evidence

Status: accepted, 2026-08-24.

## Context

The first 1,000-sample direct-UDP cell beside one active 1 GiB file transfer completed 457 exact
terminal round trips and then failed its evidence deadline. The stopped client disk showed that the
terminal and owner queue had continued correctly: all 914 INPUT/`OUTPUT_ACK` operations executed,
the interactive queue p99 upper bound was 1.047 ms, and its maximum wait was 13.022 ms.

The probe had treated the disposable runtime `status` file as a synchronous counter interface. File
progress is deliberately coalesced, and a large transfer can leave its event worker behind a long
queue of required chunk bookkeeping. The projected file therefore remained at the pre-ACK counter
even though the owner thread had executed the ACK. The probe also waited for that evidence before
copying returned bytes through its local pseudoterminal, adding observability delay to the value it
called input-to-render latency.

## Decision

`Agent::snapshot()` overlays the current atomically readable transport statistics on its coherent
in-memory snapshot. Ordinary owner-private authenticated `inspect` therefore reports live counters
even when the disposable filesystem projection is intentionally behind. A separate bounded local
control operation returns only the interactive executed count and cumulative queue wait as two
big-endian 64-bit integers. The probe uses this exact 16-byte response instead of rendering and
parsing the complete status surface for every INPUT and ACK. This does not make every other snapshot
field synchronous and does not change the runtime-tree coalescing contract.

The Ratox terminal probe uses that local control operation to obtain the cumulative interactive
execution and queue-wait counters. For every serialized trial it:

1. timestamps and sends one INPUT;
2. receives and validates the exact remote PTY byte;
3. copies that byte through the local pseudoterminal and timestamps render completion;
4. obtains the exact INPUT queue-wait delta from live counters;
5. sends `OUTPUT_ACK` and observes its execution before admitting the next INPUT.

Control inspection happens after render and is therefore outside the measured input-to-render
interval. The lab guest retains probe stderr in its explicit failure record, and the pair driver
stops immediately on that record instead of waiting for the outer capture timeout.

## Consequences

- Per-INPUT owner-queue evidence remains exact without making a disposable file an acknowledgement
  channel.
- Per-trial inspection has fixed 16-byte response work instead of repeatedly rendering the full
  Agent snapshot.
- Terminal latency no longer includes runtime-tree publication or evidence-reader work.
- Trials remain serialized and uncontaminated: the next INPUT is withheld until the previous ACK is
  visible in the live execution counter.
- The local control connection and inspection work occurs between samples. It can affect experiment
  cadence and host load, so the capture still records a complete-service product path rather than a
  bare transport microbenchmark.
- Ratox wire framing, cumulative acknowledgement semantics, and the frozen v1 protocol are
  unchanged.

## Evidence

- `tools/ratox-terminal-probe.py --self-test` covers the bounded local control header and counter
  parser in addition to the terminal frame and pseudoterminal checks.
- The owned 29-group registry passes after the live-snapshot and probe changes.
- The failed `direct-udp / ratox-matrix-bulk-1` root `pair.4jwreld_` is diagnostic only and is not an
  accepted pair proof; its stopped disk supplied the content-free counter diagnosis above.
