# No Appeal on File

## Poem

LOWER LAYER
appeal/notice.txt | THIS IS AN APPEAL
appeal/grounds.txt | THE RECORD IS WRONG
appeal/statement.txt | I WAS HERE

UPPER LAYER
appeal/status.txt | NO APPEAL ON FILE
appeal/.wh..wh..opq | 0 BYTES

MERGED FILESYSTEM
appeal/status.txt | NO APPEAL ON FILE
appeal/notice.txt | NOT FOUND
appeal/grounds.txt | NOT FOUND
appeal/statement.txt | NOT FOUND
appeal/.wh..wh..opq | NOT FOUND

IMAGE MANIFEST
lower layer | REQUIRED
upper layer | REQUIRED

## Disclosure

Disclosure: P0004-D002 / rev0068 is a machine-drafted OCI image-layout poem. Its artifact is the deterministic local layout at `poems/P0004/artifact/d002/image`. The lower layer contains three separate appeal records. The upper layer adds `appeal/status.txt` with `NO APPEAL ON FILE` and then, as its last tar member, adds the empty opaque-whiteout entry `appeal/.wh..wh..opq`.

Under OCI Image Specification v1.1.1, an opaque whiteout hides every lower-layer child of its directory. Whiteouts apply only to lower layers, so the same upper layer's status file survives even though its tar entry precedes the opaque marker; the marker itself is hidden after application. The merged filesystem therefore retains `NO APPEAL ON FILE` while none of the three lower appeal records or the deletion marker remains visible. The image manifest still requires both content-addressed layers in stack order.

The artifact is deliberately non-runnable and closed-world: its blob directory contains exactly the manifest, config, lower layer, and upper layer reachable from `index.json`, with no unreferenced side content. `tools/check_oci_whiteout_poem.py` validates both D001 and D002 without extracting layer members into the host, applies whiteouts to pre-layer state before same-layer additions, checks marker-order independence, and rejects extra blobs for this poem contract. These mechanics are not evidence of poetic quality. No current/live status, observation, or reading is claimed.

P0004-D001 received a later-turn `revise_not_promote` review because its page largely restated a single explicit-whiteout demonstration. D002 is same-turn unjudged, not admitted, not evidence-ready, not an anthology candidate, and not a reader response. P0003-D004 remains byte-frozen as an internal candidate. P0002-D010 remains the first external disclosed-reader target with zero logged responses.
