from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from micromax.portability_suite import (
    BOOT_STDLIB_PORTABILITY_MANIFEST,
    boot_stdlib_manifest_inventory,
    boot_stdlib_portability_manifest,
    boot_stdlib_word_specs,
    portability_case_name_args,
    portability_retest_argv,
    portability_retest_command,
    portability_retest_env,
    portability_retest_metadata,
    selected_boot_stdlib_word_inventory,
    load_portability_cases,
    portability_case_record,
    portability_inventory,
    portability_summary,
    run_portability_cases,
    select_boot_stdlib_manifest_entries,
    select_portability_cases,
)

ROOT = Path(__file__).resolve().parents[1]


def test_default_portability_corpus_runs_cleanly() -> None:
    cases = load_portability_cases()
    assert len(cases) >= 10

    results = run_portability_cases(cases)
    failed = [r for r in results if not r.ok]
    assert failed == []


def test_portability_corpus_includes_kernel_and_stdlib_coverage() -> None:
    cases = load_portability_cases()
    cats = {str(c.get('category') or '') for c in cases}
    names = {str(c.get('name') or '') for c in cases}
    assert 'kernel' in cats
    assert 'stdlib' in cats
    assert any('expect_error_contains' in c for c in cases)
    assert {
        'return-stack-roundtrip',
        'return-stack-peek-and-depth',
        'return-stack-lifo-peek-roundtrip',
        'pick-zero-equivalent-to-dup',
        'pick-one-equivalent-to-over',
        'pick-two-copies-third-item',
        'pick-three-copies-fourth-item',
        'pick-four-copies-fifth-item',
        'roll-zero-is-null-op',
        'roll-one-equivalent-to-swap',
        'roll-two-equivalent-to-rot',
        'roll-three-rotates-four-items',
        'roll-four-rotates-five-items',
        'pick-negative-index-errors',
        'roll-negative-index-errors',
        'pick-underflow-errors-on-too-shallow-stack',
        'roll-underflow-errors-on-too-shallow-stack',
        'execute-xt',
        'wordlist-search-order-lookup',
        'module-in-defines-into-existing-module',
        'set-current-roundtrip',
        'while-loop-increments-to-bound',
        'when-false-skips-quote',
        'zero-equals-predicate',
        'catch-success-returns-zero-ior',
        'catch-success-hides-exception-frame-from-rdepth',
        'catch-success-counts-only-user-return-stack-items',
        'catch-throw-restores-return-stack-depth',
        'catch-throw-preserves-outer-user-return-stack-items',
        'catch-throw-preserves-outer-return-stack-value',
        'catch-throw-preserves-outer-return-stack-order',
        'catch-success-preserves-outer-return-stack-order',
        'nested-catch-success-preserves-outer-return-stack-order',
        'nested-catch-success-counts-only-outer-user-return-stack-items',
        'nested-catch-throw-counts-only-outer-user-return-stack-items',
        'nested-catch-throw-preserves-outer-visible-return-stack-value',
        'nested-catch-success-preserves-outer-visible-return-stack-value',
        'constant-pushes-bound-value',
        'variable-store-and-fetch',
        'list-clone-pop-leaves-original-intact',
        'map-delete-removes-key',
        'map-merge-overrides-destination',
        'map-keys-return-sorted-list',
        'map-items-return-sorted-pairs',
        'map-items-empty-map-returns-empty-list',
        'to-int-parses-string',
        'to-str-renders-list',
        'string-typed-less-than',
        'locals-shadow-outer-definition',
        'session-local-store-query-and-unlocal',
        'type-predicates-recognize-basic-values',
        'map-has-key-predicate',
        'get-current-reflects-set-current',
        'definitions-follows-top-of-search-order',
        'definitions-current-survives-later-set-order',
        'also-duplicates-top-search-order-entry',
        'only-resets-search-order-length-to-one',
        'dict-version-bumps-on-definition',
        'dict-version-stable-across-find',
        'dict-version-stable-across-get-order',
        'host-api-version-string',
        'host-feature-present-is-true',
        'host-feature-missing-is-false',
        'host-features-return-sorted-list',
        'host-features-deduplicate-seeded-inventory',
        'host-features-empty-list',
        'stdlib-qdup-zero-leaves-zero',
        'stdlib-qdup-nonzero-duplicates',
        'stdlib-one-plus-increments',
        'stdlib-one-minus-decrements',
        'stdlib-two-times-doubles',
        'stdlib-two-slash-halves-with-sign-propagation',
        'stdlib-nip-drops-under-top-item',
        'stdlib-tuck-copies-top-under-next',
        'stdlib-2dup-copies-pair',
        'stdlib-2drop-removes-pair',
        'stdlib-2nip-drops-underlying-pair',
        'stdlib-2over-copies-leading-pair',
        'stdlib-2tuck-tucks-top-pair-under-copy',
        'stdlib-2swap-exchanges-top-pairs',
        'stdlib-zero-greater-predicate',
        'stdlib-zero-not-equals-predicate',
        'stdlib-not-equals-predicate',
        'stdlib-not-equals-handles-strings',
        'stdlib-negate-zero-is-zero',
        'stdlib-negate-inverts-sign',
        'stdlib-zero-less-predicate',
        'stdlib-abs-normalizes-sign',
        'stdlib-max-picks-greater-value',
        'stdlib-min-picks-smaller-value',
        'stdlib-bi',
        'stdlib-dip',
        'stdlib-keep',
        'stdlib-2dip',
        'stdlib-2keep',
        'stdlib-tri',
        'stdlib-try-question-failure-restores-stack',
        'stdlib-try-question-success-returns-result-and-flag',
        'stdlib-try-handler-on-failure',
        'stdlib-try-success-ignores-handler',
        'stdlib-try-handler-error-wins-on-failure',
        'stdlib-recover-handler-on-failure',
        'stdlib-recover-success-ignores-handler',
        'stdlib-recover-handler-error-wins-on-failure',
        'stdlib-ensure-success-runs-cleanup',
        'stdlib-ensure-failure-reraises-after-cleanup',
        'stdlib-ensure-cleanup-error-wins-on-success',
        'stdlib-ensure-cleanup-error-wins-on-failure',
        'stdlib-finally-success-runs-cleanup',
        'stdlib-finally-failure-reraises-after-cleanup',
        'stdlib-finally-cleanup-error-wins-on-success',
        'stdlib-finally-cleanup-error-wins-on-failure',
        'stdlib-assert-true-drops-message-and-keeps-outer-stack',
        'stdlib-assert-false-throws-message-and-preserves-outer-stack',
        'budget-catch-flags-exhaustion',
        'compiled-question-is-false-for-primitive-xt',
    } <= names


def test_load_portability_cases_rejects_duplicate_names_and_bad_expectations(tmp_path) -> None:
    p = tmp_path / 'bad.json'
    p.write_text(
        json.dumps(
            [
                {'name': 'dup', 'category': 'kernel', 'source': '1', 'expect_stack': [1]},
                {'name': 'dup', 'category': 'kernel', 'source': '2', 'expect_stack': [2]},
            ]
        ),
        encoding='utf-8',
    )
    with pytest.raises(ValueError, match='duplicate portability case name'):
        load_portability_cases(p)

    p.write_text(
        json.dumps(
            [
                {
                    'name': 'bad',
                    'category': 'kernel',
                    'source': '1',
                    'expect_stack': [1],
                    'expect_error_contains': 'oops',
                }
            ]
        ),
        encoding='utf-8',
    )
    cases = load_portability_cases(p)
    assert cases[0]['expect_stack'] == [1]
    assert cases[0]['expect_error_contains'] == 'oops'



def test_load_portability_cases_normalizes_tags_host_features_and_rejects_nonportable_expect_stack(tmp_path) -> None:
    p = tmp_path / 'tags.json'
    p.write_text(
        json.dumps(
            [
                {
                    'name': 'ok',
                    'category': 'kernel',
                    'tags': ['alpha', 'alpha', 'beta'],
                    'host_features': ['mx.demo', 'mx.demo', 'mx.extra'],
                    'source': '1',
                    'expect_stack': [1],
                },
                {'name': 'bad', 'category': 'kernel', 'source': '1', 'expect_stack': [{'x': 1.5}]},
            ]
        ),
        encoding='utf-8',
    )
    with pytest.raises(TypeError, match='non-portable value'):
        load_portability_cases(p)

    p.write_text(
        json.dumps(
            [
                {
                    'name': 'ok',
                    'category': 'kernel',
                    'tags': ['alpha', 'alpha', 'beta'],
                    'host_features': ['mx.demo', 'mx.demo', 'mx.extra'],
                    'source': '1',
                    'expect_stack': [1],
                }
            ]
        ),
        encoding='utf-8',
    )
    cases = load_portability_cases(p)
    assert cases[0]['tags'] == ['alpha', 'beta']
    assert cases[0]['host_features'] == ['mx.demo', 'mx.extra']



def test_run_portability_case_can_validate_post_error_stack_when_expected() -> None:
    result = run_portability_cases(
        [
            {
                'name': 'ensure-failure-stack',
                'category': 'stdlib',
                'source': '123 [ drop drop ] [ 999 ] ensure',
                'expect_error_contains': 'Stack underflow',
                'expect_stack': [123, 999],
            }
        ]
    )
    assert [row.ok for row in result] == [True]



