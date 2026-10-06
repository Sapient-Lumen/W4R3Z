# Removable-media local fallback post-detach worker lifecycle stays launcher-supervised and daemon-free

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, reproducibility, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt

The removable-media local fallback has narrowed into a first coding lane: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite filesystem-family admission, inert mounted tree, physical root-pinned walk, one selected regular-file subject, capture-first into `/work`, verified capture committed into authoritative quarantine store before detach, later work restarted in a fresh worker with `/ingest` absent, one digest-bound launcher-preopened read-only preserved subject, one broker-collected declared derivative sink, capability mode before later tool mainline, closed-world reviewed descriptors, launcher-owned stdio, reviewed environment/argv/cwd, launcher-pinned executable identity, launcher-pinned runtime dependency closure, and launcher-fixed unprivileged credentials.

This page closes the next process-lifetime seam:

> **the later worker must not daemonize, leave orphan descendants, or let background subprocesses outlive the launcher evidence window.**

See also:
- ADR: `adrs/ADR-0342-removable-media-local-fallback-post-detach-worker-lifecycle-stays-launcher-supervised-and-daemon-free.md`
- previous cut: `docs/752-removable-media-local-fallback-post-detach-credential-envelope-stays-launcher-fixed-and-non-elevating.md`
- capability-mode handoff: `docs/746-removable-media-local-fallback-post-detach-later-tool-code-enters-capability-mode-before-mainline-and-stays-there.md`
- launcher/preopen posture: `docs/294-oblivious-sandboxing-launchers.md`
- process ownership background: `docs/235-process-contracts-and-service-ownership.md`
- compiled capability map: `spec/preopen.map.schema.json`

## Why this needs a hard decision

The first lane now pins what the worker can see, how it starts, which code it runs, which runtime dependency closure it may use, and which credential envelope executes it.
That still does not say whether the process is a bounded one-shot worker or a hidden process supervisor.

Without this cut, the first lane could still depend on:

- daemonization or double-fork behavior that outlives the launcher,
- background helpers spawned after the reviewed executable starts,
- orphan descendants that keep descriptors or derivative sinks open,
- derivative receipts emitted while the worker tree is still alive,
- host-local process cleanup folklore rather than receipt-visible lifecycle evidence.

Those are authority and evidence-ordering risks under another name.
For the first lane, the honest rule is: **the launcher supervises and reaps the entire worker tree before derivative evidence becomes authoritative.**

## Accepted cut

For the first host-local removable-media ingest lane:

### 1) Worker lifecycle is launcher-supervised and daemon-free

The later worker records `launcher-supervised-no-daemon-or-orphan-descendants`.
The launcher starts and observes the reviewed worker tree for the single post-detach operation.
The worker does not become a daemon, service, detached session, or long-lived helper.

### 2) Descendant behavior stays closed in the first lane

The later worker records `no-background-descendants-or-unreviewed-subprocesses`.
Double-fork, session detachment, shell helper fanout, service activation, plugin helper launch, and unreviewed subprocess execution stay out of the first lane.
A later compatibility lane may admit helpers, but only with an explicit wrapper/broker process-tree contract and receipts.

### 3) Reap happens before authoritative derivative receipt

The later worker records `launcher-reaps-entire-worker-tree-before-receipt`.
The import receipt records `worker-exit-observed-before-derivative-receipt`.
The launcher/broker may collect and remeasure the declared derivative sink, but the derivative locator does not become authoritative until worker exit is observed and the entire worker tree is reaped.

### 4) Plans, receipts, and preopen maps expose lifecycle posture

The canonical examples now carry:

- `post_detach_process_lifecycle_posture`
- `post_detach_descendant_posture`
- `post_detach_reap_posture`
- `post_detach_worker_exit_posture`

The attach grant also carries:

- `post_detach_lifecycle_receipt_posture`
  - canonical value: `receipt-records-worker-exit-and-descendant-reap`
- `post_detach_process_lifecycle_required`

The preopen map carries the same posture under launcher-focused names:

- `process_lifecycle_posture`
- `descendant_posture`
- `reap_posture`
- `worker_exit_posture`

Together with the descriptor set, launch context, executable digest, wrapper digest, runtime dependency closure digest, and credential envelope, these fields make the worker's lifetime reviewable without consulting launcher folklore.

## Canonical first-cut example stack

The worker-lifecycle cut is now explicit in:

- `spec/examples/device.attach.grant.removable-media-local-ingest.json`
- `spec/examples/content.import.plan.removable-media-local-ingest.json`
- `spec/examples/device.detach.receipt.removable-media-local-ingest.json`
- `spec/examples/content.import.receipt.removable-media-local-ingest.json`
- `spec/examples/preopen.map.removable-media-local-ingest-post-detach.json`

Together they now say:

- executable selection is launcher-owned and digest-pinned,
- wrapper and runtime closure identity are receipt-visible,
- the worker credential envelope is launcher-fixed and unprivileged,
- the worker process tree is launcher-supervised and daemon-free,
- background descendants and unreviewed subprocesses stay out,
- worker exit and tree reap happen before derivative receipt authority,
- and helper subprocess behavior stays out unless a later explicit wrapper/broker lane admits and receipts it.

## Why this cut is worth making now

Without this decision, the archive could produce receipts that look complete but still hide process lifetime drift:

- a sanitizer could leave a helper holding the derivative sink after the broker collected bytes,
- a double-forked descendant could continue operating under a narrow but still real descriptor set,
- receipt timing could claim completion before the reviewed worker tree actually ended,
- and support would have to reconstruct process ancestry and cleanup from host-local logs instead of typed evidence.

This is deliberately boring and strict.
The first lane is a one-shot post-detach worker, not a service supervisor.

## Compatibility impact

Some existing tools assume helper subprocesses or plugin helper launch.
Those tools are not rejected forever; they simply do not fit the first lane unless wrapped by an explicit broker/launcher contract that:

- declares the helper process tree,
- pins helper code and runtime dependencies,
- keeps helper descriptors and credentials reviewed,
- reaps the entire tree before receipt authority,
- and records the process-tree shape in receipts.

That later lane can be designed when a real compatibility target needs it.
The current first lane remains daemon-free and launcher-reaped.

Last updated: 2026-05-18r498
