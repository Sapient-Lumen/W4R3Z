# Python surface — rev0010

## `pathpressure.py`

Core objects:

```text
PathHeadReply
PathPressurePolicy
PathPressureTranscript
PathPressureDecision
PathAlarm
run_path_pressure_lookup
```

Purpose: decide whether a mutable-head lookup is clean enough to accept or should continue asking more path families.

## `witnesspoison.py`

Core objects:

```text
WitnessHint
ReceiptAnalysis
analyze_witness_receipts
```

Purpose: verify and group witness receipts so one garden family or contradictory witness cannot become a fake alarm quorum.

## `seedcapture.py`

Core objects:

```text
SeedCapturePolicy
SeedCapturePressure
analyze_seed_capture_pressure
select_diverse_seed_entries
```

Purpose: detect entrance portfolio capture pressure and choose diverse bootstrap entries.

## `revocation_pressure.py`

Core objects:

```text
RevocationHeadMemory
RevocationHeadVerdict
RevocationAuthorityState
```

Purpose: preserve revoked grant hashes across stale revocation-head replay and detect same-sequence revocation forks.

## `succession.py`

Core objects:

```text
KeySuccessionRecord
SuccessionMemory
SuccessionVerdict
```

Purpose: model co-signed key rotation and local rollback/fork detection for mutable-control-plane keys.

## Tests

```text
tests/test_rev0010_risk_first.py  # 12 tests
```
