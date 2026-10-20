# ADR 0109: reserve and fence the protected route

- Status: accepted construction policy; product coordinator pending
- Date: 2026-08-21
- Scope: multi-route Ratox isolation, live-loss semantics, and bulk-worker cleanup
- Depends on: ADR 0059, ADR 0105, ADR 0106, ADR 0107, and ADR 0108

## Context

Four forced-TCP routes advanced 32 transfers at eight per route, but calling route zero “protected”
while it also carried eight bulk transfers was not repeatable. In correctly sequenced live-loss runs,
Ratox completed 40 samples once and then exceeded a five-second receive deadline on the next run.

Removing bulk from route zero eliminated the catastrophic stall, but one unpinned run still produced
a 506.113 ms outlier. Pinning the primary agent and probe to vCPU 0 and the three bulk agents to vCPU
1 produced a complete live-loss cell below the provisional 250 ms miss boundary.

Per-file cancellation also proved unreliable under active bulk. Serializing one cancel worker per
route removed local socket flooding but did not make every toxcore control succeed. The accepted run
received 10 successful replies and six errors. One route still had local transfer state and required
an identity-preserving worker recycle.

## Decision

1. A configured protected route carries Ratox and control only by default. Bulk is not admitted on
   it merely because nominal transfer capacity is unused.
2. Route protection includes a separately accounted CPU/service class. Transport identity alone is
   not a latency isolation boundary. The two-vCPU construction policy uses vCPU 0 for the primary
   agent and probe and vCPU 1 for auxiliary bulk agents.
3. The qualified local construction point while Ratox is active is 24 bulk transfers: eight on each
   of routes one, two, and three. Recovering route-zero bulk capacity requires later evidence and an
   explicit scheduler policy.
4. Loss of an active route purges its process-local toxcore transfers. IoTox does not reassign those
   transfers. Restart from unchanged savedata must recover the same route identity, establish a new
   confirmed application session, and begin with an empty transfer set.
5. Per-file cancel is attempted once as best-effort cleanup. If a bulk worker remains non-empty, the
   coordinator fences and restarts only that worker. It cannot mark the route ready until identity,
   TCP/application confirmation, and empty local transfer state are proved.
6. Worker restart is reclamation, not transfer continuation. Future reassignment operates only on
   stable immutable object identities after the old attempt is fenced.

## Evidence

The verified compact proof is `.sandwurm/exports/pairs/pair.0xk33kco` (180 KiB). It records 24 active
transfers, 8 faulted, 16 unaffected and progressed, zero reassigned, same-identity recovery on both
sides, and all four routes confirmed at evidence release. Ratox rendered 40/40 exact samples with
p50 111.045 ms, p95 164.825 ms, and maximum 232.356 ms. Cleanup attempted 16 controls, received 10
successes and 6 errors, then recycled one still-non-empty client bulk worker; the total route restart
count was two including recovery of the deliberately faulted device worker.

## Consequences

- The first product coordinator needs route-role admission and resource placement, not only a list
  of Tox identities.
- Capacity reporting must distinguish protected reservation from schedulable bulk capacity.
- Cancellation errors are operator-visible evidence; successful worker fencing can reclaim state but
  cannot retroactively turn those controls into successes.
- The 232.356 ms maximum is a narrow construction pass, not comfortable production headroom. The
  separate 1,000-sample matrix and long-running churn gates remain required.
- Single-route operation remains unchanged when no multi-route policy is configured.