def test_select_portability_cases_can_filter_by_category_tag_and_name() -> None:
    cases = load_portability_cases()

    stack_ops = select_portability_cases(cases, tags=['stack-shuffle'])
    assert {c['name'] for c in stack_ops} >= {
        'pick-zero-equivalent-to-dup',
        'pick-one-equivalent-to-over',
        'pick-two-copies-third-item',
        'pick-three-copies-fourth-item',
        'pick-four-copies-fifth-item',
        'roll-zero-is-null-op',
        'roll-one-equivalent-to-swap',
        'roll-two-equivalent-to-rot',
        'roll-three-rotates-four-items',
        'roll-four-rotates-five-items',
        'pick-negative-index-errors',
        'roll-negative-index-errors',
        'pick-underflow-errors-on-too-shallow-stack',
        'roll-underflow-errors-on-too-shallow-stack',
        'stdlib-nip-drops-under-top-item',
        'stdlib-tuck-copies-top-under-next',
        'stdlib-2dup-copies-pair',
        'stdlib-2drop-removes-pair',
        'stdlib-2nip-drops-underlying-pair',
        'stdlib-2over-copies-leading-pair',
        'stdlib-2tuck-tucks-top-pair-under-copy',
        'stdlib-2swap-exchanges-top-pairs',
        'stdlib-2rot-rotates-three-pairs-left',
        'stdlib-2rot-moves-front-pair-to-back',
        'stdlib-2to-r-2r-from-roundtrip',
        'stdlib-2r-fetch-preserves-pair-on-return-stack',
        'stdlib-2r-fetch-keeps-return-stack-depth',
        'stdlib-rdrop-removes-top-return-stack-item',
        'stdlib-rdrop-preserves-older-return-stack-items',
        'stdlib-2rdrop-removes-pair-from-return-stack',
        'stdlib-2rdrop-preserves-older-return-stack-items',
    }

    stdlib = select_portability_cases(cases, categories=['stdlib'])
    assert stdlib
    assert all(c['category'] == 'stdlib' for c in stdlib)

    namespaces = select_portability_cases(cases, tags=['namespaces'])
    assert {c['name'] for c in namespaces} >= {
        'wordlist-search-order-lookup',
        'module-in-defines-into-existing-module',
        'module-use',
        'set-current-roundtrip',
        'get-current-reflects-set-current',
        'also-duplicates-top-search-order-entry',
        'only-resets-search-order-length-to-one',
        'search-order-prefers-first-entry-on-conflict',
        'find-prefers-latest-definition-within-wordlist',
        'get-order-roundtrip-preserves-precedence',
    }

    exact = select_portability_cases(cases, names=['set-current-roundtrip', 'stdlib-tri'])
    assert {c['name'] for c in exact} == {'set-current-roundtrip', 'stdlib-tri'}

    recover = select_portability_cases(cases, name_contains='recover')
    assert [c['name'] for c in recover] == [
        'stdlib-recover-handler-on-failure',
        'stdlib-recover-success-ignores-handler',
        'stdlib-recover-handler-error-wins-on-failure',
    ]






def test_boot_stdlib_words_have_explicit_portability_manifest_entries() -> None:
    core = (ROOT / 'src' / 'micromax' / 'stdlib' / 'core.mx').read_text(encoding='utf-8')
    words = re.findall(r'^:\s+([^\s]+)', core, flags=re.MULTILINE)
    cases = load_portability_cases()
    names = {str(c.get('name') or '') for c in cases}

    assert set(words) == set(boot_stdlib_portability_manifest())
    for word, expected_names in boot_stdlib_portability_manifest().items():
        assert expected_names, word
        assert set(expected_names) <= names


def test_portability_case_record_summary_and_inventory_are_machine_friendly() -> None:
    cases = load_portability_cases()
    selected = select_portability_cases(cases, tags=['memory'])
    assert {c['name'] for c in selected} == {
        'constant-pushes-bound-value',
        'variable-store-and-fetch',
        'map-delete-removes-key',
        'map-merge-overrides-destination',
    }

    record = portability_case_record(selected[0])
    assert set(record) >= {'name', 'category', 'source', 'expect_stack', 'tags'}

    host_case = next(c for c in cases if c['name'] == 'host-feature-present-is-true')
    host_record = portability_case_record(host_case)
    assert host_record['host_features'] == ['mx.demo']

    summary = portability_summary(cases)
    assert summary['count'] == len(cases)
    assert summary['by_category']['kernel'] >= 1
    assert summary['by_tag']['combinators'] >= 1
    assert summary['by_tag']['memory'] == 4

    inventory = portability_inventory(selected)
    assert inventory['count'] == 4
    assert inventory['case_names'] == [
        'constant-pushes-bound-value',
        'variable-store-and-fetch',
        'map-delete-removes-key',
        'map-merge-overrides-destination',
    ]
    assert inventory['categories'] == [{'name': 'kernel', 'count': 4}]
    assert {'name': 'maps', 'count': 2} in inventory['tags']


def test_boot_stdlib_manifest_helpers_are_machine_friendly() -> None:
    cases = load_portability_cases()
    manifest = boot_stdlib_portability_manifest()
    assert manifest == BOOT_STDLIB_PORTABILITY_MANIFEST

    selected = select_boot_stdlib_manifest_entries(manifest, words=["try", "ensure"])
    assert list(selected) == ["try", "ensure"]
    assert selected["try"] == BOOT_STDLIB_PORTABILITY_MANIFEST["try"]
    assert selected["ensure"] == BOOT_STDLIB_PORTABILITY_MANIFEST["ensure"]

    substring = select_boot_stdlib_manifest_entries(manifest, word_contains="tr")
    assert [word for word in substring] == ["tri", "try?", "try"]

    inventory = boot_stdlib_manifest_inventory(cases, selected)
    assert inventory["word_count"] == 2
    assert inventory["all_cases_present"] is True
    assert inventory["missing_words"] == []
    assert inventory["manifest_case_count"] == len(set(
        BOOT_STDLIB_PORTABILITY_MANIFEST["try"] + BOOT_STDLIB_PORTABILITY_MANIFEST["ensure"]
    ))
    assert inventory["words"] == [
        {
            "word": "try",
            "case_names": BOOT_STDLIB_PORTABILITY_MANIFEST["try"],
            "covered": True,
            "missing_case_names": [],
        },
        {
            "word": "ensure",
            "case_names": BOOT_STDLIB_PORTABILITY_MANIFEST["ensure"],
            "covered": True,
            "missing_case_names": [],
        },
    ]


