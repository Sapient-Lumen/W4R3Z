# Rev227 — shared visible docs/help cue model

Rev227 lifts one more tiny visible surface out of `tui.py` and into the shared
editor core. Rev265 extends that same surface with parsed visible-image,
inline-code, inline-markup, literal-source, structure, table, definition, heading, block, and nearest-heading section metadata:

- `Editor.docs_cues_model(lines, cols)`
- hostcall / convenience word `ed.docs-cues` / `docs-cues`
- composed `screen_model(lines, cols)["docs_cues"]`

The model stays deliberately **viewport-local**, **span-first**, and
**docs/help-only**. It reports the small markdown-ish scanability cues the
reference curses TUI paints for visible help/docs rows without turning
Micromax into a richer rich-text or syntax-tree project.

## What it exposes

For each visible docs/help row, the model reports:

- stable row placement: `view_y`, `screen_y`, `line`, `start_col`, `text`
- inert/help metadata: `inert`, `line_role`, `heading_level`, `table_kind`,
  `definition_role`
- parsed visible-definition metadata: `definition_entries` (`kind`, `role`, normalized `id`, tiny target fields for reference definitions, owning ids for continuation rows)
- parsed visible block metadata: `block_entries` (`kind`, `role`, visible row spans/text, tiny fence/info-string/grouping fields)
- nearest-heading section metadata: `section_entry` (`title`, resolved `fragment`, `level`, `source_kind`, source line/col, breadcrumb `path`)
- parsed visible-heading metadata: `heading_entries` (`role`, `source_kind`, `level`, `title`, resolved `fragment`, `fragment_source`)
- visible cue spans: `link_spans`, `dim_spans`, `bold_spans`, `italic_spans`
- parsed visible-link metadata: `link_entries` (`kind`, source spans, `target`, `target_kind`, `target_doc`, `target_fragment`)
- parsed visible-image metadata: `image_entries` (`kind`, source spans, `alt_text`, `target`, `target_kind`, `target_doc`, `target_fragment`)
- parsed visible-code metadata: `code_entries` (`kind`, full/body spans, `delimiter_length`, `text`)
- parsed visible inline-markup metadata: `markup_entries` (`kind`, full/body spans, `delimiter`, `delimiter_length`, `text`)
- parsed visible literal-source metadata: `literal_entries` (`kind`, full spans, visible `text`, tiny `detail`)
- parsed visible table metadata: `table_entries` (`kind`, visible cell spans/text, `column`, and tiny delimiter alignment fields)
- parsed visible structure metadata: `structure_entries` (`kind`, visible marker spans/text plus tiny list/task/blockquote/thematic fields)
- small counters: `link_count`, `image_count`, `code_count`, `markup_count`, `literal_count`, `table_count`, `structure_count`, `heading_count`, `section_count`, `definition_count`, `block_count`, `span_count`

Top-level link-summary fields now also include:

- `link_rows`, `link_entry_count`
- `heading_rows`, `heading_entry_count`, `heading_title_entry_count`, `heading_underline_entry_count`
- `section_rows`, `section_distinct_count`
- `definition_rows`, `definition_entry_count`
- `block_rows`, `block_entry_count`
- `fenced_code_entry_count`, `fenced_code_opener_entry_count`, `fenced_code_body_entry_count`, `fenced_code_closer_entry_count`
- `html_block_entry_count`, `indented_code_entry_count`
- `reference_definition_entry_count`, `reference_definition_cont_entry_count`
- `footnote_definition_entry_count`, `footnote_definition_cont_entry_count`
- `local_doc_link_count`, `fragment_link_count`
- `external_link_count`, `footnote_link_count`
- `image_rows`, `image_entry_count`
- `local_doc_image_count`, `fragment_image_count`, `external_image_count`
- `code_rows`, `code_entry_count`
- `markup_rows`, `markup_entry_count`
- `strong_entry_count`, `emphasis_entry_count`, `strike_entry_count`
- `literal_rows`, `literal_entry_count`
- `raw_html_entry_count`, `escaped_markdown_entry_count`
- `table_rows`, `table_entry_count`
- `table_header_cell_count`, `table_body_cell_count`, `table_delimiter_cell_count`
- `structure_rows`, `structure_entry_count`
- `list_entry_count`, `task_entry_count`
- `blockquote_entry_count`, `blockquote_alert_entry_count`, `thematic_break_entry_count`

