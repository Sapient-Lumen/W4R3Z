# Sandwurm sync route-balance evidence

Date: 2026-08-25

Status: accepted first Gate 4 topology qualification

## Claim

Two simultaneous source-linked IoTox guests each used one signed protected primary and two separately
keyed, reciprocally authenticated bulk workers. Under the default fixed selector, two overlapping
two-object tree pulls used the same eligible eight-slot bulk route. Under the conservative adaptive
selector, the corresponding second pull used the idle bulk route. The original cells ran fixed
first; independently booted counterbalance cells ran adaptive first. After the clean between-policy
subscriber-Agent restart with the same identity, authority, signed route inventory, and savedata,
the other policy produced the same placement invariant.

Every job requested, admitted, and committed exactly two immutable objects. All four signed HEADs were
explicitly activated, staging and route work returned to zero, and neither carrier cell needed a HEAD
retry. The same guests then completed 40 protected-primary Ratox samples with no render at or above
250 ms.

## Accepted compact cells

| Route | Phase order | Compact proof | Fixed placement | Adaptive placement | Fixed / adaptive phase | Ratox p95 | Whole-VM span | Pair manifest SHA-256 | Compact index SHA-256 |
|---|---|---|---|---|---:|---:|---:|---|---|
| direct UDP | fixed → adaptive | `.sandwurm/exports/pairs/pair.ul1pdq7m` | same carrier | distinct carriers | 1,333 / 1,574 ms | 18.324 ms | 194,385,567,207 ns | `3366f5ccea1715b563d6977136e34e42a395c3e61850ec05071bb45c8d029796` | `9d3457e21dce766331549020a23e7b90b4e05dc627c912106cc0008dd0b2ce4b` |
| direct UDP | adaptive → fixed | `.sandwurm/exports/pairs/pair.hhmma27l` | same carrier | distinct carriers | 1,567 / 1,267 ms | 21.743 ms | 300,177,986,396 ns | `3014e0b6338ff5cb11d7cbc05374d5ce339f18af83df9f53a08980882b77487f` | `96404ca4089a12bd6f5003b5b0d975ae4c5300ad0f3fe8321a3aa25e9ddf6d7f` |
| forced TCP | fixed → adaptive | `.sandwurm/exports/pairs/pair.pz9aapaj` | same carrier | distinct carriers | 1,403 / 1,083 ms | 107.040 ms | 515,713,659,651 ns | `52a72d1ad6c0f406aed7afc36e9ea38bb499a1c5bc38194b078683db7e447140` | `5ad5332cde2fd3dcc3e08e8405905c790b1358946de8d39777ef75a2a6ad3fff` |
| forced TCP | adaptive → fixed | `.sandwurm/exports/pairs/pair.jn5aqbr6` | same carrier | distinct carriers | 1,119 / 1,151 ms | 97.669 ms | 478,005,257,254 ns | `35fa3e8aa9878157f8094123047939b86e31b8941026ec59ddb528bc22380623` | `08bc3eb8fdfcfa2d75c932f217aead2089937c58691b74f1b3c8472f8c1b3655` |

Each independently verified compact export allocates 229,376 bytes and contains no guest disk,
identity secret, bootstrap secret, or mutable runtime state. All four bind source revision
`19c138fd007b8d8d07f1b4318c170384802aa421-dirty`, rev0039, and binary
`02ceeb072ae23d18675b600deecc11deb8b87bf516564baf33bef63832b15397`.
After strict raw and compact verification, the audited workspace cleaner removed all four private
raw VM roots; the compact paths in the table are the retained evidence surface.

The fixed-first direct-UDP client/device receipt hashes are
`66d289354cb647327436386901c274d5d258e65f4667d370f1e34dd53bdaf003` and
`cfc89b407fd4b914791b151159d2c893fdf817b323d2696a399a5ff957afe2d7`.
The fixed-first forced-TCP hashes are
`ff14bc4a22c857229d49ec840108577c94a7f3f398a056f7690bd83387c7feca` and
`5b821a684e591c4dc98ec75f5ee8d8347b670a4e7e6e32cce9faf8f0b12a3184`.
The adaptive-first direct-UDP hashes are
`141866fd0beb64d9020f97b33c84da50b47401c70930f4e7aadddfab8e3e9ad8` and
`eb8c10a58c3030eda8ed4a1375d2b4e307f4c37ff4de46a497c4eb29596c812e`.
The adaptive-first forced-TCP hashes are
`c6619eee03f3702a96e6156351f4704787a0534740b70658dff09c75c7e48417` and
`91b867b6a423b82301980d73ca51b144d7be3d560ccf33b8f57077ab14e583a2`.

The balance fixture contains one 8,192-byte payload and an 8,259-byte canonical treepack artifact.
Its small size deliberately makes overlap depend on the first job reaching `awaiting-objects` with
positive route admission before the second pull begins, rather than on a timing assumption. Fixed and
adaptive each make exactly two initial-admission decisions and perform four total activations.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-route-balance
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-route-balance

./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.hhmma27l sync-tree-route-balance
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.jn5aqbr6 sync-tree-route-balance
```

The verifier binds two ready bulk routes on both roles, explicit policy phase order, exact carrier
equality for fixed, exact carrier inequality for adaptive, two policy decisions per phase, four
activations, the 8,259-byte artifact, bounded HEAD retry totals, both native carrier classes, all Ratox rows, content-free process
intervals, exact receipt hashes, and compact-file digests. Its self-test rejects altered evidence.

## Exact nonclaims

The phase durations are recorded lifecycle evidence, not an adaptive speed claim: the fixture is tiny
and TCP reconnect dominates the whole-VM span. The fixed-first and adaptive-first cells counterbalance
policy order, but do not prove randomized route startup or fault order, throughput, proportional
sharing, first-byte fairness, scheduler-phase resource cost, larger populations, independent TCP
relays, physical path or host diversity, multi-source download, byte striping, or live migration.
ADR 0172 subsequently closes one separate bounded single-pull cancellation-tail row; it does not
change this placement experiment. ADR 0173 subsequently closes one eight-job small-object
population/resource row without retroactively turning this fixture into a performance result. ADR
0171 freezes this interpretation.
