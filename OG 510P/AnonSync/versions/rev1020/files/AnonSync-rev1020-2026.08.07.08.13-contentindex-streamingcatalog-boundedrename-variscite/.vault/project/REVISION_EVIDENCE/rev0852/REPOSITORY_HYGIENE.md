# Rev0852 repository hygiene

The active release projection contains **276 files / 17,622,237 bytes**. The
source delta is confined to **10 active files**, with **600 insertions** and
**129 deletions**. Bundled third-party source is unchanged.

The exact active patch applies to the sealed rev0851 parent and reproduces all
**276/276** active files by path, byte count, and SHA-256. Generated build trees,
objects, archives, executables, VCS metadata, symlinks, and Python bytecode are
excluded from the release inventory. The final manifest is an exact inventory
of every package file other than the manifest itself.

The release still carries substantial historical evidence: the evidence tree
contains thousands of files and is materially larger than the active delta.
That supports lineage verification but amplifies routine copying and package
inspection. Future handoffs should preserve immutable revision hashes and
selective evidence indexes without recursively expanding every old execution
artifact.

The principal build amplifiers remain:

- `src/sync_domain.cpp`: **15,287 lines**;
- `src/sync_domain_selftests.cpp`: **9,348 lines**;
- `CMakeLists.txt`: **2,698 lines**.

A dependency-light policy-boundary change still required a broad all-target
rebuild, and the monolithic core dominated clean-build wall time. The next
refactors should reduce translation-unit fan-out and replace repetitive
registration text with checked generated inventories. Source-spelling audits
remain justified for dangerous primitive ownership—as the process-topology
failure demonstrated—but should be removed when an equivalent typed boundary or
behavioral oracle exists.