Current `line_role` values include:

- `heading-title` / `heading-underline`
- `table-header` / `table-delimiter`
- `thematic-break`
- `fenced-fence` / `fenced-body`
- `html-block`
- `indented-code`
- `definition`

Top-level metadata records whether the model is active plus the current
viewport geometry (`lines`, `cols`, `x`, `y`, `width`, `height`) and help-doc
identity.

## Why this exists

Rev223–rev226 already made the visible edit window increasingly inspectable:

- search-match spans
- `showchars` replacement text/spans
- final painted row text
- non-text viewport cue spans

That still left one awkward renderer-only surface for future UIs, tests,
scripts, and LLM handoffs: **the markdown-ish help/docs emphasis cues still
lived inside `_render`**.

`docs_cues_model(...)` closes that gap while staying small:

- smaller than a syntax tree
- smaller than a theme/style API
- smaller than a richer docs widget system

It is just one inspectable snapshot of the visible docs/help cues the reference
TUI already paints.

## Example shape

```python
{
  "active": 1,
  "enabled": 1,
  "help_doc": "help-browser",
  "rows": [
    {
      "view_y": 4,
      "screen_y": 4,
      "line": 12,
      "start_col": 0,
      "text": "A [link](other.md), ![img](pic.png), `code`, **strong**, and <kbd>",
      "inert": 0,
      "line_role": "",
      "heading_level": 0,
      "table_kind": "",
      "definition_role": "",
      "heading_entries": [],
      "section_entry": {
        "kind": "section",
        "title": "Intro",
        "fragment": "intro",
        "level": 2,
        "path": "Guide › Intro",
      },
      "definition_entries": [],
      "block_entries": [],
      "link_spans": [[3, 7]],
      "link_entries": [
        {
          "kind": "link",
          "start": 2,
          "end": 18,
          "label_start": 3,
          "label_end": 7,
          "display": "link",
          "target": "other.md",
          "target_kind": "file",
          "target_doc": "other.md",
          "target_fragment": "",
        },
      ],
      "image_entries": [
        {
          "kind": "image",
          "start": 20,
          "end": 35,
          "alt_start": 22,
          "alt_end": 25,
          "alt_text": "img",
          "target": "pic.png",
          "target_kind": "file",
          "target_doc": "pic.png",
          "target_fragment": "",
        },
      ],
      "code_entries": [
        {
          "kind": "code",
          "start": 41,
          "end": 47,
          "body_start": 42,
          "body_end": 46,
          "delimiter_length": 1,
          "text": "code",
        },
      ],
      "markup_entries": [
        {
          "kind": "strong",
          "start": 53,
          "end": 63,
          "body_start": 55,
          "body_end": 61,
          "delimiter": "**",
          "delimiter_length": 2,
          "text": "strong",
        },
      ],
      "literal_entries": [
        {
          "kind": "raw-html-tag",
          "start": 65,
          "end": 70,
          "text": "<kbd>",
          "detail": "kbd",
        },
      ],
      "table_entries": [],
      "structure_entries": [],
      "dim_spans": [[2, 3], [7, 18], [20, 35], [41, 47], [53, 55], [61, 63]],
      "bold_spans": [[41, 42], [46, 47], [55, 61]],
      "italic_spans": [],
      "link_count": 1,
      "image_count": 1,
      "code_count": 1,
      "markup_count": 1,
      "literal_count": 1,
      "table_count": 0,
      "structure_count": 0,
      "span_count": 9,
    },
  ],
}
```

## Renderer relationship

The minimal curses TUI now reuses this shared docs/help cue model instead of
recomputing heading/link/list/blockquote/table emphasis row by row.

Actual terminal attributes still remain renderer policy:

- links still choose underline (and color when available)
- dim spans still choose `A_DIM`
- bold/italic spans still choose terminal emphasis attributes
- inert rows still map to the same dimmed presentation choices

So the shared model owns **where** the visible docs/help cues are, while the
TUI still owns **how** to style them.
