# Massive soak campaign completion

Date: 2026-09-29

Status: mixed. Sync, terminal, and person background soaks passed. Toxic
default completed degraded-but-pass-heavy. Toxic forced-TCP completed degraded
and remains a noisy route.

Campaign root:

```text
.sandwurm/massive-soak/run.20260927T183851Z.mnzthkw0
```

Primary status command:

```sh
python3 tools/run-massive-soak.py status \
  --root .sandwurm/massive-soak \
  --hash-logs --json
```

## Accepted cells

### Sync three-writer 24h

Proof root:

```text
.sandwurm/lab/three-writer-soak-24h/run.w5BKWVqE
```

Verifier:

```sh
tools/iotox-sandwurm-lab.sh verify-three-writer \
  .sandwurm/lab/three-writer-soak-24h/run.w5BKWVqE
```

Result:

- verifier status: `passed`;
- VM substrate: `cloud-hypervisor`;
- network class: `none`;
- nodes: 3;
- directed read-write shares: 6;
- tree lane cap: 4;
- soak cycles: 288;
- soak elapsed: 101,757,283 ms, about 28h15m57s;
- daemon restarts during soak: 11;
- restart settle passes: 11;
- stalled cycle recoveries: 5;
- recovery rehearsal: passed;
- storage fault rehearsal: passed;
- read-only start refused: true;
- ENOSPC live observed: true;
- evidence contains secrets: false.

This is the strongest local sync evidence currently retained in the repo lab:
three writers, long elapsed runtime, restarts, repair, maintenance lifecycle,
writer cutoff, recovery rehearsal, and storage-fault rehearsal all in one
verified proof.

### Terminal 24h

Receipt:

```text
.sandwurm/massive-soak/run.20260927T183851Z.mnzthkw0/proof/terminal-long-soak.receipt
```

Result:

- `iotox terminal soak-verify` returned 0;
- status summary contained `accepted=1`;
- observed seconds: 86400;
- maximum sample gap: 300 seconds.

### Person background 24h

Log:

```text
.sandwurm/massive-soak/run.20260927T183851Z.mnzthkw0/logs/person.background-24h.log
```

Result:

- bounded native scheduler loop completed;
- 1440 cycles;
- content-free local store health evidence only;
- no remote-delivery or backup proof is claimed by this cell.

## Toxic compatibility loop results

The Toxic loops were launched with `--keep-going`, so intermittent friendship,
route, or Toxic PTY evidence misses were recorded as failed iterations instead
of ending the elapsed campaign early.

### Default/native Toxic multidevice bridge

Summary:

```text
.sandwurm/massive-soak/run.20260927T183851Z.mnzthkw0/toxic/default/default.summary.json
```

Result:

- iterations: 555;
- passed: 539;
- failed: 16;
- pass rate: about 97.1%;
- final status classification: `completed-degraded`.

The failures were mostly wait/control timeouts around friend-request or Toxic
evidence windows. This is strong compatibility evidence for the default lab
route, but not a perfect zero-flake run.

### Forced-TCP Toxic multidevice bridge

Summary:

```text
.sandwurm/massive-soak/run.20260927T183851Z.mnzthkw0/toxic/forced-tcp/forced-tcp.summary.json
```

Result:

- iterations: 206;
- passed: 116;
- failed: 90;
- pass rate: about 56.3%;
- final status classification: `completed-degraded`.

Forced-TCP proved that the path can work repeatedly, but it is not currently
boring enough to call a graduated daily-driver Toxic bridge route. Most
failures were missed or slow friend-request/evidence windows in the Toxic
forced-TCP harness.

Follow-up hardening on the same date found two harness-side issues worth
fixing before rerunning the Toxic cells:

- Toxic's PTY can render a pending request adjacent to the command echo, such
  as `/requests0 : KEY`, which the old clean-line parser missed even though a
  human could see the request.
- A multidevice outbound bridge retry sends a new bridge body after the live
  command has already committed the sender's bridge store. That is an
  additional legitimate outbound record, so the final status assertion must
  account for retry-created local records instead of requiring fixed
  `entries=4 outbound=3` on every device.

The hardened harness now accepts Toxic's command-echo-adjacent request rows,
prints request/friend-event/status/Toxic-screen dossiers on request wait
failures, and expects final bridge-store counts dynamically when retries create
extra local outbound records. The product route label was also narrowed to
`default-qualified-forced-tcp-degraded` until a follow-up soak earns a stronger
forced-TCP claim.

Follow-up on 2026-09-30 found that the remaining Toxic failures clustered
around one-shot friendship setup and a stale/small Toxic bootstrap file rather
than bridge semantics. The harness now retries Toxic `/add`, IoTox
`transport-peer-request`, and IoTox self-mesh requests during the existing
request window, preserves retry errors as diagnostics, and writes a
numeric-only lab-local Toxic node file from a refreshed set of official
TCP-capable nodes. IoTox-originated retries now remove the exact pending peer
before sending a fresh request, because toxcore rejects duplicate pending
requests without re-sending them. Fresh one-iteration smokes passed for both
default/native and forced-TCP multidevice Toxic after the initial change. This
is a meaningful operator-lab hardening, not a graduation claim; forced-TCP
still needs a boring long rerun before the route label can be strengthened.

## Operator tooling change from this run

Before this review, `tools/run-massive-soak.py status` flattened completed
Toxic loops with any failed iteration into `completed-failed`, which obscured
the difference between “nothing worked” and “a long keep-going loop produced a
mixed pass/fail distribution.” The runner now reports mixed Toxic loop results
as `completed-degraded` and exposes:

- `toxic_iterations`;
- `toxic_passed`;
- `toxic_failures`;
- `toxic_pass_rate`;
- `toxic_first_iteration`;
- `toxic_last_iteration`;
- `toxic_summary_status`.

The campaign remains `attention` when degraded cells exist. That is deliberate:
degraded is evidence worth studying, not a stable pass.

## Product readout

- Sync looks materially stronger after this run.
- Terminal 24h native soak is accepted.
- Person background scheduling is boring at 24h, but still content-free/local
  unless paired with live delivery/fanout evidence.
- Default Toxic compatibility is usable but still has rare lab flakes.
- Forced-TCP Toxic compatibility works often enough to keep improving, but is
  not yet a route we should describe as smooth or stable.
