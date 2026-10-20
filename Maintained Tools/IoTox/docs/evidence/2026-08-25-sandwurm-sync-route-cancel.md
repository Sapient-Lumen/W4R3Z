# Sandwurm multi-route sync cancellation evidence

Date: 2026-08-25

Status: accepted Gate 4 bounded cancellation-tail qualification

## Claim

Two simultaneous source-linked IoTox guests each used one signed protected primary and two separately
keyed, reciprocally authenticated bulk workers. The subscriber selected one auxiliary route through
the conservative adaptive policy, admitted both immutable objects, and observed positive receive
bytes on that exact route key and worker incarnation before issuing `sync-cancel` for the bound job.

On both native carrier classes the same job became terminal `cancelled`, no incoming transfer or
private staging survived, signed coordinator work changed from two to zero, no reassignment occurred,
both bulk routes remained ready, and neither an accepted HEAD nor activation was created. The same
guests then completed 40 protected-primary Ratox samples with no render at or above 250 ms.

## Accepted compact cells

| Route | Compact proof | Positive bytes | Active receives | Work before → after | Reassignments | Cancel tail | Ratox p95 / max | Whole-VM span | Pair manifest SHA-256 | Compact index SHA-256 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.fpkne1pg` | 2,742 | 1 | 2 → 0 | 0 | 70 ms | 19.991 / 21.686 ms | 343,581,493,020 ns | `31b14107be629875e53b6fefbdbab95f23516306732062f38e4fd6d30cd4d9c1` | `86f18667c03cffa1ca3fe0a9ee0c8a018bf4047a01501aac321d3e1825782e3f` |
| forced TCP | `.sandwurm/exports/pairs/pair.r_4luysy` | 78,147 | 1 | 2 → 0 | 0 | 80 ms | 95.177 / 129.300 ms | 427,871,646,541 ns | `5e7f3fa8c97d0e59fdcab486119077d224197faa3f72fa25cd5692ac8008b3b9` | `3ab437edade969030753e667923c98819b31bc127618916e08f526242bd1d9ff` |

Each compact export allocates 229,376 bytes and contains no guest disk, identity secret, bootstrap
secret, mutable runtime state, path, FileId, or content. Both bind source revision
`b092d652286fa76d68dc1c2221f2c500dcc6322e-dirty`, rev0039, c-toxcore 0.2.23 with
`iotox-file-rr1`, and binary
`1eb2c2cb71300252147de3da3d1a62d6d07231636f3bc2556ffa09292ae2920b`.

The direct-UDP client/device receipt hashes are
`49dc3cfda40d40a272c552c9eb38c389d32738343da4d3bf3370978be9ea59da` and
`b3a6e8f216f4329370d9918cf58d9611594ca1d9fbfc3779b3df6eac5182552d`.
The forced-TCP hashes are
`e905e69a38a205d35048c9e6e4a0c3f88d3b5dd8fa55bb8d1fcf13568e9364ea` and
`994a21eb20f2ca133f86b3d52721886f2ab06dbd050f2e4460c98b222d3a3e25`.

After strict raw and compact verification, the audited workspace cleaner removed the two accepted
raw roots and two rejected development roots, reclaiming 9.2 GiB. The same cleanup checkpoint
removed 5.7 GiB of reproducible build lanes and stale sandbox temporaries, for 14.9 GiB reclaimed in
total. Both compact proofs passed strict verification again after deletion.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-route-cancel
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-route-cancel

./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.fpkne1pg sync-tree-route-cancel
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.r_4luysy sync-tree-route-cancel
```

The verifier binds two ready bulk routes on both roles, adaptive policy, exact auxiliary route and
nonzero worker identity, one selection, one or two active receives, positive pre-cancel bytes and
work, zero residual work/reassignment, a 0–5,000 ms monotonic tail, terminal cancellation without
convergence/activation, all Ratox rows, resource intervals, carrier class, receipt hashes, and compact
file digests.

## Exact nonclaims

The observed 70/80 ms values are construction-host observations, not fleet latency promises. This
does not prove remote cancellation acknowledgement, cancellation under concurrent-job pressure,
fair release ordering, cancellation during simultaneous route failure, byte-prefix reuse,
multi-source download, byte striping, live migration, independent relay diversity, or physical host
diversity. ADR 0172 freezes this interpretation.
