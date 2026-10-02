# Sandwurm immutable sync route-loss evidence

Date: 2026-08-25

Status: accepted Gate 3 qualification

## Claim

Two simultaneous source-linked IoTox guests each constructed one signed three-member route set: one
protected primary and two separately keyed authenticated bulk workers. The subscriber began a real
two-object directory pull, stopped the exact running bulk carrier only after positive provider
progress, fenced its old attempt, rejected its retained terminal truth, reassigned the missing
immutable work to the other ready carrier, converged and explicitly activated the exact signed tree,
then recovered the stopped savedata identity under a fresh worker incarnation within its one-restart
budget.

The same cell then completed 40 exact Ratox keypress-to-render samples and captured content-free
process resources on both roles. Every sample remained strictly below 250 ms. Direct UDP rendered
p50/p95/p99/maximum at 16.119/22.310/26.230/26.230 ms; forced TCP rendered
91.572/103.665/119.527/119.527 ms. Neither cell produced a 250 ms miss.

## Accepted compact cells

| Route | Compact proof | Fault position | Loss / reassign / stale / recover | Ratox p95 | Whole-VM span | Pair manifest SHA-256 | Compact index SHA-256 |
|---|---|---:|---|---:|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.gqw1gzkd` | 224,844 B | 1 / 1 / 2 / 1 | 22.310 ms | 452,847,232,857 ns | `1fffb2d5c315f525365948ec8c8dace43f58a4b993c1cdc88b8595831f799f91` | `de43205157149b5531c0223122416f0f79c377d4aad9950eaa31b3787b2ab8bf` |
| forced TCP | `.sandwurm/exports/pairs/pair.9i62wfpa` | 150,810 B | 1 / 1 / 2 / 1 | 103.665 ms | 413,466,699,331 ns | `87ef3b7790f481365a1ee1870611f40dd97906dc0c4e023cc59c4b125ba1ed9d` | `a154fa309d6dc200e3c6573621941502f5fbcf932af8ef169a64d7f91a908bd9` |

Each independently verified compact export allocates 229,376 bytes, contains no secrets or guest
disks, and binds source revision `19c138fd007b8d8d07f1b4318c170384802aa421-dirty`, rev0039, and
binary `c0b3cc60add80ad72d5a25fa2d3a757d3d4f9323e0497e672f73e6b16706325a`.
The build was intentionally qualified from the reviewed working tree before its documentation
commit; the exact binary and every retained file are independently hashed by the proof.

Both routes converge the same artifact
`a079be557aba734548322fa95ab91825c01735adf4bf0028f6b2dca4a458d93e`, manifest
`f9483c05ea4d93ec6e7c191a334d854d26d84db8f04c85c8ae5cac2b4f8d8bb7`, and HEAD record
`ac21e81c8f3fc365e47c7e7fcf82c78a9b32c029af6cafc411063584e6f7cfa9`.
The materialized tree contains three directories, three files, 4,194,389 content bytes, and payload
SHA-256 `374921f176ff69a68f433edce6fcd97f8f103229f5572060675f061f48bf0a0e`.

The direct-UDP client/device receipt hashes are
`42e3dc3a04de3f4d42a756efc9db79974a18863e2f7de2ae1554d256a4fd40c7` and
`37554a49f1afb55d7984a5b9c98899be8173e6eb31d38e98da62fa8e06b1874b`;
the forced-TCP hashes are
`a73d27d46f239ea42a52722d178a1d8e4c8f81343872cb8e63a3951100f76b43` and
`d6b673fa7455fed452c7b109280acfc1e4a2055d0d66e2f211ad2faf17396c12`.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-route-loss
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-route-loss

./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.gqw1gzkd sync-tree-route-loss
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.9i62wfpa sync-tree-route-loss
```

The verifier checks route observations, exact source/binary and receipt hashes, signed sync truth,
recovery counters, distinct stopped/final carriers, both resource intervals, all 40 ordered Ratox
rows, and the strict 250 ms protected-route ceiling. Its self-test also rejects altered evidence.

## Exact nonclaims

This proves one publisher, one subscriber, one two-object tree, one deterministic mid-transfer loss,
one replacement bulk route, one same-savedata recovery, and subsequent protected Ratox operation for
each native carrier class on this construction host. It does not prove byte striping, concurrent
Ratox sampling during the exact loss instant, adaptive scheduling, randomized fault order, independent
TCP relays, physical path/host diversity, multi-source download, hours-long churn, or production
policy replacement. Those claims remain Gate 4/5 work. ADR 0169 freezes the interpretation.
