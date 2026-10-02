# ADR 0341: wake sync automation from source changes

Status: accepted. Implemented 2026-09-09.

## Context

Tree-v2 read-write synchronization had the correct durable semantics but a weak everyday latency
shape: local changes reached peers only when an owner explicitly ran `sync-publish`/`sync-checkpoint`
or when the periodic automation cycle reached the namespace. Wider object lanes and cached CAS
inventory removed measured transfer/storage amplification, but they did not shorten the wait before
the first local branch publication after an ordinary file edit.

Bidirectional automation also has two logically different jobs: publish this device's source-tree
changes and pull remote writer branches. Treating a bidirectional peer-pull timer as proof that local
work was published would blur branch causality and hide a real product boundary.

## Decision

Add a runtime-only source-change wake path:

- `SyncAutomationScheduler::trigger_source_change(namespace, now)` accelerates the next local
  publication/reconciliation for `publish`, `writable`, and `bidirectional` policies without editing
  the signed automation record.
- For `bidirectional`, a source change schedules a local `publish` action. The existing round-robin
  remote-source pull schedule remains separate and keeps its independent per-peer retry clocks.
- The Agent installs a best-effort Linux `inotify` watch set during automation reload for local
  source paths from `publish`, `writable`, and `bidirectional` policies.
- The watch set is bounded to 4,096 directories, recurses over existing non-symlink directories, and
  refreshes its tree after newly created watched subdirectories are observed.
- Watch setup or watch-read failure does not disable synchronization. The periodic interval/retry
  loop remains the availability path.

This changes no Tox wire frame, no local-control operation number, no signed policy format, no
authority capability, and no namespace policy. It is a latency accelerator above the existing durable
model.

## Consequences

The default experience improves for ordinary Linux source trees: after a write, close, create,
delete, move, or metadata change inside a watched source tree, automation is eligible to run on the
next Agent service cycle rather than waiting for the configured interval.

The watcher deliberately over-triggers. A duplicate local reconciliation is safe because branch
publication is content-addressed, generation-checked, and idempotent when no visible source event is
present. Missing an event is handled by the next periodic scan.

The watcher does not provide cross-platform filesystem semantics, runtime immutability, Unicode or
case-folding portability, symlink support, ACL/xattr propagation, permanent purge, or backup
independence. It also does not replace the explicit storage/corruption/power-cut trust graduation
matrix.

## Evidence

The owned unit/integration registry now covers scheduler wake semantics and a real recursive
`inotify` source tree, including a dynamically created subdirectory. The focused Ratox controller
process and sync process/verifier gates were rerun because this work shares the Agent service loop.

Accepted local checks:

```text
nix develop -c bash -lc 'cmake --build build -j2 --target iotox_tests && ctest --test-dir build -R "^iotox\\.unit-and-integration$" --output-on-failure'
nix develop -c bash -lc 'ctest --test-dir build -R "^iotox\\.(terminal-posix-process|terminal-cgroup-recovery-process|terminal-cgroup-memory-resource-process|terminal-cgroup-cpu-resource-process|terminal-cgroup-io-resource-process|terminal-cgroup-pressure-admission-process|terminal-controller-process|ratox-restart-fence-process|ratox-r7-analyzer|ratox-terminal-probe|ratox-cli-reconnect-probe)$" --output-on-failure'
nix develop -c bash -lc 'ctest --test-dir build -R "^iotox\\.(sync-publication-process|sync-retention-process|sync-transaction-process|sync-rollback-process|sync-tree-process|sync-three-writer-sandwurm-verifier|sync-power-cut-sandwurm-verifier|sync-metadata-corruption-sandwurm-verifier|sync-projection-descriptor-sandwurm-verifier|sync-shadow-sandwurm-verifier)$" --output-on-failure'
nix develop -c bash -lc 'cmake --build build -j2 --target iotox && ctest --test-dir build -R "^iotox\\.(client-version|client-help|bootstrap-seeds|workspace-cleaner|binary-process-lifecycle)$" --output-on-failure'
nix build .#checks.x86_64-linux.iotox-package .#checks.x86_64-linux.iotox-source-linked --print-build-logs
```

Earlier partial local checks while developing the same change:

```text
nix develop -c bash -lc 'ctest --test-dir build -R "^iotox\\.unit-and-integration$" --output-on-failure'
nix develop -c bash -lc 'ctest --test-dir build -R "^iotox\\.terminal-controller-process$" --output-on-failure'
```
