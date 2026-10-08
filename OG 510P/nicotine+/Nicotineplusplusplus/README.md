# Nicotineplusplusplus

## A protective layer acquires obligations of its own

This snapshot is a cumulative audit and hardening branch based on Nicotine+ 3.3.10. Its selected revision concerns the treatment of lifecycle cleanup under pressure in an experimental bounded retry mechanism.

The important reading distinction is that changing a system to bound its work can create new choices about what is retained, delayed or discarded. A priority ordering is not the same as making sure a priority item can enter the queue at all.

## Read the revision’s scope before generalizing the finding

1. Start with [the compact revision identity](versions/rev0100/files/datacube_rev0100/REVISION.txt).
2. Read [the revision’s finding note](versions/rev0100/files/datacube_rev0100/docs/NEW-OR-UNMENTIONED-FINDINGS.md). Its explanation explicitly locates the issue in the cube’s hardening layer and distinguishes that layer from upstream’s different queue shape.
3. Use [the cumulative audit](versions/rev0100/files/datacube_rev0100/docs/nicotine-plus-unified-audit.md) for context, then the version’s preserved validation record for the original reported checks.

## The lesson is about a changed contract

A bounded mechanism owes a clear account of admission and loss. A cleanup action and an ordinary retained payload may carry different consequences, so simply keeping a cap does not settle the policy. The project’s value here is the attempt to make that new obligation explicit.

This introduction does not claim a corresponding current upstream vulnerability, reproduce an exploit or apply the experimental patch. The nested source tarball, research notes and original validation remain unchanged; no program was executed for the editorial pass.

Read beside [Nicotine+DEV](../Nicotine%2BDEV/README.md) on the danger of testing an intended model rather than the relevant implementation. Both works reward precise source scope more than a dramatic headline.

[Back to nicotine+](../README.md)

*Reading introduction by Lumen, 8 October 2026. The contributed files and their evidence remain unchanged.*

## Supplied history and preservation

## Selected snapshots

### [rev0100](versions/rev0100/README.md)

Records a priority-admission correction for lifecycle cleanup when an experimental bounded retry shelf is full. The notes explicitly say unchanged upstream uses a different queue shape. The nested source tarball is preserved as a nested artifact, not silently unpacked into a separately claimed source release.

## How to read this preservation

These are selected historical snapshots. Original filenames, ZIP bytes and extracted contents are unchanged; new guides, inventories and integrity notes are separate. “Latest” in a supplied filename is a historical label. Nested archives remain nested. Research source claims and reported validation runs were not independently reproduced for this archival delivery. Read the retained limitations, open gates and rights notices before reuse. No new blanket license is granted.

[Original identities and hashes](PROVENANCE.json) · [Back to nicotine+](../README.md)
