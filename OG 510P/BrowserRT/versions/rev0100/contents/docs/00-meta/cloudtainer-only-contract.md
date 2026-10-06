# Cloudtainer-only contract

Revision: rev0028.

BrowserRT cubes must be buildable and testable from the packaged zip using only
local cloudtainer facilities. No CDN, remote service, hosted asset, external
model, or npm dependency is part of the current contract.

## Consequences

- Source and tooling stay dependency-free unless a future revision vendors a
  dependency explicitly.
- Research is summarized by title/domain in registries; raw URLs are not embedded
  in the cube.
- Synthetic fixtures are preferred over downloaded datasets.
- Browser, OPFS, SAB, WebGPU, and mesh harnesses must create their resources
  locally and clean them up.
- Long-lived background processes are not canonical validation state.

## Testing consequence

Because cloudtainer windows can be short and process persistence can be
uncertain, validation must be decomposed. The cube now uses a manifest-defined
runner with per-test timing, timeouts, explicit parallel-safety metadata, and
sharding. Future expensive harnesses must join that runner instead of expanding a
single monolithic test command.
