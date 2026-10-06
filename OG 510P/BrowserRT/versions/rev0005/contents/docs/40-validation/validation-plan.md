# Validation plan

Revision: rev0005.

## Current release gate

```bash
make lint
```

`make lint` performs cube checks, runs the release tier with timing history, and runs cube checks again.

## Narrow commands

```bash
make turn-start
node tools/run_tests.mjs --tier smoke --jobs auto
node tools/run_tests.mjs --tier release --id runtime:smoke
node tools/run_tests.mjs --tier release --changed src/browserrt.mjs --jobs auto
node tools/run_tests.mjs --tier release --shard 1/2 --jobs auto
node tools/run_tests.mjs --tier release --explain
```

## Current release tasks

- `harness:selftest`
- `test:surface-audit`
- `test:impact-plan`
- `runtime:smoke`
- `proof:phase-zero-agent-supervisor`

`cube:check` is an audit/full task and is also called by `make lint` around the release tier.

## Future gates

Browser, OPFS, SAB, WebGPU, mesh, and chaos gates must first land as small manifest ids with resource declarations, timeouts, and non-claims. A full demo is not a substitute for sliced proofs.
