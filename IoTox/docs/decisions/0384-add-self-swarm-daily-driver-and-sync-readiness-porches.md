# ADR 0384: Add self-swarm freshness, Ratox daily-driver, and sync readiness porches

Status: accepted
Date: 2026-09-18

## Context

ADR 0383 made the owner-signed self-swarm roster real, but left three human-facing gaps:

- operators could carry `--min-generation`, but there was no durable local roster high-water file;
- roster distribution was still a copy/paste chore, and grant planning could not check the live
  alias route before printing commands; and
- the daily-owner terminal and sync-readiness stories were spread across lower-level commands.

Those gaps were not new cryptography problems. They were operator-friction problems: the repo had the
right primitives, but humans needed native porch commands that name the checks, print the exact next
steps, and refuse stale or mismatched local facts before mutation.

## Decision

Add three native porch/freshness surfaces.

### Self-swarm freshness and fan-out

Add a canonical local high-water floor record:

```text
iotox-self-swarm-floor-v1
owner=OWNER_PUBLIC_KEY_HEX
generation=N
digest=UNSIGNED_ROSTER_DIGEST_HEX
```

The floor is a local monotonic checkpoint for one owner/generation/digest. `floor-commit` writes the
first floor, advances to newer generations, is idempotent for the same generation/digest, and rejects
older generations or same-generation forks. `--floor PATH` is now a verification option for
`inspect`, `verify`, `grant-plan`, `grant-recall-stdin`, `retire-plan`, `retire-recall-stdin`,
`revoke-retired-recall-stdin`, and fan-out commands.

Add explicit live distribution:

```sh
iotox self-swarm fanout-plan ROSTER [--from ALIAS] [verification options]
iotox self-swarm fanout ROSTER [--from ALIAS] [verification options]
iotox self-swarm readiness ROSTER [--from ALIAS] [verification options]
```

`fanout-plan` prints exact `file-send` and receiver-side verify/floor-commit commands for active
members. `fanout` pre-resolves every active target alias and then queues the signed roster file over
the existing Tox file lane. Receivers still verify the owner, generation, route keys, and floor before
trusting the file.

Add `--prove-routes` as an optional live route proof. It resolves roster aliases against the running
Agent's alias/peer surface and refuses if the live alias resolves to a different Tox public key than
the rostered route key. This is not a cryptographic network transcript; it is a fail-closed guard
against planning or applying grants against stale/misbound local aliases.

`self-swarm readiness` renders a redacted count/gate report: generation, active/retired counts,
floor state, optional route-proof state, and fanout target count. It deliberately does not print
member aliases, stable principals, or Tox route keys.

The self roster deliberately does not carry route class policy. Rendered readiness, fanout plans,
and live fanout summaries therefore disclose `route-policy=not-carried-by-self-roster`,
`route-policy-authority=route-set-v2-and-explicit-run-config`, and
`privacy-fallback=not-authorized-by-roster`. Route proof checks live alias/key consistency only; it
does not certify native/Tor/I2P privacy posture.

### Ratox daily-driver porch

Add:

```sh
iotox terminal daily-plan [--root PATH] [--peer PEER]
iotox terminal profile check PATH
iotox terminal-profile-check PATH
```

`daily-plan` prints the concrete doctor, run-check, run, status, sessions, reconnect, profile-plan,
profile-check, and service-doc commands an operator needs for SSH-shaped daily use. `profile check`
decodes a terminal profile, hashes the live pinned executable and optional rescue toolbox payload,
and reports stale/mismatch states before the operator relies on the profile.

### Sync dataset readiness porch

Add:

```sh
iotox sync-dataset-readiness PATH [one-writer|read-write] [INTERVAL_SECONDS] \
  [backup-root=PATH restored-root=PATH maximum-bytes=N maximum-entries=N \
   backup-system=TEXT backup-generation=TEXT backup-failure-domain=TEXT \
   restore-provenance=TEXT verify-recovery=0|1]
```

The command runs the existing local sync-doctor inspection on the candidate source, prints the exact
storage-readiness and recovery-verify commands, and renders backup custody as
blocked unless the operator supplies explicit provenance. With `verify-recovery=1`, it also runs the
strict restore comparison inline and reports `recovery-verify=matched` or `mismatch`. Even with every
label present and a matched restore drill, the command prints `precious-data-repo-certified=0`: it
helps decide whether a dataset is a working-copy candidate, not whether IoTox is the sole system of
record.

## Consequences

Self-swarm is smoother without becoming automatic authority. The roster can now be fanned out through
the ordinary file lane, guarded by a local floor and optional live route proof, while every receiving
machine remains responsible for verification and floor commitment.

Ratox is more plausible as a daily-owner tool because stale shell/profile bytes are visible before
profile install/bind/use, and because reconnect/session/service commands are collected in one native
porch. This does not make daemon-crash PTY survival true; route reconnect and daemon/process
persistence remain separate claims.

Sync trust is easier to discuss with humans. The new dataset command joins preflight, backup custody,
and restore rehearsal in one report, but it intentionally does not certify
precious-data readiness. Independent backup custody remains a product gate;
ADR 0400 later removes storage-media certification from IoTox scope.

## Evidence

The construction evidence is native and tested:

- `include/iotox/self_swarm.hpp` and `src/self_swarm.cpp` implement canonical floor load/store,
  monotonic floor commit, and floor checks;
- `src/cli.cpp` exposes `--floor`, `--prove-routes`, `floor-status`, `floor-commit`,
  `fanout-plan`, `fanout`, redacted `self-swarm readiness`, `terminal daily-plan`, grouped
  `terminal profile check`, and `sync-dataset-readiness`;
- `src/terminal_admin_cli.cpp` exposes `terminal-profile-check`;
- `tests/test_self_swarm.cpp` covers floor rollback and same-generation fork refusal;
- `tests/test_human_cli.py` covers floor commit/status/verify, redacted self-swarm readiness,
  fanout planning, terminal daily plan, profile payload checks, dataset readiness labels, and inline
  matched restore verification; and
- `tests/test_docs_coherence.py` checks the public help surface keeps these porch commands visible.
