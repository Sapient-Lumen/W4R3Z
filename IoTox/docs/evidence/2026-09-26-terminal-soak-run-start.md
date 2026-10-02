# 2026-09-26 — Native terminal long-soak runner start

Status: completed; accepted completion is recorded in
`docs/evidence/2026-09-27-terminal-soak-accepted.md`.

After ADR 0408 added `iotox terminal soak-run`, the repository started a real
elapsed 24-hour terminal long-soak runner from the current build. A first
`nohup` launch in `run.kmhGRH` printed its first sample and then was reaped by
the launching tool session without writing a receipt. The durable run below was
restarted with `setsid`; a fresh process check showed it living under PID 1.

Command:

```sh
setsid sh -c 'exec env IOTOX_SODIUM_LIBRARY=/nix/store/2qf4asdxsbd2c0z23k5av9q3sp412gl5-libsodium-1.0.19/lib/libsodium.so \
  ./build/iotox terminal soak-run \
    --root /tmp/iotox-terminal-soak \
    --peer alias:self \
    --route native \
    --seconds 86400 \
    --sample-every 300 \
    --out "$1" >> "$2" 2>&1' \
  sh \
  <iotox-workspace>/.sandwurm/exports/terminal-soak/run.OjbHRv/terminal-24h.receipt \
  <iotox-workspace>/.sandwurm/exports/terminal-soak/run.OjbHRv/terminal-soak-run.log \
  < /dev/null &
```

Run directory:

```text
.sandwurm/exports/terminal-soak/run.OjbHRv
```

Start observation:

```text
pid=3790559
started=2026-09-26T00:15:35-04:00
expected-minimum-completion=2026-09-27T00:15:35-04:00
fresh-process-check=pid 3790559 ppid 1 sid 3790559
first-sample=sample=1 elapsed-seconds=0 signal=0
```

Validation before launch:

```text
cmake --build build -j2
IOTOX_SODIUM_LIBRARY=... ctest --test-dir build --output-on-failure
result=100% tests passed, 0 tests failed out of 81
skipped-by-environment=terminal-cgroup-recovery-process,terminal-cgroup-memory-resource-process,terminal-cgroup-cpu-resource-process,terminal-cgroup-io-resource-process,terminal-cgroup-pressure-admission-process
```

Boundary: this note is the start record. The accepted verifier result and
terminal stable manifest result are recorded in
`docs/evidence/2026-09-27-terminal-soak-accepted.md`. Re-check the retained
receipt with:

```sh
iotox terminal soak-verify .sandwurm/exports/terminal-soak/run.OjbHRv/terminal-24h.receipt
```
