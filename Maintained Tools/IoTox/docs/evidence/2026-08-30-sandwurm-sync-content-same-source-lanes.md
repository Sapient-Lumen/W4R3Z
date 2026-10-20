# Sandwurm same-source content lanes — 2026-08-30

## Claim

One content-v2 pull can hold two independently attributed immutable-object receives against one
authenticated publisher over both direct UDP and forced TCP. The root manifest remains serial, the
two live lanes have distinct request IDs and FileIds, and the revision still converges, accepts its
signed HEAD last, and activates only through the explicit token.

This is a bounded concurrency claim for ADR 0262. It is not object-byte striping, multiple physical
routes, multi-source scheduling, anonymity, or a throughput result.

## Construction

The dedicated `sync-content-same-source-lanes` scenario starts two simultaneous source-linked
Sandwurm Cloud Hypervisor guests with the repository's reused immutable private identity baseline.
The signed `sandwurm-file` namespace sets `maximum-lanes=2`; the subscriber Agent opts in with
`--max-sync-content-lanes 2`. Host traffic shaping holds the 4 MiB paged transfer open long enough
to observe live owner-private state.

Acceptance requires one `content-job=` row with `active-lanes=2` and exactly two matching
`content-lane-job=` rows. Both lanes must be transport-admitted, non-root, bound to one source, and
carry distinct nonzero request/FileId identities. Completion then independently verifies the
artifact, root manifest, signed HEAD, and explicit activation.

## Invocation

```sh
./tools/iotox-sandwurm-lab.sh up-pair \
  direct-udp sync-content-same-source-lanes
./tools/iotox-sandwurm-lab.sh up-pair \
  forced-tcp sync-content-same-source-lanes

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.895m5lwy \
  sync-content-same-source-lanes
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.bcecui0l \
  sync-content-same-source-lanes
```

The first forced-TCP attempt inherited the generic 240-second host authority deadline and timed out
before publication or content work. The established forced-TCP content gate uses 480 seconds while
the guests retain their 420-second bound. After assigning the new scenario that existing host bound,
a fresh pair passed. The failed attempt is not accepted evidence and its raw root was deleted.

## Accepted observations

Both accepted pairs record:

- scenario `sync-content-same-source-lanes`, status `passed`;
- process and signed namespace lane cap `2`;
- two simultaneously active and admitted lanes;
- one authenticated content source;
- two distinct request IDs and two distinct Tox FileIds;
- zero active root-manifest lanes during the overlap;
- one 4 MiB paged artifact with four logical chunks, one page, and four deduplicated objects;
- artifact SHA-256
  `844dbd0270ee58cf1e1b8062460e6b5f24b974a24fd482e861689d65e81598a7`;
- root-manifest SHA-256
  `f8637c280348a3af9685afdbb53a0351236ec52e26abb146ec8f3a20c39c9b66`;
- accepted HEAD-record digest
  `5418cf893bf66afe955edf1b855e9e72c4069693d245fef9a579f8917c02141c`;
- exact convergence and explicit activation in both guest receipts; and
- source-linked binary SHA-256
  `8296219d64ece148355610a04a7b83a04c509fbaf61eabf4b16312a631f4b3a7`.

Direct UDP compact proof `pair.895m5lwy` additionally binds:

- client receipt SHA-256
  `1045ac344758a285e71eaa0ba57dd691e9bd6c1051a2dd313aa0bccdb99d2fce`;
- device receipt SHA-256
  `a8a5855567f9be7a96ecb615d7fa192f73e78102d3696f4a340d3fd065851ea2`;
- lane-set commitment
  `fc4aea17a54e7c5b15fdb4bfd6506125159123556bcd1a8d0ecd2e9d6c9cff08`;
- compact pair-manifest SHA-256
  `044c312e773b5a62e753b046e9af68c0f309119711c1e3ec621e1bbb65b9788d`; and
- compact-export SHA-256
  `17ea13fe282498ff94c161d15d9c23764267b3d5dfd0dfdf9bca559bd34e1484`.

Forced TCP compact proof `pair.bcecui0l` additionally binds:

- client receipt SHA-256
  `32a2d4a19213daeb3e58453040bb6b8b30e714c00a213b0b2651e4b967b5777b`;
- device receipt SHA-256
  `b3a9b8c8aab2a1efca7820ff20f7abca9053a0abd2cfdd7c819f8aeba22483c7`;
- lane-set commitment
  `6a439b515beef785f021dd20e2b0413e4fb84cc5cbfaf5817f8789d89c350cee`;
- compact pair-manifest SHA-256
  `a1e16138ceb4587adb249203a1c0b66c6cf4982dc3397c821d446a149a9167d8`; and
- compact-export SHA-256
  `1af95a5b649eb40cab1d4b23d2e22a9a5c52ebf95ea2b6bd860d6aede3ce416b`.

Each compact root contains nine secret-free files and allocates 163,840 bytes. The independent
verifier rehashes its exact inventory and checks the lane evidence in both role receipts. Across the
preliminary and final generations, the scoped workspace cleaner removed seven multi-gigabyte raw
roots and four superseded compact roots, reclaiming 16.1 GiB. A post-clean dry run finds zero
candidates while both final compact roots still reverify.

The final source also passes all 46 registered CTest entries under GCC and Clang (the same five
host-kernel cgroup cases skip in each matrix), all 16 ASan/UBSan owned-registry shards covering 666
checks, the Sandwurm runner/verifier/exporter/cleaner self-tests, and `nix flake check`.

## Limits and next gate

The proof shows a real scheduler/transport overlap and exact terminal convergence. It does not show
that two lanes outperform one, whether more than two lanes help, whether terminal traffic suffers,
or where a common-session bottleneck sits. The next scientific gate should compare lane caps
`1/2/4/8` with fixed content, route, shaping, and competing interactive traffic, reporting artifact
throughput, completion tail, terminal latency, toxcore queue pressure, CPU, and memory. Only after a
measured benefit should a default above one be considered.
