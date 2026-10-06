# Scheduler contract audit rev0028

Revision: rev0028

Manifest task:

```txt
facility:scheduler-contract-audit
```

Command:

```txt
node tools/scheduler_contract_audit.mjs --json artifacts/audit/REV0044-SCHEDULER-CONTRACT-AUDIT.json
```

The audit exists because scheduler language is especially easy to overclaim. It checks that the `CrossLaneScheduler` proof remains attached to its docs, manifest task, impact-map coverage, artifact, and non-claims.

## Required proof artifact

```txt
artifacts/validation/REV0044-CROSS-LANE-SCHEDULER-PROBE.json
```

## Required posture

- The slice is fake-provider and release-tier.
- It is not browser Worker scheduling.
- It is not preemption.
- It is not work stealing.
- It is not an OPFS/WebGPU/render/media/cross-tab integration.
- It is not a performance claim.
