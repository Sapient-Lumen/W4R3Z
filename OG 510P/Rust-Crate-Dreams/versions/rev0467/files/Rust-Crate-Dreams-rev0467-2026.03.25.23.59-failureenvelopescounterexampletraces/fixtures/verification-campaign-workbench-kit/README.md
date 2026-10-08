# Verification Campaign Workbench Kit fixtures

These fixtures exercise the `0.1` artifact vocabulary for **P-0485 Verification Campaign Workbench Kit**.

## Core schemas

- `campaign-manifest.schema.json`
- `obligation-record.schema.json`
- `lane-result.schema.json`
- `trust-ledger.schema.json`
- `policy-evaluation.report.schema.json`
- `campaign-diff.report.schema.json`
- `verify-campaign.schema.json`

## Scenario families

- `miri_dynamic_execution_does_not_close_proof_obligation/` — dynamic UB evidence is valuable but still not the same as proof-shaped evidence.
- `kani_stub_verified_introduces_explicit_trust_surface/` — contract stubbing can accelerate proofs while still requiring a trust-ledger entry.
- `creusot_replay_context_shift_downgrades_comparability/` — replay/prover context drift should surface as only partial comparability.
- `prusti_trusted_functions_and_assumptions_block_silent_green/` — trusted functions and assumptions must influence policy, not hide in logs.
- `flux_and_verus_partial_scope_require_explicit_obligation_inventory/` — strong partial lanes still need an explicit obligation inventory before a campaign can go green.

The point of this fixture pack is to stop future passes from flattening:

- obligation inventory,
- lane semantics,
- trust surface,
- policy gates,
- and campaign comparability

into one fake “we ran verification” story.
