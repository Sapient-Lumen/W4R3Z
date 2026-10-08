# Cleaned rematch-world benchmark publications should carry one chain receipt

The archive now has several compact receipts for the first endogenous rematch-world benchmark path.
That is already much smaller than retaining broad sidecar reports, but it still leaves one final inheritor burden: knowing which tiny receipts together prove the publication was safe to keep and safe to zip.

## Why this matters

A future implementor should be able to cite one compact end-to-end receipt that says:

1. the standing seed still rebuild-matches its copied source handoffs,
2. the compiled artifact preserved those copied sections unchanged,
3. the retained publication spine still rebuild-audits cleanly without a retained fill patch, and
4. post-prune cleanup left the durable spine intact while removing exit-ready scratch.

Without that summary layer, the archive still depends on remembering a four-receipt chain by name.

## What to keep

Keep one small chain receipt that hashes those four checkpoint receipts and records the final compiled artifact digest.
That receipt should summarize the covered question-id span and the cleaned-tree posture, but it should cite the underlying checkpoint receipts instead of duplicating their detailed rows.

## Operational rule

Build the chain receipt after the post-prune audit passes and before cutting the next revision zip.
If the chain receipt is not ready, do not package the tree yet; restore the first broken checkpoint and rebuild the compact proof chain first.
