# Rev1003 authority incidents

Only the final `/root/anonsync-rev1003-authority` source and its rebuilt GCC/Clang trees are release authority.

- A cloudtainer remount removed the first unsealed worktree and build after nine passing product tests. Those results were discarded. The source was reconstructed from the exact sealed rev1002 bytes plus the externally retained binary-aware patch.
- A stale `/home/oai/share/phenakite-*` validator and build tree resurfaced during final work. It was terminated and removed; none of its results are used.
- A raw pathname-carried SHA-state prototype was retained only as rejected external evidence and is absent from the release source.
- The first focused sanitizer invocation named a target that the product dependency graph had not built. The target was built explicitly and all focused sanitizer suites then passed; the missing-target invocation is excluded.
- A preseal registry run exposed a stale rev0999 lexical oracle expecting the old temporary predecessor copy. The oracle was corrected to require the stronger current lifetime proof, and the complete final 286-test registry passed.
