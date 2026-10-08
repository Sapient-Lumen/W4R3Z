# rev0030 — negspace-peerdelta-keycrisisfold

This revision stays risk-first and adds three new local pressure surfaces before live I2P/SAM transport:

1. **Negative-space / absence evidence**: empty answers are signed observations, not truth.
2. **Peerbook + peer delta sketches**: entrance growth and address-book repair need channel/family diversity before becoming sticky local memory.
3. **Key crisis gating**: compromise, signer forks, emergency freeze, destination loss, and succession-required notices gate risky keyed operations.

The audit/refactor lane adds `keycrisisfold.py`, which keeps the new rev0030 path visible from docs, public pointers, head registry, tests, and the active surface ledger while preserving the rev0029 `foldseal.py` predecessor.

## Strong sentence

> Absence, entrances, and crisis notices are all cheap claims until local diversity, monotonic memory, and exact-scope gates make them expensive enough to use.

## New code

- `src/i2p_dht_lab/negspace.py`
- `src/i2p_dht_lab/peerbook.py`
- `src/i2p_dht_lab/peerdelta.py`
- `src/i2p_dht_lab/keycrisis.py`
- `src/i2p_dht_lab/keycrisisfold.py`
- `src/i2p_dht_lab/bootstrapjoin.py`
- `src/i2p_dht_lab/livesmoke.py`
- `src/i2p_dht_lab/keycrisisjoin.py`
- `src/i2p_dht_lab/deltarepairjoin.py`
- `tests/test_rev0030_negspace_peerdelta_keycrisis.py`
- `tests/test_rev0030_joined_branch_surfaces.py`

## Nonclaims

No live I2P/SAM transport, production DHT, production peerstore, production set-reconciliation implementation, global reputation, mutable-head consensus, Sybil resistance, anonymity guarantee, or Nicotine+ patch is included.


## Folded branchlet joins

After the initial rev0030 path was stable, two useful alternate rev0029 branchlets were folded forward instead of discarded. The active surface now also includes:

- `bootstrapjoin.py` and `livesmoke.py`: peerbook, live-probe/SAM-shadow, absence, and egress pressure before bootstrap advancement.
- `keycrisisjoin.py`: key-crisis recovery checked against checkpoint hard-negative memory and egress pressure.
- `deltarepairjoin.py`: range-delta repair joined to egress pressure and tombstone-first exact replies.
- `tests/test_rev0030_joined_branch_surfaces.py`: regression tests for the joined branchlet boundaries.

The audit/refactor lesson is that branchlets should either become visible obligations or stay explicitly historical. Hidden branchlet drift is a protocol-design smell.
