# ADR 0276: Qualify unattended one-writer synchronization

Status: accepted, 2026-09-01

## Context

ADR 0270 implemented signed `publish` and stable-principal-bound `follow` automation, but retained
only deterministic local and mock-provider evidence. M5C still required two simultaneous isolated
guests to install policy once, mutate the source, interrupt both daemon roles, and converge without
manual publication, pull, or activation. The later tree-v2 gates did not close this one-writer
treepack-v1 claim: they exercise a different signed branch protocol and writable projection.

## Decision

Add `sync-automation` as a first-class Sandwurm pair scenario on direct UDP and forced TCP. The
scenario uses only public product commands for setup:

```text
publisher: sync-create automatic-notes SOURCE 1
publisher: sync-share automatic-notes REPLICA read-only
replica:   sync-namespace-template-tree / sync-namespace-install
replica:   sync-follow PUBLISHER automatic-notes verified 1
```

Each guest bootstraps RecallRoot, migrates to authority v3, and binds the other stable device
principal to only the required synchronization capability. The replica chooses its own namespace
root. After both signed automation records exist, the gate permits no `sync-publish`, `sync-pull`,
or `sync-activate` command.

The publisher begins with generation 1. After exact verified materialization, its Agent is stopped
and restarted from the same state; its signed `publish` record must reload before a source-only
generation-2 mutation. Once the replica observes generation 2, the replica Agent is independently
stopped and restarted; its signed `follow activation=verified` record and exact source principal
must reload before the publisher makes a source-only generation-3 mutation. Application messages
form ordered barriers around every stop/restart and observed generation. The client additionally
requires a strictly higher authenticated online epoch after publisher restart. Both roles finish
with the same three SHA-256 commitments; the replica runs `sync-repair` only as a terminal
verification action.

The ordinary pair verifier requires:

- exactly two positive automation receipts and one Agent restart per role;
- exact signed-policy reload on each restarted role;
- the fixed three-generation content commitment sequence;
- zero manual transfer/activation commands after policy installation; and
- the unchanged source-linked product binary on both guests.

The generic compact exporter retains only content-free receipts, build/launch attestations, and the
pair manifest. It replays the same verifier after export.

## Evidence

The accepted direct-UDP compact proof is `pair.7vk1u4wn`; the accepted forced-TCP compact proof is
`pair.s67dd_2e`. Both bind product binary
`4ee0f545a852ec11eb42363e141ae21d9ac20100ae241fd84d8314d6f3bbad88`, two role restarts,
three identical generation hashes, verified activation on the replica, and zero manual transfer
commands. `../evidence/2026-09-01-sandwurm-sync-automation.md` records reproduction and exact
nonclaims.

## Consequences

M5C's isolated two-guest one-writer mutation/restart checkbox is complete on the available VM
substrate for both native carrier classes. A signed automation record now has genuine process and
network evidence, not just deterministic construction coverage.

This does not make IoTox the sole-copy path for important data. The hours-long shadow, selective
sync/ignore and metadata policy, tree-v2 adversarial scale, power-cut behavior, and representative
storage qualification remain separate gates. It also does not create a remote-path selection or
friendship-derived authority shortcut.
