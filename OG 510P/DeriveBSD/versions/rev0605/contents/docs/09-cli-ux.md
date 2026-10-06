# CLI and UX principles

## The UX problem we must avoid

Do not ship multiple overlapping tools with unclear guidance.

## Proposed top-level commands

- `derive init`          : create a new spec scaffold
- `derive lock`          : resolve sources and write lock
- `derive plan`          : compute the Plan (DAG + policy)
- `derive build`         : realize artifacts
- `derive install`       : install a package closure
- `derive switch`        : activate a system generation
- `derive rollback`      : revert to prior generation
- `derive verify`        : verify digests/signatures/attestations/closure proofs
- `derive attest`        : emit attestations for a realized artifact
- `derive explain`       : structured explanation of an artifact/closure
- `derive explain-policy`: show the policy decision record + trace for a plan/artifact
- `derive diff`          : diff plans/deployments (including blast-radius mode)
- `derive why-depends`   : dependency tracing
- `derive deploy`        : show/switch/rollback deployment refs (host + workloads)
- `derive compat`        : run/explain foreign binaries in a policy-governed compat view
- `derive vm`            : workload lifecycle (microVM/jail) via the control plane
- `derive gc`            : garbage collection

## Debugging must be first-class

Every failure should:
- identify the failing step
- show the exact sandbox and inputs
- emit a reproduction capsule (jail recipe + lock + plan excerpt)


Last updated: 2026-02-23
