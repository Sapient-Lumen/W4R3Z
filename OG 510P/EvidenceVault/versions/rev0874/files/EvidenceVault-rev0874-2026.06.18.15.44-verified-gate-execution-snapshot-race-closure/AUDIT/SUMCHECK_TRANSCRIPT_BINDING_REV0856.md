# Sumcheck transcript binding audit — rev0856

## Status

`transcript_challenge_binding_added_payloads_still_missing`

## Risk closed

rev0855 was a useful arithmetic step, but it still accepted explicit challenge
values in the toy transcript. That is an unbound challenge footgun: a later
operator could mistake a prover-chosen challenge field for a verifier-derived
challenge. In a non-interactive transcript, challenge derivation must bind the
public context and transcript prefix.

rev0856 adds:

```text
PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0856/transcript_challenge_contract.rev0856.json
PROOFCORE/verifiers/verify_sumcheck_fs_transcript_rev0856.py
```

The verifier now binds at least these public context fields:

```text
lane_id, revision, protocol_profile_sha256, payload_manifest_sha256, source_group_id, rights_status, canonical_payloads_missing_in_overlay, claimed_sum_mod_p, field_modulus
```

The active accept fixture derives:

```text
r1 = 10
r2 = 45
final evaluation = 92
```

## Reject fixtures

The verifier rejects:

```text
sumcheck_fs_reject_bad_challenge.rev0856.json
sumcheck_fs_reject_omit_payload_binding.rev0856.json
```

The second reject proves `payload_manifest_sha256` is not decorative metadata; it
is part of the challenge context.

## Still blocked

The 17 canonical streamfold payloads are still absent. This lane does not
recover payload bytes, does not add a root license, and does not claim SNARK,
zero knowledge, succinctness, production Fiat-Shamir security, or streamfold
protocol soundness.

Explicit bad challenge reject fixture coverage is intentional and required.
