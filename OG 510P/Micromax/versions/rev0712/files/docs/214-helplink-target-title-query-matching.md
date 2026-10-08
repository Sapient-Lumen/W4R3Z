# Rev272 — docs-link queries can match target doc and target heading titles

Rev270 taught docs-link queries to reuse the visible **source-side** context users
already had on screen: the nearest heading breadcrumb and the `Docs` / `Files` /
`External` kind label.

Rev272 closes the matching **destination-side** gap.

Filtered docs-link queries can now also reuse:

- the target doc's human title
- the target heading's human title when the link points at a fragment

That means generic labels like:

- `Metadata note`
- `Image anchor note`

can still be found with more human queries such as:

- `helplinkpick image metadata`
- `helplinkpick hidden image metadata anchor`
- `helpnavpick image metadata`

without widening the visible row shape beyond `[label kind target info]`.

## Why this was the next honest step

Micromax already has the truth needed for this search path:

- `_scan_docs()` already reads human doc titles from the docs tree
- docs-link targets are already classified into local-doc / file / fragment forms
- docs/help heading scans already resolve stable fragments for navigation

The missing piece was only query ranking. Users and future LLMs could often
remember the destination doc or destination heading better than the link's local
label, but `helplinkpick` still mostly searched the label plus raw target path.

## What changed

- `_helplink_query_meta(row)` now also appends:
  - the resolved target doc title when a local docs target is available
  - the resolved target heading title when a fragment target is available
- the new destination metadata is cached through tiny docs/title helpers instead
  of widening picker rows or adding a richer docs AST
- `helpnavpick` inherits the behavior automatically because its link half already
  starts from `help_link_rows(query)`

## Focused coverage

- `tests/test_editor_helplinkpick.py`
- `tests/test_editor_helpnavpick.py`
- `tests/test_mxcontext.py`

## Tiny fixture additions

`docs/98-help-browser.md` now carries two deliberately generic link labels:

- `Metadata note` → `177-docs-cues-image-metadata.md`
- `Image anchor note` → `177-docs-cues-image-metadata.md#image-metadata-anchor`

and `docs/177-docs-cues-image-metadata.md` now also includes the small explicit
heading `Hidden image metadata anchor {#image-metadata-anchor}` so the archive
has stable target-heading data for future tests, future UIs, and future LLMs.
