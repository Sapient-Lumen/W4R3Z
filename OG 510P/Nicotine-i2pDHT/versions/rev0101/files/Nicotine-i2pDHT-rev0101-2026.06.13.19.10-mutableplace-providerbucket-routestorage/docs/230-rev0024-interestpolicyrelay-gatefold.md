# rev0024 — interestpolicyrelay-gatefold

This revision intentionally folds three live rev0024 lanes instead of pretending only one branchlet happened.

## Risk-first lanes

1. **Interest / route / gate**: interest-mixing pressure, route-attestation capture checks, and dispatch gate audit hygiene.
2. **Policy / range / queue**: mutable namespace-policy epoch heads, Merkle-ish range repair fixtures, and garden admission queue scheduling.
3. **Clock / relay / gossip**: timed observation guards, relay tickets for bounded garden help, and gossip sieving before expensive route work.

## Audit/refactor lane

rev0024 keeps the branchlets visible through policyfold, branchletfold, clockfold, surface ledger entries, docs index pointers, and the non-failing cube audit report. The point is to reduce amnesia: recovered branchlets are tested, indexed, and named rather than silently deleted.

## Strongest rule

```text
Valid-looking contribution surfaces become capture surfaces unless time, family, budget, scope, queue, and repair evidence remain typed.
```

## Current evidence

- `tests/test_rev0024_interestmix_routeattest_gatefold.py`
- `tests/test_rev0024_policyepoch_rangemerkle_queueforge.py`
- `tests/test_rev0024_relayticket_gossipsieve_clockguard.py`
- `tests/test_rev0024_clockrelay_gossipsieve_branchlet.py`
- `scripts/ci/run_python_cloudtainer_lane.sh`

## Nonclaims

No live I2P/SAM transport, no production DHT, no production relay/gossip/policy/range/queue protocol, no private retrieval guarantee, no global reputation, no mutable-head consensus, no Sybil/anonymity guarantee, and no Nicotine+ patch.
