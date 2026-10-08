# Correction history retained

1. The mutable worktree initially passed the focused heartbeat tests.
2. A delayed unintegrated delivery-protocol branch subsequently reintroduced
   protocol files and CMake registrations after a residue scan.
3. Further delayed writes contaminated the public SQLite-owner header and then
   the implementation, producing an undeclared-type compile failure once the
   protocol files were removed.
4. Rather than patching around uncertain partial writes, publication moved to a
   new isolated tree reconstructed from the verified rev0870 parent.
5. The intended nine-file heartbeat delta was replayed, and every validation
   lane was rerun against that exact isolated source.

The failed mutable worktree is not used as lineage. This record is retained
because discovering and correcting assurance-surface drift is part of the
revision's audit work, not an embarrassment to erase.
