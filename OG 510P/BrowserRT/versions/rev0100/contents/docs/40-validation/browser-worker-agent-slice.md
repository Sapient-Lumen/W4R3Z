# Browser Worker agent slice

Revision: rev0028

Manifest task: `browser:worker-agent-proof`
Tool: `tools/browser_worker_agent_probe.mjs`
Artifact: `artifacts/validation/REV0044-BROWSER-WORKER-AGENT-PROBE.json`

## Why this slice exists

Rev0006 proved that a managed local browser/CDP fixture could boot a page, import BrowserRT, observe capabilities, and tear down. It did not prove that BrowserRT could create and use a real browser Worker.

Rev0008 adds the smallest useful Worker proof:

```txt
local server
  -> Chromium/CDP
  -> BrowserRT module import
  -> module Worker spawn
  -> shared agent runtime import inside Worker
  -> ping call with BRT1 envelope
  -> transferable ArrayBuffer sum
  -> sender detachment observed
  -> agent terminate trace
  -> teardown and policy restoration
```

## What it proves

- A browser page can import `src/browserrt.mjs` from the local fixture.
- `rt.spawnAgent()` can create a module Worker using `src/browser-agent-worker.mjs`.
- The Worker imports `src/agent-runtime.mjs`.
- The Worker posts `agent:ready`.
- A `ping` call returns and preserves the BRT1 envelope.
- A transferred `ArrayBuffer` reaches the Worker.
- The sender observes detachment after transfer.
- The Worker computes `sum-u32` and returns the expected result.
- The trace includes spawn, ready, call, result, transfer-ref, terminate, and close events.
- Temporary Chromium policy relaxation is restored.

## What it does not prove

- Browser supervisor crash/restart behavior.
- OPFS correctness.
- SharedArrayBuffer mailbox correctness.
- WebGPU correctness.
- SharedWorker or ServiceWorker correctness.
- Cross-browser conformance.
- Real browser performance.
- Cross-turn browser process persistence.

## Why it is not folded into the boot probe

The boot probe should stay cheap and conceptual: can we launch, import, observe, and tear down?

The Worker probe is a separate slice because Worker startup, module import, transfer behavior, and worker trace events are a different failure surface. Future OPFS/SAB/WebGPU tests must likewise remain separate.

## Expected artifact fields

The artifact should contain:

- `status: passed`;
- `policyRelaxation.restored: true`;
- `observations.page.crossOriginIsolated: true`;
- `observations.workerProof.pingPong: true`;
- `observations.workerProof.pingEnvelopeMagic: BRT1`;
- `observations.workerProof.sum: 60`;
- `observations.workerProof.detachedAfter: true`;
- trace kinds including `agent:spawn`, `agent:ready`, `agent:call`, `agent:result`, `object:transfer-ref`, `agent:terminate`, and `runtime:close`.
