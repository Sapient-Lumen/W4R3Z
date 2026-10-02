# Memory-high and kernel outcome telemetry — applied research for rev0033

Research date: 2026-08-19
Implementation target: IoTox rev0033
Scope: Linux cgroup v2 `memory.high`, `pids.events`, `memory.events`, `cpu.stat`, delegated-subtree ownership, and teardown attribution

## Primary sources

1. Linux kernel, **Control Group v2**
   https://docs.kernel.org/admin-guide/cgroup-v2.html
2. systemd, **Control Group APIs and Delegation**
   https://systemd.io/CGROUP_DELEGATION/

Both sources were retrieved online during rev0033 construction. The implementation treats the kernel
documentation as the controller-interface contract and the systemd document as deployment guidance
for the single-writer delegated-subtree boundary.

## Source findings applied

### `memory.high` is a throttle, not a hard ceiling

The kernel defines `memory.high` as a non-root cgroup read/write byte control whose default is `max`.
Crossing it throttles affected processes and places them under heavy reclaim pressure. Crossing the
high boundary does not itself invoke the OOM killer, and the boundary may be exceeded under extreme
conditions. `memory.max` remains the hard memory limit that can invoke in-cgroup OOM when reclaim
cannot reduce usage.

Applied consequence:

- IoTox exposes `memory.high` separately from `memory.max`.
- Both values are page aligned and exactly read back.
- `memory.high` composes monotonically beneath host policy and is clamped to the effective hard
  maximum when both exist.
- Aggregate memory reservation continues to charge only finite `memory.max`; the high threshold is
  not represented as hard reserved capacity.

### Flat-keyed controller records require key-based parsing

The kernel documents `memory.events` as a read-only flat-keyed record and explicitly warns elsewhere
in the memory controller contract not to depend on stable line positions because new entries may
appear. Current memory event keys include `high`, `max`, `oom`, `oom_kill`, and `oom_group_kill`.
`pids.events` includes `max`. Controller-enabled `cpu.stat` adds `nr_periods`, `nr_throttled`, and
`throttled_usec` to always-present usage fields.

Applied consequence:

- IoTox parses bounded LF-terminated key/value records rather than fixed line order.
- Unknown keys are accepted for forward compatibility.
- Duplicate keys, malformed names, noncanonical unsigned decimals, missing required keys, and
  truncated records fail parsing.
- `oom_group_kill` is optional with a zero fallback for kernels predating that field.
- CPU bandwidth counters are required only after the CPU controller and quota policy have been
  explicitly selected and preflighted.

### Event meanings are operational outcomes

The kernel defines:

- `pids.events:max` as the number of times the cgroup reaches `pids.max`; a fork/clone that would
  violate the policy returns `EAGAIN`.
- `memory.events:high` as throttling/direct-reclaim events caused by crossing `memory.high`.
- `memory.events:max` as attempts to cross the hard boundary.
- `memory.events:oom`, `oom_kill`, and `oom_group_kill` as distinct OOM-state and kill outcomes.
- `cpu.stat:nr_throttled` and `throttled_usec` as CPU bandwidth throttling evidence when the CPU
  controller is enabled.

Applied consequence:

IoTox captures these counters only after recursive `populated=0` and before exact leaf removal, then
adds them to owner-private cumulative runtime truth. It publishes no profile/session label, payload or
peer identity, command, path, terminal byte, or error string.

### Prefer local event files and retain an exact childless fallback

The kernel notes that `memory.events` and `pids.events` are hierarchical and provides `.local`
variants on kernels that implement them. IoTox already validates that every session cgroup is a plain
childless domain, keeps payloads from creating sub-cgroups, and treats that exact leaf as the complete
session subtree.

Applied consequence:

IoTox prefers `memory.events.local` and `pids.events.local` when present. If opening a local file fails
specifically because that kernel interface is unsupported, it falls back to the broadly available
hierarchical record. Other local-file failures do not trigger fallback. The fallback remains
attributable to the exact IoTox session object because the leaf is childless. A future child-cgroup
feature would have to require local records or define a different attribution contract.

### Teardown proof and statistics retention have different safety roles

The kernel provides recursive `cgroup.events:populated` truth and `cgroup.kill` for tree-wide fatal
termination. IoTox's existing lifecycle waits for `populated=0`, verifies the exact pinned inode, and
removes only that leaf. Statistics are useful only after that lifecycle proof; they are not a
substitute for it.

Applied consequence:

- Counters are required to start at zero before the blocked helper enters.
- They are captured after quiescence and before descriptor reset/removal.
- A statistics read/parse failure produces one incomplete outcome and no partial values.
- A statistics failure does not prevent otherwise valid cleanup of a proved-empty exact leaf.
- If exact teardown is not proved, no completed outcome is published and the existing aggregate
  reservation is conservatively stranded when applicable.

### Delegation requires one manager per subtree

systemd documents `Delegate=` as the handoff point below which a service may create and manage its own
sub-cgroups, and emphasizes the single-writer rule. The service manager retains ownership of its unit
cgroup while delegated descendants become the application's exclusive management domain.

Applied consequence:

rev0033 retains the prior requirement for one explicit administrator-delegated cgroup-v2 root,
no-follow path traversal, safe ownership/modes, controller activation, payload non-writability, and a
single IoTox manager. Kernel counters are not evidence against a privileged or same-UID competing
writer that violates that boundary.

## Construction result

rev0033 turns the research into:

- canonical local terminal profile v4 with `cgroup-memory-high-bytes`;
- host CLI parity through `--ratox-cgroup-memory-high-bytes`;
- strict validation, monotone composition, cross-layer clamp, write/read-back, and startup preflight;
- bounded future-key-compatible parsers for PID, memory, and CPU controller outcomes;
- protected zero-baseline interfaces opened before payload attachment;
- one-shot teardown outcomes captured after recursive quiescence and before exact removal;
- saturating cumulative status independent of whether aggregate reservation ceilings are enabled;
- parser, migration, composition, CLI, runtime, aggregate, and split real-kernel-oracle regression
  coverage. Memory/PID and CPU controller requirements are qualified independently; on a suitable
  delegated host the memory lane also crosses `memory.high` with live anonymous-page pressure and
  requires the corresponding event in the retained teardown outcome.

## Limits retained

This work does not provide adaptive memory management, PSI sampling, per-session or per-profile
history, causal diagnosis, parent-cgroup resource enforcement, physical memory/CPU reservation,
period synchronization, target-fleet delegation qualification, protection from privileged competing
writers, or a production activation claim. `memory.high` does not guarantee that usage stays below the
threshold and is not an OOM boundary.
