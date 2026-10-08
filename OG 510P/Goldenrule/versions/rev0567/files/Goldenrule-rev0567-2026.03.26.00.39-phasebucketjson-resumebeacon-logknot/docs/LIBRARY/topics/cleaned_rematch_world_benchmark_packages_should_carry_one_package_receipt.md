# Cleaned rematch-world benchmark packages should carry one package receipt

The archive can now prove that a rematch-world benchmark publication was rebuilt correctly and cleaned correctly before packaging.
What was still missing was one compact boundary proof that the tree the inheritor actually zips is still aligned with that chain while respecting archive-size discipline.

## Why this matters

A future inheritor should be able to cite one small package receipt that says:

1. the publication chain receipt is ready,
2. the post-prune audit still says the tree is safe to zip,
3. the compiled artifact digest agrees across those retained receipts,
4. the tree is still PDF-free,
5. `examples/scratch` is empty,
6. the scratch manifest has no active carry-over items, and
7. the current retained footprint is measured without opening a broader report family.

Without that boundary receipt, the archive still relies on an operator remembering both the cleanup rules and the size posture right before cutting a revision zip.

## What to keep

Keep one small package receipt that hashes the chain receipt and the post-prune audit, records the current retained-tree footprint, and exposes the reports bucket as the main growth surface.
That receipt should measure the tree with its own output path excluded so the size profile stays stable across rebuilds.

## Operational rule

Build the package receipt after the chain receipt passes and before cutting the next revision zip.
If the package receipt is not ready, do not package the tree yet; repair the failed hygiene check first and rebuild the compact boundary proof.
