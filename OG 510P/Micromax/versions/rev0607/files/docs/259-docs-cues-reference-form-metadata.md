# Rev317 — docs-cues reference-form metadata for links and images

Rev315 and rev316 made visible docs/help link/image **source kinds** explicit,
but they still kept all reference-style source in one coarse bucket.

That was enough to answer:

- is this visible token inline or reference-style?
- is this visible token an autolink or footnote ref?

It still was not enough to answer:

- is this reference link/image spelled as a full reference, collapsed reference,
  or shortcut reference?
- which visible rows still depend on shortcut-style source rather than explicit
  second labels?
- can an offline consumer inspect exact CommonMark-ish reference spelling
  without reparsing brackets by hand?

Rev317 keeps the contract tiny and source-view-first while answering those
questions directly.

## New per-entry field

Each visible docs/help `link_entries` and `image_entries` item now also carries
`reference_form`:

- `""` for non-reference entries
- `"full"` for `[label][id]` / `![alt][id]`
- `"collapsed"` for `[label][]` / `![alt][]`
- `"shortcut"` for `[id]` / `![alt]`

This stays deliberately tiny:

- it reuses the existing balanced-bracket helpers already used by the docs/help
  matcher
- it does not add a richer markdown AST
- it stays local to visible source-view inspection

## New row-local slices

Visible rows now also expose:

- `full_reference_link_entries`
- `collapsed_reference_link_entries`
- `shortcut_reference_link_entries`
- `full_reference_image_entries`
- `collapsed_reference_image_entries`
- `shortcut_reference_image_entries`

Rows also report the matching counts:

- `full_reference_link_count`
- `collapsed_reference_link_count`
- `shortcut_reference_link_count`
- `full_reference_image_count`
- `collapsed_reference_image_count`
- `shortcut_reference_image_count`

## New top-level summary fields

The whole snapshot now also reports:

- `full_reference_link_rows`
- `collapsed_reference_link_rows`
- `shortcut_reference_link_rows`
- `full_reference_link_count`
- `collapsed_reference_link_count`
- `shortcut_reference_link_count`
- `full_reference_image_rows`
- `collapsed_reference_image_rows`
- `shortcut_reference_image_rows`
- `full_reference_image_count`
- `collapsed_reference_image_count`
- `shortcut_reference_image_count`

## Example shape

```python
{
  "rows": [
    {
      "text": "See [full][id], [collapsed][], [shortcut], ![img][shot], ![mini][], and ![icon].",
      "full_reference_link_count": 1,
      "collapsed_reference_link_count": 1,
      "shortcut_reference_link_count": 1,
      "full_reference_image_count": 1,
      "collapsed_reference_image_count": 1,
      "shortcut_reference_image_count": 1,
      "reference_link_entries": [
        {"display": "full", "reference_form": "full"},
        {"display": "collapsed", "reference_form": "collapsed"},
        {"display": "shortcut", "reference_form": "shortcut"},
      ],
      "reference_image_entries": [
        {"alt_text": "img", "reference_form": "full"},
        {"alt_text": "mini", "reference_form": "collapsed"},
        {"alt_text": "icon", "reference_form": "shortcut"},
      ],
    },
  ],
}
```

## Why this stays honest

This is still **not** a fuller markdown AST. It simply promotes one more small
source-truth detail that CommonMark/GFM-style docs really do use: reference
links and reference images come in distinct source spellings that matter for
inspection, migration, linting, and archive-first handoff work.
