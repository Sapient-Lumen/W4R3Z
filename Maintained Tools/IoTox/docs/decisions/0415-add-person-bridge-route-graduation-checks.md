# ADR 0415: Add person, bridge, and route graduation checks

Date: 2026-09-27

## Status

Accepted.

## Context

IoTox already had the underlying primitives for person multidevice messaging,
normal Toxic compatibility, and routed privacy qualification. The problem was
that an operator still had to remember a scattered checklist: background
messenger status, retry/expiry behavior, receipt summaries, transcript
convergence, group status, Toxic default/forced-TCP labs, route-set policy, and
Tor/I2P route nonclaims.

That made the work feel less ordinary than sync and Ratox, which already have
native graduation checks. It also risked the wrong claim: “we have a lab” could
be confused with “every route and every client is globally certified.”

## Decision

Add three native, content-free, fail-closed checkers:

```sh
iotox person graduation-check [--root PATH] [--evidence NAME=LABEL...]
iotox person tox-bridge-graduation-check [--bridge-store PATH] [--evidence NAME=LABEL...]
iotox route-qualification-check [--scope all|toxic|ratox|sync|privacy] [--evidence NAME=LABEL...]
```

`person graduation-check` aggregates the lived multidevice messenger gates:
background delivery, offline retry/expiry, receipt summary, human-read
semantics, transcript convergence, group semantics, resident service
supervision, route policy, and operator review. It prints the exact status,
background-run, outbox retry/expiry, read-status, transcript-convergence,
group-status, bridge-status, and service-reality commands.

`person tox-bridge-graduation-check` aggregates the normal Toxic compatibility
bridge gates: default native Toxic, forced-TCP Toxic, inbound fanout, outbound
send, identity boundary, bridge-store status, transcript commit,
route nonclaims, and operator review. It prints the default/forced-TCP Toxic
lab commands plus the three-device multidevice bridge lab.

`route-qualification-check` makes Tor/I2P route graduation explicit per lane.
It can be scoped to all routes, the Toxic bridge, Ratox, sync, or privacy. It
prints the operator Tor smoke/verifier, I2P SAM/front commands, Toxic labs,
route-set v2 creation, and bridge graduation command. Even when complete, it
prints `silent-fallback-authorized=0` and `anonymity-certified=0`.

The operator evidence labels are safe non-space labels. They are not
cryptographic proof and do not include message contents or secrets.

## Consequences

- Person multidevice messaging now has a native daily-driver graduation porch
  that matches the sync and Ratox style.
- The Toxic bridge can be declared operator-attested without claiming that
  normal Tox clients understand IoTox person identity.
- `routes-toxic-tor` and `routes-toxic-i2p` move from “not yet qualified” to
  “evidence-gated,” which is more accurate: the project now has an explicit
  qualification path, but it still refuses silent route fallback or anonymity
  certification.
- Stable evidence was refreshed with a native `iotox.service-reality.v1`
  `terminal.service-supervision` receipt:
  `.sandwurm/exports/terminal-soak/run.OjbHRv/all-stable-evidence.service-reality.XOlEdI/stable-evidence.manifest`
  with SHA-256
  `1dfef328a55c91259d479134d71606d78f8bcf7f05a40ef136c7b0eb810d9006`.

## Tests

- `python3 tests/test_human_cli.py ./build/iotox`
- `python3 tests/test_docs_coherence.py . ./build/iotox`
- `iotox evidence dossier-status ... --scope all --manifest ...`
- `iotox ship-check all stable --evidence-manifest ...`
