# Witness policy — rev0857 streamfold payload admission lane

This lane has no private witness and includes no zero-knowledge proof material.

Public inputs are the streamfold payload manifest identity, payload admission contract identity, candidate-root verification rules, rights-block state, parent checkpoint references, and the synthetic prefix-bound sumcheck transcript fixtures.

A future operator may supply a candidate root outside this ZIP. The verifier only reads selected canonical paths beneath that root and checks exact byte length, SHA-256, `INDEX/files.csv` agreement, JSON parseability, and role coverage. The verifier does not copy payloads into the overlay, does not reveal or hide witness material, and does not grant publication rights.

This is not a SNARK, not zero knowledge, not succinct, not a production Fiat-Shamir transform, and not a streamfold correctness proof.
