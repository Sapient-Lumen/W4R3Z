# Proofcore verifier surface audit/refactor — rev0856

## Status

`proofcore_verifier_surface_refactored_and_audited`

The proofcore verifier surface now has an explicit active lane:

```text
PROOFCORE/verifiers/verify_streamfold_sumcheck_fs_lane_rev0856.py
```

and an explicit transcript-bound sumcheck verifier:

```text
PROOFCORE/verifiers/verify_sumcheck_fs_transcript_rev0856.py
```

## Refactor result

The rev0855 exact lane validator is now treated as a historical checkpoint in
rev0856. This prevents the common operator trap where an exact historical PCD
fixture is accidentally run against a later tree and either fails for the wrong
reason or silently validates a stale boundary.

A machine-readable verifier inventory was added at:

```text
PROOFCORE/verifier_surface.rev0856.json
```

## Verifier files audited

```text
PROOFCORE/verifiers/verify_pcd_envelope.py
PROOFCORE/verifiers/verify_proofcore_frontier_rev0854.py
PROOFCORE/verifiers/verify_streamfold_sumcheck_fs_lane_rev0856.py
PROOFCORE/verifiers/verify_streamfold_sumcheck_lane_rev0855.py
PROOFCORE/verifiers/verify_sumcheck_fs_transcript_rev0856.py
PROOFCORE/verifiers/verify_sumcheck_transcript_rev0855.py
```

## Remaining risk

The active verifier is still transparent harness logic, not a SNARK verifier and
not a production Fiat-Shamir implementation. The next material step remains
recovering the first four canonical streamfold payloads and checking them under
the payload admission contract.
