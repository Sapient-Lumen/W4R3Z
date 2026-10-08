from __future__ import annotations

from micromax_editor.commandbar import Prompt
from micromax_editor.prompt_refresh import begin_prompt_suggestion_rows, refresh_prompt_suggestion_rows


def test_begin_prompt_suggestion_rows_uses_first_cell_as_candidate() -> None:
    prompt = Prompt(kind="buffer")
    prompt.prefill("alp")

    assert begin_prompt_suggestion_rows(prompt, [["alpha", "buffer", "active", "3 lines"]]) is True

    assert prompt.suggestions == ["alpha"]
    assert prompt.suggestion_rows == [["alpha", "buffer", "active", "3 lines"]]
    assert prompt.suggest_start == 0
    assert prompt.suggest_end == 3
    assert prompt.suggest_base == "alp"


def test_begin_prompt_suggestion_rows_returns_false_without_rows() -> None:
    prompt = Prompt(kind="buffer")
    prompt.prefill("alp")

    assert begin_prompt_suggestion_rows(prompt, []) is False
    assert prompt.suggestions == []
    assert prompt.suggestion_rows == []


def test_refresh_prompt_suggestion_rows_does_not_call_wrong_kind_provider() -> None:
    prompt = Prompt(kind="mark")
    prompt.prefill("x")

    def fail_provider(_query: str) -> list[list[str]]:
        raise AssertionError("provider should not be called for a different prompt kind")

    assert refresh_prompt_suggestion_rows(prompt, kind="buffer", row_provider=fail_provider) is False


def test_refresh_prompt_suggestion_rows_uses_prompt_text_for_matching_kind() -> None:
    prompt = Prompt(kind="buffer")
    prompt.prefill("alp")
    seen_queries: list[str] = []

    def row_provider(query: str) -> list[list[str]]:
        seen_queries.append(query)
        return [[query + "ha", "buffer", "active", "detail"]]

    assert refresh_prompt_suggestion_rows(prompt, kind="buffer", row_provider=row_provider) is True

    assert seen_queries == ["alp"]
    assert prompt.suggestions == ["alpha"]
    assert prompt.suggestion_rows == [["alpha", "buffer", "active", "detail"]]


def test_prompt_rows_from_grouped_sections_applies_empty_query_browse_budget() -> None:
    from micromax_editor.prompt_refresh import prompt_rows_from_grouped_sections
    from micromax_editor.prompt_rows import flatten_grouped_prompt_sections

    seen_queries: list[str] = []

    def section_provider(query: str) -> list[list[object]]:
        seen_queries.append(query)
        return [
            ["A", [["a1", "kind", "menu", "info"], ["a2", "kind", "menu", "info"]]],
            ["B", [["b1", "kind", "menu", "info"]]],
        ]

    rows = prompt_rows_from_grouped_sections(
        "   ",
        limit=2,
        section_provider=section_provider,
        flatten_sections=flatten_grouped_prompt_sections,
    )

    assert seen_queries == [""]
    assert [row[0] for row in rows] == ["a1", "b1"]


def test_prompt_rows_from_grouped_sections_uses_linear_budget_for_queries() -> None:
    from micromax_editor.prompt_refresh import prompt_rows_from_grouped_sections
    from micromax_editor.prompt_rows import flatten_grouped_prompt_sections

    def section_provider(query: str) -> list[list[object]]:
        assert query == "hel"
        return [
            ["A", [["a1", "kind", "menu", "info"], ["a2", "kind", "menu", "info"]]],
            ["B", [["b1", "kind", "menu", "info"]]],
        ]

    rows = prompt_rows_from_grouped_sections(
        "  hel ",
        limit=2,
        section_provider=section_provider,
        flatten_sections=flatten_grouped_prompt_sections,
    )

    assert [row[0] for row in rows] == ["a1", "a2"]