def test_boot_stdlib_word_specs_are_machine_friendly() -> None:
    cases = load_portability_cases()
    specs = boot_stdlib_word_specs()
    assert specs["try"]["word"] == "try"
    assert specs["try"]["line"] >= 1
    assert specs["try"]["stack_effect"] == "( ..a body handler -- ..b )"
    assert "last-error" in specs["try"]["definition"]
    assert specs["ensure"]["stack_effect"] == "( ..a body cleanup -- ..b )"
    assert specs["ensure"]["definition"].startswith(">r")
    assert specs["finally"]["definition"] == "ensure"
    assert specs["finally"]["source_path"].endswith("src/micromax/stdlib/core.mx")
    assert specs["dip"]["body_tokens"] == ["swap", ">r", "call", "r>"]
    assert specs["dip"]["word_refs"] == ["swap", ">r", "call", "r>"]
    assert specs["bi"]["stdlib_refs"] == ["keep", "dip"]
    assert specs["bi"]["nonstdlib_refs"] == ["call"]
    assert specs["bi"]["dependency_order"] == ["keep", "dip"]
    assert specs["bi"]["transitive_stdlib_refs"] == ["keep", "dip"]
    assert specs["bi"]["transitive_nonstdlib_refs"] == ["call", "over", ">r", "r>", "swap"]
    assert specs["bi"]["stdlib_depth"] == 1
    assert specs["finally"]["alias_of"] == "ensure"
    assert specs["finally"]["dependency_order"] == ["ensure"]
    assert specs["finally"]["transitive_stdlib_refs"] == ["ensure"]
    assert "throw" in specs["finally"]["transitive_nonstdlib_refs"]
    assert specs["finally"]["stdlib_depth"] == 1
    assert specs["keep"]["direct_stdlib_users"] == ["bi", "tri"]
    assert specs["keep"]["transitive_stdlib_users"] == ["bi", "tri"]
    assert specs["keep"]["user_depth"] == 1
    assert specs["ensure"]["direct_stdlib_users"] == ["finally"]
    assert specs["ensure"]["transitive_stdlib_users"] == ["finally"]
    assert specs["ensure"]["user_depth"] == 1
    assert specs["keep"]["impact_words"] == ["keep", "bi", "tri"]
    assert specs["keep"]["impact_word_count"] == 3
    assert specs["ensure"]["impact_words"] == ["ensure", "finally"]
    assert specs["ensure"]["impact_word_count"] == 2

    selected = selected_boot_stdlib_word_inventory(cases=cases, words=["try", "ensure", "finally"])
    assert selected["word_count"] == 3
    assert selected["all_words_present"] is True
    assert selected["missing_words"] == []
    assert [row["word"] for row in selected["words"]] == ["try", "ensure", "finally"]
    assert selected["words"][0]["stack_effect"] == "( ..a body handler -- ..b )"
    assert selected["words"][0]["word_refs"][:3] == [">r", "catch", "dup"]
    assert selected["words"][1]["definition"].startswith(">r")
    assert selected["words"][1]["dependency_order"] == []
    assert selected["words"][2]["alias_of"] == "ensure"
    assert selected["words"][2]["transitive_stdlib_refs"] == ["ensure"]
    assert "catch" in selected["words"][2]["transitive_nonstdlib_refs"]
    assert selected["words"][2]["stdlib_depth"] == 1
    assert selected["words"][1]["direct_stdlib_users"] == ["finally"]
    assert selected["words"][1]["transitive_stdlib_users"] == ["finally"]
    assert selected["words"][1]["user_depth"] == 1
    assert selected["words"][1]["impact_words"] == ["ensure", "finally"]
    assert selected["words"][1]["impact_case_names"] == (
        BOOT_STDLIB_PORTABILITY_MANIFEST["ensure"] + BOOT_STDLIB_PORTABILITY_MANIFEST["finally"]
    )
    assert selected["words"][1]["impact_case_count"] == len(selected["words"][1]["impact_case_names"])
    assert selected["words"][1]["impact_categories"] == [{"name": "stdlib", "count": 8}]
    assert {"name": "cleanup", "count": 8} in selected["words"][1]["impact_tags"]
    assert {"name": "errors", "count": 6} in selected["words"][1]["impact_tags"]
    ensure_groups = {row["word"]: row for row in selected["words"][1]["impact_groups"]}
    assert list(ensure_groups) == ["ensure", "finally"]
    assert ensure_groups["ensure"]["paths"] == [["ensure"]]
    assert ensure_groups["ensure"]["distance"] == 0
    assert ensure_groups["ensure"]["selected_words"] == ["ensure"]
    assert ensure_groups["ensure"]["case_names"] == BOOT_STDLIB_PORTABILITY_MANIFEST["ensure"]
    assert ensure_groups["ensure"]["retest_name_args"] == portability_case_name_args(BOOT_STDLIB_PORTABILITY_MANIFEST["ensure"])
    assert ensure_groups["ensure"]["retest_env"] == portability_retest_env()
    assert ensure_groups["ensure"]["retest_argv"] == portability_retest_argv(BOOT_STDLIB_PORTABILITY_MANIFEST["ensure"])
    assert ensure_groups["ensure"]["retest_json_argv"] == portability_retest_argv(BOOT_STDLIB_PORTABILITY_MANIFEST["ensure"], json_mode=True)
    assert ensure_groups["ensure"]["retest_command"] == portability_retest_command(BOOT_STDLIB_PORTABILITY_MANIFEST["ensure"])
    assert ensure_groups["finally"]["paths"] == [["ensure", "finally"]]
    assert ensure_groups["finally"]["distance"] == 1
    assert ensure_groups["finally"]["selected_words"] == ["ensure"]
    assert ensure_groups["finally"]["alias_of"] == "ensure"
    assert ensure_groups["finally"]["case_names"] == BOOT_STDLIB_PORTABILITY_MANIFEST["finally"]
    assert selected["words"][1]["impact_stage_count"] == 2
    assert selected["words"][1]["impact_stages"] == [
        {
            'distance': 0,
            'words': ['ensure'],
            'selected_words': ['ensure'],
            'case_names': BOOT_STDLIB_PORTABILITY_MANIFEST['ensure'],
            'word_count': 1,
            'selected_word_count': 1,
            'case_count': 4,
            'retest_name_args': portability_case_name_args(BOOT_STDLIB_PORTABILITY_MANIFEST['ensure']),
            'retest_env': portability_retest_env(),
            'retest_argv': portability_retest_argv(BOOT_STDLIB_PORTABILITY_MANIFEST['ensure']),
            'retest_json_argv': portability_retest_argv(BOOT_STDLIB_PORTABILITY_MANIFEST['ensure'], json_mode=True),
            'retest_command': portability_retest_command(BOOT_STDLIB_PORTABILITY_MANIFEST['ensure']),
            'retest_json_command': portability_retest_command(BOOT_STDLIB_PORTABILITY_MANIFEST['ensure'], json_mode=True),
            'impact_categories': [{'name': 'stdlib', 'count': 4}],
            'impact_tags': [
                {'name': 'cleanup', 'count': 4},
                {'name': 'errors', 'count': 3},
            ],
        },
        {
            'distance': 1,
            'words': ['finally'],
            'selected_words': ['ensure'],
            'case_names': BOOT_STDLIB_PORTABILITY_MANIFEST['finally'],
            'word_count': 1,
            'selected_word_count': 1,
            'case_count': 4,
            'retest_name_args': portability_case_name_args(BOOT_STDLIB_PORTABILITY_MANIFEST['finally']),
            'retest_env': portability_retest_env(),
            'retest_argv': portability_retest_argv(BOOT_STDLIB_PORTABILITY_MANIFEST['finally']),
            'retest_json_argv': portability_retest_argv(BOOT_STDLIB_PORTABILITY_MANIFEST['finally'], json_mode=True),
            'retest_command': portability_retest_command(BOOT_STDLIB_PORTABILITY_MANIFEST['finally']),
            'retest_json_command': portability_retest_command(BOOT_STDLIB_PORTABILITY_MANIFEST['finally'], json_mode=True),
            'impact_categories': [{'name': 'stdlib', 'count': 4}],
            'impact_tags': [
                {'name': 'aliases', 'count': 4},
                {'name': 'cleanup', 'count': 4},
                {'name': 'errors', 'count': 3},
            ],
        },
    ]
    impact_case_names = (
        BOOT_STDLIB_PORTABILITY_MANIFEST["try"]
        + BOOT_STDLIB_PORTABILITY_MANIFEST["recover"]
        + BOOT_STDLIB_PORTABILITY_MANIFEST["ensure"]
        + BOOT_STDLIB_PORTABILITY_MANIFEST["finally"]
    )
    summary = selected["impact_summary"]
    assert summary["impact_words"] == ["try", "recover", "ensure", "finally"]
    assert summary["impact_word_count"] == 4
    assert summary["impact_case_names"] == impact_case_names
    assert summary["impact_case_count"] == len(impact_case_names)
    assert summary["impact_categories"] == [{"name": "stdlib", "count": 14}]
    assert summary["impact_tags"] == [
        {"name": "aliases", "count": 7},
        {"name": "cleanup", "count": 8},
        {"name": "errors", "count": 8},
        {"name": "recovery", "count": 6},
        {"name": "stdlib", "count": 1},
    ]
    summary_groups = {row["word"]: row for row in summary["impact_groups"]}
    assert list(summary_groups) == ["try", "recover", "ensure", "finally"]
    assert summary_groups["try"]["selected_words"] == ["try"]
    assert summary_groups["try"]["paths"] == [["try"]]
    assert summary_groups["try"]["distance"] == 0
    assert summary_groups["recover"]["selected_words"] == ["try"]
    assert summary_groups["recover"]["paths"] == [["try", "recover"]]
    assert summary_groups["recover"]["distance"] == 1
    assert summary_groups["finally"]["selected_words"] == ["ensure", "finally"]
    assert summary_groups["finally"]["paths"] == [["ensure", "finally"], ["finally"]]
    assert summary_groups["finally"]["distance"] == 0
    assert summary['impact_stage_count'] == 2
    assert summary['impact_stages'][0]['distance'] == 0
    assert summary['impact_stages'][0]['words'] == ['try', 'ensure', 'finally']
    assert summary['impact_stages'][0]['selected_words'] == ['try', 'ensure', 'finally']
    assert summary['impact_stages'][0]['case_count'] == 11
    assert summary['impact_stages'][1]['distance'] == 1
    assert summary['impact_stages'][1]['words'] == ['recover']
    assert summary['impact_stages'][1]['selected_words'] == ['try']
    assert summary['impact_stages'][1]['case_names'] == BOOT_STDLIB_PORTABILITY_MANIFEST['recover']
    assert summary["retest_name_args"] == portability_case_name_args(impact_case_names)
    assert summary["retest_env"] == portability_retest_env()
    assert summary["retest_argv"] == portability_retest_argv(impact_case_names)
    assert summary["retest_json_argv"] == portability_retest_argv(impact_case_names, json_mode=True)
    assert summary["retest_command"] == portability_retest_command(impact_case_names)
    assert summary["retest_json_command"] == portability_retest_command(impact_case_names, json_mode=True)


def test_selected_boot_stdlib_word_inventory_can_filter_impacted_words_and_distances() -> None:
    cases = load_portability_cases()

    selected = selected_boot_stdlib_word_inventory(
        cases=cases,
        words=["keep", "ensure"],
        impact_filter_words=["bi", "finally"],
    )
    assert [row["word"] for row in selected["words"]] == ["keep", "ensure"]
    assert selected["words"][0]["impact_words"] == ["bi"]
    assert selected["words"][0]["impact_case_names"] == BOOT_STDLIB_PORTABILITY_MANIFEST["bi"]
    assert selected["words"][0]["impact_stage_count"] == 1
    assert selected["words"][0]["impact_stages"][0]["distance"] == 1
    assert selected["words"][0]["impact_stages"][0]["words"] == ["bi"]
    assert selected["words"][1]["impact_words"] == ["finally"]
    assert selected["words"][1]["impact_case_names"] == BOOT_STDLIB_PORTABILITY_MANIFEST["finally"]
    assert selected["words"][1]["impact_stage_count"] == 1
    assert selected["words"][1]["impact_stages"][0]["distance"] == 1
    assert selected["impact_summary"]["impact_words"] == ["bi", "finally"]
    assert selected["impact_summary"]["impact_case_names"] == (
        BOOT_STDLIB_PORTABILITY_MANIFEST["bi"] + BOOT_STDLIB_PORTABILITY_MANIFEST["finally"]
    )
    assert selected["impact_summary"]["impact_stage_count"] == 1
    assert selected["impact_summary"]["impact_stages"][0]["distance"] == 1
    assert selected["impact_summary"]["impact_stages"][0]["words"] == ["bi", "finally"]
    options = selected["words"][0]["impact_filter_options"]
    assert [(row["name"], row["distance"], row["case_count"]) for row in options["words"]] == [("bi", 1, 1)]
    assert options["words"][0]["preview_impact_word_count"] == 1
    assert options["words"][0]["preview_impact_case_count"] == 1
    assert options["words"][0]["preview_impact_stage_count"] == 1
    assert options["word_count"] == 1
    assert [(row["distance"], row["words"], row["word_count"], row["case_count"]) for row in options["distances"]] == [(1, ["bi"], 1, 1)]
    assert options["distance_count"] == 1
    assert [(row["name"], row["count"]) for row in options["categories"]] == [("stdlib", 1)]
    assert options["category_count"] == 1
    assert [(row["name"], row["count"]) for row in options["tags"]] == [("combinators", 1)]
    assert options["tag_count"] == 1
    assert [(row["name"], row["words"], row["word_count"], row["distances"], row["distance_count"]) for row in options["names"]] == [("stdlib-bi", ["bi"], 1, [1], 1)]
    assert options["name_count"] == 1
    summary_options = selected["impact_summary"]["impact_filter_options"]
    assert [(row["name"], row["distance"], row["case_count"]) for row in summary_options["words"]] == [
        ("bi", 1, 1),
        ("finally", 1, 4),
    ]
    assert summary_options["word_count"] == 2
    assert [(row["distance"], row["words"], row["word_count"], row["case_count"]) for row in summary_options["distances"]] == [(1, ["bi", "finally"], 2, 5)]
    assert summary_options["distance_count"] == 1
    assert [(row["name"], row["count"]) for row in summary_options["categories"]] == [("stdlib", 5)]
    assert summary_options["category_count"] == 1
    assert ('cleanup', 4) in {(row['name'], row['count']) for row in summary_options["tags"]}
    assert ('errors', 3) in {(row['name'], row['count']) for row in summary_options["tags"]}
    assert ('combinators', 1) in {(row['name'], row['count']) for row in summary_options["tags"]}
    assert summary_options["tag_count"] == 4
    assert summary_options["name_count"] == 5

    roots_only = selected_boot_stdlib_word_inventory(
        cases=cases,
        words=["keep", "ensure"],
        impact_distances=[0],
    )
    assert roots_only["words"][0]["impact_words"] == ["keep"]
    assert roots_only["words"][1]["impact_words"] == ["ensure"]
    assert roots_only["impact_summary"]["impact_words"] == ["keep", "ensure"]
    assert roots_only["impact_summary"]["impact_case_names"] == (
        BOOT_STDLIB_PORTABILITY_MANIFEST["keep"] + BOOT_STDLIB_PORTABILITY_MANIFEST["ensure"]
    )
    assert roots_only["impact_summary"]["impact_stage_count"] == 1
    assert roots_only["impact_summary"]["impact_stages"][0]["distance"] == 0
    assert roots_only["impact_summary"]["impact_stages"][0]["words"] == ["keep", "ensure"]
    root_options = roots_only["impact_summary"]["impact_filter_options"]
    assert [(row["name"], row["distance"], row["case_count"]) for row in root_options["words"]] == [
        ("keep", 0, 1),
        ("ensure", 0, 4),
    ]
    assert root_options["word_count"] == 2
    assert [(row["distance"], row["words"], row["word_count"], row["case_count"]) for row in root_options["distances"]] == [(0, ["keep", "ensure"], 2, 5)]
    assert root_options["distance_count"] == 1
    assert [(row["name"], row["count"]) for row in root_options["categories"]] == [("stdlib", 5)]
    assert root_options["category_count"] == 1
    assert ('combinators', 1) in {(row['name'], row['count']) for row in root_options["tags"]}
    assert ('cleanup', 4) in {(row['name'], row['count']) for row in root_options["tags"]}
    assert ('errors', 3) in {(row['name'], row['count']) for row in root_options["tags"]}
    assert root_options["tag_count"] == 3
    assert root_options["name_count"] == 5


