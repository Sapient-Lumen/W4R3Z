# Wake from amnesia — rev0030

Start here:

1. Read `docs/289-rev0030-negspace-peerdelta-keycrisisfold.md`.
2. Run `tests/test_rev0030_negspace_peerdelta_keycrisis.py`.
3. Run `tests/test_rev0030_joined_branch_surfaces.py`.
4. Inspect `src/i2p_dht_lab/negspace.py` for the absence-is-not-truth rule.
5. Inspect `src/i2p_dht_lab/peerbook.py` and `src/i2p_dht_lab/peerdelta.py` for entrance growth and repair pressure.
6. Inspect `src/i2p_dht_lab/keycrisis.py` for local key-crisis gates.
7. Inspect `src/i2p_dht_lab/bootstrapjoin.py`, `src/i2p_dht_lab/livesmoke.py`, `src/i2p_dht_lab/deltarepairjoin.py`, and `src/i2p_dht_lab/keycrisisjoin.py` for the joined-boundary branchlet fold.
8. Inspect `src/i2p_dht_lab/keycrisisfold.py` for the current revision audit/refactor spine.

The key mental model: the DHT should grow many entrances, but every entrance and every absence response is also a capture surface. Key crisis evidence is local gating pressure, not a universal ban list. Joined branchlet surfaces prevent one good-looking local result from quietly authorizing the next local step.
