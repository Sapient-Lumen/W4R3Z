# Witness policy — rev0862 archive payload search lane

The witness for this transparent lane is the operator-supplied set of candidate directories and ZIP archives. The verifier exposes only deterministic match/absence/staging receipts derived from exact byte count and SHA-256 checks. No canonical streamfold payload bytes are embedded in this overlay. No private witness, SNARK proof, zero-knowledge proof, or succinct proof is claimed.

A future operator may provide candidate archives with `--candidate-source`; staging must occur outside the overlay and outside candidate directory roots. Staged bytes remain blocked from publication until rights closure is separately resolved.
