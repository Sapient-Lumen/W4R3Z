from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from micromax.portability_suite import (
    load_portability_cases,
    portability_case_record,
    portability_inventory,
    portability_summary,
    run_portability_cases,
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
        'execute-xt',
        'wordlist-search-order-lookup',
        'module-in-defines-into-existing-module',
        'set-current-roundtrip',
        'while-loop-increments-to-bound',
        'when-false-skips-quote',
        'zero-equals-predicate',
        'catch-success-returns-zero-ior',
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
        'stdlib-bi',
        'stdlib-dip',
        'stdlib-2dip',
        'stdlib-2keep',
        'stdlib-tri',
        'stdlib-try-question-failure-restores-stack',
        'stdlib-try-handler-on-failure',
        'stdlib-recover-handler-on-failure',
        'stdlib-ensure-success-runs-cleanup',
        'stdlib-finally-success-runs-cleanup',
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
    with pytest.raises(ValueError, match='exactly one of expect_stack or expect_error_contains'):
        load_portability_cases(p)



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



def test_select_portability_cases_can_filter_by_category_tag_and_name() -> None:
    cases = load_portability_cases()

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
    assert [c['name'] for c in recover] == ['stdlib-recover-handler-on-failure']



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
    assert '1 matching portability cases' in proc.stdout



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
    assert '16/16 portability cases passed' in proc.stdout



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
