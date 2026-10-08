# Wake from amnesia — rev0019

The current cube head is `storeflight-leasequorum-surfaceclean`.

Start here:

1. Read `docs/163-rev0019-storeflight-leasequorum-surfaceclean.md`.
2. Inspect `src/i2p_dht_lab/storeflight.py` and `src/i2p_dht_lab/storecontract.py` for the two storage layers: admission/custody receipts and exact-digest store contracts.
3. Inspect `src/i2p_dht_lab/custodyaudit.py` for challenge-bound custody proofs and replay/wrong-digest pressure.
4. Inspect `src/i2p_dht_lab/leasequorum.py` and `src/i2p_dht_lab/leaseroute.py` for entrance-channel and route-gossip capture pressure.
5. Inspect `src/i2p_dht_lab/storemesh.py`, `budgetreceipt.py`, and `roundledger.py` for multi-round garden/store evidence.
6. Inspect `src/i2p_dht_lab/surfaceclean.py`, `surfaceledger.py`, and the evidence scripts for the audit/refactor lane.
7. Run `scripts/ci/run_python_cloudtainer_lane.sh`.

The guiding sentence:

```text
store durability, entrance freshness, tombstone pressure, custody challenge, useful refusal, and repeated-round evidence must remain separate typed surfaces until local policy joins them deliberately.
```

Additional wake pointers: inspect `src/i2p_dht_lab/storagelease.py` for storage-lease fork/renewal/tombstone pressure and `src/i2p_dht_lab/readrepair.py` for replica observation and stale-cache resurrection pressure.

