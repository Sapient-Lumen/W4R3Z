# Proofcore frontier PCD audit — rev0854
rev0854 turns the rev0853 proofcore map into a parent-linked, executable completion frontier. It does not verify missing protocol payloads; it verifies that the next proof work has a narrow, hash-anchored target and that the previous PCD checkpoint can be replayed as history.
## What changed
- Added `PROOFCORE/verifiers/verify_proofcore_frontier_rev0854.py`, which reconstructs rev0853 in a temporary directory and reruns the rev0853 transparent PCD verifier.
- Added `PROOFCORE/frontier/rev0854/proof_obligation_frontier.rev0854.{json,csv}` from the rev0853 canonical path-role map.
- Added a second transparent PCD envelope: claim, public inputs, commitments, certificate, witness policy, accept fixture, and reject fixture.
- Preserved the rights block and explicit non-claims: no SNARK, no zero knowledge, no publication permission.

## Recommended next lane

`streamfold_sumcheck_toy_v2_family` is the recommended next lane. It has 17 indexed P0 paths and covers these roles: `abi_ir_or_protocol_ir, attestation_or_receipt, public_input_or_commitment`. That makes it a better next target than broad doctrine or whole-tree registry work.

## Frontier groups

| group | component | paths | roles | risk score |
|---|---:|---:|---|---:|
| `streamfold_sumcheck_toy_v2_family` | streamfold | 17 | abi_ir_or_protocol_ir:7, attestation_or_receipt:9, public_input_or_commitment:1 | 77 |
| `streamfold_fri_open_family` | streamfold | 7 | abi_ir_or_protocol_ir:6, attestation_or_receipt:1 | 37 |
| `streamfold_lookup_perm_family` | streamfold | 6 | abi_ir_or_protocol_ir:4, attestation_or_receipt:2 | 32 |
| `streamfold_halo2_multiopen_toy_v1` | streamfold | 1 | abi_ir_or_protocol_ir:1 | 14 |
| `zkrtp_policy_transition_checkpoint` | zkrtp | 8 | attestation_or_receipt:5, governance_or_rights:3 | 31 |
| `zkrtp_policy_proof_acceptance` | zkrtp | 1 | attestation_or_receipt:1 | 13 |
| `zkrtp_monitor_attestation_transition` | zkrtp | 7 | attestation_or_receipt:7 | 31 |
| `pact_surface_and_abom_receipts` | pact | 4 | attestation_or_receipt:4 | 12 |

## Commands

```bash
python3 scripts/validate_proofcore_frontier_pcd_rev0854.py
python3 PROOFCORE/verifiers/verify_proofcore_frontier_rev0854.py --fixture PROOFCORE/fixtures/accept/ev-proofcore-frontier.rev0854.accept.json
python3 PROOFCORE/verifiers/verify_proofcore_frontier_rev0854.py --fixture PROOFCORE/fixtures/reject/ev-proofcore-frontier.rev0854.reject.json --expect-fail
```
