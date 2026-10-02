# Sandwurm synchronization control-replay evidence

Date: 2026-08-24

Status: accepted construction evidence

## Claim

Two simultaneous source-linked IoTox guests independently passed the same duplicate, reordered, and
conflicting synchronization-control gate over observed direct UDP and forced TCP. Both cells used the
production binary, stable reused test identities, and the pinned local c-toxcore 0.2.23
bootstrap/relay fixture.

After generation 1 was accepted and activated, the publisher signed a one-byte-changed generation 2.
The rate-shaped subscriber admitted both original FileId-bound object offers, captured the exact
outgoing canonical HEAD and object-request frames from its private protocol journal, and injected
both object requests again. The publisher returned both retained object results but created no
additional file offers, so the duplicate controls arrived behind already-admitted file lanes. The
subscriber then replayed the exact HEAD request after all four object-result records had arrived; the
retained HEAD result emitted no additional object request. Finally, it sent the same HEAD request
message identifier with a different canonical namespace. The publisher counted and refused exactly
one conflict, emitted no replacement result, preserved the original pull, and the subscriber accepted
the HEAD last and activated only by its exact token.

## Accepted compact cells

| Route | Compact proof | Span | Pair manifest SHA-256 | Compact export SHA-256 |
|---|---|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.control_replay_udp` | 295,434,368,459 ns | `75211123e4f7c69955f9986c75ce1cc25be459daca8fd6d2132cf686ec45f78c` | `ba0a1386e868d1109dce45543a13c165550d617b9cce0cdea816821569a48cc2` |
| forced TCP | `.sandwurm/exports/pairs/pair.control_replay_tcp` | 488,259,191,922 ns | `d98193d4c9e2242d956e93c268a7ef7ab663055a253193f8e6ac735c8e3a5121` | `3882a792823fbf10bfa6eabd694c9a8adcae3cbff5f50cd30db7b61d7af207af` |

Each compact export independently verifies, contains no secrets or guest disks, and allocates
122,880 bytes. Both cells bind binary
`5f2ce692b6173164169f6c87962e9ab8c5fee84969ca198132ece993bfc645a7`, generation-2 HEAD
`d5b3dfb9578c760524d9cec7f8ab716f5833dca07b4f0289a1021ef6b61b9780`, artifact
`e934360ca89d27181ccbc0d585399d2b6665ae99655a20b9b3398f5928a937ec` (4,194,601 bytes), and
manifest `2cf46957f0fc6a5fe0621482e2fad9d3779e0cf7e5adfd418d850abf3fd306fc`
(786,568 bytes).

Both pair manifests bind the same exact deltas:

- publisher: 1 new HEAD request, 2 new object requests, 2 file offers, 3 exact replay hits, and 1
  replay conflict;
- subscriber: 2 incoming HEAD results, 4 incoming object results, and 4 outgoing object requests
  total (2 original plus 2 explicit duplicates), with 2 object lanes admitted before injection;
- both roles: exact replay, cross-lane reordering, conflict refusal, HEAD-last convergence, and
  explicit activation observed.

The UDP client/device receipt SHA-256 values are
`f3e1b2d390970aa6fbe06a147da6c139da7cba632f0d93c80d662ac3990df220` and
`56d103ee5da8a1a7986c2091dd58d49551e96578de59115293de0516e51be8f6`;
the TCP values are
`f9e86b7876c611ef70eb6ff5b4318dd09c5beadc99e0d588ab2ac9df6b05e1ca` and
`719d874b441a895bf4835d00571c9be61c36628c8793c2c7f6ffc00d96d23acb`.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-control-replay
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-control-replay

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.control_replay_udp \
  --route direct-udp --scenario sync-tree-control-replay
python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.control_replay_tcp \
  --route forced-tcp --scenario sync-tree-control-replay
```

The private source proofs contained writable guest disks and injected test identities. They were
verified before compaction and removed after the compact exports independently passed. The compact
exports contain only the verifier allowlist and bind their source manifests.

## Exact nonclaims

This is one publisher, one subscriber, one two-object directory successor, three exact replay
injections, and one deterministic conflict per carrier on this construction host. It proves
same-epoch byte-exact replay, suppression of duplicate file-offer effects, tolerance of results
reordered behind admitted file lanes, conflict refusal, HEAD-last acceptance, and separate
activation. It does not prove publisher restart replay durability, arbitrary packet permutation,
loss recovery, multiple sources, two-physical-host behavior, content-v2, OTA installation, or
safety-critical actuation. ADR 0147 freezes the interpretation.