def test_selected_boot_stdlib_word_inventory_can_filter_impacted_cases_by_tags_and_names() -> None:
    cases = load_portability_cases()

    tagged = selected_boot_stdlib_word_inventory(
        cases=cases,
        words=["ensure"],
        impact_case_tags=["errors"],
    )
    row = tagged["words"][0]
    assert row["impact_words"] == ["ensure", "finally"]
    assert row["impact_case_names"] == [
        "stdlib-ensure-failure-reraises-after-cleanup",
        "stdlib-ensure-cleanup-error-wins-on-success",
        "stdlib-ensure-cleanup-error-wins-on-failure",
        "stdlib-finally-failure-reraises-after-cleanup",
        "stdlib-finally-cleanup-error-wins-on-success",
        "stdlib-finally-cleanup-error-wins-on-failure",
    ]
    groups = {group["word"]: group for group in row["impact_groups"]}
    assert groups["ensure"]["case_count"] == 3
    assert groups["finally"]["case_count"] == 3
    assert {tag["name"]: tag["count"] for tag in row["impact_tags"]}["errors"] == 6
    assert row["impact_stage_count"] == 2
    assert row["impact_stages"][0]["words"] == ["ensure"]
    assert row["impact_stages"][1]["words"] == ["finally"]
    options = row["impact_filter_options"]
    assert [(row["name"], row["distance"], row["case_count"]) for row in options["words"]] == [
        ("ensure", 0, 3),
        ("finally", 1, 3),
    ]
    assert options["word_count"] == 2
    assert [(row["distance"], row["words"], row["word_count"], row["case_count"]) for row in options["distances"]] == [
        (0, ["ensure"], 1, 3),
        (1, ["finally"], 1, 3),
    ]
    assert options["distance_count"] == 2
    assert [(row["name"], row["count"]) for row in options["categories"]] == [("stdlib", 6)]
    assert options["category_count"] == 1
    assert ('aliases', 3) in {(row['name'], row['count']) for row in options["tags"]}
    assert ('cleanup', 6) in {(row['name'], row['count']) for row in options["tags"]}
    assert ('errors', 6) in {(row['name'], row['count']) for row in options["tags"]}
    assert options["tag_count"] == 3
    assert options["name_count"] == 6

    named = selected_boot_stdlib_word_inventory(
        cases=cases,
        words=["ensure"],
        impact_case_name_contains="cleanup-error-wins",
    )
    named_row = named["words"][0]
    assert named_row["impact_case_names"] == [
        "stdlib-ensure-cleanup-error-wins-on-success",
        "stdlib-ensure-cleanup-error-wins-on-failure",
        "stdlib-finally-cleanup-error-wins-on-success",
        "stdlib-finally-cleanup-error-wins-on-failure",
    ]
    assert named_row["impact_groups"][0]["retest_command"] == (
        "PYTHONPATH=src python tools/mxportable.py --name stdlib-ensure-cleanup-error-wins-on-success "
        "--name stdlib-ensure-cleanup-error-wins-on-failure"
    )


def test_selected_boot_stdlib_word_inventory_recommends_small_next_cuts_before_exact_case_names() -> None:
    cases = load_portability_cases()

    tagged = selected_boot_stdlib_word_inventory(
        cases=cases,
        words=["ensure"],
        impact_case_tags=["errors"],
    )
    options = tagged["words"][0]["impact_filter_options"]
    recommended = options["recommended"]
    assert len(recommended) == 5
    assert options["recommended_count"] == 5
    assert [
        (row["recommendation_rank"], row["option_family"], row["option_label"])
        for row in recommended
    ] == [
        (1, "words", "ensure"),
        (2, "words", "finally"),
        (3, "distances", "0"),
        (4, "distances", "1"),
        (5, "tags", "aliases"),
    ]
    assert all(row["preview_effect"] == "narrower" for row in recommended)
    assert all(row["preview_changes_slice"] is True for row in recommended)
    assert all(row["option_family"] != "names" for row in recommended)
    assert recommended[0]["show_impact_command"] == (
        "PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-word ensure --impact-tag errors"
    )
    assert recommended[0]["equivalent_option_count"] == 1
    assert recommended[0]["equivalent_options"] == [
        {
            "option_family": "distances",
            "option_label": "0",
            "filter_suffix": "--impact-distance 0",
            "show_impact_command": (
                "PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure "
                "--show-impact --impact-distance 0 --impact-tag errors"
            ),
        }
    ]
    assert recommended[1]["equivalent_option_count"] == 2
    assert [(row["option_family"], row["option_label"]) for row in recommended[1]["equivalent_options"]] == [
        ("distances", "1"),
        ("tags", "aliases"),
    ]
    assert recommended[4]["show_impact_command"] == (
        "PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-tag errors --impact-tag aliases"
    )
    distinct = options["recommended_distinct"]
    assert len(distinct) == 2
    assert options["recommended_distinct_count"] == 2
    assert [
        (row["recommendation_rank"], row["option_family"], row["option_label"])
        for row in distinct
    ] == [
        (1, "words", "ensure"),
        (2, "words", "finally"),
    ]
    assert distinct[0]["equivalent_option_count"] == 1
    assert distinct[1]["equivalent_option_count"] == 2
    assert distinct[0]["represented_option_count"] == 2
    assert [(row["option_family"], row["option_label"]) for row in distinct[0]["represented_alternatives"]] == [
        ("distances", "0"),
    ]
    assert distinct[0]["source_recommendation_rank"] == 1
    assert distinct[0]["represented_recommendation_ranks"] == [1, 3]
    assert distinct[0]["represented_alternative_ranks"] == [3]
    assert distinct[0]["represented_rank_min"] == 1
    assert distinct[0]["represented_rank_max"] == 3
    assert distinct[0]["representative_reason_code"] == "coarser-family"
    assert distinct[0]["representative_reason"] == "preferred as the coarsest equivalent cut over distances:0"
    assert distinct[0]["represented_alternative_labels"] == ["distances:0"]
    assert distinct[1]["represented_option_count"] == 3
    assert [(row["option_family"], row["option_label"]) for row in distinct[1]["represented_alternatives"]] == [
        ("distances", "1"),
        ("tags", "aliases"),
    ]
    assert distinct[1]["source_recommendation_rank"] == 2
    assert distinct[1]["represented_recommendation_ranks"] == [2, 4, 5]
    assert distinct[1]["represented_alternative_ranks"] == [4, 5]
    assert distinct[1]["represented_rank_min"] == 2
    assert distinct[1]["represented_rank_max"] == 5
    assert distinct[1]["representative_reason_code"] == "coarser-family"
    assert distinct[1]["representative_reason"] == "preferred as the coarsest equivalent cut over distances:1, tags:aliases"
    assert distinct[1]["represented_alternative_labels"] == ["distances:1", "tags:aliases"]
    primary = options["recommended_primary"]
    assert primary["option_family"] == "words"
    assert primary["option_label"] == "ensure"
    assert primary["recommendation_rank"] == 1
    assert primary["source_recommendation_rank"] == 1
    assert primary["show_impact_command"] == (
        "PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-word ensure --impact-tag errors"
    )
    assert primary["show_impact_json_command"] == (
        "PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-word ensure --impact-tag errors --json"
    )
    assert options["recommended_primary_command"] == primary["show_impact_command"]
    assert options["recommended_primary_json_command"] == primary["show_impact_json_command"]
    primary_group = options["recommended_primary_group"]
    assert primary_group["representative"]["option_family"] == "words"
    assert primary_group["representative"]["option_label"] == "ensure"
    assert primary_group["representative"]["show_impact_command"] == primary["show_impact_command"]
    assert primary_group["representative"]["show_impact_json_command"] == primary["show_impact_json_command"]
    assert primary_group["represented_recommendation_ranks"] == [1, 3]
    groups = options["recommended_distinct_groups"]
    assert options["recommended_distinct_group_count"] == 2
    assert [
        (group["recommendation_rank"], group["representative"]["option_family"], group["representative"]["option_label"], group["represented_alternative_count"])
        for group in groups
    ] == [
        (1, "words", "ensure", 1),
        (2, "words", "finally", 2),
    ]
    assert groups[0]["source_recommendation_rank"] == 1
    assert groups[0]["represented_recommendation_ranks"] == [1, 3]
    assert groups[0]["represented_alternative_ranks"] == [3]
    assert groups[0]["representative_reason_code"] == "coarser-family"
    assert groups[0]["representative_reason"] == "preferred as the coarsest equivalent cut over distances:0"
    assert groups[1]["source_recommendation_rank"] == 2
    assert groups[1]["represented_recommendation_ranks"] == [2, 4, 5]
    assert groups[1]["represented_alternative_ranks"] == [4, 5]
    assert groups[1]["represented_alternative_labels"] == ["distances:1", "tags:aliases"]


def test_portability_retest_helpers_dedupe_case_names_and_emit_exact_name_commands() -> None:
    case_names = [
        'stdlib-keep',
        'stdlib-bi',
        'stdlib-keep',
    ]
    assert portability_case_name_args(case_names) == [
        '--name',
        'stdlib-keep',
        '--name',
        'stdlib-bi',
    ]
    assert portability_retest_env() == {'PYTHONPATH': 'src'}
    assert portability_retest_argv(case_names) == [
        'python',
        'tools/mxportable.py',
        '--name',
        'stdlib-keep',
        '--name',
        'stdlib-bi',
    ]
    assert portability_retest_argv(case_names, json_mode=True) == [
        'python',
        'tools/mxportable.py',
        '--name',
        'stdlib-keep',
        '--name',
        'stdlib-bi',
        '--json',
    ]
    assert portability_retest_metadata(case_names) == {
        'retest_name_args': ['--name', 'stdlib-keep', '--name', 'stdlib-bi'],
        'retest_env': {'PYTHONPATH': 'src'},
        'retest_argv': ['python', 'tools/mxportable.py', '--name', 'stdlib-keep', '--name', 'stdlib-bi'],
        'retest_json_argv': ['python', 'tools/mxportable.py', '--name', 'stdlib-keep', '--name', 'stdlib-bi', '--json'],
        'retest_command': 'PYTHONPATH=src python tools/mxportable.py --name stdlib-keep --name stdlib-bi',
        'retest_json_command': 'PYTHONPATH=src python tools/mxportable.py --name stdlib-keep --name stdlib-bi --json',
    }
    assert portability_retest_command(case_names) == (
        "PYTHONPATH=src python tools/mxportable.py --name stdlib-keep --name stdlib-bi"
    )
    assert portability_retest_command(case_names, json_mode=True) == (
        "PYTHONPATH=src python tools/mxportable.py --name stdlib-keep --name stdlib-bi --json"
    )


