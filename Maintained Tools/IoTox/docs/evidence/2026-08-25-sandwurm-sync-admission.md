# Sandwurm synchronization admission-deferral evidence

Date: 2026-08-25

Status: accepted single-Agent excess-work qualification

## Claim

Two simultaneous source-linked IoTox guests independently passed the smallest real full-receive-
ledger synchronization boundary over observed direct UDP and forced TCP. The subscriber configured
one accepted receive, requested a deterministic two-object directory revision, and admitted the
first immutable object. The second exact FileId offer remained paused outside accepted Tox transfer
state until the first receive completed. Bounded Agent service retried it without changing the
scheduler attempt or overbooking storage, admitted it into the released slot, verified both objects,
accepted the signed HEAD last, and activated only through its exact local token.

Both cells ended with exactly two admitted offers, ten admission retries, zero pending offers, and
generation-1 byte-identical convergence. No second receive was accepted while the configured ledger
limit was one. This is the live counterpart to the owned attempt-identity, byte-reservation,
one-shot-cancellation, cyclic-service, and 32-record-per-pass tests frozen by ADR 0166.

## Accepted compact cells

| Route | Compact proof | Whole-VM rendezvous span | Pair manifest SHA-256 | Compact export SHA-256 |
|---|---|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.xrl6_7gv` | 269,418,196,203 ns | `f4c44ad362bb0d888759f433cac9732bf6f54b6baca8ec63df89b3ca2581c97f` | `55620525a4e2c6767ddd802280f078a897be9f6f6e5bcb28755c849a3da449ec` |
| forced TCP | `.sandwurm/exports/pairs/pair.dqbsp21_` | 296,387,576,149 ns | `038c9c8e48e93ef9d4081c4d086899e4eb7691a7c123361055d3e93540d385f9` | `b8e380b433da5dc48b7acc50546c143ba1e2b169f835c9280a1105827684c8be` |

Each independently verified compact export allocates 122,880 bytes and contains no secrets or guest
disks. Both bind source commit `7ad6681cda30ba1613f0fc3f8a34ebb64ecc3bec`, rev0039, binary
`b9d89521c1609438af1b4038b4b9154e944e69ec38a629bdee4c20933a5f8a2a`, artifact
`a079be557aba734548322fa95ab91825c01735adf4bf0028f6b2dca4a458d93e` (4,194,601 bytes),
manifest `f9483c05ea4d93ec6e7c191a334d854d26d84db8f04c85c8ae5cac2b4f8d8bb7`
(786,568 bytes), and HEAD record
`ac21e81c8f3fc365e47c7e7fcf82c78a9b32c029af6cafc411063584e6f7cfa9`.

The direct-UDP client/device receipt SHA-256 values are
`312acaa86737fbc9bf5c4c0e7dc4ba225fb6ec725dc77f3908d9d0c6f9af4dce` and
`121990817a291f2ee66f2f7c3df279d0e29f503049a1d29b289e013652615ad5`;
the forced-TCP values are
`ff68c0e402f573e637f60518388202499e74918197a3b8b8b88fd1eca95e8746` and
`5e4ec46b5a3460bc744e0558b9b802c65fb65f9b8b19e838830e244c2baa4318`.

## Latency qualification by composition

This cell deliberately isolates admission semantics and does not synthesize a Ratox latency number
from whole-VM rendezvous time. The same accepted single-Agent scheduler and carriers have separate
1,000-sample `bulk-1` proofs: direct UDP `pair.a4j1uirz` rendered p95 42.727 ms with owner p99
1.499 ms; forced TCP `pair.0vkhkq96` rendered p95/p99 57.594/70.044 ms with owner p99 1.452 ms.
Together those cells qualify the two route latency classes while this gate proves genuine full-ledger
pressure, bounded retry, eventual service, and no excess accepted receive. A simultaneous Ratox-under-
sync-deferral experiment would be additional interference science, not evidence silently implied by
this composition.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-admission
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-admission

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.xrl6_7gv \
  --route direct-udp --scenario sync-tree-admission
python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.dqbsp21_ \
  --route forced-tcp --scenario sync-tree-admission
```

The private source proofs contained writable guest disks and injected test identities. They were
strictly verified before compaction; the compact exports contain only the verifier allowlist and
bind their source manifests.

## Exact nonclaims

This proves one publisher, one subscriber, one two-object directory, one accepted-receive slot, and
ten observed retries per carrier on this construction host. It does not prove 32 simultaneous sync
objects, simultaneous terminal latency under a deferred sync offer, multiple sources, auxiliary-
route reassignment, two physical hosts, permanent GC, OTA installation, or safety-critical actuation.
ADR 0166 freezes the interpretation.
