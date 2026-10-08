# Churn transcript fixtures — rev0011 duplicate pointer

The current rev0011 churn/frontier design lives in:

```text
docs/91-churn-frontier-and-transcript-pressure.md
src/i2p_dht_lab/churnforge.py
```

This file keeps an older title in the lineage, but rev0011 does **not** ship a separate `wire_churn.py` module. The implemented fixture is a smaller deterministic churn-frontier transcript:

```text
ChurnContact
ChurnFrontier
ChurnWireEvent
ChurnWireTranscript
select_churn_frontier
assess_churn_frontier
make_churn_transcript
```

The current hard tests are:

```text
tests/test_rev0011_churnforge.py
```

Future live SAM/I2P work can grow this into signed request/response wire fixtures, but rev0011 only claims deterministic frontier/transcript pressure.
