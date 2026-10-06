# Supervision and reconciliation — rev0002

## Why this exists

A serious runtime must have an answer for worker failure, task cancellation, corrupted storage state, multi-tab races, quota pressure, and capability changes.

## Supervision tree sketch

```txt
BrowserRT root supervisor
├── ui supervisor
│   └── interactive bridge
├── cpu supervisor
│   ├── worker pool A
│   └── worker pool B
├── storage supervisor
│   ├── journal writer
│   ├── block store
│   └── compactor
├── gpu supervisor
│   └── device manager
├── mesh supervisor
│   ├── BroadcastChannel bus
│   ├── Web Locks leader election
│   └── SharedWorker coordinator
└── telemetry supervisor
    ├── trace writer
    └── replay recorder
```

Every child has:

- start policy,
- stop policy,
- restart policy,
- health probe,
- failure classifier,
- trace label.

## Reconciliation loops

Some BrowserRT tasks are controllers, not jobs. They repeatedly drive actual state toward desired state.

Examples:

- exactly one storage compactor should run per origin,
- OPFS manifest should match journaled blocks,
- visible tab should have interaction priority,
- background tabs should not stampede polling or maintenance,
- GPU device loss should invalidate GPU refs and reschedule fallbacks,
- leaked leases should be detected and reclaimed or quarantined.

## Design rule

Edge-triggered events are hints. Runtime controllers should prefer level-based reconciliation wherever possible.

