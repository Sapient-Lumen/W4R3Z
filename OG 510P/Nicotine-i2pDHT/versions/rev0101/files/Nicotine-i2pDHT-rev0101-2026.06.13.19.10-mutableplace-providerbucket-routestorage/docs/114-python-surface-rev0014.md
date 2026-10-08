# Python surface — rev0014

New modules:

```text
src/i2p_dht_lab/familydiversity.py
src/i2p_dht_lab/proofprobe.py
src/i2p_dht_lab/gardensentinel.py
src/i2p_dht_lab/sweepgrid.py
src/i2p_dht_lab/supersession.py
```

New tests:

```text
tests/test_rev0014_proofprobe_gardensentinel_sweepgrid.py
```

New audit surface:

```text
HISTORICAL_SUPERSESSION.json
artifacts/process/rev0014_cube_audit.json
```

Core tested behaviors:

- family capping keeps same-family evidence from masquerading as diversity;
- diverse commitment-only provider proofs can be accepted;
- false-provider pressure quarantines before acceptance;
- decoy true-proof weirdness quarantines;
- raw-key exposure budget is enforced at the proof-probe session layer;
- useful refusals are liveness, not availability;
- garden sentinel scoring prefers local positive evidence but quarantines semantic lies;
- witness mesh contradictions feed sentinel quarantine;
- sweepgrid detects fast-window capture and combined pressure;
- historical supersession turns known duplicate numbering into audit info rather than warnings.
