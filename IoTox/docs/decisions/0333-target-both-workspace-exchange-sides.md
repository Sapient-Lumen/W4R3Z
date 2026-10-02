# ADR 0333: Target both workspace-exchange sides by projection identity

- Status: accepted, implemented, and post-exchange Sandwurm-qualified
- Date: 2026-09-04

## Context

ADR 0332 qualifies one whole-VMM cut after the signed workspace enters `pending-exchange`. Its
accepted run retained the exact prior projection, pending journal, and no stage after reboot. That
is the pre-exchange durable side. Merely waiting for the same phase again cannot target the other
linearization: the journal remains pending while the complete projection is built, while the Linux
directory exchange occurs, and until the stable workspace record commits.

The staging pathname alone is also insufficient. Before `RENAME_EXCHANGE` it names the new pending
projection; afterward it names the old active projection. A timing label such as “projection stage”
would conflate those opposite filesystem truths.

## Decision

Upgrade the qualification instrument to v3 and classify the boundary from two independent pieces of
durable product state:

1. Decode the exact workspace record header using the frozen C++ encoding
   `stable=1,pending-exchange=2` and require raw byte 2.
2. Read the workspace's active and pending manifest digests from their fixed record offsets.
3. Read the visible worktree's canonical `.iotox-conflicts/.iotox-projection` marker and classify it
   against those two identities.
4. Double-read the workspace record around the marker read and arm only if both snapshots are equal.
   This refuses a concurrent transition to stable rather than assigning its marker to stale state.
5. Name two exact targets: `pre-exchange-pending` requires the visible marker to identify the active
   manifest; `post-exchange-pending` requires it to identify the pending manifest.
6. Carry the requested boundary, projection orientation, stage presence, raw phase byte, and phase
   encoding through the guest arm and host campaign. The v3 verifier cross-checks all of them while
   retaining read compatibility for the accepted v2 proof.
7. On recovery, require a valid pending or stable workspace and a matching canonical projection
   marker before starting any Agent. A post-exchange cut must expose the completed follower tree;
   reverting to prior after the projection exchange's `syncfs` and parent-directory `fsync` is a
   qualification failure, not an allowed old-side result.

The Sandwurm lab exposes the two cells explicitly:

```sh
./tools/iotox-sandwurm-lab.sh up-sync-power-cut pre-exchange
./tools/iotox-sandwurm-lab.sh up-sync-power-cut post-exchange
```

Both remain networkless two-epoch exact-VMM cuts. The post-exchange cell has its own NixOS
configuration, task identity, and proof root so evidence cannot be confused with the pre-exchange
campaign.

## Consequences

The observer now targets a semantic linearization rather than hoping a polling interval corresponds
to one. Deterministic fixtures cover v2 compatibility plus v3 pre- and post-exchange proof, reject a
pre-exchange projection presented as post-exchange, and retain the raw-phase regression from ADR
0332.

This does not manufacture a crash point inside the product or pause the Agent. Failure to observe the
short window times out closed; no product hook was needed.

Source-linked run `nhjaizl2` at commit
`bb0dc88b20ed1170aea9e236a3fb15d14e3b9e19` observed pending orientation and a present stage between
equal raw-byte-2 workspace snapshots. The exact VMM exited 137 without cooperative control. After a
second-kernel boot of the crash lineage, all offline views were completed; C still carried pending
byte 2, pending orientation, and the old stage. Startup converged and repaired three branches per
node in 1.631 seconds. The complete campaign took 477.636 seconds.

Compact proof `.sandwurm/exports/sync-power-cut/run.nhjaizl2` independently verifies. Its manifest
SHA-256 is `f163743ff7c4a8e82232e78b9ba6efaa29dcd0b0bffa483115331d2a5d8e3ea4`.

Both cells now pass, but they still cover only the workspace directory-exchange pair. Object
installation, branch publication, witness transitions, corrupt records, open descriptors,
repeated/random cuts, near-ceiling populations, physical power removal, and dishonest storage remain
separate gates.
