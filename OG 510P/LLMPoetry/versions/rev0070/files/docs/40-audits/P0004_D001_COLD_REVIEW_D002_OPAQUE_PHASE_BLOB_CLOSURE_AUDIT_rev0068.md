# P0004 D001 Cold Review, D002 Opaque Phase, and Blob-Closure Audit — rev0068

## Substantive result

P0004-D001, **Must Also Be Hidden**, received a delayed `revise_not_promote` review. Its OCI object was valid, but the page nearly exhausted the single explicit-whiteout mechanism, the objection was generic, and disclosure made the poem read like a solved demonstration.

P0004-D002, **No Appeal on File**, replaces one named deletion with an opaque directory event. The lower layer contains three independent appeal records. The upper layer first adds `appeal/status.txt` with `NO APPEAL ON FILE` and places the zero-byte opaque marker `appeal/.wh..wh..opq` last in the tar. The merged filesystem retains the same-layer status while every lower appeal record and the marker disappear. Both layer blobs remain manifest-required. D002 is same-turn unjudged.

## Correctness defect found

The incoming OCI checker applied tar entries sequentially. For an opaque marker appearing after a same-layer file, that model could erase the file just added. OCI semantics instead scope whiteouts to lower layers and require whiteout processing before same-layer additions regardless of archive order. The old checker therefore modeled a plausible but wrong filesystem transition for opaque layers.

## Refactor

`tools/check_oci_whiteout_poem.py` now applies each layer in two phases: first all whiteouts to the pre-layer state, then all ordinary same-layer entries. Self-tests cover a last-position opaque marker and explicit remove-then-re-add behavior. The builder and checker now support both the historical D001 schema and the D002 opaque schema, so D001 remains independently reproducible.

The checker also enforces a project-local closed-world blob contract: D002's blob directory must equal the config, manifest, lower-layer, and upper-layer descriptors reachable from `index.json`. General OCI layouts may contain additional blobs; this stricter LLMPoetry rule prevents hidden side-content from riding alongside the poem artifact.

## Boundaries

- D001's exact draft, packet, metrics, OCI spec, receipt, layout index, layout marker, and rendered surfaces remain byte-preserved.
- D002 has no same-turn judgment and is not admitted, evidence-ready, or an anthology candidate.
- P0003-D004 remains byte-frozen as an internal candidate.
- P0002-D010's reader-response log remains empty.
- Specification conformance, checker correctness, and blob closure are not literary quality evidence.
