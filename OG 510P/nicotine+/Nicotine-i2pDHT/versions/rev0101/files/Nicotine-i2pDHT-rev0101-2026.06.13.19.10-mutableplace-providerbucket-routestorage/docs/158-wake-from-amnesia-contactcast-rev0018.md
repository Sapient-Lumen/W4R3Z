# Wake from amnesia — rev0018

You are in a Python-first speculative DHT cube for a mutable DHT above I2P. It is not a Nicotine patch and not a production network implementation.

The current turn added three surfaces:

1. `livenessbudget.py`: joins adaptive lookup and private provider probe planning so liveness pressure cannot silently spend metadata. Look for raw-key exposure limits, decoy ratio, useful-refusal backoff, and fast-window capture quarantine.
2. `tombmesh.py`: joins tombstone cache, witness summaries, and mutable head events so stale alive evidence does not resurrect withdrawn/deleted/compromised records.
3. `provider_compat.py`: maps provider legacy/canonical surfaces before writing wrappers or deleting history.

Run:

```bash
scripts/ci/run_python_cloudtainer_lane.sh
```

Current hard sentence:

```text
Liveness pressure, resurrection pressure, and compatibility pressure must be budgeted before they become protocol defaults.
```

Next likely work: integrate liveness budgets with provider proof/probe sessions directly, add tombstone mesh receipts for gardens, start explicit compatibility adapters for legacy provider names, and run larger repeated-round sweeps where liveness and tombstone pressure collide.
