# Observability and replay — rev0002

## Runtime law

No performance or reliability claim without trace evidence.

BrowserRT should emit enough information to answer:

- What ran?
- Where did it run?
- What did it wait for?
- How many bytes moved?
- What capability path was selected?
- What downgraded?
- What failed?
- What recovered?
- Did the main thread get blocked?
- Did memory grow unexpectedly?

## Trace event families

```txt
runtime:boot
capability:probe
capability:select
process:start
process:exit
task:create
task:state
task:complete
task:fail
queue:push
queue:pop
memory:alloc
memory:lease
memory:release
object:materialize
storage:write
storage:read
storage:recover
gpu:dispatch
gpu:fallback
mesh:leader
mesh:message
jank:long-task
memory:measure
replay:checkpoint
```

## Replay bundle sketch

```txt
trace.brt.json
capabilities.json
tasks.jsonl
objects.manifest.json
storage-blocks/
worker-crashes.jsonl
random-seeds.json
notes.md
```

A replay does not need to perfectly reproduce every browser timing detail. It must reproduce enough to debug scheduler decisions, data movement, and recovery behavior.

## Cloudtainer value

Replay bundles are ideal for ChatGPT iteration. Instead of describing a failure, the next revision can include a compact trace and deterministic synthetic workload.

