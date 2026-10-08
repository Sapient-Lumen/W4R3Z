## Resilio seam evaluation — pathname dialect, filesystem projection, and loss boundary truth

Current official Resilio Sync docs still expose another strong non-clone seam around **pathname projection truth**.
The important current facts are not subtle:

- `Conflict files in Sync` still says case-insensitive targets can turn same-spelled names into `.Conflict` files, decomposed UTF symbols can collide even when the human sees the same glyph, prohibited filesystem symbols can be rewritten on Windows, and linked junctions can produce conflict cascades.
- `My files don't sync` still says Sync expects UTF-8 filenames, path or filename length can exceed platform ceilings, and mixed-system encoding or path-length mismatch is a first-class reason for sync failure.
- `Unsupported asterisk (*) characters at the end of file/folder names` still says certain trailing-asterisk names without extensions are invalid and may even be interpreted as system data.
- `Soft links, hard links and symbolic links` still says Windows does not support soft links, junctions, hard links, or symbolic links in Sync, while UNIX can synchronize the symbolic-link object but not automatically sync the target folders behind those links.

This is strong semantic candor.
It is also exactly why AnonSync should not clone the present page contract.
One ordinary answer to `will this pathname survive intact across this cohort, what kind of object will it become on arrival, and what loss or rewrite risk am I accepting?` still depends on combining troubleshooting prose, conflict guidance, unsupported-name notes, and link-object behavior pages.

So this tranche freezes a stronger replacement line: **visible pathname, canonical identity, normalization class, case behavior, symbol projection, length ceiling, object-kind projection, and rewrite/loss boundary become separate modeled truths.**

That is why this revision adds five more first-class pages: **Path-projection contract sheet**, **Path-equivalence review**, **Projection-capability proof**, **Filesystem-dialect timeline**, and **Path-projection lineage receipt**.