def test_prompt_rows_from_direct_or_grouped_sections_routes_query_and_browse() -> None:
    from micromax_editor.prompt_refresh import prompt_rows_from_direct_or_grouped_sections
    from micromax_editor.prompt_rows import flatten_grouped_prompt_sections

    direct_calls: list[tuple[str, int]] = []
    section_calls: list[str] = []

    def direct_provider(query: str, *, limit: int) -> list[list[str]]:
        direct_calls.append((query, limit))
        return [[query, "direct", "", ""]]

    def section_provider(query: str) -> list[list[object]]:
        section_calls.append(query)
        return [["Browse", [["browse-a", "kind", "menu", "info"], ["browse-b", "kind", "menu", "info"]]]]

    assert prompt_rows_from_direct_or_grouped_sections(
        "  doc ",
        limit=3,
        direct_provider=direct_provider,
        section_provider=section_provider,
        flatten_sections=flatten_grouped_prompt_sections,
    ) == [["doc", "direct", "", ""]]
    assert direct_calls == [("doc", 3)]
    assert section_calls == []

    browse = prompt_rows_from_direct_or_grouped_sections(
        "",
        limit=1,
        direct_provider=direct_provider,
        section_provider=section_provider,
        flatten_sections=flatten_grouped_prompt_sections,
    )
    assert [row[0] for row in browse] == ["browse-a"]
    assert section_calls == [""]


def test_resolve_prompt_target_keeps_selected_suggestion_until_text_changes() -> None:
    from micromax_editor.prompt_refresh import resolve_prompt_target

    prompt = Prompt(kind="topic")
    prompt.prefill("alp")
    prompt.begin_suggestions(
        ["alpha", "beta"],
        start=0,
        end=3,
        rows=[["alpha", "topic", "", ""], ["beta", "topic", "", ""]],
    )
    prompt.suggest_index = 1

    assert resolve_prompt_target(prompt, prompt.text) == "beta"

    prompt.text = "gamma"
    assert resolve_prompt_target(prompt, prompt.text) == "gamma"


def test_resolve_prompt_target_uses_exact_before_apropos_rows() -> None:
    from micromax_editor.prompt_refresh import resolve_prompt_target

    prompt = Prompt(kind="buffer")
    prompt.prefill("scratch")
    calls: list[str] = []

    def row_provider(query: str) -> list[list[str]]:
        calls.append(query)
        return [["apropos", "buffer", "", ""]]

    assert resolve_prompt_target(
        prompt,
        prompt.text,
        row_provider=row_provider,
        exact=lambda query: query == "scratch",
    ) == "scratch"
    assert calls == []


def test_resolve_prompt_target_can_read_nonzero_row_column() -> None:
    from micromax_editor.prompt_refresh import resolve_prompt_target

    prompt = Prompt(kind="helplink")
    prompt.prefill("install")
    prompt.begin_suggestions(
        ["Install guide"],
        start=0,
        end=7,
        rows=[["Install guide", "link", "docs/install.md", "1:1"]],
    )

    assert resolve_prompt_target(prompt, prompt.text, row_column=2) == "docs/install.md"

    prompt = Prompt(kind="helplink")
    prompt.prefill("guide")
    assert resolve_prompt_target(
        prompt,
        prompt.text,
        row_provider=lambda query: [["Guide", "link", f"{query}.md", ""]],
        row_column=2,
    ) == "guide.md"


def test_resolve_prompt_row_keeps_selected_row_until_text_changes() -> None:
    from micromax_editor.prompt_refresh import resolve_prompt_row

    prompt = Prompt(kind="helpnav")
    prompt.prefill("gui")
    prompt.begin_suggestions(
        ["Guide", "Links"],
        start=0,
        end=3,
        rows=[
            ["Guide", "heading", "", "3:1"],
            ["Links", "heading", "", "9:2"],
        ],
    )
    prompt.suggest_index = 1
    calls: list[str] = []

    def row_provider(query: str) -> list[list[str]]:
        calls.append(query)
        return [["Fresh", "heading", "", "12:4"]]

    assert resolve_prompt_row(prompt, prompt.text, row_provider=row_provider) == ["Links", "heading", "", "9:2"]
    assert calls == []

    prompt.text = "fresh"
    assert resolve_prompt_row(prompt, prompt.text, row_provider=row_provider) == ["Fresh", "heading", "", "12:4"]
    assert calls == ["fresh"]


def test_resolve_prompt_row_uses_first_row_for_typed_query() -> None:
    from micromax_editor.prompt_refresh import resolve_prompt_row

    prompt = Prompt(kind="helpoutline")
    prompt.prefill("install")

    assert resolve_prompt_row(
        prompt,
        prompt.text,
        row_provider=lambda query: [["Install", "heading", "", "7:3"]],
    ) == ["Install", "heading", "", "7:3"]


def test_parse_prompt_linecol_accepts_line_or_line_col() -> None:
    from micromax_editor.prompt_refresh import parse_prompt_linecol

    assert parse_prompt_linecol("8") == (8, 1)
    assert parse_prompt_linecol("8:5") == (8, 5)
    assert parse_prompt_linecol("bad") is None
    assert parse_prompt_linecol("") is None
