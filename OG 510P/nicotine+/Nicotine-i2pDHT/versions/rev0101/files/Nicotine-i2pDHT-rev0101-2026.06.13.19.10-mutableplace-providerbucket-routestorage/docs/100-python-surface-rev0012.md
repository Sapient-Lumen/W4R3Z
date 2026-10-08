# Python surface — rev0012

New modules:

```text
src/i2p_dht_lab/privateprovider.py
src/i2p_dht_lab/probewitness.py
src/i2p_dht_lab/chaossweep.py
src/i2p_dht_lab/wiretranscript.py
```

New tests:

```text
tests/test_rev0012_privateprovider_witness_sweep.py
```

New tested behaviors:

```text
private-ish provider probe planning
raw-key exposure budgets
commitment-only witness surfaces
decoy probe shape
provider family caps
witness receipt signing/verification
witness family diversity
witness self-contradiction quarantine
captured-fast-window sweep
wire frame signing/verification
transcript digesting
duplicate request sequence detection
```

Verification command:

```bash
scripts/ci/run_python_cloudtainer_lane.sh
```
