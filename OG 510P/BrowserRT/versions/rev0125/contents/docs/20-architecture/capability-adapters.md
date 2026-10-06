# Capability adapters — rev0002

## Principle

A BrowserRT lane is not an API. A lane is a contract with one or more adapters.

Examples:

- CPU lane: dedicated worker pool, Node worker backend, main-thread emergency fallback.
- Storage lane: OPFS async, OPFS sync worker, memory store, Node fs backend.
- GPU lane: WebGPU compute, CPU fallback.
- Render lane: OffscreenCanvas worker, main canvas fallback.
- Media lane: WebCodecs where available, generated-frame fallback.
- Audio lane: AudioWorklet where available, disabled fallback.
- ML lane: WebNN, WebGPU/wasm engine, or no-ML fallback.
- Mesh lane: SharedWorker, BroadcastChannel, Web Locks, or single-tab fallback.

## Adapter shape

```ts
type RtAdapter = {
  id: string
  lane: RtLane
  tier: RtCapabilityTier
  probe(): Promise<RtProbeResult>
  calibrate?(): Promise<RtCalibration>
  run?(task: RtTask): Promise<RtTaskResult>
  close(): Promise<void>
}
```

## Trace requirement

Every adapter choice and downgrade emits a trace event.

```txt
capability:probe
capability:select
capability:downgrade
capability:lost
capability:restore
```

## Why this matters

It lets BrowserRT be ambitious without lying. The same app can run tiny on a restricted browser and huge on an isolated, GPU-enabled, OPFS-capable environment.

