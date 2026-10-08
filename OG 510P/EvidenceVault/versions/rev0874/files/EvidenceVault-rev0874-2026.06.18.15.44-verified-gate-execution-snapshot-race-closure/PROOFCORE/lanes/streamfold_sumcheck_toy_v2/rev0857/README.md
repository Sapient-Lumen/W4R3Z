# streamfold_sumcheck_toy_v2 rev0857 lane

rev0857 turns the payload gate from a passive manifest into an executable candidate-root admission surface and tightens the toy sumcheck transcript binding.

## Payload admission

The overlay still contains zero of the 17 canonical streamfold payload bytes. This is intentional. Use the candidate verifier against a mounted canonical tree:

```bash
python3 PROOFCORE/verifiers/verify_streamfold_payload_candidate_rev0857.py --candidate-root /path/to/full/canonical/tree --mode full
```

For a smaller first recovery pass, use the four-file minimum set:

```bash
python3 PROOFCORE/verifiers/verify_streamfold_payload_candidate_rev0857.py --candidate-root /path/to/full/canonical/tree --mode minimum
```

The verifier checks exact path, size, SHA-256, `INDEX/files.csv` agreement, JSON parseability, and role coverage. It does not copy files and does not grant rights.

## Prefix-bound transcript harness

The rev0857 sumcheck fixture derives challenges from public context, the current running claim, current round polynomial, and the previous public transcript-message hashes. This closes the rev0856 gap where later rounds directly carried prior challenges but did not explicitly carry the hash of prior public round messages.

```bash
python3 PROOFCORE/verifiers/verify_sumcheck_fs_prefix_transcript_rev0857.py --fixture PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0857/fixtures/sumcheck_fs_prefix_accept.rev0857.json
```

This is not a SNARK, not zero knowledge, not succinct, and not a production Fiat-Shamir transform.
