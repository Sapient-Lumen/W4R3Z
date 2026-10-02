# ADR 0343: Qualify Ratox cgroups under delegated user services

Status: accepted. Implemented 2026-09-09.

## Context

ADR 0327 already provides one positive NixOS KVM slice for Ratox delegated cgroups under systemd.
The current founding host still needed a cheap repeatable check for the same cgroup process oracles
without requiring a full VM boot every time Ratox or Agent service-loop work changes.

Running the existing CTest entries from an ordinary shell often skips because the process does not
start inside a writable delegated cgroup-v2 subtree. Running them inside `systemd-run --user --scope
--property=Delegate=yes` is also the wrong shape on this host: the test process remains in the
delegated cgroup root, so enabling resource controllers can fail the kernel's no-internal-process
rule with `EBUSY`.

## Decision

Add `tools/ratox-cgroup-delegated-service-check.sh`. The helper runs each
`iotox_terminal_cgroup_recovery_process_tests` mode as its own transient user service:

```text
systemd-run --user --collect --wait --pipe --property=Delegate=yes \
  build/iotox_terminal_cgroup_recovery_process_tests --MODE
```

The direct transient-service shape leaves the delegated root usable for the oracle's own private
subtree. The helper preserves the oracle's exit status, prefixes each mode's output, counts passes,
skips, and failures, exits nonzero on any failure, and exits 77 only when the environment provides no
positive pass.

## Consequences

The current host now has a fast read-only qualification command for the controller-dependent Ratox
cgroup/PSI routes when a user systemd manager and delegation are available:

```text
./tools/ratox-cgroup-delegated-service-check.sh
```

On 2026-09-09 this host passed lifecycle recovery, memory/pids controls, CPU controls, and PSI
pressure-admission under delegated user services. The I/O controller oracle skipped because the
qualification filesystem did not expose cgroup-attributed block I/O. The summary was:

```text
ratox-cgroup-delegated-service-summary passes=4 skips=1 failures=0
```

This complements ADR 0327. It does not replace the VM gate, prove every Linux/systemd/kernel
combination, qualify block-I/O accounting on this filesystem, measure live PSI trigger latency,
provide a long reconnect soak, prove Tor/I2P route behavior, or activate Ratox by default.

## Evidence

Accepted local check:

```text
chmod 0755 tools/ratox-cgroup-delegated-service-check.sh && ./tools/ratox-cgroup-delegated-service-check.sh
```
