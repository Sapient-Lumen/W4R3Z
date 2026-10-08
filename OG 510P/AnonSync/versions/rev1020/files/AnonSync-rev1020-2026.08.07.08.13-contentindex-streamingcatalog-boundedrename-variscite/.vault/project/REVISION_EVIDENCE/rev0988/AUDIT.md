# Rev0988 audit

## Defect

Rev0987 reloaded the complete folder catalog three times for every successful metadata-only dematerialization. At the production frontiers of 4,096 remote effects and 1,000,000 retained paths, one pass could request 12,288 complete catalog projections.

## Correction

Rev0988 adds a deferred-transaction, one-path `FolderCatalogPathCutpoint` that binds current folder/catalog/selection metadata and zero or one exact primary-key entry. Planning, pre-unlink, and post-unlink reproof use that cutpoint. Complete catalog observations remain global pass authority. The current-format catalog row decoder is shared by complete and targeted readers.

## Executable proof

The focused folder-owner suite passes 532 checks. Its eight-file trace proves 24 exact path reads—three per successful effect—while complete catalog projections remain pass-bounded. The selective-sync audit passes 52/52, the targeted-cutpoint audit 24/24, and the structural authority audit 425/425.

## Nonclaim and next seam

The targeted cutpoint does not recompute the aggregate catalog digest, prove unrelated rows, weaken rooted or payload authority, qualify a million-path workload, or remove the replica owner’s remaining O(history) per-effect causal reconstruction. A transactionally exact targeted replica path/operation cutpoint is the next adjacent scaling seam.
