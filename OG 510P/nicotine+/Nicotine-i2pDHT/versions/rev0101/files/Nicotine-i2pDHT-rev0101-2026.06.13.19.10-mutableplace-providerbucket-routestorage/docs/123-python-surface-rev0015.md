# Python surface — rev0015

New modules:

```text
src/i2p_dht_lab/witnesscache.py
src/i2p_dht_lab/lookuptranscript.py
src/i2p_dht_lab/samshadow.py
src/i2p_dht_lab/gardenscheduler.py
src/i2p_dht_lab/provider_refactor.py
```

New tests:

```text
tests/test_rev0015_witnesscache_routingpressure_samshadow.py
```

New script behavior:

```text
scripts/evidence/run_micro_simulation.py  # now writes rev0015 witness/lookup/SAM/garden evidence
scripts/evidence/run_cube_audit.py        # now writes rev0015 cube audit report
scripts/evidence/check_surfaces.py        # now checks rev0015 current pointer and rev0016 next pointer
```

Expected local lane:

```text
surface check
micro-simulation
cube audit
pytest
compileall
zip integrity check
```

At packaging time this lane passed with 137 tests.
