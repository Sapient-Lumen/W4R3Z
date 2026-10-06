# ADR-0344: Removable-media local fallback post-detach peer interaction stays launcher-isolated and ambient-IPC-free

- Status: accepted
- Date: 2026-05-18
- Deciders: archive maintainers
- Consulted: `docs/294-oblivious-sandboxing-launchers.md`, `docs/143-resource-controls-rctl-racct-cpuset.md`, `docs/278-device-grants-and-devfs-rulesets.md`, `docs/754-removable-media-local-fallback-post-detach-resource-envelope-stays-launcher-enforced-and-receipt-visible.md`, `spec/preopen.map.schema.json`

## Context

ADR-0337 through ADR-0343 made the post-detach removable-media later worker closed-world across descriptors, launch context, executable identity, runtime dependency closure, credentials, lifecycle, and resources. A remaining host-local seam is peer interaction: a non-root, bounded, digest-pinned worker can still be influenced or observed by same-UID peers, inherited sessions, procfs/ptrace/ktrace surfaces, unreviewed IPC endpoints, or unrelated worker instances if the launcher leaves those surfaces implicit.

For the first removable-media local fallback, post-detach later work is supposed to be a one-shot computation over one preserved subject and one declared derivative sink. Ambient peer control or observation would make the receipt less trustworthy even if the worker's descriptors and resource limits were correct.

## Decision

For the first host-local removable-media fallback lane, post-detach later workers now use `launcher-isolated-peer-envelope-no-ambient-ptrace-signal-or-ipc`, `receipt-records-peer-isolation-and-signal-policy`, `launcher-only-signal-control-no-peer-or-session-control`, `no-unreviewed-ipc-sockets-shm-pipes-or-procfs`, and `procfs-ptrace-and-ktrace-unavailable-to-worker-and-peers`.

1. **The launcher owns the peer-interaction envelope.**
   - The worker is launched so unrelated same-UID processes, parent sessions, operator shells, and unrelated worker instances cannot ptrace, signal-control, attach to, observe through procfs/ktrace, or inject IPC into the run.
   - Backend details may include jail/process-visibility settings, disabled procfs mounts, ptrace/debug denial, distinct worker principals or per-run confinement, and launcher-owned process handles. The portable contract is the receipt-visible peer-interaction posture.

2. **Signal authority is launcher-only.**
   - The worker records `launcher-only-signal-control-no-peer-or-session-control`.
   - Lifecycle control remains with the launcher/broker path that already owns supervision, timeout, reaping, and receipt timing.
   - Parent TTY/session control, operator shell signals, and same-UID peer control are not part of the first lane.

3. **Unreviewed IPC stays out.**
   - The worker records `no-unreviewed-ipc-sockets-shm-pipes-or-procfs`.
   - Sockets, shared memory, named pipes, inherited IPC endpoints, procfs handles, or other peer communication surfaces are absent unless a future explicit wrapper/broker contract admits and receipts them.
   - Stdio remains launcher-owned observation, not a session or peer-control channel.

4. **Procfs/ptrace/ktrace visibility is not authority.**
   - The worker records `procfs-ptrace-and-ktrace-unavailable-to-worker-and-peers`.
   - The first lane does not rely on ambient process filesystem visibility, debugger attach policy, tracing defaults, or host-local observability folklore.
   - If a diagnostic lane needs richer observation, it must be a separately reviewed support/debug path, not the ordinary removable-media import path.

## Consequences

- The first lane no longer assumes that a low-privilege worker UID alone prevents peer control or observation.
- Receipts can distinguish successful isolated execution from a run that depended on ambient session, same-UID, procfs, ptrace, ktrace, or IPC behavior.
- Compatibility tools that need brokers, helper daemons, or debug hooks need a future explicit contract rather than hidden host-local side channels.
- The post-detach worker remains boring: one preserved subject, one declared derivative sink, one launcher-owned control path, no peer IPC/control/observation authority.

## Alternatives considered

- **Rely on the unprivileged worker user.** Rejected because same-UID or process-visibility policy can still allow observation/control on many host configurations.
- **Treat procfs/ptrace policy as host hardening.** Rejected because this lane needs artifact-visible authority, not installation folklore.
- **Allow helper IPC as long as descriptors are closed.** Rejected because IPC can be reacquired through ambient namespaces or inherited endpoints unless explicitly modeled.
- **Permit debug hooks in the ordinary lane.** Rejected because debug/support paths should be reviewed as separate leases with separate evidence.

## Follow-up

- Update the canonical removable-media local-ingest examples so they record peer-interaction, signal, IPC, and procfs/ptrace/ktrace posture.
- Add a drift check that fails if the first lane slides back to ambient peer control, unreviewed IPC, procfs/ptrace/ktrace visibility, or receipt-invisible signal policy.

## Links

- boundary doc: `docs/755-removable-media-local-fallback-post-detach-peer-interaction-stays-launcher-isolated-and-ambient-ipc-free.md`
- previous cut: `adrs/ADR-0343-removable-media-local-fallback-post-detach-resource-envelope-stays-launcher-enforced-and-receipt-visible.md`
