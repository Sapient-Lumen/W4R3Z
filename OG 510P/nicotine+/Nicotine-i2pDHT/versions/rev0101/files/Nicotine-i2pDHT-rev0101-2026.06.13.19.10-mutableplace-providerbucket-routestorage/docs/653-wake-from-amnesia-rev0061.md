# Wake from amnesia — rev0061

Current revision: `rev0061 — deliverysettlement-ackarchive-prunejoin`.

Read first:

```text
docs/647-rev0061-deliverysettlement-ackarchive-prunejoin.md
```

Then inspect:

```text
src/i2p_dht_lab/deliverysettlement.py
src/i2p_dht_lab/ackarchive.py
src/i2p_dht_lab/ackprunejoin.py
src/i2p_dht_lab/ackfold.py
```

Then run:

```text
pytest tests/test_rev0061_deliverysettlement_ackarchive_prunejoin.py
```

Memory sentence:

```text
A public-edge send that appears delivered is still not safe to prune until settlement and archive agree.
```
