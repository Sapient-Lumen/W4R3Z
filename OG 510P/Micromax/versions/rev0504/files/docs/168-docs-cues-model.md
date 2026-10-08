# Rev227 — shared visible docs/help cue model

Rev227 lifts one more tiny visible surface out of `tui.py` and into the shared
editor core. Rev265 extends that same surface with parsed visible-image,
inline-code, inline-markup, literal-source, structure, table, definition, heading, block, and nearest-heading section metadata, including heading level, explicit-vs-auto fragment-source slices, bullet-vs-ordered task-list slices, and checked-vs-unchecked task-state slices:

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
- focused visible definition-kind metadata: `reference_definition_entries`, `reference_definition_cont_entries`, `footnote_definition_entries`, `footnote_definition_cont_entries` plus matching row-local counts
- parsed visible block metadata: `block_entries` (`kind`, `role`, visible row spans/text, tiny fence/info-string/grouping fields)
- focused visible block-kind metadata: `fenced_code_entries`, `fenced_code_opener_entries`, `fenced_code_body_entries`, `fenced_code_closer_entries`, `html_block_entries`, `indented_code_entries` plus matching row-local counts
- focused visible fenced-code source metadata: `backtick_fenced_code_entries`, `tilde_fenced_code_entries`, `language_fenced_code_entries`, `bare_fenced_code_entries` plus matching row-local counts
- nearest-heading section metadata: `section_entry` (`title`, resolved `fragment`, `level`, `source_kind`, source line/col, breadcrumb `path`)
- parsed visible-heading metadata: `heading_entries` (`role`, `source_kind`, `level`, `title`, resolved `fragment`, `fragment_source`) plus focused `heading_title_entries`, `heading_underline_entries`, `atx_heading_entries`, `setext_heading_entries`, `h1_heading_entries`..`h6_heading_entries`, `explicit_fragment_heading_entries`, and `auto_fragment_heading_entries`
- visible cue spans: `link_spans`, `dim_spans`, `bold_spans`, `italic_spans`
- parsed visible-link metadata: `link_entries` (`kind`, `source_kind`, `reference_form`, source spans, `target`, `target_kind`, `target_doc`, `target_fragment`)
- focused visible link-target metadata: `local_doc_link_entries`, `fragment_link_entries`, `external_link_entries`, `footnote_link_entries` plus matching row-local target counts
- focused visible link source-kind metadata: `inline_link_entries`, `reference_link_entries`, `autolink_entries`, `footnote_ref_entries` plus matching row-local source-form counts
- focused visible link reference-form metadata: `full_reference_link_entries`, `collapsed_reference_link_entries`, `shortcut_reference_link_entries` plus matching row-local counts
- parsed visible-image metadata: `image_entries` (`kind`, `source_kind`, `reference_form`, source spans, `alt_text`, `target`, `target_kind`, `target_doc`, `target_fragment`)
- focused visible image source-kind metadata: `inline_image_entries`, `reference_image_entries` plus matching row-local source-form counts
- focused visible image reference-form metadata: `full_reference_image_entries`, `collapsed_reference_image_entries`, `shortcut_reference_image_entries` plus matching row-local counts
- focused visible image-target metadata: `local_doc_image_entries`, `fragment_image_entries`, `external_image_entries`, `footnote_image_entries` plus matching row-local target counts
- parsed visible-code metadata: `code_entries` (`kind`, full/body spans, `delimiter_length`, `text`)
- focused visible code-delimiter metadata: `single_backtick_code_entries`, `multi_backtick_code_entries` plus matching row-local counts and top-level `single_backtick_code_rows`, `multi_backtick_code_rows`, `single_backtick_code_count`, `multi_backtick_code_count`
- parsed visible inline-markup metadata: `markup_entries` (`kind`, full/body spans, `delimiter`, `delimiter_kind`, `delimiter_length`, `text`)
- focused visible inline-markup kind metadata: `strong_markup_entries`, `emphasis_markup_entries`, `strike_markup_entries` plus matching row-local counts
- focused visible inline-markup delimiter metadata: `asterisk_markup_entries`, `underscore_markup_entries`, `tilde_markup_entries` plus matching row-local counts
- parsed visible literal-source metadata: `literal_entries` (`kind`, full spans, visible `text`, tiny `detail`)
- focused visible literal-kind metadata: `raw_html_literal_entries`, `escaped_markdown_entries` plus matching row-local counts
- parsed visible table metadata: `table_entries` (`kind`, visible cell spans/text, `column`, resolved `align`, and tiny delimiter alignment fields)
- focused visible table-kind metadata: `table_header_entries`, `table_body_entries`, `table_delimiter_entries` plus matching row-local counts
- focused visible table-alignment metadata: `default_aligned_table_entries`, `left_aligned_table_entries`, `center_aligned_table_entries`, `right_aligned_table_entries` plus matching row-local counts
- parsed visible structure metadata: `structure_entries` (`kind`, visible marker spans/text plus tiny list/task/blockquote/thematic fields)
- focused visible list-marker metadata: `list_entries` plus `list_count`, `bullet_list_count`, `ordered_list_count`
- focused visible task metadata: `task_entries`, `checked_task_entries`, `unchecked_task_entries`, `bullet_task_entries`, `ordered_task_entries` plus `task_count`, `checked_task_count`, `unchecked_task_count`, `bullet_task_count`, and `ordered_task_count`
- small counters: `link_count`, `image_count`, `code_count`, `markup_count`, `literal_count`, `table_count`, `structure_count`, `heading_count`, `heading_title_count`, `heading_underline_count`, `atx_heading_count`, `setext_heading_count`, `section_count`, `definition_count`, `block_count`, `span_count`

