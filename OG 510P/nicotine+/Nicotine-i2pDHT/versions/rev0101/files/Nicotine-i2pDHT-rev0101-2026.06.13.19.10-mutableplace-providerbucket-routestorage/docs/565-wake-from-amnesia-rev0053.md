# Wake-from-amnesia — rev0053

Read in this order:

1. `docs/559-rev0053-handlercapsule-sideeffectjournal-adapterfuzz.md`
2. `docs/560-handler-capsule-boundary.md`
3. `docs/561-side-effect-journal-boundary.md`
4. `docs/562-adapter-fuzz-coverage.md`
5. `docs/563-handlerfold-audit-refactor.md`
6. `tests/test_rev0053_handlercapsule_sideeffect_adapterfuzz.py`
7. `src/i2p_dht_lab/handlercapsule.py`
8. `src/i2p_dht_lab/sideeffectjournal.py`
9. `src/i2p_dht_lab/adapterfuzz.py`
10. `src/i2p_dht_lab/handlerfold.py`

Needles: rev0053 handlercapsule sideeffectjournal adapterfuzz handlerfold edgefold.

The main memory: rev0052 rehearsed public-edge liveness; rev0053 says handler execution and side-effect memory still need their own exact-boundary capsules and journal entries.
