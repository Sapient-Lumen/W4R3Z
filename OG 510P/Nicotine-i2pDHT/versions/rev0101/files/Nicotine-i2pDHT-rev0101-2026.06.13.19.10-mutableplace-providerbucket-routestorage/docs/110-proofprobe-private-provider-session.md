# Proof-probe sessions

`proofprobe.py` connects two earlier surfaces:

- `privateprovider.py`: real probes, decoy probes, commitment-only witness surfaces, raw-content-key exposure counts, family caps.
- `proofhandshake.py`: provider availability claims, nonce-bound challenges, signed proof responses, useful refusals, wrong-content rejection, replay/deadline checks.

The hard question is no longer “did this provider sign a response?” The question is:

```text
Did a metadata-budgeted probe plan produce enough diverse challenge-bound true proofs,
without false-provider pressure, decoy weirdness, or raw-key overexposure?
```

## Decisions

`ProofProbeDecisionKind` has these intentionally conservative outcomes:

- `accept_diverse_true_proofs`
- `continue_insufficient_true_proofs`
- `continue_low_true_family_diversity`
- `continue_metadata_exposure_high`
- `continue_useful_refusals_only`
- `quarantine_false_provider_pressure`
- `quarantine_decoy_true_proof`
- `ignore_invalid_or_empty`

## Decoys are not a privacy proof

Decoys are a pressure tool, not a guarantee. A decoy true-proof is suspicious because it means a provider produced a true-provider proof for a probe that should not have identified the target in the same way as a real probe. That may mean the decoy model is weak, the provider is gaming the protocol, or the test fixture is too simple. The local action is the same: preserve evidence and do not accept.

## Useful refusal stays useful but insufficient

A bounded signed refusal says the provider/garden is alive and honest enough to refuse. It does not say the bytes are available. The session report treats useful refusals as liveness/capacity evidence, not provider truth.
