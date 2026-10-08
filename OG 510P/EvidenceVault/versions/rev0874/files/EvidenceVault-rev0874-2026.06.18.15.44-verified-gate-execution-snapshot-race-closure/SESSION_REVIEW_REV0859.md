# Session review — rev0859

Focus: close an active liveness failure in the proofcore PCD lane rather than adding doctrine.

## What changed

- Added an in-process payload receipt verifier for the rev0858 streamfold payload absence receipts.
- Added a parent-linked rev0859 proofcore lane that reconstructs rev0858 but replays its payload receipt evidence without the liveness-quarantined legacy subprocess-pipe endpoint.
- Added a subprocess/verifier-surface audit so similar risks are visible.
- Refactored the rev0858 targeted validator so rev0858 is treated as a historical checkpoint in rev0859.

## Why this mattered

During this pass, the rev0858 payload-receipt verifier was observed to print its OK marker yet not return in this cloudtainer while waiting on subprocess pipe communication. That is a severe operator trap in an active PCD chain. rev0859 leaves rev0858 hash-bound historical bytes intact and adds a new active replay path.

## Still blocked

The overlay still contains none of the 17 canonical streamfold payload bytes. Publication remains blocked pending rights decisions. No license, notice, SPDX/RO-Crate rights assertion, SNARK proof, zero-knowledge proof, succinct proof, production Fiat-Shamir security claim, or streamfold correctness claim was invented.
