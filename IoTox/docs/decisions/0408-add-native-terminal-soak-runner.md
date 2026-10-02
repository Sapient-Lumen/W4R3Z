# 0408 — Add native terminal long-soak runner

## Status

Accepted.

## Context

ADR 0407 made terminal stable evidence collectable with
`iotox evidence collect terminal`, but the 24-hour `terminal.long-soak` receipt
still depended on an operator-managed elapsed run plus a manual
`terminal soak-receipt` command. That was honest, but too easy to get wrong:
the plan command taught the required shape, not the elapsed custody loop.

## Decision

Add:

```sh
iotox terminal soak-run \
  --root PATH \
  --peer PEER \
  --route native \
  --seconds 86400 \
  --sample-every 300 \
  --out terminal-24h.receipt
```

The runner keeps elapsed wall-clock time inside the native binary, samples on
the requested cadence, handles `SIGINT`/`SIGTERM`, and writes the same
`iotox.terminal-long-soak-receipt.v1` schema that `terminal soak-receipt`
already emits. Completed runs produce accepted verifier-compatible receipts;
interrupted runs produce rejected receipts instead of disappearing.

`terminal soak-plan` now prints a `run-command=` line alongside the manual
receipt and verifier commands.

## Consequences

- The recommended terminal long-soak path is now native and repeatable.
- Manual `terminal soak-receipt` remains available for importing externally
  supervised elapsed evidence, but the ordinary path is `terminal soak-run`.
- The receipt remains content-free: root and peer are hashed, terminal data is
  not recorded, and the boundary still says this is local elapsed operator
  evidence, not proof of a production fleet.
- Stable terminal collection still refuses any `terminal.long-soak` receipt
  that fails the 86,400-second semantic verifier.
