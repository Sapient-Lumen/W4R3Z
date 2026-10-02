# ADR 0105: round-robin pinned toxcore file service

- Status: accepted and implemented
- Date: 2026-08-20
- Scope: source-linked c-toxcore finite-file fairness
- Depends on: ADR 0058 and ADR 0070

## Context

The genuine forced-TCP Ratox interference cell admitted sixteen 1 GiB file transfers but advanced
only four inside the outer 240-second completion bound. c-toxcore 0.2.23 supports 256 file pipes per
friend, yet its chunk-request loop always scans from slot zero and stops when the per-friend crypto
send window is full. A small relay send window therefore repeatedly favors low slots.

## Decision

1. Carry one minimal patch over the exact pinned 0.2.23 archive. Add a zero-initialized cursor to each
   friend and begin each file-service pass after the last transfer that received a chunk request.
2. Do not enlarge the crypto queue or reduce c-toxcore's reserved non-file packet slots.
3. Name the linked provider `0.2.23+iotox-file-rr1` in build configuration, pair receipts, and the
   captured runtime origin. Verification rejects disagreement.
4. Preserve the ordinary IoTox limit of 32 active sends and receives. Higher laboratory populations
   remain explicit opt-ins.
5. Treat 32-stream forced-TCP delivery as a separate route-layer limit: all 32 resumes and sender
   chunk admissions completed, but data from only 17 lanes reached the client inside the bound.
   Evaluate bulk striping across multiple Tox routes before another single-route 64 cell.

## Evidence

The unchanged forced-TCP 16-stream cell moved from 4/16 progressed lanes on stock 0.2.23 to 16/16 on
the patch. The final provenance-bound compact proof is
`.sandwurm/exports/pairs/pair.e_i79q7a`; all 40 terminal renders were exact, p95 was 41.108 ms,
owner-queue p99 was 0.041 ms, all lanes advanced after 18 ms, and cancellation emptied in 258 ms.
The patch SHA-256 is
`fb4080c26a9e04753681376b721d5ab0570202e4e78a32e17a9f6d18e7e0d2ed`.

## Consequences

- IoTox's source-linked provider is no longer byte-identical to upstream 0.2.23 and must never be
  reported without its variant.
- Direct-UDP construction evidence from the upstream provider remains historical. The named provider
  is independently requalified through the ordinary 32-transfer limit; its 64-transfer laboratory
  opt-in does not reach all-lane progress inside the global bound.
- The patch improves fairness without claiming aggregate throughput, route independence, upstream
  acceptance, or correctness beyond the retained topology and counts.
