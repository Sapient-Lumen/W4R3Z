# Wake from amnesia — rev0009 `forkwatch-capgrant-chaosloom`

Read this first after a context reset.

## Where we are

We are designing a generic Python-first DHT over I2P. Nicotine remains a distant consumer, not the current target. The DHT is centered on mutable heads, provider records, garden nodes, local evidence, and optional sovereignty from central entrances.

## What changed in rev0009

The user said to stop merely dreaming and start implementing/testing the riskiest guesses first. This revision adds:

```text
src/i2p_dht_lab/forkwatch.py
src/i2p_dht_lab/capgrant.py
src/i2p_dht_lab/chaos.py
tests/test_forkwatch_capgrant_chaos.py
```

The new code tests:

- valid stale mutable records after a higher sequence;
- same-sequence fork evidence;
- tampered signatures not advancing memory;
- delegated capability resource/audience/verb checks;
- revocation heads as mutable records;
- fake lookup transcripts that emit witness receipts;
- seed portfolio capture reports.

## Core sentence

```text
mutable records need local history and evidence, not just signatures
```

## How to verify

```bash
scripts/ci/run_python_cloudtainer_lane.sh
```

Expected current result:

```text
surface check
micro-simulation
pytest: 64 passed
compileall
```

## Next likely revision

`rev0010 lookupfamilies-quorumgarden-pathcapture`

Focus:

- path-family-aware lookup transcripts;
- seed-channel capture weighting;
- fork receipts tied to disjoint path families;
- revocation-head rollback/fork tests;
- comparison/fusion of `headlog.py` with `forkwatch.py` and `capability.py` with `capgrant.py`.
