# Sandwurm common-link fair-queuing evidence

Date: 2026-08-29

Status: accepted Gate 4 shared-edge mechanism qualification

## Claim

Two simultaneous source-linked IoTox guests reused the same private test identities and ran the
existing protected primary plus two separately keyed, reciprocally authenticated bulk workers. The
subscriber admitted eight independent 1,048,643-byte treepacks under adaptive placement, producing
`01010101`. Four ordinary clients simultaneously withdrew two jobs per route. Exactly four jobs
reached terminal cancellation; the other four committed and explicitly activated; work drained
16-to-zero; no reassignment occurred; and 40 protected Ratox samples completed under the unchanged
deadline.

Unlike the two negative FIFO cells, the common 4 Mbit client TAP used one HTB rate class with an
`fq_codel` leaf. The host captured that live hierarchy and its counters only after protected Ratox
completion and before allowing the guest/TAP to terminate.

## Accepted compact cells

| Route | Compact proof | Cancel tail | Active flows | Queue bytes / packets / drops | Ratox render p95 / max | Whole-VM span | Pair manifest SHA-256 | Compact export SHA-256 |
|---|---|---:|---:|---:|---:|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.am47s4qe` | 80 ms | 6 | 5,795,303 / 5,162 / 522 | 16.564 / 17.067 ms | 138,375,124,992 ns | `7cec9bd5d1dc31986a0d94d6da77135b04847d2328fde3ae9a5c996b8e1dba87` | `ac7ef3157d7fd6cc08fb88a079882e5b58810a298f53387ba66a5376b6914408` |
| forced TCP | `.sandwurm/exports/pairs/pair.78uagrhw` | 90 ms | 3 | 5,782,816 / 4,853 / 150 | 98.767 / 112.817 ms | 337,999,945,313 ns | `eb157df439cffa086a07d596ebb4c504e15c4d3d96424153f18ff2c20bb5e309` | `ae4c3a76e87957f8c348c0727fc99bf8b2059901fc0cf1ced66de476a4a9cb21` |

Each compact export allocates 270,336 bytes and contains 15 content-free evidence members. Guest
disks, private identities, bootstrap keys, FileIds, namespaces, paths, and transferred content are
excluded. Both bind source revision `6e93b5f13062dc7ca136eedd12533578a5117e7c-dirty`, rev0045,
c-toxcore 0.2.23 with `iotox-file-rr1-tcp-connect120`, and binary
`a7eb9e0bc478125a2ced8f9f8c4bd89759364c12689948d594113ebc5fc3ab53`.

The direct-UDP client/device receipt hashes are
`c290567119ffab33cd3dead61ff2afeb904fce6924790756d4d849fe7f098618` and
`00ee1186a21801d6af034068959fca2312dea22f01d7783c1b44b45f5b9240bd`.
The forced-TCP hashes are
`81801994d2ba3c43131f29162a23e1c78282c5c3234cd40a4f607dbffd9a9857` and
`38dea3cc8809eb35ce1544c68c536292efd1bb0235221744447dc501619d2247`.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-common-link-fairness
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp \
  sync-tree-route-common-link-fairness

./tools/iotox-sandwurm-lab.sh export-pair \
  .sandwurm/lab/pairs/PAIR
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.am47s4qe \
  sync-tree-route-common-link-fairness
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.78uagrhw \
  sync-tree-route-common-link-fairness
```

The strict verifier requires the exact HTB/`fq_codel` topology, 500,000-byte/s rate and ceiling,
1,000-packet leaf limit, positive class/leaf traffic, eight adaptive decisions, balanced route
pattern, four withdrawals and survivors, four activations, zero reassignment/work, resource digest,
both native connection classes, 40 Ratox rows, exact receipt hashes, and every compact-file digest.

## Interpretation and nonclaims

The negative FIFO cells and these positive fair-queue cells isolate one actionable boundary: a
protected logical route needs cooperation from the narrowest shared queue when interactive and bulk
flows contend. `fq_codel` is a qualified same-host mechanism, not a wire-protocol dependency.

This is one bounded cell per carrier with one rate, queue limit, job population, and timing. It does
not prove strict DSCP/socket priority, reserved bandwidth, arbitrary overload behavior, a universal
deployment default, independent bottlenecks, relay diversity, byte striping, multi-source download,
randomized cancellation timing, or long-running policy. ADR 0241 freezes this interpretation.
