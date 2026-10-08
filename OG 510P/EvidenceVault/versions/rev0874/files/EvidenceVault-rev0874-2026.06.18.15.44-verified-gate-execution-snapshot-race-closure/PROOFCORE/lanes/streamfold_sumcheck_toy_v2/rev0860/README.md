# streamfold_sumcheck_toy_v2 — rev0860 payload graft lane

rev0860 makes the missing canonical streamfold payload frontier executable. It does not recover payload bytes; it creates a safe isolated path for staging exact matching bytes once a canonical/candidate tree is mounted.

## Current overlay state

```text
full expected payloads:    17
full expected bytes:       25066
minimum recovery payloads: 4
payloads present here:     0
```

## Commands

```bash
python3 PROOFCORE/verifiers/prepare_streamfold_payload_graft_rev0860.py --mode full --json
python3 PROOFCORE/verifiers/prepare_streamfold_payload_graft_rev0860.py --mode minimum --json
python3 PROOFCORE/verifiers/prepare_streamfold_payload_graft_rev0860.py --self-test --json
python3 scripts/validate_streamfold_payload_graft_rev0860.py
```

When a candidate canonical tree is available:

```bash
python3 PROOFCORE/verifiers/prepare_streamfold_payload_graft_rev0860.py \
  --candidate-root /path/to/canonical/tree \
  --mode minimum \
  --stage-dir /tmp/ev-streamfold-minimum-graft \
  --json
```

The stage directory must be outside this overlay and outside the candidate root. It will contain only verified selected payloads plus `EV_STREAMFOLD_PAYLOAD_GRAFT.rev0860.json` and `payloads.sha256`.

## Non-claims

This is not a recovered payload bundle, not a rights grant, not a publication clearance, not a streamfold correctness proof, not a SNARK, not zero knowledge, and not succinct.
