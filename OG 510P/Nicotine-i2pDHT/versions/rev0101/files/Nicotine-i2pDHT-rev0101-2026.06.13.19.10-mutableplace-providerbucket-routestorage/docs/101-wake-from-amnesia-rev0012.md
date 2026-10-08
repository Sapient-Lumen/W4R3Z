# Wake from amnesia — rev0012

This cube is a DHT-over-I2P design lab. It is not a Nicotine patch and not a production DHT.

## Current stance

Mutable heads remain the control plane. Provider records remain claims, not truth. Garden nodes remain giving supernodes, not authorities.

## rev0012 result

The newest risk-first lane attacks provider confirmation and witness poisoning before live transport:

```text
privateprovider.py  -> budgeted real probes, decoys, commitments, family caps
probewitness.py     -> signed witness receipts, diversity pressure, contradiction quarantine
chaossweep.py       -> deterministic captured-fast-window parameter sweeps
wiretranscript.py   -> signed transport-neutral wire transcript fixtures
```

## Tests passed at build time

```text
surface check
micro-simulation
pytest
compileall
zip integrity check
```

## Next likely move

rev0013 should press on either:

```text
1. provider proof handshakes and challenge transcript algebra
2. mutable head fork/witness/garden interactions at larger scale
3. SAM-like fake transport latency/churn/retry behavior
4. stronger key succession and capability revocation under witness poisoning
```

Keep the rule: implement the scary algebra before live network polish.
