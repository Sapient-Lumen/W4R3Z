#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SNAP = ROOT / 'examples' / 'snapshots'
RETENTION_EXIT_PATH = SNAP / 'rematch_world_benchmark_retention_exit_receipt.json'
PRUNE_PATH = SNAP / 'rematch_world_benchmark_prune_execute_receipt.json'
POST_PRUNE_PATH = SNAP / 'rematch_world_benchmark_post_prune_audit_receipt.json'
CHAIN_PATH = SNAP / 'rematch_world_benchmark_publication_chain_receipt.json'
PACKAGE_PATH = SNAP / 'rematch_world_benchmark_package_receipt.json'
FROZEN_AUDIT_PATH = SNAP / 'rematch_world_benchmark_frozen_handoff_audit_receipt.json'
COPY_FORWARD_PATH = SNAP / 'rematch_world_benchmark_copy_forward_audit_receipt.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_closeout_lifecycle_ledger.json'
OUT_MD = ROOT / 'docs' / 'REMATCH_WORLD_BENCHMARK_CLOSEOUT_LIFECYCLE_LEDGER.md'


CLOSEOUT_RECEIPT_SPECS = [
    {
        'label': 'frozen_handoff_audit_receipt',
        'path': FROZEN_AUDIT_PATH,
        'receipt_class': 'guard_proof_receipt',
        'phase': 'seed_guards',
        'authority_role': 'upstream_guard',
        'status_getter': lambda chain, *_: {
            'ready': next(item for item in chain['chain_links'] if item['path'] == FROZEN_AUDIT_PATH.relative_to(ROOT).as_posix())['ready'],
            'status_summary': next(item for item in chain['chain_links'] if item['path'] == FROZEN_AUDIT_PATH.relative_to(ROOT).as_posix())['summary'],
        },
        'why_it_matters': 'Proves the copied seed surface still hash-matches its standalone handoff sources before any native fill is compiled.',
    },
    {
        'label': 'copy_forward_audit_receipt',
        'path': COPY_FORWARD_PATH,
        'receipt_class': 'guard_proof_receipt',
        'phase': 'filled_artifact_validation',
        'authority_role': 'upstream_guard',
        'status_getter': lambda chain, *_: {
            'ready': next(item for item in chain['chain_links'] if item['path'] == COPY_FORWARD_PATH.relative_to(ROOT).as_posix())['ready'],
            'status_summary': next(item for item in chain['chain_links'] if item['path'] == COPY_FORWARD_PATH.relative_to(ROOT).as_posix())['summary'],
        },
        'why_it_matters': 'Proves the compiled artifact preserved every copied handoff and compact decision contract root unchanged.',
    },
    {
        'label': 'retention_exit_receipt',
        'path': RETENTION_EXIT_PATH,
        'receipt_class': 'cleanup_gate_receipt',
        'phase': 'transient_exit_and_prune',
        'authority_role': 'pre_prune_gate_only',
        'status_getter': lambda _chain, retention, *_: {
            'ready': retention['exit_conditions']['retention_exit_ready'],
            'status_summary': 'retention_exit_ready=false until scratch hashes are re-proved on the current tree; this is a gate, not final package authority',
        },
        'why_it_matters': 'Declares exactly which objects are durable versus exit-ready so size discipline happens by rule instead of memory.',
    },
    {
        'label': 'prune_execute_receipt',
        'path': PRUNE_PATH,
        'receipt_class': 'cleanup_action_receipt',
        'phase': 'transient_exit_and_prune',
        'authority_role': 'cleanup_execution',
        'status_getter': lambda _chain, _retention, prune, *_: {
            'ready': prune['prune_ready'],
            'status_summary': f"deleted_count={prune['counts']['deleted_count']}, already_absent_count={prune['counts']['already_absent_count']}, removed_bytes={prune['counts']['removed_bytes']}",
        },
        'why_it_matters': 'Turns the exit-ready transient list into one explicit cleanup action and byte removal record.',
    },
    {
        'label': 'post_prune_audit_receipt',
        'path': POST_PRUNE_PATH,
        'receipt_class': 'zip_readiness_receipt',
        'phase': 'transient_exit_and_prune',
        'authority_role': 'zip_readiness_input',
        'status_getter': lambda chain, _retention, _prune, post_prune, *_: {
            'ready': post_prune['cleaned_tree_ready_for_zip'],
            'status_summary': next(item for item in chain['chain_links'] if item['path'] == POST_PRUNE_PATH.relative_to(ROOT).as_posix())['summary'],
        },
        'why_it_matters': 'Proves the durable spine still hash-matches after cleanup and that every transient row is absent or unlinked.',
    },
    {
        'label': 'publication_chain_receipt',
        'path': CHAIN_PATH,
        'receipt_class': 'final_authority_receipt',
        'phase': 'final_authority_receipts',
        'authority_role': 'inheritor_facing_chain_authority',
        'status_getter': lambda _chain, _retention, _prune, _post_prune, chain, *_: {
            'ready': chain['status_counts']['overall_chain_ready'],
            'status_summary': f"overall_chain_ready={chain['status_counts']['overall_chain_ready']} across {chain['status_counts']['ready_link_count']}/{chain['status_counts']['total_link_count']} links",
        },
        'why_it_matters': 'Compresses the surviving proof chain into one inheritor-facing citation surface after post-prune zip readiness is already known.',
    },
    {
        'label': 'package_receipt',
        'path': PACKAGE_PATH,
        'receipt_class': 'final_authority_receipt',
        'phase': 'final_authority_receipts',
        'authority_role': 'package_boundary_authority',
        'status_getter': lambda _chain, _retention, _prune, _post_prune, _chain_receipt, package: {
            'ready': package['status_counts']['package_ready'],
            'status_summary': f"package_ready={package['status_counts']['package_ready']} with {package['status_counts']['passed_check_count']}/{package['status_counts']['total_check_count']} policy checks passed",
        },
        'why_it_matters': 'Captures the final package-boundary policy checks after the closeout ladder is already complete.',
    },
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def build_report() -> dict[str, Any]:
    retention = load_json(RETENTION_EXIT_PATH)
    prune = load_json(PRUNE_PATH)
    post_prune = load_json(POST_PRUNE_PATH)
    chain = load_json(CHAIN_PATH)
    package = load_json(PACKAGE_PATH)

    durable_rows: list[dict[str, Any]] = []
    for row in retention['durable_retained_objects']:
        durable_rows.append(
            {
                'label': row['label'],
                'path': row['path'],
                'phase': 'retained_emission_proof',
                'row_class': 'durable_retained_object',
                'retention_class': row['retention_class'],
                'final_status': 'retained_after_closeout',
                'byte_count': row['byte_count'],
                'sha256': row['sha256'],
                'status_summary': 'retained as part of the durable publication set',
                'why_it_matters': 'Needed to rebuild or verify the retained rematch-world publication spine without keeping the fill patch.',
            }
        )

    prune_rows = {row['label']: row for row in prune['transient_rows']}
    post_prune_rows = {row['label']: row for row in post_prune['transient_rows']}
    transient_rows: list[dict[str, Any]] = []
    for row in retention['exit_ready_transient_objects']:
        prune_row = prune_rows[row['label']]
        audit_row = post_prune_rows[row['label']]
        transient_rows.append(
            {
                'label': row['label'],
                'path': prune_row['path'],
                'phase': 'transient_exit_and_prune',
                'row_class': 'exit_ready_transient_object',
                'retention_class': row['retention_class'],
                'final_status': audit_row['status'],
                'byte_count': row['byte_count'],
                'sha256': row['sha256'],
                'status_summary': f"prune_status={prune_row['status']}; confirmed_absent={audit_row['confirmed_absent']}",
                'why_it_matters': 'Explicit scratch/intermediate surface that may leave once the retained publication spine and cleanup receipts are in hand.',
            }
        )

    closeout_receipt_rows: list[dict[str, Any]] = []
    for spec in CLOSEOUT_RECEIPT_SPECS:
        path = spec['path']
        if not path.exists():
            raise RuntimeError(f'missing closeout receipt: {path.relative_to(ROOT)}')
        status = spec['status_getter'](chain, retention, prune, post_prune, chain, package)
        closeout_receipt_rows.append(
            {
                'label': spec['label'],
                'path': path.relative_to(ROOT).as_posix(),
                'phase': spec['phase'],
                'row_class': spec['receipt_class'],
                'retention_class': 'retained_control_receipt',
                'final_status': 'retained_after_closeout',
                'authority_role': spec['authority_role'],
                'byte_count': path.stat().st_size,
                'sha256': sha256_file(path),
                'ready': status['ready'],
                'status_summary': status['status_summary'],
                'why_it_matters': spec['why_it_matters'],
            }
        )

    lifecycle_rows = durable_rows + transient_rows + closeout_receipt_rows
    final_retained_rows = [row for row in lifecycle_rows if row['final_status'] == 'retained_after_closeout']
    final_retained_bytes = sum(int(row['byte_count']) for row in final_retained_rows)
    closeout_receipt_bytes = sum(int(row['byte_count']) for row in closeout_receipt_rows)

    if len(durable_rows) != 6:
        raise RuntimeError(f'expected 6 durable retained objects, found {len(durable_rows)}')
    if len(transient_rows) != 4:
        raise RuntimeError(f'expected 4 transient rows, found {len(transient_rows)}')
    if len(closeout_receipt_rows) != 7:
        raise RuntimeError(f'expected 7 closeout/control receipts, found {len(closeout_receipt_rows)}')
    if sum(int(row['byte_count']) for row in durable_rows) != retention['retained_byte_totals']['retained_publication_set_bytes']:
        raise RuntimeError('durable retained byte total drifted from retention exit receipt')
    if sum(int(row['byte_count']) for row in transient_rows) != retention['retained_byte_totals']['transient_exit_bytes']:
        raise RuntimeError('transient byte total drifted from retention exit receipt')
    if prune['counts']['deleted_count'] != 1 or prune['counts']['already_absent_count'] != 3:
        raise RuntimeError('unexpected prune row status counts')
    if post_prune['counts']['transient_still_present_count'] != 0:
        raise RuntimeError('expected all transient rows cleared after prune')
    if not chain['status_counts']['overall_chain_ready']:
        raise RuntimeError('expected publication chain receipt to be ready')
    if not package['status_counts']['package_ready']:
        raise RuntimeError('expected package receipt to be ready')

    lifecycle_counts = {
        'durable_retained_object_count': len(durable_rows),
        'durable_retained_bytes': sum(int(row['byte_count']) for row in durable_rows),
        'closeout_receipt_count': len(closeout_receipt_rows),
        'closeout_receipt_bytes': closeout_receipt_bytes,
        'transient_exit_object_count': len(transient_rows),
        'transient_exit_bytes': sum(int(row['byte_count']) for row in transient_rows),
        'transient_deleted_count': prune['counts']['deleted_count'],
        'transient_already_absent_count': prune['counts']['already_absent_count'],
        'final_retained_object_count': len(final_retained_rows),
        'final_retained_bytes': final_retained_bytes,
    }
    status_flags = {
        'retention_exit_ready': retention['exit_conditions']['retention_exit_ready'],
        'publication_spine_ready': retention['exit_conditions']['publication_spine_ready'],
        'cleaned_tree_ready_for_zip': post_prune['cleaned_tree_ready_for_zip'],
        'overall_chain_ready': chain['status_counts']['overall_chain_ready'],
        'package_ready': package['status_counts']['package_ready'],
    }
    main_findings = [
        f"The durable publication set is exactly {lifecycle_counts['durable_retained_object_count']} objects / {lifecycle_counts['durable_retained_bytes']} bytes, while the whole closeout proof family adds only {lifecycle_counts['closeout_receipt_count']} compact retained receipts / {lifecycle_counts['closeout_receipt_bytes']} bytes.",
        f"The transient exit surface stays tiny and explicit: {lifecycle_counts['transient_exit_object_count']} rows / {lifecycle_counts['transient_exit_bytes']} bytes, with only {lifecycle_counts['transient_deleted_count']} concrete deletion and {lifecycle_counts['transient_already_absent_count']} already-absent scratch rows in the standing example.",
        'The retention-exit receipt is intentionally not the final authority surface: it can remain `retention_exit_ready=false` even when the real closeout succeeds later at post-prune zip readiness, publication-chain readiness, and package readiness.',
        f"After closeout, the synthetic rematch-world publication path retains {lifecycle_counts['final_retained_object_count']} exact objects / {lifecycle_counts['final_retained_bytes']} bytes across the durable publication set plus the surviving proof receipts, without keeping the compiled fill patch or scratch source files.",
    ]

    return {
        'focus': 'collapse the rematch-world publication closeout into one exact lifecycle ledger so inheritors can see what must persist, what may exit, and which receipts are actual final authority without reopening seven separate receipts',
        'analysis_script': Path(__file__).relative_to(ROOT).as_posix(),
        'upstream_receipts': [
            RETENTION_EXIT_PATH.relative_to(ROOT).as_posix(),
            PRUNE_PATH.relative_to(ROOT).as_posix(),
            POST_PRUNE_PATH.relative_to(ROOT).as_posix(),
            CHAIN_PATH.relative_to(ROOT).as_posix(),
            PACKAGE_PATH.relative_to(ROOT).as_posix(),
            FROZEN_AUDIT_PATH.relative_to(ROOT).as_posix(),
            COPY_FORWARD_PATH.relative_to(ROOT).as_posix(),
        ],
        'lifecycle_counts': lifecycle_counts,
        'status_flags': status_flags,
        'durable_rows': durable_rows,
        'transient_rows': transient_rows,
        'closeout_receipt_rows': closeout_receipt_rows,
        'lifecycle_rows': lifecycle_rows,
        'main_findings': main_findings,
        'recommended_next_move': 'Use this ledger when cutting the first real native publication: keep the six-object durable publication set plus the compact proof receipts, let the explicit transient rows exit by rule, and treat final authority as post-prune audit -> publication-chain receipt -> package receipt rather than as the retention-exit gate alone.',
    }


def render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Rematch-world benchmark closeout lifecycle ledger')
    lines.append('')
    lines.append(f"Focus: {report['focus']}")
    lines.append('')
    lines.append('## Local result')
    for item in report['main_findings']:
        lines.append(f'- {item}')
    lines.append('')
    lines.append('## Lifecycle counts')
    lines.append('')
    lines.append('| category | count | bytes | note |')
    lines.append('|---|---:|---:|---|')
    counts = report['lifecycle_counts']
    lines.append(f"| durable publication set | `{counts['durable_retained_object_count']}` | `{counts['durable_retained_bytes']}` | exact objects that remain reconstructible without the fill patch |")
    lines.append(f"| closeout proof receipts | `{counts['closeout_receipt_count']}` | `{counts['closeout_receipt_bytes']}` | guard / cleanup / authority receipts retained around the durable spine |")
    lines.append(f"| transient exit surface | `{counts['transient_exit_object_count']}` | `{counts['transient_exit_bytes']}` | explicit patch/scratch rows allowed to leave after proof succeeds |")
    lines.append(f"| final retained closeout set | `{counts['final_retained_object_count']}` | `{counts['final_retained_bytes']}` | durable publication set plus surviving proof receipts |")
    lines.append('')
    lines.append('## Durable publication set')
    lines.append('')
    lines.append('| label | bytes | path |')
    lines.append('|---|---:|---|')
    for row in report['durable_rows']:
        lines.append(f"| `{row['label']}` | `{row['byte_count']}` | `{row['path']}` |")
    lines.append('')
    lines.append('## Exit-ready transient surface')
    lines.append('')
    lines.append('| label | bytes | final status | path |')
    lines.append('|---|---:|---|---|')
    for row in report['transient_rows']:
        lines.append(f"| `{row['label']}` | `{row['byte_count']}` | `{row['final_status']}` | `{row['path']}` |")
    lines.append('')
    lines.append('## Closeout proof receipts')
    lines.append('')
    lines.append('| label | phase | role | ready | bytes | path |')
    lines.append('|---|---|---|---|---:|---|')
    for row in report['closeout_receipt_rows']:
        lines.append(f"| `{row['label']}` | `{row['phase']}` | `{row['authority_role']}` | `{str(row['ready']).lower()}` | `{row['byte_count']}` | `{row['path']}` |")
    lines.append('')
    lines.append('## Exact lifecycle ledger')
    lines.append('')
    lines.append('| label | class | phase | final status | bytes | status summary |')
    lines.append('|---|---|---|---|---:|---|')
    for row in report['lifecycle_rows']:
        lines.append(f"| `{row['label']}` | `{row['row_class']}` | `{row['phase']}` | `{row['final_status']}` | `{row['byte_count']}` | {row['status_summary']} |")
    lines.append('')
    lines.append('## Implementor takeaway')
    lines.append('')
    lines.append(report['recommended_next_move'])
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    report = build_report()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(report) + '\n', encoding='utf-8')
    print(f'rematch-world-benchmark-closeout-lifecycle-ledger: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'rematch-world-benchmark-closeout-lifecycle-ledger: wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