Top-level link-summary fields now also include:

- `link_rows`, `link_entry_count`
- `local_doc_link_rows`, `fragment_link_rows`, `external_link_rows`, `footnote_link_rows`
- `inline_link_rows`, `reference_link_rows`, `full_reference_link_rows`, `collapsed_reference_link_rows`, `shortcut_reference_link_rows`, `autolink_rows`, `footnote_ref_rows`
- `heading_rows`, `heading_entry_count`, `heading_title_rows`, `heading_underline_rows`, `atx_heading_rows`, `setext_heading_rows`, `h1_heading_rows`..`h6_heading_rows`, `explicit_fragment_heading_rows`, `auto_fragment_heading_rows`, `heading_title_entry_count`, `heading_underline_entry_count`, `atx_heading_entry_count`, `setext_heading_entry_count`, `h1_heading_entry_count`..`h6_heading_entry_count`, `explicit_fragment_heading_entry_count`, and `auto_fragment_heading_entry_count`
- `section_rows`, `section_distinct_count`
- `definition_rows`, `definition_entry_count`
- `reference_definition_rows`, `reference_definition_cont_rows`
- `footnote_definition_rows`, `footnote_definition_cont_rows`
- `block_rows`, `block_entry_count`
- `backtick_fenced_code_rows`, `tilde_fenced_code_rows`, `language_fenced_code_rows`, `bare_fenced_code_rows`, `backtick_fenced_code_count`, `tilde_fenced_code_count`, `language_fenced_code_count`, `bare_fenced_code_count`
- `fenced_code_rows`, `fenced_code_opener_rows`, `fenced_code_body_rows`, `fenced_code_closer_rows`, `html_block_rows`, `indented_code_rows`
- `fenced_code_entry_count`, `fenced_code_opener_entry_count`, `fenced_code_body_entry_count`, `fenced_code_closer_entry_count`
- `html_block_entry_count`, `indented_code_entry_count`
- `reference_definition_entry_count`, `reference_definition_cont_entry_count`
- `footnote_definition_entry_count`, `footnote_definition_cont_entry_count`
- `local_doc_link_count`, `fragment_link_count`
- `external_link_count`, `footnote_link_count`
- `inline_link_count`, `reference_link_count`, `full_reference_link_count`, `collapsed_reference_link_count`, `shortcut_reference_link_count`, `autolink_count`, `footnote_ref_count`
- `image_rows`, `image_entry_count`
- `inline_image_rows`, `reference_image_rows`, `full_reference_image_rows`, `collapsed_reference_image_rows`, `shortcut_reference_image_rows`
- `inline_image_count`, `reference_image_count`, `full_reference_image_count`, `collapsed_reference_image_count`, `shortcut_reference_image_count`
- `local_doc_image_rows`, `fragment_image_rows`, `external_image_rows`, `footnote_image_rows`
- `local_doc_image_count`, `fragment_image_count`, `external_image_count`, `footnote_image_count`
- `code_rows`, `code_entry_count`
- `markup_rows`, `markup_entry_count`
- `strong_markup_rows`, `emphasis_markup_rows`, `strike_markup_rows`
- `asterisk_markup_rows`, `underscore_markup_rows`, `tilde_markup_rows`
- `strong_entry_count`, `emphasis_entry_count`, `strike_entry_count`
- `asterisk_markup_count`, `underscore_markup_count`, `tilde_markup_count`
- `literal_rows`, `literal_entry_count`
- `raw_html_rows`, `escaped_markdown_rows`
- `raw_html_entry_count`, `escaped_markdown_entry_count`
- `table_rows`, `table_entry_count`
- `table_header_rows`, `table_body_rows`, `table_delimiter_rows`
- `table_header_cell_count`, `table_body_cell_count`, `table_delimiter_cell_count`
- `structure_rows`, `structure_entry_count`
- `list_rows`, `list_entry_count`
- `bullet_list_rows`, `ordered_list_rows`
- `bullet_list_entry_count`, `ordered_list_entry_count`
- `task_rows`, `task_entry_count`, `checked_task_rows`, `unchecked_task_rows`, `checked_task_entry_count`, `unchecked_task_entry_count`
- `bullet_task_rows`, `ordered_task_rows`
- `bullet_task_entry_count`, `ordered_task_entry_count`
- `blockquote_entry_count`, `blockquote_alert_entry_count`, `thematic_break_entry_count`
- `note_blockquote_alert_rows`, `tip_blockquote_alert_rows`, `important_blockquote_alert_rows`, `warning_blockquote_alert_rows`, `caution_blockquote_alert_rows`
- `note_blockquote_alert_entry_count`, `tip_blockquote_alert_entry_count`, `important_blockquote_alert_entry_count`, `warning_blockquote_alert_entry_count`, `caution_blockquote_alert_entry_count`

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
          "source_kind": "inline",
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
