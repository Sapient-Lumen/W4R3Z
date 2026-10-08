from __future__ import annotations

import os

from micromax_editor.prompt_completion import (
    merge_completion_candidates,
    overlay_suggestion_rows,
    path_completion_candidates,
    path_needs_completion_quotes,
    prompt_token_context,
    scan_prompt_tokens,
    should_prefer_exact_common_candidate,
)


def test_scan_prompt_tokens_keeps_quoted_spaces_and_offsets() -> None:
    spans = scan_prompt_tokens('open "alpha beta.txt" next')
    assert spans == [
        ('open', 0, 4),
        ('"alpha beta.txt"', 5, 21),
        ('next', 22, 26),
    ]


def test_prompt_token_context_preserves_helpjump_tail_as_one_target() -> None:
    ctx = prompt_token_context('helpjump first heading words', len('helpjump first heading'))
    assert ctx.cmd == 'helpjump'
    assert ctx.tok_i == 2
    assert ctx.token_for_completion == 1
    assert ctx.prefix == 'first heading'
    assert ctx.tok_start == len('helpjump ')


def test_path_completion_quotes_names_that_shlex_would_misparse(tmp_path, monkeypatch) -> None:
    (tmp_path / "a'b.txt").write_text('x')
    (tmp_path / 'a\\b.txt').write_text('y')
    monkeypatch.chdir(tmp_path)

    assert path_needs_completion_quotes("a'b.txt")
    assert path_needs_completion_quotes('a\\b.txt')
    assert path_completion_candidates('a\'', at_eol=True) == ['"a\'b.txt" ']
    assert path_completion_candidates('a\\', at_eol=True) == ['"a\\\\b.txt" ']


def test_path_completion_switches_from_single_quotes_when_needed(tmp_path, monkeypatch) -> None:
    (tmp_path / "a'b.txt").write_text('x')
    monkeypatch.chdir(tmp_path)

    assert path_completion_candidates('a', at_eol=True, quote="'") == ['"a\'b.txt" ']


def test_path_completion_sorts_before_limit_with_dirs_first(tmp_path, monkeypatch) -> None:
    (tmp_path / 'b-file').write_text('x')
    (tmp_path / 'a-file').write_text('x')
    (tmp_path / 'z-dir').mkdir()
    (tmp_path / 'a-dir').mkdir()
    monkeypatch.chdir(tmp_path)

    rows = path_completion_candidates('', at_eol=True)
    assert rows[:4] == [f'a-dir{os.sep}', f'z-dir{os.sep}', 'a-file ', 'b-file ']


def test_overlay_suggestion_rows_only_replaces_provided_metadata() -> None:
    rows = [
        ['alpha ', 'command', 'builtin', 'old info'],
        ['beta ', 'command', 'builtin', 'old beta'],
    ]
    out = overlay_suggestion_rows(
        rows,
        ['alpha ', 'beta '],
        ['beta '],
        [['ignored insert', '', 'plugin', 'new beta']],
    )
    assert out == [
        ['alpha ', 'command', 'builtin', 'old info'],
        ['beta ', 'command', 'plugin', 'new beta'],
    ]


def test_should_prefer_exact_common_candidate_is_bounded_to_helper_variants() -> None:
    assert should_prefer_exact_common_candidate('help', ['help', 'helppick'], cmd='')
    assert not should_prefer_exact_common_candidate('toggle', ['toggle', 'togglelocal'], cmd='')
    assert should_prefer_exact_common_candidate('jump', ['jump', 'jumppick'], cmd='')


def test_prompt_token_context_unescapes_double_quoted_path_prefix_for_next_completion() -> None:
    ctx = prompt_token_context('open "alpha\\\\dir/file', len('open "alpha\\\\dir/file'))
    assert ctx.quote == '"'
    assert ctx.tok_inner == 'alpha\\dir/file'


def test_prompt_token_context_unescapes_quoted_quote_path_prefix_for_next_completion() -> None:
    ctx = prompt_token_context('open "alpha\\"dir/file', len('open "alpha\\"dir/file'))
    assert ctx.quote == '"'
    assert ctx.tok_inner == 'alpha"dir/file'


def test_plan_prompt_completion_application_unique_candidate_replaces_token() -> None:
    from micromax_editor.prompt_completion import plan_prompt_completion_application

    plan = plan_prompt_completion_application(
        text='help he',
        token_start=len('help '),
        token_end=len('help he'),
        prefix='he',
        candidates=['help '],
        fuzzy_candidates=False,
        cmd='help',
    )
    assert plan is not None
    assert plan.replacement_text == 'help help '
    assert plan.cursor == len('help help ')
    assert plan.suggestions == ()


def test_plan_prompt_completion_application_common_prefix_opens_session() -> None:
    from micromax_editor.prompt_completion import plan_prompt_completion_application

    plan = plan_prompt_completion_application(
        text='open alp',
        token_start=len('open '),
        token_end=len('open alp'),
        prefix='alp',
        candidates=['alpha-one ', 'alpha-two '],
        fuzzy_candidates=False,
        cmd='open',
    )
    assert plan is not None
    assert plan.replacement_text == 'open alpha-'
    assert plan.cursor == len('open alpha-')
    assert plan.suggestions == ('alpha-one ', 'alpha-two ')
    assert plan.suggestion_start == len('open ')
    assert plan.suggestion_end == len('open alpha-')


def test_plan_prompt_completion_application_exact_common_candidate_snap_is_bounded() -> None:
    from micromax_editor.prompt_completion import plan_prompt_completion_application

    plan = plan_prompt_completion_application(
        text='he',
        token_start=0,
        token_end=2,
        prefix='he',
        candidates=['help ', 'helppick '],
        fuzzy_candidates=False,
        cmd='',
    )
    assert plan is not None
    assert plan.replacement_text == 'help '
    assert plan.suggestions == ()


def test_merge_completion_candidates_add_mode_keeps_builtin_path_provenance() -> None:
    merged = merge_completion_candidates(
        base_candidates=['alpha.txt ', 'alpha-dir/'],
        fuzzy_candidates=False,
        path_mode=True,
        extra_candidates=['archive '],
        extra_mode=1,
    )
    assert merged.candidates == ('alpha.txt ', 'alpha-dir/', 'archive ')
    assert merged.path_candidates == frozenset({'alpha.txt ', 'alpha-dir/'})
    assert merged.path_mode is True


def test_merge_completion_candidates_add_mode_deduplicates_plugin_candidates() -> None:
    merged = merge_completion_candidates(
        base_candidates=["alpha.txt ", "adir/"],
        path_mode=True,
        extra_candidates=["archive ", "adir/"],
        extra_mode=1,
    )

    assert merged.candidates == ("alpha.txt ", "adir/", "archive ")
    assert merged.path_candidates == frozenset({"alpha.txt ", "adir/"})


def test_merge_completion_candidates_replace_mode_clears_path_provenance() -> None:
    merged = merge_completion_candidates(
        base_candidates=["alpha.txt "],
        fuzzy_candidates=True,
        path_mode=True,
        extra_candidates=["plugin-only "],
        extra_mode=2,
    )

    assert merged.candidates == ("plugin-only ",)
    assert merged.fuzzy_candidates is False
    assert merged.path_candidates == frozenset()
    assert merged.path_mode is False

