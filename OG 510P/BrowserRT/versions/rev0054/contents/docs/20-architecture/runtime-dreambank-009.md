# Runtime dreambank 009 — BrowserRT as a shared-memory nervous system

Revision: rev0028

This dreambank pass imagines BrowserRT not as workers sending messages, but as a small local machine with nerves. Workers, storage providers, render lanes, and future Wasm kernels exchange tiny control records through bounded mailboxes while bulk bytes move through refs.

## North-star fantasy

A future BrowserRT app has:

- a UI lane;
- CPU worker lanes;
- storage workers;
- render workers;
- GPU command providers;
- Wasm kernels;
- devtools trace consumers;
- replay recorders.

They do not clone giant JS objects. They exchange compact envelopes and object refs. Hot paths use calibrated mailbox providers.

```txt
control plane: tiny sequenced records
bulk plane: transfer refs, shared slabs, OPFS blocks, GPU buffers, streams
trace plane: append-only event stream
```

## The shared-memory frontier

The rev0025 proof adds a tiny SharedArrayBuffer ring. It is intentionally small: single producer, single consumer, fixed Int32 payloads, Node worker_threads. The point is to establish shape, evidence, and vocabulary.

Future rings should be provider-backed:

```ts
type MailboxProvider =
  | 'clone-channel'
  | 'transfer-channel'
  | 'sab-spsc-fixed'
  | 'sab-mpsc-command'
  | 'sab-trace-broadcast'
  | 'wasm-shared-memory'
```

Every provider must report:

- capability requirements;
- blocking behavior;
- overflow policy;
- close semantics;
- memory ownership;
- trace events;
- fallback provider;
- proof task id.

## Stolen design ideas

### Disruptor-style sequence discipline

A ring should use sequence numbers, not ambiguous head/tail folklore. Wraparound becomes evidence: the proof can show `write > capacity`, `read > capacity`, and no lost order.

### Bounded-channel backpressure

A full ring is not a nuisance; it is the signal. Full counters, producer waits, spill decisions, and cancellation decisions should be visible in traces.

### Wasm-thread compatibility

If BrowserRT eventually hosts Wasm plugins, the shared-memory lane must not be purely JS-object-shaped. The future ABI should accept raw offsets and lengths, and the envelope should be understandable without structured clone.

### Trace as an always-on observer

Ring events should be cheap but visible:

- `ipc:sab-ring-create`
- `ipc:sab-ring-open`
- `ipc:sab-ring-push`
- `ipc:sab-ring-full`
- `ipc:sab-ring-pop`
- `ipc:sab-ring-close`

The rev0025 proof records these for the producer side and uses worker results to prove consumer behavior.

## Dangerous dreams

- A same-origin tab cluster where the visible tab owns UI priority while hidden tabs run CPU/storage lanes.
- A trace ring consumed live by a devtools panel without disturbing the workload.
- A Wasm plugin ABI that receives object refs and a mailbox endpoint.
- A storage provider that publishes completions through a ring rather than promises.
- A GPU provider that uses a completion ring for dispatch lifecycle.
- A browser-local actor runtime where actors own inbox rings and can be replayed from trace.

## Tempering rule

No shared-memory feature becomes canonical unless it has:

- a provider contract;
- a fallback;
- a non-claim boundary;
- a trace vocabulary;
- a manifest task;
- a proof artifact.

The current proof is `ipc:sab-ring-proof`. It is not a performance benchmark and not a browser SAB proof.
