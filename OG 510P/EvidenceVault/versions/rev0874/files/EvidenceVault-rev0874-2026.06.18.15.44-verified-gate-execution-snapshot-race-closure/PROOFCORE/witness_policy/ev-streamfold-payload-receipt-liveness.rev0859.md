# Witness policy — rev0859 payload receipt liveness lane

The rev0859 lane verifies only public overlay artifacts and public hashes. The active receipt replay imports the rev0857 candidate verifier from the selected root and recomputes absence reports in-process. No private witness, canonical payload bytes, signing keys, license authority, or unpublished streamfold proof material is required or included.

The legacy rev0858 receipt verifier remains present for historical hash continuity but is not an active endpoint because it can hang in this cloudtainer while waiting on captured subprocess pipes.

Non-claims: not a rights grant, not a recovered payload bundle, not a streamfold correctness proof, not a SNARK, not zero knowledge, and not succinct.
