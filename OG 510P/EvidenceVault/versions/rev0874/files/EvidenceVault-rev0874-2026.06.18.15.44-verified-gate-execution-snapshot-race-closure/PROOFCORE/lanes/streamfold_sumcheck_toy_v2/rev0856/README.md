# rev0856 streamfold sumcheck transcript-binding lane

rev0855 made the `streamfold_sumcheck_toy_v2_family` lane executable, but its
synthetic sumcheck transcript still used explicit prover-supplied challenges.
That is useful as an arithmetic smoke test, yet it leaves the exact footgun that
non-interactive proof systems must avoid: a verifier accepting challenges that
are not bound to all public context and prior transcript material.

rev0856 adds a deterministic Fiat-Shamir-style binding contract for the toy
harness:

```bash
python3 PROOFCORE/verifiers/verify_sumcheck_fs_transcript_rev0856.py \
  --fixture PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0856/fixtures/sumcheck_fs_accept.rev0856.json
```

Reject fixtures cover a tampered challenge and an omitted payload-manifest
binding. This remains transparent harness work only. It is not a SNARK, not zero
knowledge, not succinct, not production Fiat-Shamir, and not a canonical
streamfold receipt verifier.

Derived accept-fixture challenges for Fp97 are:

```text
r1 = 10
r2 = 45
final evaluation = 92
```

The missing canonical payload gate remains the rev0855 manifest:

```text
PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0855/payload_manifest.rev0855.json
```
