# Wake from amnesia — rev0017

You are in `rev0017-regionledger-adaptivealpha-witnessrepair`.

## What matters first

The cube is still a speculative Python-first DHT lab above I2P. It is not a live transport and not a production DHT.

rev0017 adds four hard surfaces:

1. `adaptivealpha.py`: adaptive alpha/beta lookup pressure from transcripts.
2. `regionledger.py`: garden region-sweep memory with source-family and tombstone pressure.
3. `tombstonecache.py`: signed tombstone evidence and resurrection-pressure tests.
4. `witnessrepair.py`: bounded next actions for weak/contradictory witness evidence.

The audit/refactor lane extended `provider_refactor.py` so historical legacy imports can be distinguished from active legacy imports.

## Strong sentence

```text
Do not let latency, stale cache evidence, or regional reprovide pressure silently choose truth for the DHT.
```

## Verification

```bash
scripts/ci/run_python_cloudtainer_lane.sh
```

Expected local lane: surface check, micro simulation, pytest, compileall, cube audit, zip integrity.

## Next likely revision

`rev0018-livenessbudget-tombmesh-providerwrap`

Suggested focus:

- liveness budgets that join adaptive alpha with provider proof/probe planning;
- tombstone meshes across garden witnesses and mutable head memory;
- explicit compatibility wrapper or adapter plan for `providerpoison.py`;
- region-ledger receipts and garden scheduling integration;
- live-SAM preparation still through shadows, not sockets.
