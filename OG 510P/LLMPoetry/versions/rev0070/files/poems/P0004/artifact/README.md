# P0004 OCI artifacts — rev0069

D001 and D002 remain independently verifiable deterministic OCI image layouts. D002 is byte-frozen at its rev0068 artifact tree: `poems/P0004/artifact/d002`.

Use `python tools/check_oci_whiteout_poem.py .` for descriptor, tar, whiteout, merged-state, blob-closure, deterministic rebuild, and path-containment checks. The checker performs no host extraction.

The shared safety module is `tools/oci_path_safety.py`. General OCI permits unreferenced blobs; D002’s closed-world blob rule is project-local and deliberately stricter.
