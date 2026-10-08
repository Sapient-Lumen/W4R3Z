# Python surface — rev0030

New active surfaces:

```text
src/i2p_dht_lab/negspace.py
src/i2p_dht_lab/peerbook.py
src/i2p_dht_lab/peerdelta.py
src/i2p_dht_lab/keycrisis.py
src/i2p_dht_lab/keycrisisfold.py
src/i2p_dht_lab/absencegate.py
src/i2p_dht_lab/liveprobe.py
src/i2p_dht_lab/livesmoke.py
src/i2p_dht_lab/bootstrapjoin.py
src/i2p_dht_lab/deltasketch.py
src/i2p_dht_lab/deltarepairjoin.py
src/i2p_dht_lab/keycrisisjoin.py
tests/test_rev0030_negspace_peerdelta_keycrisis.py
tests/test_rev0030_joined_branch_surfaces.py
```

The tests cover:

- diverse absence accepted with watch/trust limits
- positive evidence contradicting absence
- responder absence forks
- negative-answer family floods
- peerbook entrance diversity
- channel capture
- purpose coverage
- contact-lease same-sequence forks
- peer-delta missing entry requests
- sketch rollback/fork pressure
- sketch family monoculture
- key compromise blocking
- successor recovery
- crisis rollback/fork pressure
- rev0030 fold navigation


Additional joined tests cover:

- bootstrap acceptance only after peerbook/live-probe/egress agreement;
- soft absence delaying rather than proving;
- SAM-shadow destination drift;
- key-crisis recovery blocked by checkpoint hard-negative loss;
- delta repair staying tombstone-first until exact repair material arrives.
