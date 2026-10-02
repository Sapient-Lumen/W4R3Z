# Massive soak campaign

Status: repo-level orchestrator present. The campaign is ready to plan,
preflight, smoke, launch, watch, and stop from one retained directory. Updated
2026-09-27.

The massive soak campaign is the “do these daily-driver surfaces stay boring
for a long time?” gate. It is not one test. It is a coordinated run across the
surfaces where elapsed time actually buys confidence:

- sync as a Resilio-style daily folder, especially three-writer convergence,
  retention, delete quarantine, and precious-data signoff inputs;
- Ratox terminal as a self-machine SSH-like control path;
- person multidevice messenger background delivery;
- normal Toxic compatibility bridge into the person/device world;
- resident service reality, logs, health, upgrade checks, and restartability;
- route-specific claims where a route class is explicitly in scope.

The orchestrator is:

```sh
tools/run-massive-soak.py plan
tools/run-massive-soak.py preflight
tools/run-massive-soak.py smoke
```

The default campaign root is:

```text
.sandwurm/massive-soak
```

Everything written there is operator/private lab state. The runner keeps logs,
receipts, manifests, and PID records under that root. It does not delete old
campaigns.

## What the runner covers

`tools/run-massive-soak.py plan` prints every campaign cell and the exact
command behind it. The important cells are:

| Cell | Purpose | Long form |
| --- | --- | --- |
| `sync.three-writer-24h` | VM-backed real sync long soak | `tools/iotox-sandwurm-lab.sh up-three-writer soak-24h` |
| `terminal.native-24h` | native elapsed terminal long-soak receipt | `iotox terminal soak-run --seconds 86400 ...` |
| `person.background-24h` | resident person messenger status-loop | `iotox person background-run --cycles 1440 --interval 60 ...` |
| `toxic.multidevice-default-loop` | repeated stock Toxic ↔ three-IoTox-device bridge proof | source-linked IoTox + `tools/run-toxic-multidevice-bridge-lab.py` loop |
| `toxic.multidevice-forced-tcp-loop` | same bridge proof through forced TCP | source-linked IoTox + Toxic loop with `--toxic-force-tcp` |
| `service.reality-plan` | operator service status receipt checklist | `iotox service status-plan --target all ...` |

The smoke path does not pretend to be stable evidence. It checks that the
command surface is coherent before we spend a day on it:

- mints the current accepted `sync.long-soak` verifier receipt from retained
  proof;
- runs a six-second terminal soak receipt and verifies it at six seconds;
- runs the person background worker in bounded status-loop mode;
- verifies that person, bridge, and route graduation gates fail closed without
  evidence labels;
- prints the resident service status checklist.

Each smoke run is retained under:

```text
.sandwurm/massive-soak/smoke-runs/run.*
```

The latest summary is copied to `.sandwurm/massive-soak/latest-smoke.json`.
This keeps failed rehearsals reviewable and avoids clobbering no-overwrite
native receipts.

Optional smoke cells can be added when the host is ready:

```sh
tools/run-massive-soak.py preflight --with-vm --with-toxic
tools/run-massive-soak.py smoke --with-vm-smoke
```

The Toxic loops intentionally default to the source-linked IoTox package. A
plain local debug `build/iotox` may be a runtime-loaded-provider build and can
fail before the bridge lab starts if no host `libtoxcore` is globally
available. To force a particular live binary, pass `--iotox PATH` to
`launch-long` or to `toxic-loop`; otherwise the runner resolves the same
source-linked path used by the Toxic compatibility labs and records it in the
loop log. A real `launch-long --include toxic` resolves that source-linked
binary once and passes the exact path into both Toxic loops so the default and
forced-TCP cells do not race duplicate source-linked builds.

The Toxic compatibility labs keep proof/state under the retained lab root, but
place live IoTox control runtimes under `.sandwurm/tr/` to avoid Unix-domain
socket path-length failures from deeply nested campaign directories. Normal
Tox delivery into stock Toxic is accepted on c-toxcore read receipts; Toxic
screen/autolog evidence is useful when present but is treated as diagnostic
because Toxic may receipt a message without retaining a parseable UI/log line
in this PTY harness.

Long Toxic loops run with `--keep-going`. A missed friend request or route
establishment window is still recorded as a failed iteration, but it should not
kill the whole elapsed campaign unless the operator deliberately omits
`--keep-going`. When a recorded long stage has already exited, restart it
in-place instead of hand-spawning an orphan:

