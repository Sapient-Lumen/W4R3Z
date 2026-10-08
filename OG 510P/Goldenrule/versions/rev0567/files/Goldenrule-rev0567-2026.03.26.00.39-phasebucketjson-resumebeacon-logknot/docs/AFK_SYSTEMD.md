# AFK on systemd (Idle Start/Stop)

This repo’s AFK runner contract assumes the worker may be stopped at any time and should:
- leave no orphan compute,
- preserve completed work,
- and resume cleanly.

If you run AFK work via a systemd *user* service (often triggered by an idle watcher like `xidlehook`), the key is to make stop/restart semantics explicit.

## Recommended service behavior

- `KillMode=control-group` so stopping the service kills the whole cgroup (no orphan `gr-engine` processes).
- `TimeoutStopSec` small but non-zero (e.g., 3s) so shutdown is prompt.
- `Environment=TERM_GRACE_SEC=…` so `grlab queue-work`/`grlab afk` can stop quickly without hanging.
  - `TERM_GRACE_SEC` is interpreted as “max time to wait for worker threads to exit on SIGTERM/SIGINT” before force-killing child process groups.

## Recommended `grlab` flags for idle work

When run under an idle-triggered service, the process may be stopped frequently. These defaults tend to work well:

- Use the durable queue worker:
  - `python3 -m grlab afk runs/<run_id> --workers 4`
- Keep leases relatively short to reduce “stuck running” time after crashes:
  - `--lease-seconds 60 --heartbeat-seconds 10`
- If you want retries:
  - `--retry-errors --max-attempts 5 --retry-backoff-seconds 30`
- If you want hard wall-time limits:
  - `--task-timeout-seconds 600`

Notes:
- On SIGTERM, `grlab` abandons claimed tasks back to `pending` without “charging” an attempt, so stop/start cycles don’t consume retry budget.
- `Queue.reconcile()` also releases leases whose `lease_owner` looks like `pid:<pid>` when that pid no longer exists (best-effort crash recovery).

## Minimal NixOS home-manager style snippet (example)

This is structurally similar to a common setup (paths/ids are placeholders):

```nix
systemd.user.services.afk-work = {
  description = "AFK work";
  serviceConfig = {
    Type = "simple";
    ExecStart = "${pkgs.bash}/bin/bash /home/<you>/projects/concord/afk_concord.sh";
    KillMode = "control-group";
    TimeoutStopSec = "3s";
    Environment = [ "TERM_GRACE_SEC=1" ];
    SuccessExitStatus = "0 130 143";
    Restart = "no";
  };
};
```

## Troubleshooting (if AFK compute “doesn’t happen”)

Common causes:
- The worker exits immediately due to missing `PATH` entries (no `python3`, `cargo`, `tee`, etc.).
- The worker tries to fall back to `nix develop`, but the repo flake isn’t visible to Nix (e.g., `flake.nix` exists but isn’t tracked by Git).
- The idle watcher never fires (bad `DISPLAY`/`XAUTHORITY`, or `xidlehook` not running).
- The worker runs, but you’re never actually idle for long enough to see sustained compute.

Fast checks:
- `systemctl --user status afk-idle.service -n 200`
- `systemctl --user status afk-work.service -n 200`
- `journalctl --user -u afk-work.service -n 200 --no-pager`
- `tail -n 200 runs/afk_discovery/mission_control.log` (if using `afk_concord.sh`)

If `afk_concord.sh` is your worker, ensure it prints a startup banner and dumps `PATH` + `command -v python3/cargo` into `runs/afk_discovery/mission_control.log` so failures are visible even when the unit exits immediately.

Tips:
- If you want automatic restart on crashes (but not on clean `systemctl stop`), consider `Restart=on-failure` plus `SuccessExitStatus=0 130 143`.
- For smoke debugging, run `./afk_concord.sh --once` and confirm it appends a mission banner to `runs/afk_discovery/mission_control.log`.
- If you see `Path 'flake.nix' ... is not tracked by Git`, run `git add flake.nix` (flakes only see tracked files in git repos).

## Suggested `afk_concord.sh` shape (example)

Keep this script long-running (so the service doesn’t exit while you remain idle), and avoid concurrent runs:

```bash
#!/usr/bin/env bash
set -euo pipefail

RUN_DIR="${1:-runs/<run_id>}"
exec python3 -m grlab afk "$RUN_DIR" \
  --workers 4 \
  --lease-seconds 60 \
  --heartbeat-seconds 10 \
  --retry-errors \
  --max-attempts 5 \
  --retry-backoff-seconds 30
```
