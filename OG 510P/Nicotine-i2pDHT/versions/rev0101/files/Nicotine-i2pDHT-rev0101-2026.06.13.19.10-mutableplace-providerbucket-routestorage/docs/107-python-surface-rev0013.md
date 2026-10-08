# Python surface — rev0013

New modules:

```text
src/i2p_dht_lab/proofhandshake.py
src/i2p_dht_lab/headwitness.py
src/i2p_dht_lab/latencyforge.py
src/i2p_dht_lab/cubeaudit.py
```

New tests:

```text
tests/test_rev0013_proof_head_latency_audit.py
```

New evidence script:

```text
scripts/evidence/run_cube_audit.py
```

The full local lane now runs:

```text
surface check
micro-simulation
cube audit
pytest
compileall
```

rev0013 verification result at packaging time:

```text
116 passed
```
