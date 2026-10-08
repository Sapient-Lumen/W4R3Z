## Resilio seam evaluation — transfer cost, resend geometry, and splittability ceiling

Current official Resilio Sync docs still expose another strong non-clone seam around **transfer-cost truth**.
The important current facts are not subtle:

- `When a file changes, does Resilio Sync transfer the entire file again, or just the part that's changed?` still says Sync splits files into pieces from 32KB up to 2MB and normally transfers only changed pieces.
- That same current article still says if an edit shifts all pieces, the whole file will be re-synced.
- That same current article still says the stronger `avoid whole-file resend even in shift cases` answer belongs to the separate Sync Business diff-delta lane rather than the ordinary baseline.
- `What happens when file is renamed` still says rename reuse depends on finding the same hash in Archive and that without Archive enabled the file will be re-synced again.
- `File download priority` still says priority can reorder active downloads by modification time or file size, can suspend lower-priority transfers immediately, but strictly follows prioritization rules only for files split in pieces during transfer.
- That same priority article still says queue rebuilds and the 50k active-file ceiling can change performance independently of the actual byte-cost class of any one file.

This is strong operational candor.
It is also exactly why AnonSync should not clone the present page contract.
One ordinary answer to `how many bytes will actually move here, why did this resend in full, and did priority change order or network cost?` still depends on combining a FAQ article, a rename/Archive article, and a newer priority article.

So this tranche freezes a stronger replacement line: **byte-cost class, rename-reuse basis, queue order, and splittability ceiling become separate modeled truths.**

That is why this revision adds five more first-class pages: **Transfer-cost contract sheet**, **Resend-geometry review**, **Byte-cost proof**, **Transfer-shape timeline**, and **Transfer-cost lineage receipt**.