def test_mxportable_cli_can_list_and_filter_cases() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / 'tools' / 'mxportable.py'), '--category', 'stdlib', '--name-contains', 'finally', '--list'],
        cwd=ROOT,
        env={'PYTHONPATH': str(ROOT / 'src')},
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0
    assert '[stdlib] stdlib-finally-success-runs-cleanup tags=cleanup,aliases' in proc.stdout
    assert '[stdlib] stdlib-finally-failure-reraises-after-cleanup tags=cleanup,aliases,errors' in proc.stdout
    assert '[stdlib] stdlib-finally-cleanup-error-wins-on-success tags=cleanup,aliases,errors' in proc.stdout
    assert '[stdlib] stdlib-finally-cleanup-error-wins-on-failure tags=cleanup,aliases,errors' in proc.stdout
    assert '4 matching portability cases' in proc.stdout



def test_mxportable_cli_can_filter_by_exact_name() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'tools' / 'mxportable.py'),
            '--name',
            'set-current-roundtrip',
            '--name',
            'map-keys-return-sorted-list',
            '--list',
        ],
        cwd=ROOT,
        env={'PYTHONPATH': str(ROOT / 'src')},
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0
    assert '[kernel] set-current-roundtrip tags=namespaces,wordlists,definitions' in proc.stdout
    assert '[kernel] map-keys-return-sorted-list tags=collections,maps' in proc.stdout
    assert '2 matching portability cases' in proc.stdout


def test_mxportable_cli_can_emit_json_for_list_mode() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'tools' / 'mxportable.py'),
            '--category',
            'kernel',
            '--tag',
            'memory',
            '--list',
            '--json',
        ],
        cwd=ROOT,
        env={'PYTHONPATH': str(ROOT / 'src')},
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload['summary']['count'] == 4
    assert [case['name'] for case in payload['cases']] == [
        'constant-pushes-bound-value',
        'variable-store-and-fetch',
        'map-delete-removes-key',
        'map-merge-overrides-destination',
    ]
    assert payload['summary']['by_tag']['memory'] == 4





def test_mxportable_cli_can_show_inventory_in_human_and_json_modes() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / 'tools' / 'mxportable.py'), '--tag', 'memory', '--inventory'],
        cwd=ROOT,
        env={'PYTHONPATH': str(ROOT / 'src')},
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0
    assert 'Categories:' in proc.stdout
    assert '- kernel: 4' in proc.stdout
    assert '- memory: 4' in proc.stdout
    assert '- map-delete-removes-key' in proc.stdout
    assert '4 matching portability cases' in proc.stdout

    proc_json = subprocess.run(
        [sys.executable, str(ROOT / 'tools' / 'mxportable.py'), '--tag', 'memory', '--inventory', '--json'],
        cwd=ROOT,
        env={'PYTHONPATH': str(ROOT / 'src')},
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc_json.returncode == 0
    payload = json.loads(proc_json.stdout)
    assert 'cases' not in payload
    assert payload['inventory']['count'] == 4
    assert payload['inventory']['case_names'] == [
        'constant-pushes-bound-value',
        'variable-store-and-fetch',
        'map-delete-removes-key',
        'map-merge-overrides-destination',
    ]
    assert {'name': 'memory', 'count': 4} in payload['inventory']['tags']


def test_mxportable_cli_can_run_filtered_cases() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / 'tools' / 'mxportable.py'), '--tag', 'namespaces'],
        cwd=ROOT,
        env={'PYTHONPATH': str(ROOT / 'src')},
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0
    assert '[ok] wordlist-search-order-lookup' in proc.stdout
    assert '[ok] module-in-defines-into-existing-module' in proc.stdout
    assert '[ok] set-current-roundtrip' in proc.stdout
    assert '[ok] get-current-reflects-set-current' in proc.stdout
    assert '[ok] definitions-follows-top-of-search-order' in proc.stdout
    assert '[ok] also-duplicates-top-search-order-entry' in proc.stdout
    assert '[ok] previous-drops-top-search-order-entry' in proc.stdout
    assert '[ok] only-resets-search-order-length-to-one' in proc.stdout
    assert '[ok] search-order-prefers-first-entry-on-conflict' in proc.stdout
    assert '[ok] find-prefers-latest-definition-within-wordlist' in proc.stdout
    assert '[ok] dict-version-stable-across-get-current' in proc.stdout
    namespaces = select_portability_cases(load_portability_cases(), tags=['namespaces'])
    assert f"{len(namespaces)}/{len(namespaces)} portability cases passed" in proc.stdout



def test_mxportable_cli_can_emit_json_for_run_mode() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'tools' / 'mxportable.py'),
            '--tag',
            'locals',
            '--json',
        ],
        cwd=ROOT,
        env={'PYTHONPATH': str(ROOT / 'src')},
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload['passed'] == 2
    assert payload['failed'] == 0
    assert {row['name'] for row in payload['results']} == {
        'locals-shadow-outer-definition',
        'session-local-store-query-and-unlocal',
    }
    assert all(row['ok'] is True for row in payload['results'])
    assert payload['summary']['by_tag']['locals'] == 2


def test_mxportable_cli_can_filter_show_impact_to_root_distance() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'tools' / 'mxportable.py'),
            '--stdlib-manifest',
            '--word',
            'keep',
            '--show-impact',
            '--impact-distance',
            '0',
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0
    assert 'impact filters: distances=0' in proc.stdout
    assert 'impact words: keep' in proc.stdout
    assert 'depth 0: keep :: stdlib-keep' in proc.stdout
    assert 'depth 1:' not in proc.stdout
    assert 'bi <= keep -> bi' not in proc.stdout


def test_mxportable_cli_can_filter_show_impact_to_exact_impacted_word_in_json() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'tools' / 'mxportable.py'),
            '--stdlib-manifest',
            '--word',
            'ensure',
            '--show-impact',
            '--impact-word',
            'finally',
            '--json',
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload['filters']['impact_words'] == ['finally']
    assert payload['filters']['impact_distances'] == []
    row = payload['source_inventory']['words'][0]
    assert row['impact_words'] == ['finally']
    assert row['impact_case_names'] == BOOT_STDLIB_PORTABILITY_MANIFEST['finally']
    assert row['impact_stage_count'] == 1
    assert row['impact_stages'][0]['distance'] == 1
    assert row['impact_stages'][0]['words'] == ['finally']
    assert row['show_impact_command'] == (
        'PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-word finally'
    )
    assert payload['source_inventory']['impact_summary']['impact_words'] == ['finally']
    assert payload['source_inventory']['impact_summary']['impact_case_names'] == BOOT_STDLIB_PORTABILITY_MANIFEST['finally']


def test_mxportable_cli_can_filter_show_impact_cases_by_tag_in_human_output() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'tools' / 'mxportable.py'),
            '--stdlib-manifest',
            '--word',
            'ensure',
            '--show-impact',
            '--impact-tag',
            'errors',
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0
    assert 'impact filters: tags=errors' in proc.stdout
    assert 'show impact command: PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-tag errors' in proc.stdout
    assert 'impact cases: stdlib-ensure-failure-reraises-after-cleanup' in proc.stdout
    assert 'stdlib-finally-success-runs-cleanup' not in proc.stdout
    assert 'stdlib-ensure-cleanup-error-wins-on-success' in proc.stdout
    assert 'stdlib-finally-cleanup-error-wins-on-failure' in proc.stdout


def test_mxportable_cli_show_impact_human_output_marks_replace_vs_append_facet_modes() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'tools' / 'mxportable.py'),
            '--stdlib-manifest',
            '--word',
            'ensure',
            '--show-impact',
            '--impact-tag',
            'errors',
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0
    assert 'words: ensure@0=3 [replace:--impact-word ensure; delta:w-1,c-3,d-1; result:w=1,c=3,d=1; same-result: distances:0]' in proc.stdout
    assert 'tags: aliases=3 [append:--impact-tag aliases => --impact-tag errors --impact-tag aliases; delta:w-1,c-3,d-1; result:w=1,c=3,d=1; same-result: distances:1, words:finally]' in proc.stdout
    assert 'errors=6 [append:--impact-tag errors; same-slice; result:w=2,c=6,d=2; same-result: categories:stdlib, tags:cleanup]' in proc.stdout


def test_mxportable_cli_show_impact_human_output_lists_recommended_next_cuts() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'tools' / 'mxportable.py'),
            '--stdlib-manifest',
            '--word',
            'ensure',
            '--show-impact',
            '--impact-tag',
            'errors',
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={'PYTHONPATH': 'src'},
    )
    assert proc.returncode == 0
    assert 'recommended next: words: ensure@0=3 [replace:--impact-word ensure; delta:w-1,c-3,d-1; result:w=1,c=3,d=1; same-result: distances:0] [covers: distances:0] [full ranks: 1,3] [why: preferred as the coarsest equivalent cut over distances:0]' in proc.stdout
    assert 'command: PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-word ensure --impact-tag errors' in proc.stdout
    assert 'recommended:' in proc.stdout
    assert '1. words: ensure@0=3 [replace:--impact-word ensure; delta:w-1,c-3,d-1; result:w=1,c=3,d=1; same-result: distances:0]' in proc.stdout
    assert '2. words: finally@1=3 [replace:--impact-word finally; delta:w-1,c-3,d-1; result:w=1,c=3,d=1; same-result: distances:1, tags:aliases]' in proc.stdout
    assert '5. tags: aliases=3 [append:--impact-tag aliases => --impact-tag errors --impact-tag aliases; delta:w-1,c-3,d-1; result:w=1,c=3,d=1; same-result: distances:1, words:finally]' in proc.stdout
    assert 'recommended distinct:' in proc.stdout
    assert '1. words: ensure@0=3 [replace:--impact-word ensure; delta:w-1,c-3,d-1; result:w=1,c=3,d=1; same-result: distances:0] [covers: distances:0] [full ranks: 1,3] [why: preferred as the coarsest equivalent cut over distances:0]' in proc.stdout
    assert '2. words: finally@1=3 [replace:--impact-word finally; delta:w-1,c-3,d-1; result:w=1,c=3,d=1; same-result: distances:1, tags:aliases] [covers: distances:1, tags:aliases] [full ranks: 2,4,5] [why: preferred as the coarsest equivalent cut over distances:1, tags:aliases]' in proc.stdout
    assert 'recommended distinct groups:' in proc.stdout
    assert '1. words: ensure' in proc.stdout
    assert 'alternatives: distances:0' in proc.stdout
    assert 'full ranks: 1,3' in proc.stdout
    assert 'why: preferred as the coarsest equivalent cut over distances:0' in proc.stdout
    assert '2. words: finally' in proc.stdout
    assert 'alternatives: distances:1, tags:aliases' in proc.stdout
    assert 'full ranks: 2,4,5' in proc.stdout
    assert 'why: preferred as the coarsest equivalent cut over distances:1, tags:aliases' in proc.stdout


