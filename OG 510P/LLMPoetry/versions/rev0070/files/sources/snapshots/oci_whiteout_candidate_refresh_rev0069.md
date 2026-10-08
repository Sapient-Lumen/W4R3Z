# OCI opaque-whiteout candidate refresh — rev0069

Sources: Open Container Initiative Image Specification v1.1.1, `layer.md` and `manifest.md`.  
Accessed: 2026-06-18T15:08:00-04:00.  
Web evidence references: `turn943141view0`, `turn943141view1`, `turn943141view3`.

This is a bounded excerpt note, not a full or complete capture of the specifications.

Bounded facts used:

- Whiteouts apply only to lower/parent layers and disappear from the resulting filesystem.
- `.wh..wh..opq` hides every lower child and descendant of its directory.
- An opaque whiteout is applied before same-layer additions regardless of tar-member order.
- Manifest layers are listed from base to upper stack order, and the final filesystem must match application of those layers.

Candidate implication: D002’s same-layer `NO APPEAL ON FILE` survives while the lower appeal records disappear; both layer descriptors remain required. Conformance is not reader evidence or a quality proof.
