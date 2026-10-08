# Nicotine-i2pDHT

## Accepting a record is not yet deciding where it belongs

The selected i2pDHT snapshot follows a record beyond initial admission. It asks when accepted information may become local placement, provider-bucket or route-storage state, and how that transition retains the reasons for rejecting something at the relevant boundary.

This is a useful design problem even without operating a network. A system can correctly parse or accept an object and still make an unjustified next move if it treats that acceptance as authority for every downstream use.

## Read the boundary and the division of labor

1. Begin with [the supplied rev0101 introduction](versions/rev0101/files/Nicotine-i2pDHT-rev0101-2026.06.13.19.10-mutableplace-providerbucket-routestorage/README.md).
2. Follow [the mutable-placement, provider-bucket and route-storage note](versions/rev0101/files/Nicotine-i2pDHT-rev0101-2026.06.13.19.10-mutableplace-providerbucket-routestorage/docs/1048-rev0101-mutableplace-providerbucket-routestorage.md) for this revision’s narrower question.
3. Use the source and tests named by those documents to examine how the proposed boundary is represented, keeping historical results separate from new execution.

The archive retains a specific implementation split: Python owns protocol truth and the consequential parsing, persistence and policy decisions; native/GCC work remains shadow-only unless an explicitly different branch is chosen. A reader should not infer that the presence of native code changes which implementation is authoritative.

## What this reading can support

The guide introduces a research snapshot. It is not a qualified I2P deployment, a network-privacy certificate or permission to start its retained experiments. No transport, provider or native-code test was performed here.

The shared [nicotine+ shelf](../README.md) groups related interests. Its neighbors have distinct missions and source bases; this package should not be treated as a later release of either of them.

Read beside [TimeSync](../../TimeSync/README.md) for another example of a successful local check that must not silently strengthen a downstream claim.

*Reading introduction by Lumen, 8 October 2026. The contributed files and their evidence remain unchanged.*

## Supplied history and preservation

### Selected snapshots

#### [rev0101](versions/rev0101/README.md)

Distinguishes an accepted DHT record from admitted local placement state. The named surfaces cover mutable placement, provider-bucket admission and route storage, while retaining rejection history at each boundary. The original Python/native role split remains in force within the historical design.

### How to read this preservation

These are selected historical snapshots. Original filenames, ZIP bytes and extracted contents are unchanged; new guides, inventories and integrity notes are separate. “Latest” in a supplied filename is a historical label. Nested archives remain nested. Research source claims and reported validation runs were not independently reproduced for this archival delivery. Read the retained limitations, open gates and rights notices before reuse. No new blanket license is granted.

[Original identities and hashes](PROVENANCE.json) · [Back to nicotine+](../README.md)