def test_mxportable_cli_show_impact_tag_facets_preserve_current_tag_slice_in_json() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'tools' / 'mxportable.py'),
            '--stdlib-manifest',
            '--word',
            'ensure',
            '--show-impact',
            '--impact-tag',
            'errors',
            '--json',
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    recommended = payload['source_inventory']['impact_summary']['impact_filter_options']['recommended']
    assert [
        (row['recommendation_rank'], row['option_family'], row['option_label'])
        for row in recommended
    ] == [
        (1, 'words', 'ensure'),
        (2, 'words', 'finally'),
        (3, 'distances', '0'),
        (4, 'distances', '1'),
        (5, 'tags', 'aliases'),
    ]
    assert all(row['preview_effect'] == 'narrower' for row in recommended)
    assert recommended[0]['equivalent_option_count'] == 1
    assert [(row['option_family'], row['option_label']) for row in recommended[0]['equivalent_options']] == [('distances', '0')]
    assert recommended[1]['equivalent_option_count'] == 2
    assert [(row['option_family'], row['option_label']) for row in recommended[1]['equivalent_options']] == [('distances', '1'), ('tags', 'aliases')]
    options = payload['source_inventory']['impact_summary']['impact_filter_options']
    distinct = options['recommended_distinct']
    assert options['recommended_distinct_count'] == 2
    assert [
        (row['recommendation_rank'], row['option_family'], row['option_label'])
        for row in distinct
    ] == [
        (1, 'words', 'ensure'),
        (2, 'words', 'finally'),
    ]
    assert distinct[0]['represented_option_count'] == 2
    assert [(row['option_family'], row['option_label']) for row in distinct[0]['represented_alternatives']] == [('distances', '0')]
    assert distinct[0]['source_recommendation_rank'] == 1
    assert distinct[0]['represented_recommendation_ranks'] == [1, 3]
    assert distinct[0]['represented_alternative_ranks'] == [3]
    assert distinct[0]['representative_reason_code'] == 'coarser-family'
    assert distinct[0]['representative_reason'] == 'preferred as the coarsest equivalent cut over distances:0'
    assert distinct[1]['represented_option_count'] == 3
    assert [(row['option_family'], row['option_label']) for row in distinct[1]['represented_alternatives']] == [('distances', '1'), ('tags', 'aliases')]
    assert distinct[1]['source_recommendation_rank'] == 2
    assert distinct[1]['represented_recommendation_ranks'] == [2, 4, 5]
    assert distinct[1]['represented_alternative_ranks'] == [4, 5]
    assert distinct[1]['representative_reason_code'] == 'coarser-family'
    assert distinct[1]['representative_reason'] == 'preferred as the coarsest equivalent cut over distances:1, tags:aliases'
    primary = options['recommended_primary']
    assert primary['option_family'] == 'words'
    assert primary['option_label'] == 'ensure'
    assert primary['show_impact_command'] == (
        'PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-word ensure --impact-tag errors'
    )
    assert primary['show_impact_json_command'] == (
        'PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-word ensure --impact-tag errors --json'
    )
    assert options['recommended_primary_command'] == primary['show_impact_command']
    assert options['recommended_primary_json_command'] == primary['show_impact_json_command']
    primary_group = options['recommended_primary_group']
    assert primary_group['representative']['option_family'] == 'words'
    assert primary_group['representative']['option_label'] == 'ensure'
    assert primary_group['representative']['show_impact_command'] == primary['show_impact_command']
    assert primary_group['representative']['show_impact_json_command'] == primary['show_impact_json_command']
    assert primary_group['represented_recommendation_ranks'] == [1, 3]
    groups = options['recommended_distinct_groups']
    assert options['recommended_distinct_group_count'] == 2
    assert [
        (group['recommendation_rank'], group['representative']['option_family'], group['representative']['option_label'], group['represented_alternative_count'])
        for group in groups
    ] == [
        (1, 'words', 'ensure', 1),
        (2, 'words', 'finally', 2),
    ]
    assert groups[0]['source_recommendation_rank'] == 1
    assert groups[0]['represented_recommendation_ranks'] == [1, 3]
    assert groups[0]['represented_alternative_ranks'] == [3]
    assert groups[0]['representative_reason_code'] == 'coarser-family'
    assert groups[0]['representative_reason'] == 'preferred as the coarsest equivalent cut over distances:0'
    assert groups[1]['source_recommendation_rank'] == 2
    assert groups[1]['represented_recommendation_ranks'] == [2, 4, 5]
    assert groups[1]['represented_alternative_ranks'] == [4, 5]
    assert groups[1]['represented_alternative_labels'] == ['distances:1', 'tags:aliases']
    tags = {row['name']: row for row in payload['source_inventory']['impact_summary']['impact_filter_options']['tags']}
    assert tags['errors']['family_mode'] == 'append'
    assert tags['errors']['current_family_argv'] == ['--impact-tag', 'errors']
    assert tags['errors']['effective_family_argv'] == ['--impact-tag', 'errors']
    assert tags['errors']['show_impact_command'] == (
        'PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-tag errors'
    )
    assert tags['errors']['preview_impact_word_count'] == 2
    assert tags['errors']['preview_impact_case_count'] == 6
    assert tags['errors']['preview_impact_stage_count'] == 2
    assert tags['errors']['preview_is_current_slice'] is True
    assert tags['errors']['preview_changes_slice'] is False
    assert tags['errors']['preview_effect'] == 'same-slice'
    assert tags['errors']['preview_impact_word_delta'] == 0
    assert tags['errors']['preview_impact_case_delta'] == 0
    assert tags['errors']['preview_impact_stage_delta'] == 0
    assert tags['cleanup']['family_mode'] == 'append'
    assert tags['cleanup']['current_family_argv'] == ['--impact-tag', 'errors']
    assert tags['cleanup']['effective_family_argv'] == ['--impact-tag', 'errors', '--impact-tag', 'cleanup']
    assert tags['cleanup']['show_impact_command'] == (
        'PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-tag errors --impact-tag cleanup'
    )


def test_mxportable_cli_can_filter_show_impact_cases_by_name_in_json() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'tools' / 'mxportable.py'),
            '--stdlib-manifest',
            '--word',
            'ensure',
            '--show-impact',
            '--impact-name-contains',
            'cleanup-error-wins',
            '--json',
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload['filters']['impact_tags'] == []
    assert payload['filters']['impact_name_contains'] == 'cleanup-error-wins'
    row = payload['source_inventory']['words'][0]
    assert row['impact_case_names'] == [
        'stdlib-ensure-cleanup-error-wins-on-success',
        'stdlib-ensure-cleanup-error-wins-on-failure',
        'stdlib-finally-cleanup-error-wins-on-success',
        'stdlib-finally-cleanup-error-wins-on-failure',
    ]
    assert row['impact_groups'][0]['case_names'] == [
        'stdlib-ensure-cleanup-error-wins-on-success',
        'stdlib-ensure-cleanup-error-wins-on-failure',
    ]
    assert row['impact_groups'][1]['case_names'] == [
        'stdlib-finally-cleanup-error-wins-on-success',
        'stdlib-finally-cleanup-error-wins-on-failure',
    ]
    assert payload['source_inventory']['impact_summary']['impact_case_count'] == 4


def test_mxportable_cli_can_show_boot_stdlib_manifest_source_metadata() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'tools' / 'mxportable.py'),
            '--stdlib-manifest',
            '--word',
            'try',
            '--show-source',
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0
    assert '[ok] try' in proc.stdout
    assert 'source: ' in proc.stdout
    assert 'src/micromax/stdlib/core.mx:' in proc.stdout
    assert '( ..a body handler -- ..b )' in proc.stdout
    assert 'def: >r' in proc.stdout

    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'tools' / 'mxportable.py'),
            '--stdlib-manifest',
            '--word',
            'ensure',
            '--show-source',
            '--json',
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload['manifest']['word_count'] == 1
    assert payload['source_inventory']['word_count'] == 1
    row = payload['source_inventory']['words'][0]
    assert row['word'] == 'ensure'
    assert row['stack_effect'] == '( ..a body cleanup -- ..b )'
    assert row['definition'].startswith('>r')




def test_mxportable_cli_can_show_boot_stdlib_manifest_dependency_metadata() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'tools' / 'mxportable.py'),
            '--stdlib-manifest',
            '--word',
            'bi',
            '--show-deps',
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0
    assert '[ok] bi' in proc.stdout
    assert 'refs: keep, dip, call' in proc.stdout
    assert 'stdlib refs: keep, dip' in proc.stdout
    assert 'nonstdlib refs: call' in proc.stdout

    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'tools' / 'mxportable.py'),
            '--stdlib-manifest',
            '--word',
            'finally',
            '--show-source',
            '--show-deps',
            '--json',
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload['filters']['show_source'] is True
    assert payload['filters']['show_deps'] is True
    row = payload['source_inventory']['words'][0]
    assert row['word'] == 'finally'
    assert row['alias_of'] == 'ensure'
    assert row['word_refs'] == ['ensure']
    assert row['stdlib_refs'] == ['ensure']
    assert row['nonstdlib_refs'] == []
