# Related work research pass 008 — recovery, logs, checkpoints, simulation

Revision: rev0028

## Direction

This pass treats BrowserRT as a future recovery kernel. The immediate code slice stays small: a fake journaled memory provider with manifest checkpoint, post-checkpoint journal replay, torn-tail handling, corrupt-manifest rejection, and trace evidence.

## Ideas stolen

### SQLite WAL

SQLite WAL sharpened the primitive split: write, read, and checkpoint are distinct operations. BrowserRT should not hide checkpointing inside vague persistence language. The cube now says recovery providers must name their journal, manifest, replay, and checkpoint semantics.

### SQLite WAL file shape

SQLite's separation of main database, wal file, and shared-memory coordination pressure maps cleanly onto BrowserRT provider layers: manifest as checkpointed truth, journal as roll-forward tail, and future mesh/lock surfaces as coordination rather than data truth.

### RocksDB / LSM storage

RocksDB reinforced that fast writes create later maintenance work. BrowserRT should expect compaction/checkpoint lanes and should trace when maintenance is deferred rather than pretending storage is merely `put/get`.

### ARIES-style recovery vocabulary

ARIES vocabulary points toward logging decisions explicitly enough that redo/undo/replay can be reasoned about. BrowserRT is not implementing ARIES, but the cube borrows the instinct: recovery decisions must be inspectable trace events.

### FoundationDB deterministic simulation

FoundationDB's simulation discipline reinforced that fake providers are not childish. They are the cheap place to force recovery state machines through failures before browser fixtures become expensive.

### Kubernetes controllers

Kubernetes controllers sharpened the idea that storage recovery should be a reconciler: observe current provider state, compare it with desired manifest/journal state, then drive toward convergence with traceable steps.

### OpenTelemetry traces

OpenTelemetry trace/span vocabulary reinforced that recovery should emit structured causal evidence. For now BrowserRT emits event kinds; later these can become spans with parent ids, attributes, and statuses.

## Cube pressure

The rev0025 slice deliberately stays fake-provider-only. A future OPFS crash/restart proof should only arrive after the fake recovery contract stops moving.
