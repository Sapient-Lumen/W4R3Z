# ADR 0412: Add native graduation dashboards

Status: Accepted.

## Context

By ADRs 0395--0411, IoTox had the hard gates for stable release, precious-data
sync signoff, Ratox daily-driver evidence, self-swarm operation, and person
multidevice messaging. The remaining problem was operator coherence. A careful
owner could pass the gates by reading several docs and composing many commands,
but the binary did not yet provide one native porch per frontier.

That made the product feel more fragile than the underlying checks: stable
evidence could pass, but finding the full command trail still depended too
much on repository prose; person messaging had stores and workers, but no
single daily-driver plan; self-swarm had readiness and fanout, but no ordinary
dashboard for join/retire/grant/floor work.

## Decision

IoTox adds native dashboards and command trails:

```sh
iotox evidence dossier-plan ...
iotox evidence dossier-status DIR ...
iotox sync precious-status ... --evidence-dir DIR
iotox self-swarm daily-status ROSTER ...
iotox person messenger-plan ...
```

`evidence dossier-plan` prints the complete stable dossier trail: sync trust,
backup, runbook, retention, evidence collection, precious-data signoff, Ratox
daily/service/soak planning, terminal evidence collection, manifest creation,
dossier status, and stable ship-check.

`evidence dossier-status` checks the expected receipt files with the same
native sync/terminal shape checks as manifest generation, then separately
verifies the supplied stable manifest SHA bindings. It reports
accepted/missing/blocked per gate and stays blocked until the manifest is
complete for the selected scope.

`sync precious-status --evidence-dir ...` now points directly at the operator
signoff command, stable manifest command, and sync stable ship-check command
once the local within-scope precious-data gates are signable.

`self-swarm daily-status` is a redacted self-machine dashboard. It validates
the roster and optional floor/route-proof checks, counts active and retired
members, reports fanout target count, and prints readiness, fanout, grant, and
retire commands. Unknown, retired, stale, wrong-principal, and wrong-route
cases remain fail-closed.

`person messenger-plan` is the daily multidevice messaging porch. It prints
messenger status, background runner, outbox retry/expiry, card refresh, and
receive commands while naming the important semantics: device receipts are
device-received, not human-read; transcript order is local, not global
consensus; group semantics are IoTox signed envelopes above route delivery,
not normal Tox group identity.

## Consequences

- The stable release path can now be reviewed from native binary commands
  before `ship-check all stable` is attempted.
- Precious-data signoff remains explicitly local and operator-owned: no
  disk-loss, host-compromise, filesystem-wide-corruption, or content-custody
  certification is implied.
- Ratox daily-driver graduation stays evidence-gated but has a clearer command
  trail through daily status, service artifacts, soak receipts, and terminal
  evidence collection.
- Self-swarm and person messaging become more ordinary to operate without
  weakening the owner-signed roster, high-water floors, route proof, contact
  card floors, outbox expiry, or receipt semantics.
- These dashboards are porches, not background authority roots. They do not
  install services, send secret contents, create independent witnesses, or
  silently convert Tox friendship/groupchat state into IoTox authority.
