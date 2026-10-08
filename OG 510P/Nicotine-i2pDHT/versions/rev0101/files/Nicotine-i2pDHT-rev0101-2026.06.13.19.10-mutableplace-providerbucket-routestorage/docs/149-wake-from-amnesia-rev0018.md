# Wake from amnesia — rev0018

Current revision: `rev0018 siblingcast-keyspacecartography-surfaceaudit`.

## What matters

- The cube remains a Python-first DHT design lab above I2P.
- This revision does not touch live SAM/I2P transport.
- The new work asks whether records are actually replicated across close, diverse siblings and whether routing memory sees enough of keyspace.

## New hard guesses made executable

```text
A signed STORE receipt is evidence, not durable truth.
A close sibling set can be captured.
Many accepted receipts from one family are not replication health.
Useful refusal is positive capacity evidence, not success.
A local keyspace map can reveal holes and monoculture before a lookup lies with confidence.
```

## Fast verification

```bash
scripts/ci/run_python_cloudtainer_lane.sh
```

Expected rev0018 lane summary:

```text
surface check
micro-simulation
pytest: 175 passed
compileall
cube audit
zip integrity check
```

## Next likely work

`rev0019 livenessbudget-tombmesh-providerwrap`: connect sibling-broadcast receipts to region-ledger/garden scheduling, build tombstone mesh pressure across mutable heads and witness cache, and finish the providerpoison/provider_poison compatibility migration.
