# rev0074 public trace capture kit replay audit

rev0074 packages the missing public/pretrained trace lane into an executable capture/replay kit.

## What it proves

- The capture-kit files are emitted and hash-tracked.
- A schema-valid non-public Q/K/V fixture loads through the public trace gate as external, not public/pretrained evidence.
- The same Q/K/V bundle can be exported to the native QK replay binary.
- Native CPU replay processed `32` rows with quality rate `1.0`.

## What it does not prove

- It does not contain a real public/pretrained model trace.
- It does not measure GPU/fused attention kernels.
- It does not promote materialized score storage as a deployment win.

## Next action

Run `artifacts/capture-kit/REV0074_RUN_PUBLIC_TRACE_CAPTURE_AND_REPLAY.sh` on a model-enabled machine with reviewed model/license provenance.
