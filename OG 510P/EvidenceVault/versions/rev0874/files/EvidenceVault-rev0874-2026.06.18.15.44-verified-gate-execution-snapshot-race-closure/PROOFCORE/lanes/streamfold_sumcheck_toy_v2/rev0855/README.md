# Streamfold sumcheck toy v2 lane — rev0855

rev0855 converts the rev0854 `streamfold_sumcheck_toy_v2_family` frontier target into an executable lane gate.

The lane has two parts:

1. `payload_manifest.rev0855.json` records the exact `17` canonical paths, hashes, byte counts, roles, and absence status that must be closed before real streamfold correctness work can be claimed.
2. `protocol_profile.rev0855.json` plus the synthetic fixtures exercise a transparent toy sumcheck transcript verifier so the next proof work has runnable algebraic checks, not just registry prose.

The synthetic transcript is deliberately public and tiny. It proves that the harness catches bad sumcheck round consistency, not that the absent canonical `streamfold` artifacts are correct.
