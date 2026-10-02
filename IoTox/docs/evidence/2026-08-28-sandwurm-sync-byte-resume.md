# Sandwurm immutable sync byte-resume evidence

Date: 2026-08-28

Status: accepted direct-UDP and forced-TCP qualification

## Claim

Two simultaneous source-linked IoTox guests each constructed one protected primary and two
separately keyed authenticated bulk workers. The subscriber began a real two-object directory pull,
stopped the exact active bulk carrier only after positive receive progress, fenced that incarnation,
and reassigned the missing immutable objects to the other ready carrier. Unlike the earlier Gate 3
cell, the replacement attempts inherited the exact private positive prefixes and asked c-toxcore for
only the remaining suffixes.

Both native carrier classes retained two concurrently active object prefixes. In each cell the
lifetime retained-attempt count exactly equals the resumed-attempt count, retained bytes exactly
equal resumed bytes, the live retained-partial gauge returns to zero, and the retention-fallback
counter remains zero. Both objects still pass complete SHA-256 verification before commit; accepted
HEAD remains last and activation remains explicit. One loss, one reassignment, two stale terminals,
and one same-savedata route recovery are observed in each cell. Forty protected Ratox renders then
remain strictly below 250 ms.

## Accepted compact cells

| Route | Compact proof | Observed fault position | Retained / resumed | Fallbacks | Loss / reassign / stale / recover | Ratox p50 / p95 / max | Whole-VM span | Pair manifest SHA-256 | Compact index SHA-256 |
|---|---|---:|---:|---:|---|---|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.jlcr7zms` | 112,422 B | 2 attempts, 315,330 B / 2 attempts, 315,330 B | 0 | 1 / 1 / 2 / 1 | 13.002 / 17.406 / 17.962 ms | 372,460,984,249 ns | `ea3fb021e9f1811c9c431559a1450438d87a8d38677379416d41c3d7aeed25fe` | `db4f2649534cf3f7630d361a37983a79e6227186fa17400b37aaaf2392a89226` |
| forced TCP | `.sandwurm/exports/pairs/pair.okks1io5` | 93,228 B | 2 attempts, 252,264 B / 2 attempts, 252,264 B | 0 | 1 / 1 / 2 / 1 | 87.665 / 94.578 / 106.344 ms | 372,586,192,303 ns | `4730cd1f2cc058799d399ba23f9786f0281e5da9afde591d5945a515fe807f7b` | `7153fd4dcc5ef2ab585f563f4576804fcc8f6b40900326251bbe941398f8bfd3` |

The observed fault position is the joined provider position for the transfer selected to trigger
loss. Retained/resumed bytes are the aggregate across every positive whole-object attempt active on
that carrier, so the aggregate is intentionally greater than the singled-out fault position. An
earlier rejected direct-UDP run exposed this legitimate two-object concurrency and caused the gate
to replace its incorrect exactly-one assumption with the stronger aggregate equality invariant.

Each independently reverified compact export allocates 253,952 bytes, contains no secrets or guest
disks, and binds clean source revision `3185e8914761b07d2f7f66420fe09c7cc0854cbd` and binary
`97ccac9341c6e87709645be22533395526159fd739b47bcef357026991801a19`.
Both cells converge artifact
`a079be557aba734548322fa95ab91825c01735adf4bf0028f6b2dca4a458d93e`, manifest
`f9483c05ea4d93ec6e7c191a334d854d26d84db8f04c85c8ae5cac2b4f8d8bb7`, and HEAD
`ac21e81c8f3fc365e47c7e7fcf82c78a9b32c029af6cafc411063584e6f7cfa9`.
The materialized tree has three directories, three files, 4,194,389 content bytes, and payload
SHA-256 `374921f176ff69a68f433edce6fcd97f8f103229f5572060675f061f48bf0a0e`.

The direct-UDP client/device receipt hashes are
`c6693c71cfbc88cb363d9aafee94f2dd006f7a4e2038bd0aa9e8266d579c8024` and
`4416f7cef17cd124751d1f3f4af708b829b1a653b7d8e8967310920149958399`;
the forced-TCP hashes are
`bf16f38b64cbfef6db666c017067aa0ce452684c99d5dd19fc9c492f537a6a03` and
`dff92910be5cccbc43f866577fa417f5ab0876c919bd2e557518d6f28df8ba82`.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-route-loss
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-route-loss

./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.jlcr7zms sync-tree-route-loss
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.okks1io5 sync-tree-route-loss
```

The verifier binds the observed UDP/TCP carrier, exact source and binary, both guest receipts and
chains, positive bounded retained/resumed attempts, exact aggregate byte equality, zero residual
partial/fallback state, route-loss lifecycle, convergence/activation, both resource intervals, and
all 40 ordered protected Ratox rows. Its self-test rejects altered new and historical records.

## Exact nonclaims

This is same-process, same-object, cross-carrier suffix continuation after one deterministic route
loss. It does not prove process- or guest-restart continuation, range-bundle continuation, repeated
or very-late loss, resource savings attributable only to byte reuse, physical host/path diversity,
multi-source download, arbitrary cross-network policy, Tor, I2P, or production performance. The
complete digest remains authoritative; retained bytes are an optimization, never trust. ADR 0224
freezes the interpretation.
