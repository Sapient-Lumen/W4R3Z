# ADR 0260: Qualify selected actual-Tor content-worker loss

Status: accepted, 2026-08-30

## Context

ADR 0259 proved that two independently authorized publishers could contribute complementary
objects through two exact actual-Tor workers while writer authority and HEAD remained on native
primary sessions. It did not prove the safety boundary when one selected worker disappeared after
positive content progress.

Content-v2 already froze every source onto one carrier before HEAD dispatch and specified that exact
carrier loss fails the whole job. The qualification seam could stop the first eligible worker after
a byte threshold, but could not name a route. Recovery accounting also tracked ordinary sync jobs
only. A content-only fault could therefore fail the content job without giving the selected worker's
bounded restart policy a complete affected-job population.

## Decision

Add the qualification-only `--qualify-route-stop-worker KEY` selector. It is valid only with
`--qualify-route-stop-after-bytes`, must name one signed auxiliary bulk member, and arms the existing
one-shot fault only for a transfer on that exact route. Owner-private status exposes the selected
route, stopped worker incarnation, positive byte position, carrier-loss count, reassignment count,
affected-job count, and recovery count.

Include content-v2 subscriber jobs in the qualification fault population. The worker may consume its
one signed restart only after every affected ordinary sync and content job is terminal. A content job
is terminal only when complete, failed, or cancelled. Recovery creates a new worker incarnation for
the same signed route; it does not revive, rebind, or continue the failed content job.

Accept the Sandwurm `sync-content-multi-route-actual-tor-loss` gate. It reuses ADR 0259's two native
publisher authority sessions and two exact Tor workers, targets the second worker, and stops it only
after at least 65,536 received bytes. Acceptance requires:

- positive committed-object and fetched-byte progress before the fault;
- whole-job failure with the exact auxiliary-carrier-loss reason;
- empty transient staging, no accepted HEAD, and no activation;
- exactly one carrier loss, zero reassignment, and one affected job;
- the same signed route returning under a different worker incarnation after one restart;
- unchanged native primary session epochs;
- no native downgrade, same-job rebinding, or implicit retry; and
- convergence only through a distinct explicit `sync-pull-multi-route` job.

This changes no peer framing, route-set encoding, local-control operation, authority rule, or default
runtime behavior. Both qualification flags remain inert unless explicitly supplied by the lab.

## Evidence

Accepted compact proof `pair.w31xqgd_` records:

- fault route
  `478CD68E0D2035CD1B63CC07558070EBEA7897DAB135896115BB85B524E23C1A`;
- worker incarnation `2197901807973525542` stopped at 72,663 bytes and recovered as
  `17674373597288179784`;
- two committed objects and 528 fetched bytes before whole-job failure;
- one carrier loss, zero reassignment, one worker recovery, and unchanged native epochs `1/1`;
- failed job `9581108307482772732` and distinct replacement job `6950339517546930232`;
- four primary-source and three secondary-source objects in the successful replacement pull;
- two Tor instances, authenticated three-hop circuit observations, and eight successful guest source
  streams; and
- zero unexpected-context packets in both TAP captures.

The same source-linked binary SHA-256
`efc0b415f4198a67949ab7fce70b5c30f83c6cff3c6b69d4262b46ba9674fa04` appears in both guest
receipts. The independent verifier accepts both the raw proof and its 15,958,016-byte compact
export. See `../evidence/2026-08-30-sandwurm-sync-content-actual-tor-loss.md`.

## Consequences

The selected-worker-loss safety gate is closed: routed multi-source content fails closed without
downgrading authority or bytes, exact route capacity can recover independently, and retry is an
explicit new transaction. Verified CAS objects remain reusable immutable truth, but partial staging,
the failed FileId/CTA1 attempt, and the failed job are not resumed.

This is one same-computer, two-VM, one-public-Tox-target, one-time-window mechanism result. It does
not prove transparent failover, same-source multi-lane striping, byte striping, performance gain,
per-source circuit or physical-path diversity, anonymity, I2P content-v2, Agent-restart recovery, or
behavior across physical hosts. Comparative multi-lane science is the next content frontier.
