# Witness policy — proofcore frontier rev0854

This lane is transparent: all checked data is public inside the overlay bundle. The only reconstructed state is the historical rev0853 checkpoint, recreated by reversing the rev0853-to-rev0854 overlay patch in a temporary directory and restoring cyclic parent surfaces from snapshots carried in `PROOFCORE/parent_snapshots/rev0853/`.

No private witness, secret key, trusted setup material, or zk-SNARK proving key is included. The verifier must fail closed if parent replay, frontier recomputation, rights status, or required role coverage drift.

Completion trigger: after the full canonical tree is mounted, replace this frontier-only witness policy with one lane-specific policy for `streamfold_sumcheck_toy_v2_family` that states the public inputs, private witness boundary, verifier/receipt format, and accept/reject fixtures.
