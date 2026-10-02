# Genuine Sandwurm bounded-range convergence — 2026-08-22

## Result

IoTox passed the `sync-file-range` two-guest gate over both direct UDP and forced TCP. In each cell,
the publisher created and the subscriber explicitly activated a complete deterministic 4 MiB
generation 1. The publisher then changed one bounded region, created a parent-linked signed
generation 2, and offered its manifest first. The subscriber negotiated `state-sync-ranges-v1`,
requested one range, fetched 128 bytes, reused 4,194,176 verified local bytes, reconstructed the
exact 4,194,304-byte successor, accepted its signed HEAD last, and explicitly activated that exact
HEAD token.

Both carriers produced the same final identities and accounting:

| Field | Value |
|---|---:|
| generation | 2 |
| artifact bytes | 4,194,304 |
| range count | 1 |
| fetched bytes | 128 |
| reused bytes | 4,194,176 |
| artifact SHA-256 | `0e2590fa6bcc290f7307cb0c0a34cc807934895293f4be25aafb102383075411` |
| manifest SHA-256 | `322dd3fffdda3747ca592f2627138d8ae32fd064680b34aa4dd238b01804e032` |
| signed HEAD record | `dead8d7be3834b7d06128ae25a6b343168c48e154ac3af60a605944c7a85b31d` |
| guest binary SHA-256 | `dd768ebbffad2e3cb65fd027a30bae65aed0e986e2be941040f3a7d2ad659caa` |

## Retained proof

The independently reverified content-free compact exports are:

- direct UDP: `.sandwurm/exports/pairs/pair.b2l3yof_`;
- forced TCP: `.sandwurm/exports/pairs/pair.uketizc_`.

Each compact export occupies 98,304 allocated bytes. The exporter omits guest disks, injected
identities, bootstrap secret material, and runtime state. The repository verifier checked the
manifest, both guest receipts, launch chains, route observation, cross-guest revision identity, and
range accounting after export.

## Boundaries exercised

- two simultaneous stock Cloud Hypervisor guests under Sandwurm;
- the pinned source-linked c-toxcore 0.2.23 provider rather than the mock transport;
- reused immutable private Tox/device identities with fresh per-run authority and sync state;
- authority-ledger v3 one-way `sync.publish` and `sync.subscribe` grants;
- explicit HELLO negotiation of both `state-sync-v1` and `state-sync-ranges-v1`;
- complete generation-1 transfer, accepted-HEAD-last transition, and manual activation;
- locally signed, exact-parent generation-2 publication after a bounded source mutation;
- manifest-first range planning against the accepted generation-1 basis;
- request-selected FileId and a genuine Tox finite-file range bundle;
- durable target attempt, complete artifact SHA-256, immutable commit, accepted HEAD, then exact-token
  activation;
- independent direct-UDP and forced-TCP observation with identical final content and signed state.

## Scientific corrections during construction

The first launch attempt correctly refused a Nix source closure that did not contain newly untracked
source files; staging the coherent source set repaired that packaging boundary. A later preliminary
runner placed the generation-2 barrier before delivery of generation 1's completion token, leaving
the publisher and host waiting on opposite sides. Moving the successor phase after `sync-finished`
repaired the laboratory ordering. Neither observation was accepted as product evidence; the retained
cells are fresh successful runs after both corrections.

## Nonclaims

This proves exact one-source successor reconstruction and substantial byte reuse on two route
classes. It is not a throughput or latency benchmark. It does not prove continuation of a partially
received range bundle across restart/disconnect, deterministic-directory convergence, multi-source
scheduling, destructive GC safety, coordinated-replay resistance, or
power-loss behavior on deployment storage.

Missing/corrupt accepted-basis whole-successor recovery is now proved separately in
`2026-08-22-sandwurm-sync-corrupt-basis.md`; corrupt target-object scrub remains open.
