# Wake from amnesia — rev0024 relayticket/gossipsieve/clockguard

Start here after sleeping:

1. Read `docs/213-rev0024-interestmix-routeattest-gatefold.md` as the merged rev0024 snapshot.
2. Read `docs/222-clock-guard-and-time-window-pressure.md` before trusting any TTL/sequence-bearing object.
3. Read `docs/223-relay-ticket-garden-capacity-boundaries.md` before designing relay, wake, or garden gateway behavior.
4. Read `docs/224-gossip-sieve-before-expensive-work.md` before admitting route/provider/witness hints.
5. Read `docs/225-branchlet-fold-audit-refactor.md` before pruning historical branchlets.

The rev0024 mood:

```text
Helpful entrances are not harmless entrances.
```

The next risky frontier is to connect these admissions to queue scheduling and cover work so that metadata budget, relay capacity, useful refusal, and gossip pressure share one local planner.
