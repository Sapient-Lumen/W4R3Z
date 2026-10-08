# Rev265 — docs-cues nearest-heading section metadata

Rev262 made visible heading rows explicit, but future UIs/scripts/LLMs still had
to answer one practical docs/help question by rerunning breadcrumbs elsewhere:
**which heading section owns this visible row right now?**

Rev265 adds one tiny shared answer:

- each visible docs/help row now also carries `section_entry`
- rows also report `section_count` (`0` or `1`)
- top-level docs-cues snapshots now report:
  - `section_rows`
  - `section_distinct_count`

## Row shape

`section_entry` is a tiny nearest-heading snapshot:

- `kind` — always `section`
- `heading_line` / `heading_end_line` / `heading_col` — owning heading source span
- `level` — heading level (`1..6`)
- `title` — human heading title
- `fragment` — resolved heading fragment id
- `explicit_fragment` / `fragment_source` — whether the fragment came from an explicit attr-list id or the ordinary auto-slug path
- `source_kind` — `atx` or `setext`
- `path` — breadcrumb-like title path (`Guide › Links › Deep Dive`)
- `path_titles` — the same breadcrumb as an array of titles

## Why this exists

The recent docs-cues thread already exposed visible links, images, code,
inline markup, tables, structure, headings, definitions, and block metadata.
That still left one boring but useful question unanswered for ordinary prose,
definition rows, and inert block rows:

- *which heading section owns this line?*

Micromax already had enough shared heading knowledge to answer that:

- heading titles
- resolved fragments
- help outline rows
- help-nav grouping
- nearest-heading breadcrumbs

Rev265 simply packages that same truth into the visible docs-cues snapshot so
future archive readers do not have to rerun heading scans by hand.

## Example

```python
{
  "text": "code line",
  "line_role": "fenced-body",
  "block_entries": [{"kind": "fenced-code", "role": "body", ...}],
  "section_count": 1,
  "section_entry": {
    "kind": "section",
    "heading_line": 4,
    "heading_end_line": 4,
    "heading_col": 3,
    "level": 2,
    "title": "Links",
    "fragment": "links",
    "explicit_fragment": "",
    "fragment_source": "auto",
    "source_kind": "atx",
    "path": "Guide › Links",
    "path_titles": ["Guide", "Links"],
  },
}
```

That means fenced/html/indented docs rows can now stay visibly inert **without**
losing their surrounding section context in the shared headless model.
