# ADR 0231: Resume bounded ranges across available carrier loss

Status: accepted implementation, deterministic failure coverage, and genuine Sandwurm
qualification, 2026-08-29.

## Context

ADR 0224 already permits a whole immutable-object prefix to move from a dead auxiliary carrier to a
fresh authenticated carrier under the `available` failover policy. ADR 0230 gives an ordinary
same-carrier bounded-range retry the same exact-prefix primitive. The remaining native-route gap was
therefore not a framing or hashing problem: the subscriber still treated loss of a concrete range
lane as unsupported, even when another authorized range-capable carrier was ready.

Fail-closed privacy policy is a separate invariant. ADR 0228 deliberately discards an I2P range
prefix and blocks the old job rather than moving bytes or work into a different route class. A safe
native available-policy continuation must not weaken that behavior.

## Decision

- A concrete range lane under `available` policy may survive loss of its authenticated auxiliary
  carrier. The subscriber first retires local transport truth, removes the old FileId from eligible
  dispatch, and makes repeated observations of the same missing carrier idempotent.
- Under the namespace transaction, only an exact canonical private partial with a positive size
  strictly below the complete bundle and an available seek-capable receive seam is retained. A
  positive inspected prefix that fails those checks is discarded and increments
  `range-retention-fallbacks`; absent, empty, complete, or otherwise unusable staging is discarded.
- The old signed active-attempt record is finished and its scheduler reservation is fenced before
  replacement. Delayed old result, offer, and terminal truth cannot address the inert lane.
- Replacement requires the same primary authority context, a distinct authenticated auxiliary
  carrier, and negotiated bounded-range support. The subscriber allocates a fresh scheduler attempt,
  request message ID, and nonzero FileId, then atomically hands any retained inode to that attempt.
  The signed HEAD and canonical range plan do not change.
- Carrier reassignment is not a logical range retry and does not consume the one-retry budget or
  increment `requested_objects`. The already committed manifest plus the completed range remain the
  same two logical objects.
- The replacement offer must match the new FileId and complete bundle size. Before seeking, the
  subscriber reopens and revalidates the exact handed-off path and size. Complete target SHA-256,
  immutable commit, signed HEAD acceptance last, and explicit activation remain mandatory.
- Cleanup failures restore an owned inert lane before terminal job cleanup so retained bytes cannot
  be orphaned. Cancellation or failure after carrier loss discards that exact inactive staging.
- `fail-closed` behavior is unchanged: carrier loss retires and discards the partial, fences the
  attempt, blocks replacement, and requires explicit recovery policy. No route-class exception is
  introduced.
- The default-off qualification seam gains `--qualify-route-stop-file-bytes N`. When present, the
  byte threshold can arm only on an incoming auxiliary transfer of that exact complete size. The
  value must exceed `--qualify-route-stop-after-bytes`; zero/default preserves the historical first
  eligible receive. This is laboratory control, not product routing policy.

No sync frame, feature bit, authority format, content identity, range encoding, or default failover
policy changes.

## Evidence

The owned subscriber test first commits a manifest for a signed generation-4 successor, starts its
bounded range on one auxiliary carrier, writes exactly half the canonical bundle into the attempt
inode, and removes that carrier. It proves duplicate loss is inert, stale old offers and terminals
are rejected, a replacement without range negotiation is refused without mutating the prefix, and
a distinct authenticated carrier receives the unchanged plan under a fresh attempt and FileId from
the exact retained offset. Final artifact equality, accepted HEAD generation, zero active signed
attempts, zero retries, and exact retained/resumed equality are required.

A subsequent deterministic extension loses the replacement after the inherited 50% prefix grows
to 75%, then moves that same inode to a third distinct carrier under a third attempt and FileId.
Duplicate observations at both loss boundaries and stale offers/terminals from both retired
carriers are inert. Cumulative retained and resumed bytes equal 50% plus 75%; requested-object and
ordinary range-retry counts do not change; final artifact and signed-attempt-journal checks remain
identical. This closes repeatability in the owned service boundary, not genuine route timing.

The genuine `sync-file-range-route-loss` gate passes from source revision
`21c9814af7e59ddf9699fa909928403ecf5808ef` with product revision `rev0045` and binary SHA-256
`e79a4388fc967b082ff743bf62bf49483688af3546afbd44f777afedc40bd82e`:

| Route | Compact proof | Fault = retained = resumed | Loss / reassign / stale / recovery | Discard / fallback | Pair span |
|---|---|---:|---:|---:|---:|
| direct UDP | `pair.urbhf0je` | 283,797 bytes | 1 / 1 / 1 / 1 | 0 / 0 | 422,150,781,688 ns |
| forced TCP | `pair.n76biwao` | 293,394 bytes | 1 / 1 / 1 / 1 | 0 / 0 | 495,698,530,166 ns |

Each cell first activates a genuine 4 MiB basis, then transfers the successor's 786,496-byte
manifest without consuming the size-selected fault. The exact 1 MiB range loses one carrier after
at least 256 KiB, moves to the other ready native carrier under a distinct attempt, receives only
the suffix, reuses 3 MiB of verified basis, reconstructs the same 4 MiB generation 2, accepts its
HEAD last, and explicitly activates it. The stopped savedata identity returns within one restart
budget. Both 155,648-byte compact exports independently pass the strict verifier.

## Consequences

Available-policy native range synchronization no longer retransmits an exact positive prefix merely
because its auxiliary carrier died. Range work now has the same stale-safe attempt boundary as
whole-object continuation while preserving range reconstruction and authority ordering.

This does not resume a Tox handle, survive IoTox process or guest restart, retain bytes across a
primary-authority epoch loss, reuse bytes for a distinct explicit job, combine multiple sources,
stripe one range concurrently, authorize cross-class failover, or prove latency/throughput gains.
ADR 0232 subsequently qualifies a genuine two-loss repetition over direct UDP and forced TCP.
ADR 0233 qualifies a separate one-loss row after at least 15/16 of the range. Three-plus,
repeated-late, and final-chunk races remain separate science. ADR 0228's fail-closed I2P prefix
discard and explicit fresh-job recovery remain unchanged.
