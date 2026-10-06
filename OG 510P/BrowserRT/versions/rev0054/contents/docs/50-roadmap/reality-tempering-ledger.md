# Reality tempering ledger

Revision: rev0028

## Why keep ambition large now

Early architecture decisions are expensive to reverse. BrowserRT should dream
large enough that the first contracts do not block storage, GPU, mesh, replay,
plugins, or browser testing later.

## Why implementation must stay tiny now

The cloudtainer window is the build boundary. Complex browser tests are
expensive. A giant integration harness will fail operationally before it teaches
us anything. The cube must therefore grow through tiny verified slices.

## Ambitions retained only as pressure

- browser userspace kernel,
- local compute node,
- cross-tab mesh,
- replay debugger,
- capability-scoped plugin runtime,
- provider marketplace,
- real storage/GPU/render/media lanes.

## Ambitions not yet claims

- production runtime quality,
- real-world performance,
- cross-browser conformance,
- security boundary for untrusted plugins,
- persistent process model across assistant turns,
- full OPFS/SAB/WebGPU correctness,
- multi-tab distributed scheduling.

## Current best next slices

1. Browser Worker spawn proof.
2. OPFS async write/read proof.
3. SAB mailbox smoke in isolated browser context.
4. WebGPU compute smoke behind provider gating.
5. Trace viewer stub that can read current proof artifacts.

Each must be separate, timed, manifest-addressable, and teardown-owned.
