# ADR 0232: Qualify repeated native bounded-range loss

Status: accepted implementation and genuine direct-UDP/forced-TCP Sandwurm qualification,
2026-08-29.

## Context

ADR 0231 permits one native `available`-policy bounded range to carry an exact private prefix from
a dead authenticated auxiliary carrier into a fresh attempt on another carrier. Its deterministic
test repeats that transition, but one real loss does not establish that recovered route identity,
stale terminal fencing, cumulative prefix accounting, and scheduler recovery compose when the
replacement carrier also dies.

A timing-only second fault was not an acceptable gate. With two carriers and a small successor, the
replacement could complete before the first stopped savedata identity returned. Earlier host-side
packet-size classification also starved status traffic behind the shaped transfer, making the
experiment test qdisc timing rather than the protocol boundary.

## Decision

- Keep `--qualify-route-stop-count` default-off and bounded to `1|2`. Count two is laboratory
  control only; it does not alter ordinary route policy or production scheduling.
- For count two only, defer the exact bounded object/range request frame created by first-loss
  reassignment until the exact stopped worker identity is authenticated and ready again. The queue
  shares `maximum_worker_queue`; overflow fails instead of creating unbounded laboratory state.
- Release that request once, onto the already selected replacement carrier, after recovery. Expose
  `qualification-deferred-frames` and `qualification-deferred-frame-releases` as owner-private,
  content-free status. Ordinary product and one-fault paths remain zero/zero.
- Stop the replacement only after it has positive progress and the first carrier has recovered.
  Apply the unchanged ADR 0231 sequence again: retire transport truth, finish and fence the old
  signed attempt, hide the old FileId, validate the strict prefix, allocate fresh attempt/message/
  FileId identities, and resume only from that offset on the recovered carrier.
- Require exactly two losses, reassignments, stale-terminal fences, recoveries, retained attempts,
  resumed attempts, and aggregate worker restarts. Cumulative retained bytes must equal cumulative
  resumed bytes, with zero discarded bytes, zero retention fallback, and no range-retry use.
- Require final carrier equality with the initially stopped carrier. This proves the two-member
  alternation rather than merely counting two faults on one identity.
- Preserve the existing full-object digest, range reconstruction, signed-HEAD-last acceptance, and
  explicit activation gates. No framing, feature bit, FileId format, signed record, object identity,
  authority rule, or default failover behavior changes.

## Evidence

The genuine `sync-file-range-repeated-route-loss` cell first activates a deterministic 4 MiB basis,
then publishes generation 2 with one changed 1 MiB range and a 786,496-byte manifest. The basis path
is shaped at 4 Mbit/s and the target range at 256 kbit/s. The second route fault cannot arm until the
first exact savedata identity has returned ready and the replacement has positive range progress.

Both accepted cells use product revision `rev0045` and binary SHA-256
`88093a006d9a9e0bedb7af6be5ed3efb47399279a289c7b7c44eb86748257bca`:

| Route | Compact proof | Final fault position | Retained = resumed | Loss/reassign/stale/recover/restart | Span |
|---|---|---:|---:|---:|---:|
| direct UDP | `pair.le38qcl5` | 278,313 bytes | 542,916 bytes | 2 / 2 / 2 / 2 / 2 | 470,693,993,820 ns |
| forced TCP | `pair.8u14ddcy` | 289,281 bytes | 564,852 bytes | 2 / 2 / 2 / 2 / 2 | 601,510,872,772 ns |

Each result records zero discarded bytes, zero fallback, zero final retained partials, zero deferred
frames, one deferred-frame release, one 1 MiB range fetched, and 3 MiB of verified basis reused. The
same exact 4 MiB artifact, manifest, and linked generation-2 HEAD are verified and explicitly
activated. Both 163,840-byte compact exports independently pass the strict offline verifier.

## Consequences

The native two-carrier range path is no longer qualified only for its first failure. On the tested
same-process job, one exact prefix survives two sequential authenticated carrier deaths and three
fresh transport attempts without retransmitting either saved prefix.

ADR 0233 subsequently qualifies a distinct single loss after at least 15/16 of one range. ADR 0235
later adds a separately named, still-bounded three-loss gate without changing this decision's exact
two-loss contract. This ADR alone does not prove three or more losses, repeated late loss,
final-chunk races, daemon or guest restart,
primary-authority epoch loss, explicit-new-job prefix reuse, concurrent multi-source striping,
cross-class migration, fail-closed I2P continuation, Tor-to-Tor continuation, randomized timing,
two physical hosts, or a performance improvement. The deferred request is a qualification barrier,
not a product scheduler feature.
