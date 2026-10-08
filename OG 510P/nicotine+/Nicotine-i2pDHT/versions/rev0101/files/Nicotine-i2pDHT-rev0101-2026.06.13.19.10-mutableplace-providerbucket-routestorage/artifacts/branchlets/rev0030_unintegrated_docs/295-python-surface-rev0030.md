# Python surface — rev0030

Active new modules:

```text
src/i2p_dht_lab/absencegate.py
src/i2p_dht_lab/keycrisis.py
src/i2p_dht_lab/peerbook.py
src/i2p_dht_lab/deltasketch.py
src/i2p_dht_lab/rangesetdelta.py
src/i2p_dht_lab/liveprobe.py
src/i2p_dht_lab/branchrecoverfold.py
```

Active new test:

```text
tests/test_rev0030_negspace_peer_delta_keycrisis.py
```

The test pins:

- durable tombstone-supported absence;
- fast empty capture and positive-conflict quarantine;
- normal key succession versus compromise recovery rotation;
- key-crisis rollback/fork/previous-link mismatch;
- peerbook acceptance and introducer capture;
- SAM-shadow contact probe binding and no-router clean skip;
- delta-sketch tombstone-first/exact/fork pressure;
- range-set delta tombstone-first/family/replay pressure;
- branchrecoverfold navigation and rev0029 predecessor fold.
