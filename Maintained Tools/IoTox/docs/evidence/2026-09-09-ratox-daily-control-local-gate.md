# Ratox daily-control local gate

Date: 2026-09-09

Status: accepted local current-tree gate

Latest rerun: commit `6a276a7` after ADRs 0345--0348.

Additional isolated VM check: the ADR 0349 implementation tree passed
`nix build .#checks.x86_64-linux.ratox-sudo-vm --no-link -L`.

## Claim

The current tree has one repeatable local command that exercises the Ratox daily-control surface
without launching VMs by default:

```sh
./tools/ratox-daily-control-gate.sh --build
```

The command builds the relevant local targets, runs the focused Ratox process/probe/analyzer CTest
set, then runs the delegated-user-service cgroup helper.

## Result

The focused CTest set passed 6/6:

- `iotox.terminal-posix-process`
- `iotox.terminal-controller-process`
- `iotox.ratox-restart-fence-process`
- `iotox.ratox-r7-analyzer`
- `iotox.ratox-terminal-probe`
- `iotox.ratox-cli-reconnect-probe`

The delegated cgroup helper result was:

```text
ratox-cgroup-delegated-service-summary passes=4 skips=1 failures=0
```

The passing branches were lifecycle recovery, memory/pids controls, CPU controls, and PSI pressure
admission. The I/O branch skipped because this filesystem did not expose cgroup-attributed block
I/O to the oracle.

## Nonclaims

This is a local current-tree gate. It does not replace Sandwurm route evidence, hours-long soak,
actual Tor/I2P continuity, daemon-death PTY supervision, every host PAM/sudo policy, every cgroup
controller deployment, independent review, or production activation.
