# Command-stream isolation

During rev0826, unrelated temporary-root build streams repeatedly appeared in
the same cloudtainer and one shared pointer was overwritten. They were treated
as untrusted rather than merged.

Release controls:

- source pinned to the private absolute root `/tmp/as826-authority-8X6qxyHq/work/AnonSync`;
- exact parent pinned to `/tmp/as826-authority-8X6qxyHq/parent/AnonSync`;
- all observed external rev0826 build process groups terminated before sealing;
- active source compared against parent and required to equal the exact nine-file allowlist;
- source patch generated from a fresh Git import of the exact parent;
- patch applied to a second fresh parent import and all 189 active files compared by byte count and SHA-256;
- build directories and evidence scratch remain outside the source tree; and
- package verifier rejects build trees, binaries, VCS metadata, and Python caches.

The aggregate CTest interruption is retained as evidence and not rewritten as a
pass. Complete inventory coverage is the union of three disjoint passing ranges.