def test_mxportable_cli_can_show_boot_stdlib_manifest_transitive_closure_metadata() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'tools' / 'mxportable.py'),
            '--stdlib-manifest',
            '--word',
            'finally',
            '--show-closure',
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0
    assert '[ok] finally' in proc.stdout
    assert 'dependency order: ensure' in proc.stdout
    assert 'transitive stdlib refs: ensure' in proc.stdout
    assert 'transitive nonstdlib refs: ' in proc.stdout
    assert 'catch' in proc.stdout
    assert 'stdlib depth: 1' in proc.stdout

    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'tools' / 'mxportable.py'),
            '--stdlib-manifest',
            '--word',
            'bi',
            '--show-source',
            '--show-closure',
            '--json',
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload['filters']['show_source'] is True
    assert payload['filters']['show_closure'] is True
    row = payload['source_inventory']['words'][0]
    assert row['word'] == 'bi'
    assert row['dependency_order'] == ['keep', 'dip']
    assert row['transitive_stdlib_refs'] == ['keep', 'dip']
    assert 'over' in row['transitive_nonstdlib_refs']
    assert row['stdlib_depth'] == 1




def test_mxportable_cli_can_show_boot_stdlib_manifest_reverse_user_metadata() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'tools' / 'mxportable.py'),
            '--stdlib-manifest',
            '--word',
            'ensure',
            '--show-users',
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0
    assert '[ok] ensure' in proc.stdout
    assert 'direct stdlib users: finally' in proc.stdout
    assert 'transitive stdlib users: finally' in proc.stdout
    assert 'user depth: 1' in proc.stdout

    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'tools' / 'mxportable.py'),
            '--stdlib-manifest',
            '--word',
            'keep',
            '--show-source',
            '--show-users',
            '--json',
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload['filters']['show_source'] is True
    assert payload['filters']['show_users'] is True
    row = payload['source_inventory']['words'][0]
    assert row['word'] == 'keep'
    assert row['direct_stdlib_users'] == ['bi', 'tri']
    assert row['transitive_stdlib_users'] == ['bi', 'tri']
    assert row['user_depth'] == 1



def test_mxportable_cli_can_show_boot_stdlib_manifest_change_impact_metadata() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'tools' / 'mxportable.py'),
            '--stdlib-manifest',
            '--word',
            'keep',
            '--show-impact',
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0
    assert '[ok] keep' in proc.stdout
    assert 'impact words: keep, bi, tri' in proc.stdout
    assert 'impact cases: stdlib-keep, stdlib-bi, stdlib-tri' in proc.stdout
    assert 'impact filter options:' in proc.stdout
    assert 'words: keep@0=1 [replace:--impact-word keep; delta:w-2,c-2,d-1; result:w=1,c=1,d=1; same-result: distances:0, names:stdlib-keep], bi@1=1 [replace:--impact-word bi; delta:w-2,c-2,d-1; result:w=1,c=1,d=1; same-result: names:stdlib-bi], tri@1=1 [replace:--impact-word tri; delta:w-2,c-2,d-1; result:w=1,c=1,d=1; same-result: names:stdlib-tri]' in proc.stdout
    assert 'distances: 0(words=keep,cases=1) [replace:--impact-distance 0; delta:w-2,c-2,d-1; result:w=1,c=1,d=1; same-result: names:stdlib-keep, words:keep], 1(words=bi,tri,cases=2) [replace:--impact-distance 1; delta:w-1,c-1,d-1; result:w=2,c=2,d=1]' in proc.stdout
    assert 'categories: stdlib=3 [replace:--impact-category stdlib; same-slice; result:w=3,c=3,d=2; same-result: tags:combinators]' in proc.stdout
    assert 'tags: combinators=3 [append:--impact-tag combinators; same-slice; result:w=3,c=3,d=2; same-result: categories:stdlib]' in proc.stdout
    assert 'names: stdlib-keep[words=keep;depths=0] [replace:--impact-name stdlib-keep; delta:w-2,c-2,d-1; result:w=1,c=1,d=1; same-result: distances:0, words:keep], stdlib-bi[words=bi;depths=1] [replace:--impact-name stdlib-bi; delta:w-2,c-2,d-1; result:w=1,c=1,d=1; same-result: words:bi], stdlib-tri[words=tri;depths=1] [replace:--impact-name stdlib-tri; delta:w-2,c-2,d-1; result:w=1,c=1,d=1; same-result: words:tri]' in proc.stdout
    assert 'impact groups:' in proc.stdout
    assert 'keep <= keep :: stdlib-keep' in proc.stdout
    assert 'bi <= keep -> bi :: stdlib-bi' in proc.stdout
    assert 'impact stages:' in proc.stdout
    assert 'depth 0: keep :: stdlib-keep' in proc.stdout
    assert 'depth 1: bi, tri :: stdlib-bi, stdlib-tri' in proc.stdout
    assert 'impact categories: stdlib=3' in proc.stdout
    assert 'impact tags: combinators=3' in proc.stdout
    assert 'impact case count: 3' in proc.stdout
    assert 'Selected impact summary:' in proc.stdout
    assert 'retest command: PYTHONPATH=src python tools/mxportable.py --name stdlib-keep --name stdlib-bi --name stdlib-tri' in proc.stdout
    assert 'retest json: PYTHONPATH=src python tools/mxportable.py --name stdlib-keep --name stdlib-bi --name stdlib-tri --json' in proc.stdout

    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'tools' / 'mxportable.py'),
            '--stdlib-manifest',
            '--word',
            'ensure',
            '--show-source',
            '--show-impact',
            '--json',
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload['filters']['show_source'] is True
    assert payload['filters']['show_impact'] is True
    row = payload['source_inventory']['words'][0]
    assert row['word'] == 'ensure'
    assert row['selected_words'] == ['ensure']
    assert row['selected_word_count'] == 1
    assert row['impact_words'] == ['ensure', 'finally']
    assert row['impact_case_names'] == (
        BOOT_STDLIB_PORTABILITY_MANIFEST['ensure'] + BOOT_STDLIB_PORTABILITY_MANIFEST['finally']
    )
    assert row['impact_case_count'] == len(row['impact_case_names'])
    assert row['show_impact_command'] == (
        'PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact'
    )
    assert row['show_impact_json_command'] == (
        'PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --json'
    )
    row_groups = {group['word']: group for group in row['impact_groups']}
    assert row_groups['ensure']['paths'] == [['ensure']]
    assert row_groups['ensure']['distance'] == 0
    assert row_groups['ensure']['retest_argv'] == [
        'python',
        'tools/mxportable.py',
        '--name',
        'stdlib-ensure-success-runs-cleanup',
        '--name',
        'stdlib-ensure-failure-reraises-after-cleanup',
        '--name',
        'stdlib-ensure-cleanup-error-wins-on-success',
        '--name',
        'stdlib-ensure-cleanup-error-wins-on-failure',
    ]
    assert row_groups['finally']['paths'] == [['ensure', 'finally']]
    assert row_groups['finally']['distance'] == 1
    assert row['impact_stage_count'] == 2
    row_options = row['impact_filter_options']
    assert [(row['name'], row['distance'], row['case_count']) for row in row_options['words']] == [
        ('ensure', 0, 4),
        ('finally', 1, 4),
    ]
    assert row_options['word_count'] == 2
    assert row_options['words'][0]['filter_argv'] == ['--impact-word', 'ensure']
    assert row_options['words'][0]['filter_family'] == 'impact-word'
    assert row_options['words'][0]['family_mode'] == 'replace'
    assert row_options['words'][0]['current_family_argv'] == []
    assert row_options['words'][0]['effective_family_argv'] == ['--impact-word', 'ensure']
    assert row_options['words'][0]['filter_suffix'] == '--impact-word ensure'
    assert row_options['words'][0]['show_impact_command'] == (
        'PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-word ensure'
    )
    assert row_options['words'][0]['preview_impact_word_count'] == 1
    assert row_options['words'][0]['preview_impact_case_count'] == 4
    assert row_options['words'][0]['preview_impact_stage_count'] == 1
    assert row_options['words'][0]['preview_effect'] == 'narrower'
    assert row_options['words'][0]['preview_impact_word_delta'] == -1
    assert row_options['words'][0]['preview_impact_case_delta'] == -4
    assert row_options['words'][0]['preview_impact_stage_delta'] == -1
    assert row_options['words'][1]['filter_argv'] == ['--impact-word', 'finally']
    assert row_options['words'][1]['filter_suffix'] == '--impact-word finally'
    assert row_options['words'][1]['show_impact_command'] == (
        'PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-word finally'
    )
    assert [(row['distance'], row['words'], row['word_count'], row['case_count']) for row in row_options['distances']] == [
        (0, ['ensure'], 1, 4),
        (1, ['finally'], 1, 4),
    ]
    assert row_options['distance_count'] == 2
    assert row_options['distances'][0]['filter_argv'] == ['--impact-distance', '0']
    assert row_options['distances'][0]['filter_suffix'] == '--impact-distance 0'
    assert row_options['distances'][0]['show_impact_command'] == (
        'PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-distance 0'
    )
    assert row_options['distances'][1]['filter_argv'] == ['--impact-distance', '1']
    assert row_options['distances'][1]['filter_suffix'] == '--impact-distance 1'
    assert row_options['distances'][1]['show_impact_command'] == (
        'PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-distance 1'
    )
    assert row_options['categories'][0]['name'] == 'stdlib'
    assert row_options['categories'][0]['count'] == 8
    assert row_options['categories'][0]['filter_argv'] == ['--impact-category', 'stdlib']
    assert row_options['categories'][0]['filter_suffix'] == '--impact-category stdlib'
    assert row_options['categories'][0]['show_impact_command'] == (
        'PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-category stdlib'
    )
    assert row_options['category_count'] == 1
    assert ('aliases', 4) in {(row['name'], row['count']) for row in row_options['tags']}
    assert ('cleanup', 8) in {(row['name'], row['count']) for row in row_options['tags']}
    assert ('errors', 6) in {(row['name'], row['count']) for row in row_options['tags']}
    assert row_options['tag_count'] == 3
    cleanup_tag = next(row for row in row_options['tags'] if row['name'] == 'cleanup')
    assert cleanup_tag['filter_argv'] == ['--impact-tag', 'cleanup']
    assert cleanup_tag['filter_family'] == 'impact-tag'
    assert cleanup_tag['family_mode'] == 'append'
    assert cleanup_tag['current_family_argv'] == []
    assert cleanup_tag['effective_family_argv'] == ['--impact-tag', 'cleanup']
    assert cleanup_tag['filter_suffix'] == '--impact-tag cleanup'
    assert cleanup_tag['show_impact_command'] == (
        'PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-tag cleanup'
    )
    assert cleanup_tag['preview_impact_word_count'] == 2
    assert cleanup_tag['preview_impact_case_count'] == 8
    assert cleanup_tag['preview_impact_stage_count'] == 2
    assert row_options['name_count'] == 8
    ensure_name = next(row for row in row_options['names'] if row['name'] == 'stdlib-ensure-success-runs-cleanup')
    assert ensure_name['filter_argv'] == ['--impact-name', 'stdlib-ensure-success-runs-cleanup']
    assert ensure_name['filter_suffix'] == '--impact-name stdlib-ensure-success-runs-cleanup'
    assert ensure_name['show_impact_command'] == (
        'PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-name stdlib-ensure-success-runs-cleanup'
    )
    assert row['impact_stages'][0]['distance'] == 0
    assert row['impact_stages'][0]['words'] == ['ensure']
    assert row['impact_stages'][1]['distance'] == 1
    assert row['impact_stages'][1]['words'] == ['finally']
    assert payload['source_inventory']['impact_summary']['selected_words'] == ['ensure']
    assert payload['source_inventory']['impact_summary']['selected_word_count'] == 1
    assert payload['source_inventory']['impact_summary']['impact_words'] == ['ensure', 'finally']
    assert payload['source_inventory']['impact_summary']['impact_case_names'] == (
        BOOT_STDLIB_PORTABILITY_MANIFEST['ensure'] + BOOT_STDLIB_PORTABILITY_MANIFEST['finally']
    )
    assert payload['source_inventory']['impact_summary']['impact_stage_count'] == 2
    assert payload['source_inventory']['impact_summary']['show_impact_command'] == (
        'PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact'
    )
    summary_options = payload['source_inventory']['impact_summary']['impact_filter_options']
    assert [(row['name'], row['distance'], row['case_count']) for row in summary_options['words']] == [
        ('ensure', 0, 4),
        ('finally', 1, 4),
    ]
    assert summary_options['word_count'] == 2
    assert summary_options['words'][0]['filter_suffix'] == '--impact-word ensure'
    assert summary_options['words'][0]['show_impact_command'] == (
        'PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-word ensure'
    )
    assert summary_options['words'][1]['filter_suffix'] == '--impact-word finally'
    assert summary_options['words'][1]['show_impact_command'] == (
        'PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-word finally'
    )
    assert [(row['distance'], row['words'], row['word_count'], row['case_count']) for row in summary_options['distances']] == [
        (0, ['ensure'], 1, 4),
        (1, ['finally'], 1, 4),
    ]
    assert summary_options['distance_count'] == 2
    assert summary_options['distances'][0]['filter_suffix'] == '--impact-distance 0'
    assert summary_options['distances'][0]['show_impact_command'] == (
        'PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-distance 0'
    )
    assert summary_options['distances'][1]['filter_suffix'] == '--impact-distance 1'
    assert summary_options['distances'][1]['show_impact_command'] == (
        'PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-distance 1'
    )
    assert summary_options['categories'][0]['name'] == 'stdlib'
    assert summary_options['categories'][0]['count'] == 8
    assert summary_options['categories'][0]['filter_suffix'] == '--impact-category stdlib'
    assert summary_options['categories'][0]['show_impact_command'] == (
        'PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-category stdlib'
    )
    assert summary_options['category_count'] == 1
    assert ('aliases', 4) in {(row['name'], row['count']) for row in summary_options['tags']}
    assert ('cleanup', 8) in {(row['name'], row['count']) for row in summary_options['tags']}
    assert ('errors', 6) in {(row['name'], row['count']) for row in summary_options['tags']}
    assert summary_options['tag_count'] == 3
    errors_tag = next(row for row in summary_options['tags'] if row['name'] == 'errors')
    assert errors_tag['filter_suffix'] == '--impact-tag errors'
    assert errors_tag['show_impact_command'] == (
        'PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-tag errors'
    )
    assert errors_tag['preview_impact_word_count'] == 2
    assert errors_tag['preview_impact_case_count'] == 6
    assert errors_tag['preview_impact_stage_count'] == 2
    assert summary_options['name_count'] == 8
    finally_name = next(row for row in summary_options['names'] if row['name'] == 'stdlib-finally-cleanup-error-wins-on-failure')
    assert finally_name['filter_suffix'] == '--impact-name stdlib-finally-cleanup-error-wins-on-failure'
    assert finally_name['show_impact_command'] == (
        'PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-impact --impact-name stdlib-finally-cleanup-error-wins-on-failure'
    )
    assert payload['source_inventory']['impact_summary']['impact_stages'][0]['distance'] == 0
    assert payload['source_inventory']['impact_summary']['impact_stages'][0]['words'] == ['ensure']
    assert payload['source_inventory']['impact_summary']['impact_stages'][1]['distance'] == 1
    assert payload['source_inventory']['impact_summary']['impact_stages'][1]['words'] == ['finally']
    assert payload['source_inventory']['impact_summary']['impact_categories'] == [{'name': 'stdlib', 'count': 8}]
    assert {'name': 'cleanup', 'count': 8} in payload['source_inventory']['impact_summary']['impact_tags']
    assert {'name': 'errors', 'count': 6} in payload['source_inventory']['impact_summary']['impact_tags']
    assert row['impact_categories'] == [{'name': 'stdlib', 'count': 8}]
    assert {'name': 'cleanup', 'count': 8} in row['impact_tags']
    assert {'name': 'errors', 'count': 6} in row['impact_tags']
    assert payload['source_inventory']['impact_summary']['retest_command'] == (
        'PYTHONPATH=src python tools/mxportable.py '
        '--name stdlib-ensure-success-runs-cleanup '
        '--name stdlib-ensure-failure-reraises-after-cleanup '
        '--name stdlib-ensure-cleanup-error-wins-on-success '
        '--name stdlib-ensure-cleanup-error-wins-on-failure '
        '--name stdlib-finally-success-runs-cleanup '
        '--name stdlib-finally-failure-reraises-after-cleanup '
        '--name stdlib-finally-cleanup-error-wins-on-success '
        '--name stdlib-finally-cleanup-error-wins-on-failure'
    )


