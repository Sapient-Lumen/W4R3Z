# PROOFCORE glossary — rev0853

`PCD` / proof-carrying data: data that carries proof or certificate material sufficient for a verifier to check a prescribed property of the data and, in stronger forms, the history that produced it.

`Transparent deterministic PCD envelope`: this rev0853 lane's modest envelope. Verification is deterministic Python over public files and hashes. It is useful, but it is not zero knowledge, succinct, recursive, or cryptographically sound in the SNARK sense.

`Claim`: the exact statement being checked. The first claim is overlay integrity and rights-block preservation.

`Public input`: values the verifier may inspect directly: expected revision, patch-chain endpoint, required file paths, known canonical-index counts, rights status, and absence of root rights sentinels.

`Witness`: private data used by a prover. The first lane has no private witness; its witness policy is `public-only`.

`Commitment`: a hash or identifier binding the claim to a file or value without restating the whole payload.

`Receipt` / `certificate`: an object attached to data that records the claim, verifier, public-input identity, and expected verification result. In a zkVM/SNARK lane, this would hold the cryptographic proof or point at it.

`Verifier`: executable code that checks the claim against public inputs and any proof/certificate material.

`Accept fixture`: a test vector that the verifier must accept.

`Reject fixture`: a test vector with a controlled mutation that the verifier must reject.
