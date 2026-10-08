from __future__ import annotations

from micromax_editor.tui import md_list_marker


def test_md_list_marker_accepts_common_bullet_and_ordered_forms() -> None:
    assert md_list_marker('- bullet') == (0, 1, 'bullet')
    assert md_list_marker('  + plus bullet') == (2, 3, 'bullet')
    assert md_list_marker('   12. ordered') == (3, 6, 'ordered')
    assert md_list_marker('1) alt ordered') == (0, 2, 'ordered')
    assert md_list_marker('*') == (0, 1, 'bullet')


def test_md_list_marker_rejects_non_list_or_codeish_lines() -> None:
    assert md_list_marker('plain text') is None
    assert md_list_marker('----') is None
    assert md_list_marker('1.item') is None
    assert md_list_marker('    - code-ish indent') is None
    assert md_list_marker('1234567890. too many digits') is None


def test_md_list_marker_can_opt_into_nested_source_view_mode() -> None:
    assert md_list_marker('    - nested bullet', max_leading_spaces=None) == (4, 5, 'bullet')
    assert md_list_marker('         12. nested ordered', max_leading_spaces=None) == (9, 12, 'ordered')
