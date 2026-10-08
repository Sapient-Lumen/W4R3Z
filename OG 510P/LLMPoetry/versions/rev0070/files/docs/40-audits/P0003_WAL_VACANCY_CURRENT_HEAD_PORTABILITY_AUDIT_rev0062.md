# P0003 WAL Vacancy / Current-Head Portability Audit — rev0062

## Priority decision

The cube's most dangerous unfinished dependency was external: P0002-D010 still needs a real reader. Waiting cannot honestly produce that evidence, but it also should not freeze creation or invite fabricated responses. P0002-D028 therefore stays terminal and the reader pilot stays open while a separate poem family begins.

## Substantive forward movement

`P0003-D001` is not a registry exercise. The revision packages a real SQLite database and required WAL sidecar. The main file contains a sparse vacancy report. A later committed transaction in the WAL contains the fuller poem. The builder verifies that the main database SHA-256 is identical before and after the commit, before checkpoint. The checker then proves, on disposable copies, that the main file alone reads the base report and the pair reads the committed poem.

This makes absence, residue, adjacency, and commitment operative in the artifact. Whether that pressure survives as poetry is deliberately unresolved until a later-turn cold review.

## Severe architectural fault corrected

Three current-state validators had encoded P0002 as the permanent global poem family. They treated a legitimate new poem head as invalid even when STATE, release paths, and provenance were coherent. That coupling would have forced future work either into endless P0002 successors or into validator bypasses.

Rev0062 resolves the active poem and draft suffix from `STATE.current_head`, checks that poem's own metadata/index/resources, and leaves P0002 candidate/fallback gates historical. The reader target may remain P0002-D010 while the provenance head is P0003-D001.

## Parent-chain defect corrected

A second audit pass found that the generated revision receipt and release manifest still named `rev0059` as the parent even though this work began from the user-supplied `rev0061` archive. The lineage arrays already contained the correct `rev0061 -> rev0062` edge, so the mismatch could have passed while two revisions were effectively omitted from the release-facing provenance. Rev0062 now records the exact rev0061 input filename and SHA-256, and `check_revision_lineage_freshness.py` blocks any future disagreement among the lineage entry, revision receipt, and release manifest.

The same pass removed two other false-current labels: the P0002-D028 judgment is now explicitly the previous-head judgment, and the P0002-D010 reader kit is validated as the active evaluation target rather than being forced to equal the unrelated global provenance head.

## Extracted-package defect corrected

Fresh extraction exposed a manifest/package mismatch invisible in the work tree: `build_manifest.py` admitted a root-level `__pycache__` entry while `package_release.py` omitted it. The resulting ZIP was intact but failed its own manifest-coverage gate after extraction. Manifest construction and validation now share the packager's root-and-nested bytecode-cache exclusion rule; generated Python bytecode is neither release content nor provenance.

## Boundaries

- P0003-D001 is same-turn unjudged; there is no cold review and no D002.
- P0002-D028 remains terminal; there is no D029.
- P0002-D010's response log remains empty; no human evidence was fabricated.
- WAL correctness proves storage behavior only, not poetic quality.
- The packaged originals should not be opened normally; validation uses disposable copies to avoid checkpoint mutation.

## Next

Cold-review P0003-D001 in a later turn without checkpointing the packaged originals, while keeping PILOT-0048 open for one real disclosed P0002-D010 response; do not create P0002-D029.
