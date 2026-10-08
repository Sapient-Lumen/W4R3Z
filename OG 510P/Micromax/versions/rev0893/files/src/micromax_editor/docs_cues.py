from __future__ import annotations

from typing import Any

from .markdown_docs import (
    md_docs_continuation_line,
    md_escaped_markdown_matches,
    md_fenced_code_line_flags,
    md_heading_auto_id,
    md_help_image_reference_form,
    md_help_image_source_kind,
    md_help_link_reference_form,
    md_help_link_source_kind,
    md_help_link_target_info,
    md_html_block_line_flags,
    md_html_comment_line_spans,
    md_image_matches,
    md_indented_code_line_flags,
    md_inline_code_delimiter_spans,
    md_inline_code_matches,
    md_inline_code_spans,
    md_inline_markup_delimiter_kind,
    md_link_matches,
    md_raw_html_tag_matches,
)


def _merge_spans(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Merge overlapping/adjacent ``[start,end)`` spans."""

    if not spans:
        return []
    spans2 = sorted((int(a), int(b)) for a, b in spans if int(b) > int(a))
    out: list[tuple[int, int]] = []
    cur_a, cur_b = spans2[0]
    for a, b in spans2[1:]:
        if a <= cur_b:
            cur_b = max(cur_b, b)
        else:
            out.append((cur_a, cur_b))
            cur_a, cur_b = a, b
    out.append((cur_a, cur_b))
    return out



DOCS_CUE_ZERO_METRIC_KEYS: tuple[str, ...] = (
    'row_count',
    'cue_rows',
    'link_rows',
    'link_entry_count',
    'local_doc_link_rows',
    'fragment_link_rows',
    'external_link_rows',
    'footnote_link_rows',
    'inline_link_rows',
    'reference_link_rows',
    'full_reference_link_rows',
    'collapsed_reference_link_rows',
    'shortcut_reference_link_rows',
    'autolink_rows',
    'footnote_ref_rows',
    'local_doc_link_count',
    'fragment_link_count',
    'external_link_count',
    'footnote_link_count',
    'inline_link_count',
    'reference_link_count',
    'full_reference_link_count',
    'collapsed_reference_link_count',
    'shortcut_reference_link_count',
    'autolink_count',
    'footnote_ref_count',
    'image_rows',
    'image_entry_count',
    'inline_image_rows',
    'reference_image_rows',
    'full_reference_image_rows',
    'collapsed_reference_image_rows',
    'shortcut_reference_image_rows',
    'local_doc_image_rows',
    'fragment_image_rows',
    'external_image_rows',
    'footnote_image_rows',
    'inline_image_count',
    'reference_image_count',
    'full_reference_image_count',
    'collapsed_reference_image_count',
    'shortcut_reference_image_count',
    'local_doc_image_count',
    'fragment_image_count',
    'external_image_count',
    'footnote_image_count',
    'code_rows',
    'code_entry_count',
    'single_backtick_code_rows',
    'multi_backtick_code_rows',
    'single_backtick_code_count',
    'multi_backtick_code_count',
    'markup_rows',
    'markup_entry_count',
    'strong_markup_rows',
    'emphasis_markup_rows',
    'strike_markup_rows',
    'asterisk_markup_rows',
    'underscore_markup_rows',
    'tilde_markup_rows',
    'strong_entry_count',
    'emphasis_entry_count',
    'strike_entry_count',
    'asterisk_markup_count',
    'underscore_markup_count',
    'tilde_markup_count',
    'table_rows',
    'table_entry_count',
    'table_header_rows',
    'table_body_rows',
    'table_delimiter_rows',
    'default_aligned_table_rows',
    'left_aligned_table_rows',
    'center_aligned_table_rows',
    'right_aligned_table_rows',
    'table_header_cell_count',
    'table_body_cell_count',
    'table_delimiter_cell_count',
    'default_aligned_table_entry_count',
    'left_aligned_table_entry_count',
    'center_aligned_table_entry_count',
    'right_aligned_table_entry_count',
    'structure_rows',
    'structure_entry_count',
    'list_rows',
    'list_entry_count',
    'bullet_list_rows',
    'ordered_list_rows',
    'bullet_list_entry_count',
    'ordered_list_entry_count',
    'task_rows',
    'task_entry_count',
    'checked_task_rows',
    'unchecked_task_rows',
    'checked_task_entry_count',
    'unchecked_task_entry_count',
    'bullet_task_rows',
    'ordered_task_rows',
    'bullet_task_entry_count',
    'ordered_task_entry_count',
    'blockquote_rows',
    'blockquote_entry_count',
    'blockquote_alert_rows',
    'blockquote_alert_entry_count',
    'note_blockquote_alert_rows',
    'tip_blockquote_alert_rows',
    'important_blockquote_alert_rows',
    'warning_blockquote_alert_rows',
    'caution_blockquote_alert_rows',
    'note_blockquote_alert_entry_count',
    'tip_blockquote_alert_entry_count',
    'important_blockquote_alert_entry_count',
    'warning_blockquote_alert_entry_count',
    'caution_blockquote_alert_entry_count',
    'thematic_break_rows',
    'thematic_break_entry_count',
    'heading_rows',
    'heading_entry_count',
    'heading_title_rows',
    'heading_underline_rows',
    'atx_heading_rows',
    'setext_heading_rows',
    'h1_heading_rows',
    'h2_heading_rows',
    'h3_heading_rows',
    'h4_heading_rows',
    'h5_heading_rows',
    'h6_heading_rows',
    'explicit_fragment_heading_rows',
    'auto_fragment_heading_rows',
    'heading_title_entry_count',
    'heading_underline_entry_count',
    'atx_heading_entry_count',
    'setext_heading_entry_count',
    'h1_heading_entry_count',
    'h2_heading_entry_count',
    'h3_heading_entry_count',
    'h4_heading_entry_count',
    'h5_heading_entry_count',
    'h6_heading_entry_count',
    'explicit_fragment_heading_entry_count',
    'auto_fragment_heading_entry_count',
    'section_rows',
    'section_distinct_count',
    'definition_rows',
    'definition_entry_count',
    'reference_definition_rows',
    'reference_definition_cont_rows',
    'footnote_definition_rows',
    'footnote_definition_cont_rows',
    'reference_definition_entry_count',
    'reference_definition_cont_entry_count',
    'footnote_definition_entry_count',
    'footnote_definition_cont_entry_count',
    'block_rows',
    'block_entry_count',
    'backtick_fenced_code_rows',
    'tilde_fenced_code_rows',
    'language_fenced_code_rows',
    'bare_fenced_code_rows',
    'backtick_fenced_code_count',
    'tilde_fenced_code_count',
    'language_fenced_code_count',
    'bare_fenced_code_count',
    'fenced_code_rows',
    'fenced_code_opener_rows',
    'fenced_code_body_rows',
    'fenced_code_closer_rows',
    'html_block_rows',
    'indented_code_rows',
    'fenced_code_entry_count',
    'fenced_code_opener_entry_count',
    'fenced_code_body_entry_count',
    'fenced_code_closer_entry_count',
    'html_block_entry_count',
    'indented_code_entry_count',
    'literal_rows',
    'literal_entry_count',
    'raw_html_rows',
    'escaped_markdown_rows',
    'raw_html_entry_count',
    'escaped_markdown_entry_count',
)


def _zero_docs_cue_metrics() -> dict[str, int]:
    """Return the stable zero-valued docs-cues metric schema."""

    return {key: 0 for key in DOCS_CUE_ZERO_METRIC_KEYS}

def docs_cues_model_from_parts(
    self,
    *,
    lines: int,
    cols: int,
    layout: dict[str, Any],
    window: dict[str, Any],
) -> dict[str, Any]:
    """Return shared visible docs/help scanability spans for one edit window.

    This keeps the contract deliberately viewport-local and span-first: it
    exposes the tiny markdown-ish emphasis/link/list/blockquote/table cues
    the reference TUI paints for docs/help buffers without promoting them
    into a broader theme system or a full markdown AST.
    """

    from .tui import (
        md_autolink_token_spans,
        md_blockquote_alert_marker,
        md_blockquote_body_span,
        md_blockquote_prefix,
        md_emphasis_spans,
        md_escaped_markdown_token_spans,
        md_footnote_ref_token_spans,
        md_image_token_spans,
        md_inline_markup_delimiter_spans,
        md_inline_markup_matches,
        md_link_label_spans,
        md_link_source_token_spans,
        md_list_marker,
        md_raw_html_tag_token_spans,
        md_strikethrough_spans,
        md_strong_spans,
        md_table_cell_entries,
        md_table_delimiter_entries,
        md_table_pipe_spans,
        md_table_row_kinds,
        md_task_body_span,
        md_task_checkbox,
        md_thematic_break_char_spans,
        md_thematic_break_span,
    )

    h = max(0, int(lines))
    w = max(0, int(cols))
    viewport_h = int(layout.get("viewport_height", 0) or 0)
    viewport_w = int(layout.get("viewport_width", 0) or 0)
    help_topic = self.current_help_doc_topic()
    enabled = bool(help_topic)
    out: dict[str, Any] = {
        **_zero_docs_cue_metrics(),
        "active": 1 if enabled and viewport_h > 0 and viewport_w > 0 else 0,
        "enabled": 1 if enabled else 0,
        "help_doc": str(help_topic or ""),
        "lines": h,
        "cols": w,
        "y": int(layout.get("viewport_y", 0) or 0),
        "x": int(layout.get("viewport_x", 0) or 0),
        "width": int(max(0, viewport_w)),
        "height": int(max(0, viewport_h)),
        "rows": [],
    }
    if viewport_h <= 0 or viewport_w <= 0:
        return out

    rows_by_view_y = {
        int(row.get("view_y", -1)): dict(row)
        for row in list(window.get("rows") or [])
        if isinstance(row, dict)
    }
    line_comment_spans: list[list[tuple[int, int]]] = []
    defs: dict[str, str] = {}
    footdefs: dict[str, tuple[int, int]] = {}
    fence_flags: list[bool] = []
    html_block_flags: list[bool] = []
    indented_code_flags: list[bool] = []
    heading_roles: dict[int, tuple[str, int]] = {}
    fenced_roles: dict[int, str] = {}
    definition_roles: dict[int, tuple[str, int, int]] = {}
    table_kinds: dict[int, str] = {}
    table_alignments_by_line: dict[int, dict[int, str]] = {}
    heading_entries_by_line: dict[int, list[dict[str, Any]]] = {}
    section_entry_by_line: dict[int, dict[str, Any]] = {}
    definition_entries_by_line: dict[int, list[dict[str, Any]]] = {}
    block_entries_by_line: dict[int, list[dict[str, Any]]] = {}
    eb = self.cur()
    if enabled:
        buf_lines = eb.buf.lines
        defs = self._md_reference_defs(buf_lines)
        footdefs = self._md_footnote_defs(buf_lines)
        fence_flags = md_fenced_code_line_flags(buf_lines)
        html_block_flags = md_html_block_line_flags(buf_lines)
        line_comment_spans = md_html_comment_line_spans(buf_lines)
        indented_code_flags = md_indented_code_line_flags(
            buf_lines,
            fence_flags=fence_flags,
            html_block_flags=html_block_flags,
        )
        heading_roles = self._md_heading_line_roles(buf_lines)
        section_entry_by_line = self._md_section_entry_by_line(buf_lines)
        fenced_roles = self._md_fenced_code_line_roles(buf_lines)
        definition_roles = self._md_definition_line_roles(buf_lines)
        definition_entries_by_line = self._md_definition_entries_by_line(buf_lines)
        block_entries_by_line = self._md_block_entries_by_line(buf_lines)
        table_kinds = md_table_row_kinds([str(ln) for ln in buf_lines])
        for line_idx, kind in sorted(table_kinds.items()):
            if str(kind) != "delimiter":
                continue
            alignments = {
                int(entry.get("column", 0) or 0): str(entry.get("align", "default") or "default")
                for entry in md_table_delimiter_entries(str(buf_lines[int(line_idx)]))
            }
            if not alignments:
                continue
            table_alignments_by_line[int(line_idx)] = dict(alignments)
            header_idx = int(line_idx) - 1
            if table_kinds.get(header_idx) == "header":
                table_alignments_by_line[header_idx] = dict(alignments)
            body_idx = int(line_idx) + 1
            while table_kinds.get(body_idx) == "body":
                table_alignments_by_line[body_idx] = dict(alignments)
                body_idx += 1
        seen_heading_ids: dict[str, int] = {}
        for line0, line1, level, title, explicit_fragment, _col0 in self._md_heading_scan(buf_lines):
            resolved_fragment = str(explicit_fragment or md_heading_auto_id(title, seen=seen_heading_ids))
            source_kind = 'atx' if int(line1) <= int(line0) + 1 else 'setext'
            for idx in range(int(line0), int(line1)):
                role = 'underline' if source_kind == 'setext' and idx == int(line1) - 1 else 'title'
                entry: dict[str, Any] = {
                    'kind': 'heading',
                    'role': str(role),
                    'source_kind': str(source_kind),
                    'level': int(level),
                    'title': str(title),
                    'fragment': str(resolved_fragment),
                    'explicit_fragment': str(explicit_fragment),
                    'fragment_source': 'explicit' if str(explicit_fragment) else 'auto',
                }
                if role == 'underline':
                    stripped = str(buf_lines[idx]).strip()
                    marker = '=' if stripped.startswith('=') else '-'
                    entry['marker'] = str(marker)
                    entry['marker_count'] = int(sum(1 for ch in stripped if ch == marker))
                heading_entries_by_line.setdefault(int(idx), []).append(entry)

    rows: list[dict[str, Any]] = []
    cue_rows = 0
    link_rows = 0
    link_entry_count = 0
    local_doc_link_rows = 0
    fragment_link_rows = 0
    external_link_rows = 0
    footnote_link_rows = 0
    inline_link_rows = 0
    reference_link_rows = 0
    full_reference_link_rows = 0
    collapsed_reference_link_rows = 0
    shortcut_reference_link_rows = 0
    autolink_rows = 0
    footnote_ref_rows = 0
    local_doc_link_count = 0
    fragment_link_count = 0
    external_link_count = 0
    footnote_link_count = 0
    inline_link_count = 0
    reference_link_count = 0
    full_reference_link_count = 0
    collapsed_reference_link_count = 0
    shortcut_reference_link_count = 0
    autolink_count = 0
    footnote_ref_count = 0
    image_rows = 0
    image_entry_count = 0
    inline_image_rows = 0
    reference_image_rows = 0
    full_reference_image_rows = 0
    collapsed_reference_image_rows = 0
    shortcut_reference_image_rows = 0
    local_doc_image_rows = 0
    fragment_image_rows = 0
    external_image_rows = 0
    footnote_image_rows = 0
    inline_image_count = 0
    reference_image_count = 0
    full_reference_image_count = 0
    collapsed_reference_image_count = 0
    shortcut_reference_image_count = 0
    local_doc_image_count = 0
    fragment_image_count = 0
    external_image_count = 0
    footnote_image_count = 0
    code_rows = 0
    code_entry_count = 0
    single_backtick_code_rows = 0
    multi_backtick_code_rows = 0
    single_backtick_code_count = 0
    multi_backtick_code_count = 0
    markup_rows = 0
    markup_entry_count = 0
    strong_markup_rows = 0
    emphasis_markup_rows = 0
    strike_markup_rows = 0
    asterisk_markup_rows = 0
    underscore_markup_rows = 0
    tilde_markup_rows = 0
    strong_entry_count = 0
    emphasis_entry_count = 0
    strike_entry_count = 0
    asterisk_markup_count = 0
    underscore_markup_count = 0
    tilde_markup_count = 0
    table_rows = 0
    table_entry_count = 0
    table_header_rows = 0
    table_body_rows = 0
    table_delimiter_rows = 0
    default_aligned_table_rows = 0
    left_aligned_table_rows = 0
    center_aligned_table_rows = 0
    right_aligned_table_rows = 0
    table_header_cell_count = 0
    table_body_cell_count = 0
    table_delimiter_cell_count = 0
    default_aligned_table_entry_count = 0
    left_aligned_table_entry_count = 0
    center_aligned_table_entry_count = 0
    right_aligned_table_entry_count = 0
    structure_rows = 0
    structure_entry_count = 0
    list_rows = 0
    list_entry_count = 0
    bullet_list_rows = 0
    ordered_list_rows = 0
    bullet_list_entry_count = 0
    ordered_list_entry_count = 0
    task_rows = 0
    task_entry_count = 0
    checked_task_rows = 0
    unchecked_task_rows = 0
    checked_task_entry_count = 0
    unchecked_task_entry_count = 0
    bullet_task_rows = 0
    ordered_task_rows = 0
    bullet_task_entry_count = 0
    ordered_task_entry_count = 0
    blockquote_rows = 0
    blockquote_entry_count = 0
    blockquote_alert_rows = 0
    blockquote_alert_entry_count = 0
    note_blockquote_alert_rows = 0
    tip_blockquote_alert_rows = 0
    important_blockquote_alert_rows = 0
    warning_blockquote_alert_rows = 0
    caution_blockquote_alert_rows = 0
    note_blockquote_alert_entry_count = 0
    tip_blockquote_alert_entry_count = 0
    important_blockquote_alert_entry_count = 0
    warning_blockquote_alert_entry_count = 0
    caution_blockquote_alert_entry_count = 0
    thematic_break_rows = 0
    thematic_break_entry_count = 0
    heading_rows = 0
    heading_entry_count = 0
    heading_title_rows = 0
    heading_underline_rows = 0
    atx_heading_rows = 0
    setext_heading_rows = 0
    h1_heading_rows = 0
    h2_heading_rows = 0
    h3_heading_rows = 0
    h4_heading_rows = 0
    h5_heading_rows = 0
    h6_heading_rows = 0
    explicit_fragment_heading_rows = 0
    auto_fragment_heading_rows = 0
    heading_title_entry_count = 0
    heading_underline_entry_count = 0
    atx_heading_entry_count = 0
    setext_heading_entry_count = 0
    h1_heading_entry_count = 0
    h2_heading_entry_count = 0
    h3_heading_entry_count = 0
    h4_heading_entry_count = 0
    h5_heading_entry_count = 0
    h6_heading_entry_count = 0
    explicit_fragment_heading_entry_count = 0
    auto_fragment_heading_entry_count = 0
    section_rows = 0
    visible_section_paths: set[str] = set()
    definition_rows = 0
    definition_entry_count = 0
    reference_definition_rows = 0
    reference_definition_cont_rows = 0
    footnote_definition_rows = 0
    footnote_definition_cont_rows = 0
    reference_definition_entry_count = 0
    reference_definition_cont_entry_count = 0
    footnote_definition_entry_count = 0
    footnote_definition_cont_entry_count = 0
    block_rows = 0
    block_entry_count = 0
    backtick_fenced_code_rows = 0
    tilde_fenced_code_rows = 0
    language_fenced_code_rows = 0
    bare_fenced_code_rows = 0
    backtick_fenced_code_count = 0
    tilde_fenced_code_count = 0
    language_fenced_code_count = 0
    bare_fenced_code_count = 0
    fenced_code_rows = 0
    fenced_code_opener_rows = 0
    fenced_code_body_rows = 0
    fenced_code_closer_rows = 0
    html_block_rows = 0
    indented_code_rows = 0
    fenced_code_entry_count = 0
    fenced_code_opener_entry_count = 0
    fenced_code_body_entry_count = 0
    fenced_code_closer_entry_count = 0
    html_block_entry_count = 0
    indented_code_entry_count = 0
    literal_rows = 0
    literal_entry_count = 0
    raw_html_rows = 0
    escaped_markdown_rows = 0
    raw_html_entry_count = 0
    escaped_markdown_entry_count = 0
    for view_y in range(int(viewport_h)):
        row = dict(rows_by_view_y.get(int(view_y), {}))
        text = str(row.get("text", "") or "")
        line_index = int(row["line"]) if "line" in row else -1
        start_col = int(row.get("start_col", 0) or 0)
        link_spans: list[tuple[int, int]] = []
        link_entries: list[dict[str, Any]] = []
        local_doc_link_entries: list[dict[str, Any]] = []
        fragment_link_entries: list[dict[str, Any]] = []
        external_link_entries: list[dict[str, Any]] = []
        footnote_link_entries: list[dict[str, Any]] = []
        inline_link_entries: list[dict[str, Any]] = []
        reference_link_entries: list[dict[str, Any]] = []
        full_reference_link_entries: list[dict[str, Any]] = []
        collapsed_reference_link_entries: list[dict[str, Any]] = []
        shortcut_reference_link_entries: list[dict[str, Any]] = []
        autolink_entries: list[dict[str, Any]] = []
        footnote_ref_entries: list[dict[str, Any]] = []
        image_entries: list[dict[str, Any]] = []
        inline_image_entries: list[dict[str, Any]] = []
        reference_image_entries: list[dict[str, Any]] = []
        full_reference_image_entries: list[dict[str, Any]] = []
        collapsed_reference_image_entries: list[dict[str, Any]] = []
        shortcut_reference_image_entries: list[dict[str, Any]] = []
        local_doc_image_entries: list[dict[str, Any]] = []
        fragment_image_entries: list[dict[str, Any]] = []
        external_image_entries: list[dict[str, Any]] = []
        footnote_image_entries: list[dict[str, Any]] = []
        code_entries: list[dict[str, Any]] = []
        single_backtick_code_entries: list[dict[str, Any]] = []
        multi_backtick_code_entries: list[dict[str, Any]] = []
        markup_entries: list[dict[str, Any]] = []
        strong_markup_entries: list[dict[str, Any]] = []
        emphasis_markup_entries: list[dict[str, Any]] = []
        strike_markup_entries: list[dict[str, Any]] = []
        asterisk_markup_entries: list[dict[str, Any]] = []
        underscore_markup_entries: list[dict[str, Any]] = []
        tilde_markup_entries: list[dict[str, Any]] = []
        literal_entries: list[dict[str, Any]] = []
        raw_html_literal_entries: list[dict[str, Any]] = []
        escaped_markdown_entries: list[dict[str, Any]] = []
        table_entries: list[dict[str, Any]] = []
        table_header_entries: list[dict[str, Any]] = []
        table_body_entries: list[dict[str, Any]] = []
        table_delimiter_entries: list[dict[str, Any]] = []
        default_aligned_table_entries: list[dict[str, Any]] = []
        left_aligned_table_entries: list[dict[str, Any]] = []
        center_aligned_table_entries: list[dict[str, Any]] = []
        right_aligned_table_entries: list[dict[str, Any]] = []
        structure_entries: list[dict[str, Any]] = []
        list_entries: list[dict[str, Any]] = []
        task_entries: list[dict[str, Any]] = []
        checked_task_entries: list[dict[str, Any]] = []
        unchecked_task_entries: list[dict[str, Any]] = []
        bullet_task_entries: list[dict[str, Any]] = []
        ordered_task_entries: list[dict[str, Any]] = []
        blockquote_entries: list[dict[str, Any]] = []
        blockquote_alert_entries: list[dict[str, Any]] = []
        note_blockquote_alert_entries: list[dict[str, Any]] = []
        tip_blockquote_alert_entries: list[dict[str, Any]] = []
        important_blockquote_alert_entries: list[dict[str, Any]] = []
        warning_blockquote_alert_entries: list[dict[str, Any]] = []
        caution_blockquote_alert_entries: list[dict[str, Any]] = []
        thematic_break_entries: list[dict[str, Any]] = []
        heading_entries: list[dict[str, Any]] = []
        heading_title_entries: list[dict[str, Any]] = []
        heading_underline_entries: list[dict[str, Any]] = []
        atx_heading_entries: list[dict[str, Any]] = []
        setext_heading_entries: list[dict[str, Any]] = []
        h1_heading_entries: list[dict[str, Any]] = []
        h2_heading_entries: list[dict[str, Any]] = []
        h3_heading_entries: list[dict[str, Any]] = []
        h4_heading_entries: list[dict[str, Any]] = []
        h5_heading_entries: list[dict[str, Any]] = []
        h6_heading_entries: list[dict[str, Any]] = []
        explicit_fragment_heading_entries: list[dict[str, Any]] = []
        auto_fragment_heading_entries: list[dict[str, Any]] = []
        section_entry: dict[str, Any] = {}
        definition_entries: list[dict[str, Any]] = []
        reference_definition_entries: list[dict[str, Any]] = []
        reference_definition_cont_entries: list[dict[str, Any]] = []
        footnote_definition_entries: list[dict[str, Any]] = []
        footnote_definition_cont_entries: list[dict[str, Any]] = []
        block_entries: list[dict[str, Any]] = []
        fenced_code_entries: list[dict[str, Any]] = []
        backtick_fenced_code_entries: list[dict[str, Any]] = []
        tilde_fenced_code_entries: list[dict[str, Any]] = []
        language_fenced_code_entries: list[dict[str, Any]] = []
        bare_fenced_code_entries: list[dict[str, Any]] = []
        fenced_code_opener_entries: list[dict[str, Any]] = []
        fenced_code_body_entries: list[dict[str, Any]] = []
        fenced_code_closer_entries: list[dict[str, Any]] = []
        html_block_entries: list[dict[str, Any]] = []
        indented_code_entries: list[dict[str, Any]] = []
        dim_spans: list[tuple[int, int]] = []
        bold_spans: list[tuple[int, int]] = []
        italic_spans: list[tuple[int, int]] = []
        line_role = ""
        heading_level = 0
        table_kind = ""
        definition_role = ""
        inert = False
        if enabled and 0 <= int(line_index) < len(eb.buf.lines):
            line_is_fenced = bool(int(line_index) < len(fence_flags) and fence_flags[int(line_index)])
            fenced_role = str(fenced_roles.get(int(line_index), '') or '') if line_is_fenced else ''
            is_fenced_fence = fenced_role == 'fence'
            is_fenced_body = fenced_role == 'body'
            line_is_html_block = bool(int(line_index) < len(html_block_flags) and html_block_flags[int(line_index)])
            line_is_indented_code = bool(int(line_index) < len(indented_code_flags) and indented_code_flags[int(line_index)])
            inert = bool(line_is_fenced or line_is_html_block or line_is_indented_code)
            heading_role, heading_level = (heading_roles.get(int(line_index)) or ('', 0)) if not inert else ('', 0)
            definition_role, def_col0, def_col1 = (definition_roles.get(int(line_index)) or ('', 0, 0)) if not inert else ('', 0, 0)
            line_is_definition = bool(definition_role)
            table_kind = '' if inert else str(table_kinds.get(int(line_index), '') or '')
            is_table_header = table_kind == 'header'
            is_table_delim = table_kind == 'delimiter'
            is_thematic_break = (not inert) and (md_thematic_break_span(text) is not None)
            if heading_role == 'title':
                line_role = 'heading-title'
            elif heading_role == 'underline':
                line_role = 'heading-underline'
            elif is_table_header:
                line_role = 'table-header'
            elif is_table_delim:
                line_role = 'table-delimiter'
            elif is_thematic_break:
                line_role = 'thematic-break'
            elif is_fenced_fence:
                line_role = 'fenced-fence'
            elif is_fenced_body:
                line_role = 'fenced-body'
            elif line_is_html_block:
                line_role = 'html-block'
            elif line_is_indented_code:
                line_role = 'indented-code'
            elif line_is_definition:
                line_role = 'definition'

            next_line = md_docs_continuation_line(
                eb.buf.lines,
                int(line_index) + 1,
                fence_flags=fence_flags,
                html_block_flags=html_block_flags,
                comment_spans=line_comment_spans,
            )
            next_next_line = md_docs_continuation_line(
                eb.buf.lines,
                int(line_index) + 2,
                fence_flags=fence_flags,
                html_block_flags=html_block_flags,
                comment_spans=line_comment_spans,
            )
            masked_spans = line_comment_spans[int(line_index)] if int(line_index) < len(line_comment_spans) else []
            heading_entries = [
                {
                    **dict(entry),
                    'start': 0,
                    'end': int(len(text)),
                    'text': str(text),
                }
                for entry in heading_entries_by_line.get(int(line_index), [])
            ] if not inert else []
            heading_title_entries = [
                dict(entry)
                for entry in heading_entries
                if str(entry.get("role", "") or "") == "title"
            ]
            heading_underline_entries = [
                dict(entry)
                for entry in heading_entries
                if str(entry.get("role", "") or "") == "underline"
            ]
            atx_heading_entries = [
                dict(entry)
                for entry in heading_entries
                if str(entry.get("source_kind", "") or "") == "atx"
            ]
            setext_heading_entries = [
                dict(entry)
                for entry in heading_entries
                if str(entry.get("source_kind", "") or "") == "setext"
            ]
            h1_heading_entries = [
                dict(entry)
                for entry in heading_entries
                if int(entry.get("level", 0) or 0) == 1
            ]
            h2_heading_entries = [
                dict(entry)
                for entry in heading_entries
                if int(entry.get("level", 0) or 0) == 2
            ]
            h3_heading_entries = [
                dict(entry)
                for entry in heading_entries
                if int(entry.get("level", 0) or 0) == 3
            ]
            h4_heading_entries = [
                dict(entry)
                for entry in heading_entries
                if int(entry.get("level", 0) or 0) == 4
            ]
            h5_heading_entries = [
                dict(entry)
                for entry in heading_entries
                if int(entry.get("level", 0) or 0) == 5
            ]
            h6_heading_entries = [
                dict(entry)
                for entry in heading_entries
                if int(entry.get("level", 0) or 0) == 6
            ]
            explicit_fragment_heading_entries = [
                dict(entry)
                for entry in heading_entries
                if str(entry.get("fragment_source", "") or "") == "explicit"
            ]
            auto_fragment_heading_entries = [
                dict(entry)
                for entry in heading_entries
                if str(entry.get("fragment_source", "") or "") == "auto"
            ]
            section_entry = dict(section_entry_by_line.get(int(line_index), {}))
            definition_entries = [
                {
                    key: value
                    for key, value in dict(entry).items()
                    if key != 'render_end'
                }
                for entry in definition_entries_by_line.get(int(line_index), [])
            ] if not inert else []
            reference_definition_entries = [
                dict(entry)
                for entry in definition_entries
                if str(entry.get("kind", "") or "") == "reference-definition"
            ]
            reference_definition_cont_entries = [
                dict(entry)
                for entry in definition_entries
                if str(entry.get("kind", "") or "") == "reference-definition-cont"
            ]
            footnote_definition_entries = [
                dict(entry)
                for entry in definition_entries
                if str(entry.get("kind", "") or "") == "footnote-definition"
            ]
            footnote_definition_cont_entries = [
                dict(entry)
                for entry in definition_entries
                if str(entry.get("kind", "") or "") == "footnote-definition-cont"
            ]
            block_entries = [dict(entry) for entry in block_entries_by_line.get(int(line_index), [])]
            fenced_code_entries = [
                dict(entry)
                for entry in block_entries
                if str(entry.get("kind", "") or "") == "fenced-code"
            ]
            backtick_fenced_code_entries = [
                dict(entry)
                for entry in fenced_code_entries
                if str(entry.get("marker_kind", "") or "") == "backtick"
            ]
            tilde_fenced_code_entries = [
                dict(entry)
                for entry in fenced_code_entries
                if str(entry.get("marker_kind", "") or "") == "tilde"
            ]
            language_fenced_code_entries = [
                dict(entry)
                for entry in fenced_code_entries
                if int(entry.get("has_language", 0) or 0) == 1
            ]
            bare_fenced_code_entries = [
                dict(entry)
                for entry in fenced_code_entries
                if int(entry.get("has_language", 0) or 0) == 0
            ]
            fenced_code_opener_entries = [
                dict(entry)
                for entry in fenced_code_entries
                if str(entry.get("role", "") or "") == "opener"
            ]
            fenced_code_body_entries = [
                dict(entry)
                for entry in fenced_code_entries
                if str(entry.get("role", "") or "") == "body"
            ]
            fenced_code_closer_entries = [
                dict(entry)
                for entry in fenced_code_entries
                if str(entry.get("role", "") or "") == "closer"
            ]
            html_block_entries = [
                dict(entry)
                for entry in block_entries
                if str(entry.get("kind", "") or "") == "html-block"
            ]
            indented_code_entries = [
                dict(entry)
                for entry in block_entries
                if str(entry.get("kind", "") or "") == "indented-code"
            ]
            if not inert:
                link_matches = md_link_matches(
                    text,
                    defs,
                    footdefs,
                    masked_spans=masked_spans,
                    next_line=next_line,
                    next_next_line=next_next_line,
                )
                link_spans = [
                    (int(m.label_start), int(m.label_end))
                    for m in link_matches
                ]
                link_entries = []
                for match in link_matches:
                    meta = md_help_link_target_info(str(match.target or ""))
                    source_kind = str(md_help_link_source_kind(text, int(match.start), int(match.end), str(match.kind)))
                    reference_form = str(md_help_link_reference_form(text, int(match.start), int(match.end), str(match.kind)))
                    link_entries.append(
                        {
                            "kind": str(match.kind),
                            "source_kind": str(source_kind),
                            "reference_form": str(reference_form),
                            "start": int(match.start),
                            "end": int(match.end),
                            "label_start": int(match.label_start),
                            "label_end": int(match.label_end),
                            "display": str(match.display),
                            "target": str(match.target),
                            "target_kind": str(meta.get("target_kind", "") or ""),
                            "target_doc": str(meta.get("doc", "") or ""),
                            "target_fragment": str(meta.get("fragment", "") or ""),
                        }
                    )
                local_doc_link_entries = [
                    dict(entry)
                    for entry in link_entries
                    if str(entry.get("target_kind", "") or "") in {"doc", "doc-fragment", "file", "file-fragment"}
                ]
                fragment_link_entries = [
                    dict(entry)
                    for entry in link_entries
                    if str(entry.get("target_kind", "") or "") in {"fragment", "footnote", "doc-fragment", "file-fragment"}
                ]
                external_link_entries = [
                    dict(entry)
                    for entry in link_entries
                    if str(entry.get("target_kind", "") or "") in {"external", "mailto"}
                ]
                footnote_link_entries = [
                    dict(entry)
                    for entry in link_entries
                    if str(entry.get("target_kind", "") or "") == "footnote"
                ]
                inline_link_entries = [
                    dict(entry)
                    for entry in link_entries
                    if str(entry.get("source_kind", "") or "") == "inline"
                ]
                reference_link_entries = [
                    dict(entry)
                    for entry in link_entries
                    if str(entry.get("source_kind", "") or "") == "reference"
                ]
                full_reference_link_entries = [
                    dict(entry)
                    for entry in link_entries
                    if str(entry.get("reference_form", "") or "") == "full"
                ]
                collapsed_reference_link_entries = [
                    dict(entry)
                    for entry in link_entries
                    if str(entry.get("reference_form", "") or "") == "collapsed"
                ]
                shortcut_reference_link_entries = [
                    dict(entry)
                    for entry in link_entries
                    if str(entry.get("reference_form", "") or "") == "shortcut"
                ]
                autolink_entries = [
                    dict(entry)
                    for entry in link_entries
                    if str(entry.get("source_kind", "") or "") == "autolink"
                ]
                footnote_ref_entries = [
                    dict(entry)
                    for entry in link_entries
                    if str(entry.get("source_kind", "") or "") == "footnote"
                ]
                image_matches = md_image_matches(
                    text,
                    defs,
                    masked_spans=masked_spans,
                    next_line=next_line,
                    next_next_line=next_next_line,
                )
                image_entries = []
                for match in image_matches:
                    meta = md_help_link_target_info(str(match.target or ""))
                    source_kind = str(md_help_image_source_kind(text, int(match.start), int(match.end), str(match.kind)))
                    reference_form = str(md_help_image_reference_form(text, int(match.start), int(match.end), str(match.kind)))
                    image_entries.append(
                        {
                            "kind": str(match.kind),
                            "source_kind": str(source_kind),
                            "reference_form": str(reference_form),
                            "start": int(match.start),
                            "end": int(match.end),
                            "alt_start": int(match.alt_start),
                            "alt_end": int(match.alt_end),
                            "alt_text": str(match.alt_text),
                            "target": str(match.target),
                            "target_kind": str(meta.get("target_kind", "") or ""),
                            "target_doc": str(meta.get("doc", "") or ""),
                            "target_fragment": str(meta.get("fragment", "") or ""),
                        }
                    )
                inline_image_entries = [
                    dict(entry)
                    for entry in image_entries
                    if str(entry.get("source_kind", "") or "") == "inline"
                ]
                reference_image_entries = [
                    dict(entry)
                    for entry in image_entries
                    if str(entry.get("source_kind", "") or "") == "reference"
                ]
                full_reference_image_entries = [
                    dict(entry)
                    for entry in image_entries
                    if str(entry.get("reference_form", "") or "") == "full"
                ]
                collapsed_reference_image_entries = [
                    dict(entry)
                    for entry in image_entries
                    if str(entry.get("reference_form", "") or "") == "collapsed"
                ]
                shortcut_reference_image_entries = [
                    dict(entry)
                    for entry in image_entries
                    if str(entry.get("reference_form", "") or "") == "shortcut"
                ]
                local_doc_image_entries = [
                    dict(entry)
                    for entry in image_entries
                    if str(entry.get("target_kind", "") or "") in {"doc", "doc-fragment", "file", "file-fragment"}
                ]
                fragment_image_entries = [
                    dict(entry)
                    for entry in image_entries
                    if str(entry.get("target_kind", "") or "") in {"fragment", "footnote", "doc-fragment", "file-fragment"}
                ]
                external_image_entries = [
                    dict(entry)
                    for entry in image_entries
                    if str(entry.get("target_kind", "") or "") in {"external", "mailto"}
                ]
                footnote_image_entries = [
                    dict(entry)
                    for entry in image_entries
                    if str(entry.get("target_kind", "") or "") == "footnote"
                ]
                code_matches = md_inline_code_matches(text)
                code_entries = [
                    {
                        "kind": str(match.kind),
                        "start": int(match.start),
                        "end": int(match.end),
                        "body_start": int(match.body_start),
                        "body_end": int(match.body_end),
                        "delimiter_length": int(match.delimiter_length),
                        "delimiter_kind": ("single-backtick" if int(match.delimiter_length) == 1 else "multi-backtick"),
                        "text": str(match.text),
                    }
                    for match in code_matches
                ]
                single_backtick_code_entries = [
                    dict(entry)
                    for entry in code_entries
                    if int(entry.get("delimiter_length", 0) or 0) == 1
                ]
                multi_backtick_code_entries = [
                    dict(entry)
                    for entry in code_entries
                    if int(entry.get("delimiter_length", 0) or 0) > 1
                ]
                markup_matches = md_inline_markup_matches(text)
                markup_entries = [
                    {
                        "kind": str(match.kind),
                        "start": int(match.start),
                        "end": int(match.end),
                        "body_start": int(match.body_start),
                        "body_end": int(match.body_end),
                        "delimiter": str(match.delimiter),
                        "delimiter_length": int(match.delimiter_length),
                        "delimiter_kind": str(md_inline_markup_delimiter_kind(str(match.delimiter))),
                        "text": str(match.text),
                    }
                    for match in markup_matches
                ]
                strong_markup_entries = [
                    dict(entry)
                    for entry in markup_entries
                    if str(entry.get("kind", "") or "") == "strong"
                ]
                emphasis_markup_entries = [
                    dict(entry)
                    for entry in markup_entries
                    if str(entry.get("kind", "") or "") == "emphasis"
                ]
                strike_markup_entries = [
                    dict(entry)
                    for entry in markup_entries
                    if str(entry.get("kind", "") or "") == "strike"
                ]
                asterisk_markup_entries = [
                    dict(entry)
                    for entry in markup_entries
                    if str(entry.get("delimiter_kind", "") or "") == "asterisk"
                ]
                underscore_markup_entries = [
                    dict(entry)
                    for entry in markup_entries
                    if str(entry.get("delimiter_kind", "") or "") == "underscore"
                ]
                tilde_markup_entries = [
                    dict(entry)
                    for entry in markup_entries
                    if str(entry.get("delimiter_kind", "") or "") == "tilde"
                ]
                literal_entries = [
                    {
                        "kind": str(match.kind),
                        "start": int(match.start),
                        "end": int(match.end),
                        "text": str(match.text),
                        "detail": str(match.detail),
                    }
                    for match in (
                        md_raw_html_tag_matches(text, masked_spans=masked_spans)
                        + md_escaped_markdown_matches(text, masked_spans=masked_spans)
                    )
                ]
                literal_entries.sort(key=lambda entry: (int(entry["start"]), int(entry["end"])))
                raw_html_literal_entries = [
                    dict(entry)
                    for entry in literal_entries
                    if str(entry.get("kind", "") or "") == "raw-html-tag"
                ]
                escaped_markdown_entries = [
                    dict(entry)
                    for entry in literal_entries
                    if str(entry.get("kind", "") or "") == "escaped-markdown"
                ]
                code_spans = md_inline_code_spans(text)
                code_delim_spans = md_inline_code_delimiter_spans(text)
                strong_spans = md_strong_spans(text)
                emphasis_spans = md_emphasis_spans(text)
                strike_spans = md_strikethrough_spans(text)
                inline_markup_delim_spans = md_inline_markup_delimiter_spans(text)
                pipe_spans = md_table_pipe_spans(text) if table_kind else []
                if table_kind == "delimiter":
                    table_entries = [dict(entry) for entry in md_table_delimiter_entries(text)]
                elif table_kind in {"header", "body"}:
                    table_entries = [
                        {
                            **dict(entry),
                            "kind": f"{table_kind}-cell",
                        }
                        for entry in md_table_cell_entries(text)
                    ]
                if table_entries:
                    alignments = table_alignments_by_line.get(int(line_index), {})
                    table_entries = [
                        {
                            **dict(entry),
                            "align": str(
                                alignments.get(
                                    int(entry.get("column", 0) or 0),
                                    entry.get("align", "default") or "default",
                                )
                            ),
                        }
                        for entry in table_entries
                    ]
                table_header_entries = [
                    dict(entry)
                    for entry in table_entries
                    if str(entry.get("kind", "") or "") == "header-cell"
                ]
                table_body_entries = [
                    dict(entry)
                    for entry in table_entries
                    if str(entry.get("kind", "") or "") == "body-cell"
                ]
                table_delimiter_entries = [
                    dict(entry)
                    for entry in table_entries
                    if str(entry.get("kind", "") or "") == "delimiter-cell"
                ]
                default_aligned_table_entries = [
                    dict(entry)
                    for entry in table_entries
                    if str(entry.get("align", "default") or "default") == "default"
                ]
                left_aligned_table_entries = [
                    dict(entry)
                    for entry in table_entries
                    if str(entry.get("align", "default") or "default") == "left"
                ]
                center_aligned_table_entries = [
                    dict(entry)
                    for entry in table_entries
                    if str(entry.get("align", "default") or "default") == "center"
                ]
                right_aligned_table_entries = [
                    dict(entry)
                    for entry in table_entries
                    if str(entry.get("align", "default") or "default") == "right"
                ]
                list_info = md_list_marker(text, max_leading_spaces=None)
                list_marker_spans = [tuple(int(x) for x in list_info[:2])] if list_info else []
                task_info = md_task_checkbox(text, max_leading_spaces=None)
                task_box_spans = [tuple(int(x) for x in task_info[:2])] if task_info else []
                checked_task_body = []
                task_body = md_task_body_span(text, max_leading_spaces=None)
                if task_info and bool(task_info[2]) and task_body is not None:
                    checked_task_body = [tuple(int(x) for x in task_body)]
                blockquote_info = md_blockquote_prefix(text)
                blockquote_prefix_spans = [tuple(int(x) for x in blockquote_info[:2])] if blockquote_info else []
                blockquote_body = []
                body_span = md_blockquote_body_span(text)
                if blockquote_info and body_span is not None:
                    blockquote_body = [tuple(int(x) for x in body_span)]
                blockquote_alert_info = md_blockquote_alert_marker(text)
                blockquote_alert_spans = [tuple(int(x) for x in blockquote_alert_info[:2])] if blockquote_alert_info else []
                footnote_ref_spans = md_footnote_ref_token_spans(
                    text,
                    footdefs,
                    masked_spans=masked_spans,
                    next_line=next_line,
                    next_next_line=next_next_line,
                )
                autolink_token_spans = md_autolink_token_spans(
                    text,
                    masked_spans=masked_spans,
                    next_line=next_line,
                    next_next_line=next_next_line,
                )
                image_token_spans = md_image_token_spans(
                    text,
                    defs,
                    masked_spans=masked_spans,
                    next_line=next_line,
                    next_next_line=next_next_line,
                )
                link_source_token_spans = md_link_source_token_spans(
                    text,
                    defs,
                    footdefs,
                    masked_spans=masked_spans,
                    next_line=next_line,
                    next_next_line=next_next_line,
                )
                raw_html_tag_spans = md_raw_html_tag_token_spans(
                    text,
                    masked_spans=masked_spans,
                )
                escaped_markdown_spans = md_escaped_markdown_token_spans(
                    text,
                    masked_spans=masked_spans,
                )
                thematic_break_chars = md_thematic_break_char_spans(text) if is_thematic_break else []
                structure_entries = []
                if list_info:
                    a, b, list_kind = list_info
                    list_entry = {
                        "kind": "list-marker",
                        "start": int(a),
                        "end": int(b),
                        "text": str(text[int(a):int(b)]),
                        "list_kind": str(list_kind),
                        "marker": str(text[int(a):int(b)]),
                    }
                    structure_entries.append(list_entry)
                    list_entries.append(dict(list_entry))
                if task_info:
                    a, b, checked = task_info
                    task_entry: dict[str, Any] = {
                        "kind": "task-checkbox",
                        "start": int(a),
                        "end": int(b),
                        "text": str(text[int(a):int(b)]),
                        "checked": 1 if checked else 0,
                    }
                    if list_info:
                        la, lb, list_kind = list_info
                        task_entry["list_kind"] = str(list_kind)
                        task_entry["list_marker"] = str(text[int(la):int(lb)])
                    if task_body is not None:
                        task_entry["body_start"] = int(task_body[0])
                        task_entry["body_end"] = int(task_body[1])
                    structure_entries.append(task_entry)
                    task_entries.append(dict(task_entry))
                checked_task_entries = [
                    dict(entry)
                    for entry in task_entries
                    if int(entry.get("checked", 0) or 0) == 1
                ]
                unchecked_task_entries = [
                    dict(entry)
                    for entry in task_entries
                    if int(entry.get("checked", 0) or 0) == 0
                ]
                bullet_task_entries = [
                    dict(entry)
                    for entry in task_entries
                    if str(entry.get("list_kind", "") or "") == "bullet"
                ]
                ordered_task_entries = [
                    dict(entry)
                    for entry in task_entries
                    if str(entry.get("list_kind", "") or "") == "ordered"
                ]
                if blockquote_info:
                    a, b, depth = blockquote_info
                    quote_entry: dict[str, Any] = {
                        "kind": "blockquote-prefix",
                        "start": int(a),
                        "end": int(b),
                        "text": str(text[int(a):int(b)]),
                        "depth": int(depth),
                    }
                    if body_span is not None:
                        quote_entry["body_start"] = int(body_span[0])
                        quote_entry["body_end"] = int(body_span[1])
                    structure_entries.append(quote_entry)
                    blockquote_entries.append(dict(quote_entry))
                if blockquote_alert_info:
                    a, b, alert_kind = blockquote_alert_info
                    alert_entry = {
                        "kind": "blockquote-alert",
                        "start": int(a),
                        "end": int(b),
                        "text": str(text[int(a):int(b)]),
                        "alert_kind": str(alert_kind),
                    }
                    structure_entries.append(alert_entry)
                    blockquote_alert_entries.append(dict(alert_entry))
                note_blockquote_alert_entries = [
                    dict(entry)
                    for entry in blockquote_alert_entries
                    if str(entry.get("alert_kind", "") or "") == "note"
                ]
                tip_blockquote_alert_entries = [
                    dict(entry)
                    for entry in blockquote_alert_entries
                    if str(entry.get("alert_kind", "") or "") == "tip"
                ]
                important_blockquote_alert_entries = [
                    dict(entry)
                    for entry in blockquote_alert_entries
                    if str(entry.get("alert_kind", "") or "") == "important"
                ]
                warning_blockquote_alert_entries = [
                    dict(entry)
                    for entry in blockquote_alert_entries
                    if str(entry.get("alert_kind", "") or "") == "warning"
                ]
                caution_blockquote_alert_entries = [
                    dict(entry)
                    for entry in blockquote_alert_entries
                    if str(entry.get("alert_kind", "") or "") == "caution"
                ]
                if is_thematic_break:
                    thematic_span = md_thematic_break_span(text)
                    if thematic_span is not None:
                        a, b = thematic_span
                        marker = ""
                        for ch in text[int(a):int(b)]:
                            if ch in '-_*':
                                marker = ch
                                break
                        thematic_entry = {
                            "kind": "thematic-break",
                            "start": int(a),
                            "end": int(b),
                            "text": str(text[int(a):int(b)]),
                            "marker": str(marker),
                            "marker_count": int(len(thematic_break_chars)),
                        }
                        structure_entries.append(thematic_entry)
                        thematic_break_entries.append(dict(thematic_entry))
                structure_entries.sort(key=lambda entry: (int(entry.get("start", 0)), int(entry.get("end", 0)), str(entry.get("kind", ""))))
                definition_marker_spans = [(int(def_col0), int(def_col1))] if int(def_col1) > int(def_col0) else []
                dim_spans = _merge_spans(
                    code_spans
                    + code_delim_spans
                    + strike_spans
                    + inline_markup_delim_spans
                    + pipe_spans
                    + checked_task_body
                    + blockquote_body
                    + masked_spans
                    + image_token_spans
                    + link_source_token_spans
                    + raw_html_tag_spans
                    + escaped_markdown_spans
                )
                bold_spans = _merge_spans(
                    strong_spans
                    + code_delim_spans
                    + list_marker_spans
                    + task_box_spans
                    + blockquote_prefix_spans
                    + blockquote_alert_spans
                    + footnote_ref_spans
                    + autolink_token_spans
                    + thematic_break_chars
                    + definition_marker_spans
                )
                italic_spans = _merge_spans(emphasis_spans)

        row_entry = {
            "view_y": int(view_y),
            "screen_y": int(row["screen_y"]) if "screen_y" in row else int(layout.get("viewport_y", 0) or 0) + int(view_y),
            "line": int(line_index),
            "start_col": int(start_col),
            "text": text,
            "inert": 1 if inert else 0,
            "line_role": str(line_role),
            "heading_level": int(heading_level),
            "table_kind": str(table_kind),
            "definition_role": str(definition_role),
            "link_spans": [[int(a), int(b)] for a, b in link_spans],
            "link_entries": link_entries,
            "local_doc_link_entries": local_doc_link_entries,
            "fragment_link_entries": fragment_link_entries,
            "external_link_entries": external_link_entries,
            "footnote_link_entries": footnote_link_entries,
            "inline_link_entries": inline_link_entries,
            "reference_link_entries": reference_link_entries,
            "full_reference_link_entries": full_reference_link_entries,
            "collapsed_reference_link_entries": collapsed_reference_link_entries,
            "shortcut_reference_link_entries": shortcut_reference_link_entries,
            "autolink_entries": autolink_entries,
            "footnote_ref_entries": footnote_ref_entries,
            "image_entries": image_entries,
            "inline_image_entries": inline_image_entries,
            "reference_image_entries": reference_image_entries,
            "full_reference_image_entries": full_reference_image_entries,
            "collapsed_reference_image_entries": collapsed_reference_image_entries,
            "shortcut_reference_image_entries": shortcut_reference_image_entries,
            "local_doc_image_entries": local_doc_image_entries,
            "fragment_image_entries": fragment_image_entries,
            "external_image_entries": external_image_entries,
            "footnote_image_entries": footnote_image_entries,
            "code_entries": code_entries,
            "single_backtick_code_entries": single_backtick_code_entries,
            "multi_backtick_code_entries": multi_backtick_code_entries,
            "markup_entries": markup_entries,
            "strong_markup_entries": strong_markup_entries,
            "emphasis_markup_entries": emphasis_markup_entries,
            "strike_markup_entries": strike_markup_entries,
            "asterisk_markup_entries": asterisk_markup_entries,
            "underscore_markup_entries": underscore_markup_entries,
            "tilde_markup_entries": tilde_markup_entries,
            "literal_entries": literal_entries,
            "raw_html_literal_entries": raw_html_literal_entries,
            "escaped_markdown_entries": escaped_markdown_entries,
            "table_entries": table_entries,
            "table_header_entries": table_header_entries,
            "table_body_entries": table_body_entries,
            "table_delimiter_entries": table_delimiter_entries,
            "default_aligned_table_entries": default_aligned_table_entries,
            "left_aligned_table_entries": left_aligned_table_entries,
            "center_aligned_table_entries": center_aligned_table_entries,
            "right_aligned_table_entries": right_aligned_table_entries,
            "structure_entries": structure_entries,
            "list_entries": list_entries,
            "task_entries": task_entries,
            "checked_task_entries": checked_task_entries,
            "unchecked_task_entries": unchecked_task_entries,
            "bullet_task_entries": bullet_task_entries,
            "ordered_task_entries": ordered_task_entries,
            "blockquote_entries": blockquote_entries,
            "blockquote_alert_entries": blockquote_alert_entries,
            "note_blockquote_alert_entries": note_blockquote_alert_entries,
            "tip_blockquote_alert_entries": tip_blockquote_alert_entries,
            "important_blockquote_alert_entries": important_blockquote_alert_entries,
            "warning_blockquote_alert_entries": warning_blockquote_alert_entries,
            "caution_blockquote_alert_entries": caution_blockquote_alert_entries,
            "thematic_break_entries": thematic_break_entries,
            "heading_entries": heading_entries,
            "heading_title_entries": heading_title_entries,
            "heading_underline_entries": heading_underline_entries,
            "atx_heading_entries": atx_heading_entries,
            "setext_heading_entries": setext_heading_entries,
            "h1_heading_entries": h1_heading_entries,
            "h2_heading_entries": h2_heading_entries,
            "h3_heading_entries": h3_heading_entries,
            "h4_heading_entries": h4_heading_entries,
            "h5_heading_entries": h5_heading_entries,
            "h6_heading_entries": h6_heading_entries,
            "explicit_fragment_heading_entries": explicit_fragment_heading_entries,
            "auto_fragment_heading_entries": auto_fragment_heading_entries,
            "section_entry": section_entry,
            "definition_entries": definition_entries,
            "reference_definition_entries": reference_definition_entries,
            "reference_definition_cont_entries": reference_definition_cont_entries,
            "footnote_definition_entries": footnote_definition_entries,
            "footnote_definition_cont_entries": footnote_definition_cont_entries,
            "block_entries": block_entries,
            "fenced_code_entries": fenced_code_entries,
            "backtick_fenced_code_entries": backtick_fenced_code_entries,
            "tilde_fenced_code_entries": tilde_fenced_code_entries,
            "language_fenced_code_entries": language_fenced_code_entries,
            "bare_fenced_code_entries": bare_fenced_code_entries,
            "fenced_code_opener_entries": fenced_code_opener_entries,
            "fenced_code_body_entries": fenced_code_body_entries,
            "fenced_code_closer_entries": fenced_code_closer_entries,
            "html_block_entries": html_block_entries,
            "indented_code_entries": indented_code_entries,
            "dim_spans": [[int(a), int(b)] for a, b in dim_spans],
            "bold_spans": [[int(a), int(b)] for a, b in bold_spans],
            "italic_spans": [[int(a), int(b)] for a, b in italic_spans],
            "link_count": int(len(link_spans)),
            "local_doc_link_count": int(len(local_doc_link_entries)),
            "fragment_link_count": int(len(fragment_link_entries)),
            "external_link_count": int(len(external_link_entries)),
            "footnote_link_count": int(len(footnote_link_entries)),
            "inline_link_count": int(len(inline_link_entries)),
            "reference_link_count": int(len(reference_link_entries)),
            "full_reference_link_count": int(len(full_reference_link_entries)),
            "collapsed_reference_link_count": int(len(collapsed_reference_link_entries)),
            "shortcut_reference_link_count": int(len(shortcut_reference_link_entries)),
            "autolink_count": int(len(autolink_entries)),
            "footnote_ref_count": int(len(footnote_ref_entries)),
            "image_count": int(len(image_entries)),
            "inline_image_count": int(len(inline_image_entries)),
            "reference_image_count": int(len(reference_image_entries)),
            "full_reference_image_count": int(len(full_reference_image_entries)),
            "collapsed_reference_image_count": int(len(collapsed_reference_image_entries)),
            "shortcut_reference_image_count": int(len(shortcut_reference_image_entries)),
            "local_doc_image_count": int(len(local_doc_image_entries)),
            "fragment_image_count": int(len(fragment_image_entries)),
            "external_image_count": int(len(external_image_entries)),
            "footnote_image_count": int(len(footnote_image_entries)),
            "code_count": int(len(code_entries)),
            "single_backtick_code_count": int(len(single_backtick_code_entries)),
            "multi_backtick_code_count": int(len(multi_backtick_code_entries)),
            "markup_count": int(len(markup_entries)),
            "strong_markup_count": int(len(strong_markup_entries)),
            "emphasis_markup_count": int(len(emphasis_markup_entries)),
            "strike_markup_count": int(len(strike_markup_entries)),
            "asterisk_markup_count": int(len(asterisk_markup_entries)),
            "underscore_markup_count": int(len(underscore_markup_entries)),
            "tilde_markup_count": int(len(tilde_markup_entries)),
            "literal_count": int(len(literal_entries)),
            "raw_html_literal_count": int(len(raw_html_literal_entries)),
            "escaped_markdown_count": int(len(escaped_markdown_entries)),
            "table_count": int(len(table_entries)),
            "table_header_count": int(len(table_header_entries)),
            "table_body_count": int(len(table_body_entries)),
            "table_delimiter_count": int(len(table_delimiter_entries)),
            "default_aligned_table_count": int(len(default_aligned_table_entries)),
            "left_aligned_table_count": int(len(left_aligned_table_entries)),
            "center_aligned_table_count": int(len(center_aligned_table_entries)),
            "right_aligned_table_count": int(len(right_aligned_table_entries)),
            "structure_count": int(len(structure_entries)),
            "list_count": int(len(list_entries)),
            "bullet_list_count": int(sum(1 for entry in list_entries if str(entry.get("list_kind", "") or "") == "bullet")),
            "ordered_list_count": int(sum(1 for entry in list_entries if str(entry.get("list_kind", "") or "") == "ordered")),
            "task_count": int(len(task_entries)),
            "checked_task_count": int(len(checked_task_entries)),
            "unchecked_task_count": int(len(unchecked_task_entries)),
            "bullet_task_count": int(len(bullet_task_entries)),
            "ordered_task_count": int(len(ordered_task_entries)),
            "blockquote_count": int(len(blockquote_entries)),
            "blockquote_alert_count": int(len(blockquote_alert_entries)),
            "note_blockquote_alert_count": int(len(note_blockquote_alert_entries)),
            "tip_blockquote_alert_count": int(len(tip_blockquote_alert_entries)),
            "important_blockquote_alert_count": int(len(important_blockquote_alert_entries)),
            "warning_blockquote_alert_count": int(len(warning_blockquote_alert_entries)),
            "caution_blockquote_alert_count": int(len(caution_blockquote_alert_entries)),
            "thematic_break_count": int(len(thematic_break_entries)),
            "heading_count": int(len(heading_entries)),
            "heading_title_count": int(len(heading_title_entries)),
            "heading_underline_count": int(len(heading_underline_entries)),
            "atx_heading_count": int(len(atx_heading_entries)),
            "setext_heading_count": int(len(setext_heading_entries)),
            "h1_heading_count": int(len(h1_heading_entries)),
            "h2_heading_count": int(len(h2_heading_entries)),
            "h3_heading_count": int(len(h3_heading_entries)),
            "h4_heading_count": int(len(h4_heading_entries)),
            "h5_heading_count": int(len(h5_heading_entries)),
            "h6_heading_count": int(len(h6_heading_entries)),
            "explicit_fragment_heading_count": int(len(explicit_fragment_heading_entries)),
            "auto_fragment_heading_count": int(len(auto_fragment_heading_entries)),
            "section_count": 1 if section_entry else 0,
            "definition_count": int(len(definition_entries)),
            "reference_definition_count": int(len(reference_definition_entries)),
            "reference_definition_cont_count": int(len(reference_definition_cont_entries)),
            "footnote_definition_count": int(len(footnote_definition_entries)),
            "footnote_definition_cont_count": int(len(footnote_definition_cont_entries)),
            "block_count": int(len(block_entries)),
            "fenced_code_count": int(len(fenced_code_entries)),
            "backtick_fenced_code_count": int(len(backtick_fenced_code_entries)),
            "tilde_fenced_code_count": int(len(tilde_fenced_code_entries)),
            "language_fenced_code_count": int(len(language_fenced_code_entries)),
            "bare_fenced_code_count": int(len(bare_fenced_code_entries)),
            "fenced_code_opener_count": int(len(fenced_code_opener_entries)),
            "fenced_code_body_count": int(len(fenced_code_body_entries)),
            "fenced_code_closer_count": int(len(fenced_code_closer_entries)),
            "html_block_count": int(len(html_block_entries)),
            "indented_code_count": int(len(indented_code_entries)),
            "span_count": int(len(link_spans) + len(dim_spans) + len(bold_spans) + len(italic_spans)),
        }
        if line_role or link_spans or dim_spans or bold_spans or italic_spans:
            cue_rows += 1
        if link_entries:
            link_rows += 1
            link_entry_count += int(len(link_entries))
            if local_doc_link_entries:
                local_doc_link_rows += 1
            if fragment_link_entries:
                fragment_link_rows += 1
            if external_link_entries:
                external_link_rows += 1
            if footnote_link_entries:
                footnote_link_rows += 1
            if inline_link_entries:
                inline_link_rows += 1
            if reference_link_entries:
                reference_link_rows += 1
            if full_reference_link_entries:
                full_reference_link_rows += 1
            if collapsed_reference_link_entries:
                collapsed_reference_link_rows += 1
            if shortcut_reference_link_entries:
                shortcut_reference_link_rows += 1
            if autolink_entries:
                autolink_rows += 1
            if footnote_ref_entries:
                footnote_ref_rows += 1
            for entry in link_entries:
                target_kind = str(entry.get("target_kind", "") or "")
                source_kind = str(entry.get("source_kind", "") or "")
                reference_form = str(entry.get("reference_form", "") or "")
                if target_kind in {"external", "mailto"}:
                    external_link_count += 1
                if target_kind in {"doc", "doc-fragment", "file", "file-fragment"}:
                    local_doc_link_count += 1
                if target_kind in {"fragment", "footnote", "doc-fragment", "file-fragment"}:
                    fragment_link_count += 1
                if target_kind == "footnote":
                    footnote_link_count += 1
                if source_kind == "inline":
                    inline_link_count += 1
                elif source_kind == "reference":
                    reference_link_count += 1
                    if reference_form == "full":
                        full_reference_link_count += 1
                    elif reference_form == "collapsed":
                        collapsed_reference_link_count += 1
                    elif reference_form == "shortcut":
                        shortcut_reference_link_count += 1
                elif source_kind == "autolink":
                    autolink_count += 1
                elif source_kind == "footnote":
                    footnote_ref_count += 1
        if image_entries:
            image_rows += 1
            image_entry_count += int(len(image_entries))
            if inline_image_entries:
                inline_image_rows += 1
            if reference_image_entries:
                reference_image_rows += 1
            if full_reference_image_entries:
                full_reference_image_rows += 1
            if collapsed_reference_image_entries:
                collapsed_reference_image_rows += 1
            if shortcut_reference_image_entries:
                shortcut_reference_image_rows += 1
            if local_doc_image_entries:
                local_doc_image_rows += 1
            if fragment_image_entries:
                fragment_image_rows += 1
            if external_image_entries:
                external_image_rows += 1
            if footnote_image_entries:
                footnote_image_rows += 1
            for entry in image_entries:
                source_kind = str(entry.get("source_kind", "") or "")
                reference_form = str(entry.get("reference_form", "") or "")
                target_kind = str(entry.get("target_kind", "") or "")
                if source_kind == "inline":
                    inline_image_count += 1
                elif source_kind == "reference":
                    reference_image_count += 1
                    if reference_form == "full":
                        full_reference_image_count += 1
                    elif reference_form == "collapsed":
                        collapsed_reference_image_count += 1
                    elif reference_form == "shortcut":
                        shortcut_reference_image_count += 1
                if target_kind in {"external", "mailto"}:
                    external_image_count += 1
                if target_kind in {"doc", "doc-fragment", "file", "file-fragment"}:
                    local_doc_image_count += 1
                if target_kind in {"fragment", "footnote", "doc-fragment", "file-fragment"}:
                    fragment_image_count += 1
                if target_kind == "footnote":
                    footnote_image_count += 1
        if code_entries:
            code_rows += 1
            code_entry_count += int(len(code_entries))
            if single_backtick_code_entries:
                single_backtick_code_rows += 1
            if multi_backtick_code_entries:
                multi_backtick_code_rows += 1
            for entry in code_entries:
                if int(entry.get("delimiter_length", 0) or 0) == 1:
                    single_backtick_code_count += 1
                elif int(entry.get("delimiter_length", 0) or 0) > 1:
                    multi_backtick_code_count += 1
        if markup_entries:
            markup_rows += 1
            markup_entry_count += int(len(markup_entries))
            if strong_markup_entries:
                strong_markup_rows += 1
            if emphasis_markup_entries:
                emphasis_markup_rows += 1
            if strike_markup_entries:
                strike_markup_rows += 1
            if asterisk_markup_entries:
                asterisk_markup_rows += 1
            if underscore_markup_entries:
                underscore_markup_rows += 1
            if tilde_markup_entries:
                tilde_markup_rows += 1
            for entry in markup_entries:
                kind = str(entry.get("kind", "") or "")
                delimiter_kind = str(entry.get("delimiter_kind", "") or "")
                if kind == "strong":
                    strong_entry_count += 1
                elif kind == "emphasis":
                    emphasis_entry_count += 1
                elif kind == "strike":
                    strike_entry_count += 1
                if delimiter_kind == "asterisk":
                    asterisk_markup_count += 1
                elif delimiter_kind == "underscore":
                    underscore_markup_count += 1
                elif delimiter_kind == "tilde":
                    tilde_markup_count += 1
        if literal_entries:
            literal_rows += 1
            literal_entry_count += int(len(literal_entries))
            if raw_html_literal_entries:
                raw_html_rows += 1
            if escaped_markdown_entries:
                escaped_markdown_rows += 1
            for entry in literal_entries:
                kind = str(entry.get("kind", "") or "")
                if kind == "raw-html-tag":
                    raw_html_entry_count += 1
                elif kind == "escaped-markdown":
                    escaped_markdown_entry_count += 1
        if table_entries:
            table_rows += 1
            table_entry_count += int(len(table_entries))
            if table_header_entries:
                table_header_rows += 1
            if table_body_entries:
                table_body_rows += 1
            if table_delimiter_entries:
                table_delimiter_rows += 1
            if default_aligned_table_entries:
                default_aligned_table_rows += 1
            if left_aligned_table_entries:
                left_aligned_table_rows += 1
            if center_aligned_table_entries:
                center_aligned_table_rows += 1
            if right_aligned_table_entries:
                right_aligned_table_rows += 1
            for entry in table_entries:
                kind = str(entry.get("kind", "") or "")
                align = str(entry.get("align", "default") or "default")
                if kind == "header-cell":
                    table_header_cell_count += 1
                elif kind == "body-cell":
                    table_body_cell_count += 1
                elif kind == "delimiter-cell":
                    table_delimiter_cell_count += 1
                if align == "default":
                    default_aligned_table_entry_count += 1
                elif align == "left":
                    left_aligned_table_entry_count += 1
                elif align == "center":
                    center_aligned_table_entry_count += 1
                elif align == "right":
                    right_aligned_table_entry_count += 1
        if structure_entries:
            structure_rows += 1
            structure_entry_count += int(len(structure_entries))
            for entry in structure_entries:
                kind = str(entry.get("kind", "") or "")
                if kind == "list-marker":
                    list_entry_count += 1
                elif kind == "task-checkbox":
                    task_entry_count += 1
                elif kind == "blockquote-prefix":
                    blockquote_entry_count += 1
                elif kind == "blockquote-alert":
                    blockquote_alert_entry_count += 1
                    alert_kind = str(entry.get("alert_kind", "") or "")
                    if alert_kind == "note":
                        note_blockquote_alert_entry_count += 1
                    elif alert_kind == "tip":
                        tip_blockquote_alert_entry_count += 1
                    elif alert_kind == "important":
                        important_blockquote_alert_entry_count += 1
                    elif alert_kind == "warning":
                        warning_blockquote_alert_entry_count += 1
                    elif alert_kind == "caution":
                        caution_blockquote_alert_entry_count += 1
                elif kind == "thematic-break":
                    thematic_break_entry_count += 1
        if list_entries:
            list_rows += 1
            kinds = {str(entry.get("list_kind", "") or "") for entry in list_entries}
            if "bullet" in kinds:
                bullet_list_rows += 1
            if "ordered" in kinds:
                ordered_list_rows += 1
            for entry in list_entries:
                list_kind = str(entry.get("list_kind", "") or "")
                if list_kind == "bullet":
                    bullet_list_entry_count += 1
                elif list_kind == "ordered":
                    ordered_list_entry_count += 1
        if task_entries:
            task_rows += 1
            if checked_task_entries:
                checked_task_rows += 1
            if unchecked_task_entries:
                unchecked_task_rows += 1
            task_kinds = {str(entry.get("list_kind", "") or "") for entry in task_entries}
            if "bullet" in task_kinds:
                bullet_task_rows += 1
            if "ordered" in task_kinds:
                ordered_task_rows += 1
            for entry in task_entries:
                if int(entry.get("checked", 0) or 0) == 1:
                    checked_task_entry_count += 1
                else:
                    unchecked_task_entry_count += 1
                list_kind = str(entry.get("list_kind", "") or "")
                if list_kind == "bullet":
                    bullet_task_entry_count += 1
                elif list_kind == "ordered":
                    ordered_task_entry_count += 1
        if blockquote_entries:
            blockquote_rows += 1
        if blockquote_alert_entries:
            blockquote_alert_rows += 1
            if note_blockquote_alert_entries:
                note_blockquote_alert_rows += 1
            if tip_blockquote_alert_entries:
                tip_blockquote_alert_rows += 1
            if important_blockquote_alert_entries:
                important_blockquote_alert_rows += 1
            if warning_blockquote_alert_entries:
                warning_blockquote_alert_rows += 1
            if caution_blockquote_alert_entries:
                caution_blockquote_alert_rows += 1
        if thematic_break_entries:
            thematic_break_rows += 1
        if heading_entries:
            heading_rows += 1
            heading_entry_count += int(len(heading_entries))
            if heading_title_entries:
                heading_title_rows += 1
            if heading_underline_entries:
                heading_underline_rows += 1
            if atx_heading_entries:
                atx_heading_rows += 1
            if setext_heading_entries:
                setext_heading_rows += 1
            if h1_heading_entries:
                h1_heading_rows += 1
            if h2_heading_entries:
                h2_heading_rows += 1
            if h3_heading_entries:
                h3_heading_rows += 1
            if h4_heading_entries:
                h4_heading_rows += 1
            if h5_heading_entries:
                h5_heading_rows += 1
            if h6_heading_entries:
                h6_heading_rows += 1
            if explicit_fragment_heading_entries:
                explicit_fragment_heading_rows += 1
            if auto_fragment_heading_entries:
                auto_fragment_heading_rows += 1
            for entry in heading_entries:
                role = str(entry.get("role", "") or "")
                source_kind = str(entry.get("source_kind", "") or "")
                level = int(entry.get("level", 0) or 0)
                if role == "title":
                    heading_title_entry_count += 1
                elif role == "underline":
                    heading_underline_entry_count += 1
                if source_kind == "atx":
                    atx_heading_entry_count += 1
                elif source_kind == "setext":
                    setext_heading_entry_count += 1
                if level == 1:
                    h1_heading_entry_count += 1
                elif level == 2:
                    h2_heading_entry_count += 1
                elif level == 3:
                    h3_heading_entry_count += 1
                elif level == 4:
                    h4_heading_entry_count += 1
                elif level == 5:
                    h5_heading_entry_count += 1
                elif level == 6:
                    h6_heading_entry_count += 1
                frag_source = str(entry.get("fragment_source", "") or "")
                if frag_source == "explicit":
                    explicit_fragment_heading_entry_count += 1
                elif frag_source == "auto":
                    auto_fragment_heading_entry_count += 1
        if section_entry:
            section_rows += 1
            path = str(section_entry.get("path", "") or "")
            if path:
                visible_section_paths.add(path)
        if definition_entries:
            definition_rows += 1
            definition_entry_count += int(len(definition_entries))
            if reference_definition_entries:
                reference_definition_rows += 1
            if reference_definition_cont_entries:
                reference_definition_cont_rows += 1
            if footnote_definition_entries:
                footnote_definition_rows += 1
            if footnote_definition_cont_entries:
                footnote_definition_cont_rows += 1
            for entry in definition_entries:
                kind = str(entry.get("kind", "") or "")
                if kind == "reference-definition":
                    reference_definition_entry_count += 1
                elif kind == "reference-definition-cont":
                    reference_definition_cont_entry_count += 1
                elif kind == "footnote-definition":
                    footnote_definition_entry_count += 1
                elif kind == "footnote-definition-cont":
                    footnote_definition_cont_entry_count += 1
        if block_entries:
            block_rows += 1
            block_entry_count += int(len(block_entries))
            if fenced_code_entries:
                fenced_code_rows += 1
            if backtick_fenced_code_entries:
                backtick_fenced_code_rows += 1
            if tilde_fenced_code_entries:
                tilde_fenced_code_rows += 1
            if language_fenced_code_entries:
                language_fenced_code_rows += 1
            if bare_fenced_code_entries:
                bare_fenced_code_rows += 1
            if fenced_code_opener_entries:
                fenced_code_opener_rows += 1
            if fenced_code_body_entries:
                fenced_code_body_rows += 1
            if fenced_code_closer_entries:
                fenced_code_closer_rows += 1
            if html_block_entries:
                html_block_rows += 1
            if indented_code_entries:
                indented_code_rows += 1
            for entry in block_entries:
                kind = str(entry.get("kind", "") or "")
                role = str(entry.get("role", "") or "")
                if kind == "fenced-code":
                    fenced_code_entry_count += 1
                    marker_kind = str(entry.get("marker_kind", "") or "")
                    if marker_kind == "backtick":
                        backtick_fenced_code_count += 1
                    elif marker_kind == "tilde":
                        tilde_fenced_code_count += 1
                    if int(entry.get("has_language", 0) or 0) == 1:
                        language_fenced_code_count += 1
                    else:
                        bare_fenced_code_count += 1
                    if role == "opener":
                        fenced_code_opener_entry_count += 1
                    elif role == "body":
                        fenced_code_body_entry_count += 1
                    elif role == "closer":
                        fenced_code_closer_entry_count += 1
                elif kind == "html-block":
                    html_block_entry_count += 1
                elif kind == "indented-code":
                    indented_code_entry_count += 1
        rows.append(row_entry)

    out.update(
        {
            "rows": rows,
            "row_count": int(len(rows)),
            "cue_rows": int(cue_rows),
            "link_rows": int(link_rows),
            "link_entry_count": int(link_entry_count),
            "local_doc_link_rows": int(local_doc_link_rows),
            "fragment_link_rows": int(fragment_link_rows),
            "external_link_rows": int(external_link_rows),
            "footnote_link_rows": int(footnote_link_rows),
            "inline_link_rows": int(inline_link_rows),
            "reference_link_rows": int(reference_link_rows),
            "full_reference_link_rows": int(full_reference_link_rows),
            "collapsed_reference_link_rows": int(collapsed_reference_link_rows),
            "shortcut_reference_link_rows": int(shortcut_reference_link_rows),
            "autolink_rows": int(autolink_rows),
            "footnote_ref_rows": int(footnote_ref_rows),
            "local_doc_link_count": int(local_doc_link_count),
            "fragment_link_count": int(fragment_link_count),
            "external_link_count": int(external_link_count),
            "footnote_link_count": int(footnote_link_count),
            "inline_link_count": int(inline_link_count),
            "reference_link_count": int(reference_link_count),
            "full_reference_link_count": int(full_reference_link_count),
            "collapsed_reference_link_count": int(collapsed_reference_link_count),
            "shortcut_reference_link_count": int(shortcut_reference_link_count),
            "autolink_count": int(autolink_count),
            "footnote_ref_count": int(footnote_ref_count),
            "image_rows": int(image_rows),
            "image_entry_count": int(image_entry_count),
            "inline_image_rows": int(inline_image_rows),
            "reference_image_rows": int(reference_image_rows),
            "full_reference_image_rows": int(full_reference_image_rows),
            "collapsed_reference_image_rows": int(collapsed_reference_image_rows),
            "shortcut_reference_image_rows": int(shortcut_reference_image_rows),
            "local_doc_image_rows": int(local_doc_image_rows),
            "fragment_image_rows": int(fragment_image_rows),
            "external_image_rows": int(external_image_rows),
            "footnote_image_rows": int(footnote_image_rows),
            "inline_image_count": int(inline_image_count),
            "reference_image_count": int(reference_image_count),
            "full_reference_image_count": int(full_reference_image_count),
            "collapsed_reference_image_count": int(collapsed_reference_image_count),
            "shortcut_reference_image_count": int(shortcut_reference_image_count),
            "local_doc_image_count": int(local_doc_image_count),
            "fragment_image_count": int(fragment_image_count),
            "external_image_count": int(external_image_count),
            "footnote_image_count": int(footnote_image_count),
            "code_rows": int(code_rows),
            "code_entry_count": int(code_entry_count),
            "single_backtick_code_rows": int(single_backtick_code_rows),
            "multi_backtick_code_rows": int(multi_backtick_code_rows),
            "single_backtick_code_count": int(single_backtick_code_count),
            "multi_backtick_code_count": int(multi_backtick_code_count),
            "markup_rows": int(markup_rows),
            "markup_entry_count": int(markup_entry_count),
            "strong_markup_rows": int(strong_markup_rows),
            "emphasis_markup_rows": int(emphasis_markup_rows),
            "strike_markup_rows": int(strike_markup_rows),
            "asterisk_markup_rows": int(asterisk_markup_rows),
            "underscore_markup_rows": int(underscore_markup_rows),
            "tilde_markup_rows": int(tilde_markup_rows),
            "strong_entry_count": int(strong_entry_count),
            "emphasis_entry_count": int(emphasis_entry_count),
            "strike_entry_count": int(strike_entry_count),
            "asterisk_markup_count": int(asterisk_markup_count),
            "underscore_markup_count": int(underscore_markup_count),
            "tilde_markup_count": int(tilde_markup_count),
            "table_rows": int(table_rows),
            "table_entry_count": int(table_entry_count),
            "table_header_rows": int(table_header_rows),
            "table_body_rows": int(table_body_rows),
            "table_delimiter_rows": int(table_delimiter_rows),
            "default_aligned_table_rows": int(default_aligned_table_rows),
            "left_aligned_table_rows": int(left_aligned_table_rows),
            "center_aligned_table_rows": int(center_aligned_table_rows),
            "right_aligned_table_rows": int(right_aligned_table_rows),
            "table_header_cell_count": int(table_header_cell_count),
            "table_body_cell_count": int(table_body_cell_count),
            "table_delimiter_cell_count": int(table_delimiter_cell_count),
            "default_aligned_table_entry_count": int(default_aligned_table_entry_count),
            "left_aligned_table_entry_count": int(left_aligned_table_entry_count),
            "center_aligned_table_entry_count": int(center_aligned_table_entry_count),
            "right_aligned_table_entry_count": int(right_aligned_table_entry_count),
            "structure_rows": int(structure_rows),
            "structure_entry_count": int(structure_entry_count),
            "list_rows": int(list_rows),
            "list_entry_count": int(list_entry_count),
            "bullet_list_rows": int(bullet_list_rows),
            "ordered_list_rows": int(ordered_list_rows),
            "bullet_list_entry_count": int(bullet_list_entry_count),
            "ordered_list_entry_count": int(ordered_list_entry_count),
            "task_rows": int(task_rows),
            "task_entry_count": int(task_entry_count),
            "checked_task_rows": int(checked_task_rows),
            "unchecked_task_rows": int(unchecked_task_rows),
            "checked_task_entry_count": int(checked_task_entry_count),
            "unchecked_task_entry_count": int(unchecked_task_entry_count),
            "bullet_task_rows": int(bullet_task_rows),
            "ordered_task_rows": int(ordered_task_rows),
            "bullet_task_entry_count": int(bullet_task_entry_count),
            "ordered_task_entry_count": int(ordered_task_entry_count),
            "blockquote_rows": int(blockquote_rows),
            "blockquote_entry_count": int(blockquote_entry_count),
            "blockquote_alert_rows": int(blockquote_alert_rows),
            "blockquote_alert_entry_count": int(blockquote_alert_entry_count),
            "note_blockquote_alert_rows": int(note_blockquote_alert_rows),
            "tip_blockquote_alert_rows": int(tip_blockquote_alert_rows),
            "important_blockquote_alert_rows": int(important_blockquote_alert_rows),
            "warning_blockquote_alert_rows": int(warning_blockquote_alert_rows),
            "caution_blockquote_alert_rows": int(caution_blockquote_alert_rows),
            "note_blockquote_alert_entry_count": int(note_blockquote_alert_entry_count),
            "tip_blockquote_alert_entry_count": int(tip_blockquote_alert_entry_count),
            "important_blockquote_alert_entry_count": int(important_blockquote_alert_entry_count),
            "warning_blockquote_alert_entry_count": int(warning_blockquote_alert_entry_count),
            "caution_blockquote_alert_entry_count": int(caution_blockquote_alert_entry_count),
            "thematic_break_rows": int(thematic_break_rows),
            "thematic_break_entry_count": int(thematic_break_entry_count),
            "heading_rows": int(heading_rows),
            "heading_entry_count": int(heading_entry_count),
            "heading_title_rows": int(heading_title_rows),
            "heading_underline_rows": int(heading_underline_rows),
            "atx_heading_rows": int(atx_heading_rows),
            "setext_heading_rows": int(setext_heading_rows),
            "h1_heading_rows": int(h1_heading_rows),
            "h2_heading_rows": int(h2_heading_rows),
            "h3_heading_rows": int(h3_heading_rows),
            "h4_heading_rows": int(h4_heading_rows),
            "h5_heading_rows": int(h5_heading_rows),
            "h6_heading_rows": int(h6_heading_rows),
            "explicit_fragment_heading_rows": int(explicit_fragment_heading_rows),
            "auto_fragment_heading_rows": int(auto_fragment_heading_rows),
            "heading_title_entry_count": int(heading_title_entry_count),
            "heading_underline_entry_count": int(heading_underline_entry_count),
            "atx_heading_entry_count": int(atx_heading_entry_count),
            "setext_heading_entry_count": int(setext_heading_entry_count),
            "h1_heading_entry_count": int(h1_heading_entry_count),
            "h2_heading_entry_count": int(h2_heading_entry_count),
            "h3_heading_entry_count": int(h3_heading_entry_count),
            "h4_heading_entry_count": int(h4_heading_entry_count),
            "h5_heading_entry_count": int(h5_heading_entry_count),
            "h6_heading_entry_count": int(h6_heading_entry_count),
            "explicit_fragment_heading_entry_count": int(explicit_fragment_heading_entry_count),
            "auto_fragment_heading_entry_count": int(auto_fragment_heading_entry_count),
            "section_rows": int(section_rows),
            "section_distinct_count": int(len(visible_section_paths)),
            "definition_rows": int(definition_rows),
            "definition_entry_count": int(definition_entry_count),
            "reference_definition_rows": int(reference_definition_rows),
            "reference_definition_cont_rows": int(reference_definition_cont_rows),
            "footnote_definition_rows": int(footnote_definition_rows),
            "footnote_definition_cont_rows": int(footnote_definition_cont_rows),
            "reference_definition_entry_count": int(reference_definition_entry_count),
            "reference_definition_cont_entry_count": int(reference_definition_cont_entry_count),
            "footnote_definition_entry_count": int(footnote_definition_entry_count),
            "footnote_definition_cont_entry_count": int(footnote_definition_cont_entry_count),
            "block_rows": int(block_rows),
            "block_entry_count": int(block_entry_count),
            "backtick_fenced_code_rows": int(backtick_fenced_code_rows),
            "tilde_fenced_code_rows": int(tilde_fenced_code_rows),
            "language_fenced_code_rows": int(language_fenced_code_rows),
            "bare_fenced_code_rows": int(bare_fenced_code_rows),
            "backtick_fenced_code_count": int(backtick_fenced_code_count),
            "tilde_fenced_code_count": int(tilde_fenced_code_count),
            "language_fenced_code_count": int(language_fenced_code_count),
            "bare_fenced_code_count": int(bare_fenced_code_count),
            "fenced_code_rows": int(fenced_code_rows),
            "fenced_code_opener_rows": int(fenced_code_opener_rows),
            "fenced_code_body_rows": int(fenced_code_body_rows),
            "fenced_code_closer_rows": int(fenced_code_closer_rows),
            "html_block_rows": int(html_block_rows),
            "indented_code_rows": int(indented_code_rows),
            "fenced_code_entry_count": int(fenced_code_entry_count),
            "fenced_code_opener_entry_count": int(fenced_code_opener_entry_count),
            "fenced_code_body_entry_count": int(fenced_code_body_entry_count),
            "fenced_code_closer_entry_count": int(fenced_code_closer_entry_count),
            "html_block_entry_count": int(html_block_entry_count),
            "indented_code_entry_count": int(indented_code_entry_count),
            "literal_rows": int(literal_rows),
            "literal_entry_count": int(literal_entry_count),
            "raw_html_rows": int(raw_html_rows),
            "escaped_markdown_rows": int(escaped_markdown_rows),
            "raw_html_entry_count": int(raw_html_entry_count),
            "escaped_markdown_entry_count": int(escaped_markdown_entry_count),
        }
    )
    return out
