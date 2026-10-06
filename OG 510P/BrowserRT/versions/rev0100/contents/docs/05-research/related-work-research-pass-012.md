# Related-work research pass 012: model-walked mailbox correctness

Revision: rev0028

This pass shifts ambition from "build a faster mailbox" to "make mailbox semantics executable before the mailbox becomes ambitious." The frame ring is still tiny, but it is the seed of a future BrowserRT binary transport. That future will fail if wrap, backpressure, close, payload boundaries, and ordering are only checked by one happy-path worker test.

## Sources inspected

No external source code is imported into the cube. These are research inspirations recorded as source families only.

- Hypothesis stateful testing: rule-based state machines compare a system under test against a simplified model and generate operation sequences, not just values.
- fast-check model-based testing: commands have preconditions and apply to both the real system and the model.
- QuickCheck / QuviQ state-machine testing: properties plus generated call sequences are a protocol-testing shape, not only a pure-function testing shape.
- TLA+ / PlusCal: concurrent and distributed algorithms deserve small abstract models to catch design errors before implementation complexity hardens.
- Rust Loom: concurrency primitives can be tested by exploring execution permutations; BrowserRT should eventually imitate this idea for mailbox interleavings.
- FoundationDB simulation: fake providers and deterministic simulation are infrastructure, not toys.
- Jepsen and Porcupine: histories should be checked against explicit consistency/linearizability models when BrowserRT grows beyond SPSC.
- AFL / AFL++ / coverage-guided fuzzing: binary parsers and frame envelopes eventually need mutation/corpus pressure, but not in the release tier yet.
- AWS formal-methods practice: formal and semi-formal methods are useful precisely when the hidden substrate is more complex than the external API.

## Stolen ideas

### 1. Every provider needs a model oracle

The mailbox provider should have a stupid reference model:

```txt
model = FIFO queue of { seq, payload }
```

The real ring may use wrap sentinels, byte padding, Atomics, counters, and shared memory. The model does not. Tests compare externally visible behavior.

### 2. Rejection is a first-class operation

A frame push that returns `false` is not "nothing happened" unless the test proves nothing happened. The new slice records rejection-no-mutation checks for oversize and full rings.

### 3. Tiny deterministic walks beat one large flaky proof

A cheap seeded model walk belongs in the release tier. Browser/CDP and true interleaving tests can stay scoped and expensive. This prevents the testing facility from turning every mailbox change into a cloudtainer timeout risk.

### 4. History is the future API

When BrowserRT grows toward MPSC, MPMC, cross-tab mailboxes, actors, or storage leaders, success/failure should be expressed as histories and invariants, not just screenshots or throughput numbers.

## Ambition unlocked

BrowserRT can eventually have a "model lab" for runtime providers:

```txt
provider contract -> reference model -> generated commands -> trace history -> checker -> minimized counterexample
```

That could cover:

- bounded channels;
- framed SAB mailboxes;
- OPFS block stores;
- journal replay;
- cross-tab locks;
- actor supervision;
- scheduler admission/backpressure;
- GPU fallback selection.

## Tempering rule

Model walks are not exhaustive formal verification. They are cheap executable pressure. Every future model-walk artifact must say exactly what it does not explore: browser behavior, true thread interleavings, real timing, quota, eviction, hardware GPU, or cross-browser conformance.