```sh
tools/run-massive-soak.py restart-stage \
  --root .sandwurm/massive-soak \
  --stage toxic.multidevice-default-loop \
  --stage toxic.multidevice-forced-tcp-loop \
  --reason "Toxic loop should continue after transient handshake misses"
```

`restart-stage` preserves the prior PID/log/summary path in the campaign
manifest history, writes a fresh restart log, archives the stale terminal
Toxic summary, replaces it with a `restarted-running` marker, and lets
`toxic-loop` continue iteration numbering from the existing retained proof
root. The restarted loop overwrites that marker with its final summary when it
exits.

Completed Toxic loops are summarized as counts, not just pass/fail. A loop
with at least one successful iteration and at least one failed iteration is
reported by `status` as `completed-degraded`; the campaign stays in
`attention` because those failures still require operator review. The normal
default route should trend strongly toward pass-heavy evidence. Forced-TCP is
expected to be noisier in this lab and should not be treated as a graduated
daily-driver bridge until its pass/fail ratio and failure modes are reviewed.
After the 2026-09-29 loop, the Toxic harness was hardened to parse
command-echo-adjacent `/requests0 : KEY` rows, emit richer request-failure
dossiers, and account for retry-created bridge-store records. A follow-up
Toxic-only soak should be used to decide whether forced-TCP can move out of
`default-qualified-forced-tcp-degraded`.

A short real Toxic rehearsal is:

```sh
tools/run-massive-soak.py toxic-loop \
  --root .sandwurm/massive-soak/toxic-rehearsal/default \
  --seconds 1 \
  --variant default

tools/run-massive-soak.py toxic-loop \
  --root .sandwurm/massive-soak/toxic-rehearsal/forced-tcp \
  --seconds 1 \
  --variant forced-tcp
```

## Launching the real elapsed campaign

Launch only the surfaces you intend to watch:

```sh
tools/run-massive-soak.py launch-long \
  --include sync \
  --include terminal \
  --include person \
  --include toxic
```

For a dry run that writes the manifest but starts nothing:

```sh
tools/run-massive-soak.py launch-long \
  --include sync \
  --include terminal \
  --include person \
  --include toxic \
  --dry-run
```

Every launched process records:

- exact command;
- PID;
- log path;
- expected duration;
- receipt path when the native command writes one.

Inspect it:

```sh
tools/run-massive-soak.py status
tools/run-massive-soak.py watch --samples 12 --interval 300
```

After the Sandwurm three-writer sync cell exits, `status` parses the retained
`proof-root=` from the sync stage log and runs `verify-three-writer` against
that proof. A completed sync cell should therefore report `completed-ok` only
after the guest sync receipt and the outer Cloud Hypervisor live-chain receipt
are both present and the formal verifier accepts the proof.

Bring it down safely:

```sh
tools/run-massive-soak.py stop
```

`stop` sends `SIGTERM` only to the PIDs recorded in the campaign manifest. It
does not search for broad process names and does not delete proof roots.

## Pass/fail interpretation

The massive soak should be considered useful only if the whole chain is
reviewed after completion:

```sh
tools/run-massive-soak.py status --hash-logs --json
iotox terminal soak-verify .sandwurm/massive-soak/current/proof/terminal-long-soak.receipt
tools/iotox-sandwurm-lab.sh status-three-writer PROOF_ROOT
tools/iotox-sandwurm-lab.sh verify-three-writer PROOF_ROOT
iotox person graduation-check --root .sandwurm/massive-soak/current/person ...
iotox person tox-bridge-graduation-check --root .sandwurm/massive-soak/current/person ...
iotox route-qualification-check --scope all ...
```

The route/person graduation checks still need evidence labels. The soak runner
does not manufacture those labels. It retains the logs and receipts that an
operator can review and cite.

## Boundaries

The native person background cell is intentionally a resident status-loop when
no outbox fixture is seeded. Live send/retry/fanout pressure is covered by the
Toxic multidevice loops, which create fresh private IoTox devices and exercise
normal Toxic ingress/egress through the bridge.

This campaign is not storage-media qualification, disk-loss proof,
host-compromise proof, or anonymity certification. It is an elapsed local lab
for the surfaces IoTox actually ships:

- synchronized working copies with recovery-custody gates;
- profile-bound self-machine terminal control;
- person/device messaging and Toxic bridge compatibility;
- explicit route-class evidence;
- resident service reality.

If a smoke or long cell fails, fix the repo or host setup, keep the failed run
for evidence, and start a fresh campaign. Do not overwrite rejected receipts
or re-label a failed soak as accepted.
