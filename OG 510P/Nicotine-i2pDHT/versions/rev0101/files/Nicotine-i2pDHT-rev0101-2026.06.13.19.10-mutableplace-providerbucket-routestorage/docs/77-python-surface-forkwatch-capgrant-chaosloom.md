# Python surface — rev0009

## `forkwatch.py`

Primary classes and functions:

```text
MutableHeadObservation
MutableHeadMemory
HeadVerdict
HeadForkEvidence
WitnessReceipt
select_best_mutable_record
receipts_for_target
```

This module handles local mutable-head history, not network transport.

## `capgrant.py`

Primary classes and functions:

```text
CapabilityGrant
CapabilityRequest
CapabilityEvaluator
RevocationEntry
RevocationHead
make_revocation_mutable_head
```

This module handles bounded delegation and revocation-head structure.

## `chaos.py`

Primary classes and functions:

```text
FakeReplica
FakeAsyncLookupHarness
LookupTranscript
SeedCaptureReport
assess_seed_capture
```

This module creates deterministic adversarial transcripts. It also preserves compatibility with the earlier `headlog.py` chaos surface.

## Test lane

```bash
pytest -q tests/test_forkwatch_capgrant_chaos.py
```

The full cube lane remains:

```bash
scripts/ci/run_python_cloudtainer_lane.sh
```

## Notable overlap with older modules

The cube now has both:

```text
headlog.py      older versioned-head model with prev pointers
forkwatch.py    record-native mutable observation memory
capability.py   older chain-verifiable capability sketch
capgrant.py     newer verb/resource/audience evaluator sketch
```

This duplication is intentional for now. The project is still in deep-guess mode; conflicting prototypes are evidence, not mess. The next revision should compare and fuse them.
