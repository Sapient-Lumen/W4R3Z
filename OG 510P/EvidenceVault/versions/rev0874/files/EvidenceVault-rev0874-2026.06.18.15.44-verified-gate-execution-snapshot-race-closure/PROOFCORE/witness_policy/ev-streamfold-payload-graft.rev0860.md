# Witness policy — rev0860 streamfold payload graft lane

This lane is transparent and deterministic. No private witness, SNARK witness, secret randomness, or zero-knowledge material is included.

The only external witness-like input this lane anticipates is a future operator-supplied candidate canonical tree passed to `prepare_streamfold_payload_graft_rev0860.py --candidate-root`. Such a tree is not included in this overlay. Candidate bytes may be staged only if they match the carried rev0855 manifest by exact path, byte length, and SHA-256, and only into an isolated stage directory outside the overlay root.

Publication remains blocked until rights decisions are complete.