def test_mxportable_cli_can_show_combined_retest_summary_for_multiple_words() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'tools' / 'mxportable.py'),
            '--stdlib-manifest',
            '--word',
            'keep',
            '--word',
            'ensure',
            '--show-impact',
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0
    assert 'Selected impact summary:' in proc.stdout
    assert 'impact words: keep, bi, tri, ensure, finally' in proc.stdout
    assert 'impact cases: stdlib-keep, stdlib-bi, stdlib-tri, stdlib-ensure-success-runs-cleanup' in proc.stdout
    assert 'impact groups:' in proc.stdout
    assert 'bi <= keep -> bi :: stdlib-bi' in proc.stdout
    assert 'retest: PYTHONPATH=src python tools/mxportable.py --name stdlib-bi' in proc.stdout
    assert 'finally <= ensure -> finally :: stdlib-finally-success-runs-cleanup' in proc.stdout
    assert 'impact stages:' in proc.stdout
    assert 'depth 0: keep, ensure :: stdlib-keep, stdlib-ensure-success-runs-cleanup' in proc.stdout
    assert 'depth 1: bi, tri, finally :: stdlib-bi, stdlib-tri, stdlib-finally-success-runs-cleanup' in proc.stdout
    assert 'impact categories: stdlib=11' in proc.stdout
    assert 'impact tags: aliases=4, cleanup=8, combinators=3, errors=6' in proc.stdout
    assert 'retest command: PYTHONPATH=src python tools/mxportable.py --name stdlib-keep --name stdlib-bi --name stdlib-tri --name stdlib-ensure-success-runs-cleanup' in proc.stdout
def test_mxportable_cli_show_impact_uses_full_corpus_for_case_inventory() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'tools' / 'mxportable.py'),
            '--name',
            'stdlib-keep',
            '--stdlib-manifest',
            '--word',
            'keep',
            '--show-impact',
            '--json',
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload['summary']['count'] == 1
    assert payload['source_inventory']['impact_summary']['impact_categories'] == [{'name': 'stdlib', 'count': 3}]
    assert payload['source_inventory']['impact_summary']['impact_tags'] == [
        {'name': 'combinators', 'count': 3},
    ]


def test_mxportable_cli_can_show_boot_stdlib_manifest_in_human_and_json_modes() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / 'tools' / 'mxportable.py'), '--stdlib-manifest', '--word', 'try', '--word', 'ensure'],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0
    assert '[ok] try' in proc.stdout
    assert 'stdlib-try-handler-error-wins-on-failure' in proc.stdout
    assert '[ok] ensure' in proc.stdout
    assert '2/2 boot stdlib words covered' in proc.stdout

    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'tools' / 'mxportable.py'),
            '--stdlib-manifest',
            '--word-contains',
            'tr',
            '--json',
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload['manifest']['word_count'] == 3
    assert payload['manifest']['all_cases_present'] is True
    assert payload['filters']['words'] == []
    assert payload['filters']['word_contains'] == 'tr'
    assert [row['word'] for row in payload['manifest']['words']] == ['tri', 'try?', 'try']


def test_mxportable_cli_show_impact_summary_groups_merge_selected_roots() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'tools' / 'mxportable.py'),
            '--stdlib-manifest',
            '--word',
            'ensure',
            '--word',
            'finally',
            '--show-impact',
            '--json',
        ],
        check=False,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    groups = {row['word']: row for row in payload['source_inventory']['impact_summary']['impact_groups']}
    assert groups['ensure']['selected_words'] == ['ensure']
    assert groups['ensure']['paths'] == [['ensure']]
    assert groups['ensure']['distance'] == 0
    assert groups['finally']['selected_words'] == ['ensure', 'finally']
    assert groups['finally']['paths'] == [['ensure', 'finally'], ['finally']]
    assert groups['finally']['distance'] == 0
    assert groups['finally']['case_names'] == BOOT_STDLIB_PORTABILITY_MANIFEST['finally']
    assert groups['finally']['retest_command'] == (
        'PYTHONPATH=src python tools/mxportable.py '
        '--name stdlib-finally-success-runs-cleanup '
        '--name stdlib-finally-failure-reraises-after-cleanup '
        '--name stdlib-finally-cleanup-error-wins-on-success '
        '--name stdlib-finally-cleanup-error-wins-on-failure'
    )
    assert payload['source_inventory']['impact_summary']['impact_stage_count'] == 1
    assert payload['source_inventory']['impact_summary']['impact_stages'][0]['distance'] == 0
    assert payload['source_inventory']['impact_summary']['impact_stages'][0]['words'] == ['ensure', 'finally']
    assert payload['source_inventory']['impact_summary']['impact_stages'][0]['selected_words'] == ['ensure', 'finally']
