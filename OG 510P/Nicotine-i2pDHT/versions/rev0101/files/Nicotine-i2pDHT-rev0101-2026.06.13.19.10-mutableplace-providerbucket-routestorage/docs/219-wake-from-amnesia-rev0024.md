# Wake from amnesia — rev0024

Start here:

1. `docs/213-rev0024-policyepoch-rangemerkle-queueforge.md`
2. `src/i2p_dht_lab/policyepoch.py`
3. `src/i2p_dht_lab/rangemerkle.py`
4. `src/i2p_dht_lab/queueforge.py`
5. `tests/test_rev0024_policyepoch_rangemerkle_queueforge.py`

Mental model:

```text
namespace policy is mutable, but not global truth
range roots request repair, but exact proofs carry the useful evidence
garden queues should preserve head/witness/seed work under provider floods
```

The riskiest unresolved edge is still independence: source-family labels are local hints, not proof that two observations came through truly independent I2P paths.
