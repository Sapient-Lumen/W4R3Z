# Ratox daily-control rerun — 2026-09-17

Status: accepted local current-tree rerun.

## Command

```sh
./tools/ratox-daily-control-gate.sh --build
```

## Result

The focused CTest set passed 6/6:

- `iotox.terminal-posix-process`
- `iotox.terminal-controller-process`
- `iotox.ratox-restart-fence-process`
- `iotox.ratox-r7-analyzer`
- `iotox.ratox-terminal-probe`
- `iotox.ratox-cli-reconnect-probe`

Delegated cgroup helper result:

```text
ratox-cgroup-delegated-service-summary passes=4 skips=1 failures=0
```

The passing branches were lifecycle recovery, memory/pids controls, CPU controls, and PSI
pressure-admission. The I/O branch skipped because this qualification filesystem still did not expose
cgroup-attributed block I/O to the oracle.

## Boundary

This refreshes the owner-local daily-control evidence after the accepted 24-hour sync soak and
cleanup/doc changes. It is not a production activation. It does not replace a longer interactive
reconnect soak, actual Tor/I2P continuity cells, daemon-death PTY supervision work, host-specific
PAM/sudo review, fleet cgroup review, or independent security/operations review.
