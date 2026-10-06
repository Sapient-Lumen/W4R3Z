# Removable-media local fallback post-detach peer interaction stays launcher-isolated and ambient-IPC-free

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, reproducibility, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt

The removable-media local fallback has narrowed into a first coding lane: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite filesystem-family admission, inert mounted tree, physical root-pinned walk, one selected regular-file subject, capture-first into `/work`, verified capture committed into authoritative quarantine store before detach, later work restarted in a fresh worker with `/ingest` absent, one digest-bound launcher-preopened read-only preserved subject, one broker-collected declared derivative sink, capability mode before later tool mainline, closed-world reviewed descriptors, launcher-owned stdio, reviewed environment/argv/cwd, launcher-pinned executable identity, launcher-pinned runtime dependency closure, launcher-fixed unprivileged credentials, launcher-supervised daemon-free lifecycle, and a launcher-enforced resource envelope.

This page closes the next peer-interaction seam:

> **the later worker must not be controlled or observed by ambient same-UID peers, parent sessions, procfs/ptrace/ktrace, or unreviewed IPC while producing derivative evidence.**

See also:
- ADR: `adrs/ADR-0344-removable-media-local-fallback-post-detach-peer-interaction-stays-launcher-isolated-and-ambient-ipc-free.md`
- previous cut: `docs/754-removable-media-local-fallback-post-detach-resource-envelope-stays-launcher-enforced-and-receipt-visible.md`
- launcher/preopen posture: `docs/294-oblivious-sandboxing-launchers.md`
- device grant/devfs posture: `docs/278-device-grants-and-devfs-rulesets.md`
- compiled capability map: `spec/preopen.map.schema.json`

## Why this needs a hard decision

The first lane now pins the worker's descriptors, startup context, executable, runtime closure, credentials, process lifetime, and resource budget. That still does not say whether other host-local processes can attach to it, signal it, trace it, inspect it through procfs, or communicate through an unreviewed IPC namespace.

Without this cut, the first lane could still depend on:

- host defaults for ptrace/debug permissions,
- procfs or ktrace visibility that varies by installation,
- same-UID peer processes sharing the worker principal,
- parent TTY/session signals or operator shell attachment,
- unreviewed sockets, shared memory, pipes, or helper-daemon IPC,
- receipt text that says the worker was bounded but not whether peer control or observation was excluded.

Those are authority risks, not convenience knobs. For the first lane, the boring rule is: **the launcher owns the worker's only control path, and peer interaction posture is receipt-visible.**

## Accepted cut

For the first host-local removable-media ingest lane:

### 1) Peer interaction is launcher-isolated

The later worker records `launcher-isolated-peer-envelope-no-ambient-ptrace-signal-or-ipc`.
The launcher creates a peer envelope in which unrelated same-UID processes, parent sessions, operator shells, and unrelated worker instances cannot attach to, signal-control, trace, inspect, or IPC-inject into the run.

Backend details are implementation choices. They may include jail/process-visibility settings, disabled procfs mounts, ptrace/debug denial, per-run confinement, distinct worker principals, launcher-owned process handles, or equivalent mechanisms. The portable contract is the posture string plus receipt evidence, not a specific knob name.

### 2) Signal control is launcher-only

The later worker records `launcher-only-signal-control-no-peer-or-session-control`.
Timeouts, termination, and lifecycle observation are part of the launcher/broker control path that already owns supervision and reaping. Parent TTY/session control, operator shell signals, and same-UID peer signals are not admitted authority in the first lane.

### 3) Unreviewed IPC stays out

The later worker records `no-unreviewed-ipc-sockets-shm-pipes-or-procfs`.
The first lane admits only the reviewed descriptor set and launcher-owned observation channels. It does not admit unreviewed Unix sockets, inet sockets, shared memory, named pipes, inherited IPC endpoints, procfs handles, or helper-daemon IPC.

### 4) Procfs, ptrace, and ktrace are unavailable

The later worker records `procfs-ptrace-and-ktrace-unavailable-to-worker-and-peers`.
Procfs visibility, debugger attach, process tracing, and host-local observability defaults do not become part of ordinary derivative authority. A diagnostic/support lane can exist later, but it must be a separate lease and receipt path.

### 5) Receipts expose the posture

The later worker records `receipt-records-peer-isolation-and-signal-policy`.
Canonical examples carry peer-interaction posture through:

- `post_detach_peer_interaction_posture`
- `post_detach_peer_interaction_receipt_posture`
- `post_detach_signal_posture`
- `post_detach_ipc_posture`
- `post_detach_procfs_posture`

The preopen map carries the launcher-facing equivalents:

- `peer_interaction_posture`
- `peer_interaction_receipt_posture`
- `signal_posture`
- `ipc_posture`
- `procfs_posture`

Together with the descriptor set, launch context, executable digest, wrapper digest, runtime dependency closure digest, credential envelope, lifecycle posture, and resource envelope, these fields make the worker's external control and observation boundary reviewable without reading host-local jail, procfs, or service defaults.

## Canonical first-cut example stack

The peer-interaction cut is now explicit in:

- `spec/examples/device.attach.grant.removable-media-local-ingest.json`
- `spec/examples/content.import.plan.removable-media-local-ingest.json`
- `spec/examples/device.detach.receipt.removable-media-local-ingest.json`
- `spec/examples/content.import.receipt.removable-media-local-ingest.json`
- `spec/examples/preopen.map.removable-media-local-ingest-post-detach.json`

Together they now say:

- the launcher/broker path is the only reviewed control path,
- same-UID peers and parent sessions cannot signal-control the worker,
- procfs, ptrace, and ktrace are not ambient observation authority,
- unreviewed sockets, shared memory, pipes, and helper IPC stay out,
- the receipt records the peer/signal posture,
- and debug/support lanes must be explicit rather than hiding in the ordinary import path.

## Why this cut is worth making now

Without this decision, the archive could produce receipts that look complete but still hide peer authority:

- an unrelated same-UID process could attach to or signal the worker,
- support tooling could rely on procfs/ktrace visibility that is not in the receipt,
- helper IPC could smuggle control into the run after descriptors were reviewed,
- parent session behavior could influence lifecycle or observations,
- and the same preserved subject could produce a derivative under a peer-influenced execution envelope.

This cut keeps the first lane narrow: one worker, one preserved subject, one declared bounded derivative slot, one launcher-owned control path, no ambient peer interaction authority.

## Compatibility impact

Some tools need helper daemons, broker IPC, debug traces, or richer process observation. Those tools are not rejected forever; they require an explicit later compatibility lane that:

- declares the helper or debug authority,
- binds it to a reviewed wrapper/broker contract,
- records the peer-interaction posture in receipts,
- preserves the one-subject and derivative-egress invariants unless separately reviewed.

The current first lane remains ambient-IPC-free and launcher-isolated.

Last updated: 2026-05-18r500
