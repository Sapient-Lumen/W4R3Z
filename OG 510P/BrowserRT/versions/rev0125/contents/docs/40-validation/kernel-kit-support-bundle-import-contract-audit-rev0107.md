# Kernel Kit support bundle import — rev0107

Status: rev0107 linked refinement. Runtime revision remains rev0107.

The support bundle import reader validates a pasted support bundle in the browser-light path. It now preserves `storage-pressure-checkpoint`, `storagePressureCheckpointPresent`, `lifecycleCheckpointPresent`, and the exact command `browser:opfs-lane-quota-backpressure-proof` without executing that command.

Task vocabulary: `demo:kernel-kit-support-bundle-import-proof` and `facility:kernel-kit-support-bundle-import-audit`.

Non-claims: No production support-bundle import claim. No support-bundle authenticity or signature claim. This browser-light reader is not trust validation, telemetry ingestion, command execution, or automated triage.
