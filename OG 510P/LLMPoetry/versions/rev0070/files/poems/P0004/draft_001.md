# Must Also Be Hidden

## Poem

LOWER LAYER
appeal/objection.txt | I OBJECT TO THIS RECORD

UPPER LAYER
appeal/.wh.objection.txt | 0 BYTES

MERGED FILESYSTEM
appeal/objection.txt | NOT FOUND
appeal/.wh.objection.txt | NOT FOUND

IMAGE MANIFEST
lower layer | REQUIRED
upper layer | REQUIRED

## Disclosure

Disclosure: P0004-D001 / rev0067 is a machine-drafted OCI image-layout poem. Its artifact is the valid local layout at `poems/P0004/artifact/d001/image`. The lower layer adds `appeal/objection.txt` containing `I OBJECT TO THIS RECORD`. The upper layer adds only the empty regular file `appeal/.wh.objection.txt`. Under the OCI Image Specification, that `.wh.` entry is a whiteout for the lower-layer objection; applying it removes the objection from the merged filesystem, and the whiteout marker itself must also be hidden. The final merged view therefore contains neither path, while the image manifest still references both content-addressed layer blobs in stack order.

The artifact is deliberately non-runnable. No current/live container status or remote registry observation is claimed. `tools/check_oci_whiteout_poem.py` verifies descriptor sizes and SHA-256 digests, layer order, tar-member safety, the exact lower-layer statement, the zero-byte upper-layer whiteout, and the final merged absence without extracting either tar into the host filesystem. P0004-D001 is same-turn unjudged, not admitted, not evidence-ready, not an anthology candidate, and not a reader response.

The source pressure is bounded to OCI Image Specification v1.1.1: layer removals are represented by whiteout entries; a whiteout is an empty file named with `.wh.` plus the deleted basename; it applies only to lower layers and is hidden after application; manifests list layers from base upward; and image-layout blobs are addressed by the digest of their contents. The release page identified v1.1.1, dated March 3, 2025, as the latest release when checked on June 18, 2026. Mechanism correctness is not poem quality. P0003-D004 remains byte-frozen as an internal candidate, P0002-D010 still has zero real-reader responses, and neither dependency is rewritten as evidence here.
