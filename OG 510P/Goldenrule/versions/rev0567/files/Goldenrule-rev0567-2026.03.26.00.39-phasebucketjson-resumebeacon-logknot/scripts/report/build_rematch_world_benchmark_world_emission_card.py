#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SEED = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
EVIDENCE_RECEIPT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_receipt.json'
PREFLIGHT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_preflight_receipt.json'
FROZEN_AUDIT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_frozen_handoff_audit_receipt.json'
COPY_FORWARD_AUDIT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_copy_forward_audit_receipt.json'
BUNDLE = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_publication_bundle_receipt.json'
SPINE_AUDIT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_publication_spine_audit_receipt.json'
RETENTION_EXIT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_retention_exit_receipt.json'
PRUNE = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_prune_execute_receipt.json'
POST_PRUNE = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_post_prune_audit_receipt.json'
CHAIN = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_publication_chain_receipt.json'
PACKAGE = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_package_receipt.json'
MUTATION_GUARD = ROOT / 'scripts' / 'tools' / 'rematch_world_benchmark_mutation_guard.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_world_emission_card.json'
OUT_MD = ROOT / 'docs' / 'REMATCH_WORLD_BENCHMARK_WORLD_EMISSION_CARD.md'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def load_module(path: Path, module_name: str) -> Any:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'could not load {module_name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def section_question_map(guard: Any) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for row in guard.ALLOWED_MUTABLE_PREFIX_ROWS:
        prefix = row['prefix']
        if not prefix.startswith('section_status.'):
            continue
        section = prefix.split('.', 1)[1]
        mapping[section] = list(row['linked_question_ids'])
    return mapping


def build_report() -> dict[str, Any]:
    seed = load_json(SEED)
    evidence_receipt = load_json(EVIDENCE_RECEIPT)
    preflight = load_json(PREFLIGHT)
    frozen_audit = load_json(FROZEN_AUDIT)
    copy_forward = load_json(COPY_FORWARD_AUDIT)
    bundle = load_json(BUNDLE)
    spine = load_json(SPINE_AUDIT)
    retention_exit = load_json(RETENTION_EXIT)
    prune = load_json(PRUNE)
    post_prune = load_json(POST_PRUNE)
    chain = load_json(CHAIN)
    package = load_json(PACKAGE)
    guard = load_module(MUTATION_GUARD, 'rematch_world_benchmark_mutation_guard')

    question_map = section_question_map(guard)
    recommended_fill_order = list(seed['recommended_fill_order'])
    pending_native_sections = []
    for idx, section in enumerate(recommended_fill_order, start=1):
        status = seed['section_status'][section]
        if status != 'pending_fill':
            continue
        pending_native_sections.append(
            {
                'fill_order_index': idx,
                'section': section,
                'linked_question_ids': question_map.get(section, []),
                'status': status,
            }
        )

    frozen_rows = [
        {
            'section': row['section_path'],
            'linked_question_ids': row['linked_question_ids'],
            'source_kind': row['source_kind'],
            'source_path': row['source_path'],
            'exact_match': row['exact_match'],
        }
        for row in frozen_audit['audited_sections']
    ]

    durable_rows = list(retention_exit['durable_retained_objects'])
    transient_rows = list(retention_exit['exit_ready_transient_objects'])
    durable_bytes = sum(int(row['byte_count']) for row in durable_rows)
    transient_bytes = sum(int(row['byte_count']) for row in transient_rows)
    decision_emission = bundle['decision_emission']

    landing_steps = [
        {
            'order': 1,
            'stage': 'freeze copied seed surface',
            'tool_path': 'scripts/tools/audit_rematch_world_benchmark_frozen_handoffs.py',
            'receipt_path': FROZEN_AUDIT.relative_to(ROOT).as_posix(),
            'success_summary': f"exact_match_count={frozen_audit['status_counts']['exact_match_count']} across {frozen_audit['status_counts']['audited_section_count']} copied sections",
        },
        {
            'order': 2,
            'stage': 'retain tiny provenance for distilled run facts',
            'tool_path': 'scripts/tools/build_rematch_world_benchmark_evidence_receipt.py',
            'receipt_path': EVIDENCE_RECEIPT.relative_to(ROOT).as_posix(),
            'success_summary': f"strict_coverage_passed={str(evidence_receipt['strict_coverage_passed']).lower()} with scratch_source_count={evidence_receipt['scratch_source_count']}",
        },
        {
            'order': 3,
            'stage': 'compile back and preflight the filled artifact',
            'tool_path': 'scripts/tools/rematch_world_benchmark_publication_preflight.py',
            'receipt_path': PREFLIGHT.relative_to(ROOT).as_posix(),
            'success_summary': (
                'preflight_ready=true, mutation_surface_ok=true, completion_ready=true, '
                f"filled_world_section_count={preflight['status_counts']['filled_world_section_count']}"
            ),
        },
        {
            'order': 4,
            'stage': 'prove copied handoffs survived compilation unchanged',
            'tool_path': 'scripts/tools/audit_rematch_world_benchmark_copy_forward.py',
            'receipt_path': COPY_FORWARD_AUDIT.relative_to(ROOT).as_posix(),
            'success_summary': f"exact_match_count={copy_forward['status_counts']['exact_match_count']} and mismatch_count={copy_forward['status_counts']['mismatch_count']}",
        },
        {
            'order': 5,
            'stage': 'bundle one compact phase-3 emission proof',
            'tool_path': 'scripts/tools/build_rematch_world_benchmark_publication_bundle_receipt.py',
            'receipt_path': BUNDLE.relative_to(ROOT).as_posix(),
            'success_summary': (
                f"patch_elision_ready={str(bundle['patch_elision_ready']).lower()}, "
                f"world_emission_ready={str(decision_emission['world_emission_ready']).lower()}, "
                f"emitted_question_id_count={decision_emission['emitted_question_id_count']}"
            ),
        },
        {
            'order': 6,
            'stage': 'audit the retained publication spine',
            'tool_path': 'scripts/tools/audit_rematch_world_benchmark_publication_spine.py',
            'receipt_path': SPINE_AUDIT.relative_to(ROOT).as_posix(),
            'success_summary': f"publication_spine_ready={str(spine['publication_spine_ready']).lower()} with durable_spine_bytes={spine['retained_bytes']['durable_spine_bytes']}",
        },
        {
            'order': 7,
            'stage': 'decide whether intermediates may exit',
            'tool_path': 'scripts/tools/build_rematch_world_benchmark_retention_exit_receipt.py',
            'receipt_path': RETENTION_EXIT.relative_to(ROOT).as_posix(),
            'success_summary': (
                f"retention_exit_ready={str(retention_exit['exit_conditions']['retention_exit_ready']).lower()} "
                '(this is a gate, not the final zip authority)'
            ),
        },
        {
            'order': 8,
            'stage': 'prune exit-ready transients by rule',
            'tool_path': 'scripts/tools/prune_rematch_world_benchmark_transients.py --execute',
            'receipt_path': PRUNE.relative_to(ROOT).as_posix(),
            'success_summary': (
                f"prune_ready={str(prune['prune_ready']).lower()}, "
                f"deleted_count={prune['counts']['deleted_count']}, already_absent_count={prune['counts']['already_absent_count']}"
            ),
        },
        {
            'order': 9,
            'stage': 'prove cleaned tree zip-readiness',
            'tool_path': 'scripts/tools/audit_rematch_world_benchmark_post_prune_state.py',
            'receipt_path': POST_PRUNE.relative_to(ROOT).as_posix(),
            'success_summary': f"cleaned_tree_ready_for_zip={str(post_prune['cleaned_tree_ready_for_zip']).lower()} with transient_still_present_count={post_prune['counts']['transient_still_present_count']}",
        },
        {
            'order': 10,
            'stage': 'emit inheritor-facing chain and package proofs',
            'tool_path': 'scripts/tools/build_rematch_world_benchmark_publication_chain_receipt.py + scripts/tools/build_rematch_world_benchmark_package_receipt.py',
            'receipt_path': f"{CHAIN.relative_to(ROOT).as_posix()} ; {PACKAGE.relative_to(ROOT).as_posix()}",
            'success_summary': (
                f"overall_chain_ready={str(chain['status_counts']['overall_chain_ready']).lower()}, "
                f"package_ready={str(package['status_counts']['package_ready']).lower()}"
            ),
        },
    ]

    return {
        'focus': 'collapse the first endogenous rematch-world benchmark fill, copy-forward, phase-3 emission, prune, and package discipline into one inheritor-facing control surface',
        'analysis_script': Path(__file__).relative_to(ROOT).as_posix(),
        'seed_path': SEED.relative_to(ROOT).as_posix(),
        'mutation_guard_path': MUTATION_GUARD.relative_to(ROOT).as_posix(),
        'pending_native_sections': pending_native_sections,
        'pending_native_section_count': len(pending_native_sections),
        'copied_frozen_sections': frozen_rows,
        'copied_frozen_section_count': len(frozen_rows),
        'mutable_prefix_count': len(guard.ALLOWED_MUTABLE_PREFIX_ROWS),
        'frozen_prefix_count': len(guard.FROZEN_PREFIX_ROWS),
        'phase3_emission': {
            'world_emission_ready': decision_emission['world_emission_ready'],
            'bundle_matches_standing_contract': decision_emission['bundle_matches_standing_contract'],
            'emitted_question_id_count': decision_emission['emitted_question_id_count'],
            'emitted_question_ids': decision_emission['emitted_question_ids'],
            'emitted_sections': decision_emission['emitted_sections'],
            'allowed_open_interval_count': decision_emission['allowed_open_interval_count'],
        },
        'durable_publication_objects': durable_rows,
        'durable_publication_object_count': len(durable_rows),
        'durable_publication_bytes': durable_bytes,
        'transient_exit_objects': transient_rows,
        'transient_exit_object_count': len(transient_rows),
        'transient_exit_bytes': transient_bytes,
        'retention_gate': retention_exit['exit_conditions'],
        'chain_status_counts': chain['status_counts'],
        'package_status_counts': package['status_counts'],
        'package_policy_checks': package['policy_checks'],
        'landing_steps': landing_steps,
        'recommended_next_move': 'On the first real endogenous rematch-world run, fill only the five pending native sections, keep the eight copied sections frozen, and treat the authoritative publication closeout as bundle -> spine audit -> post-prune audit -> chain receipt -> package receipt rather than as the pre-prune retention gate alone.',
    }


def render_md(report: dict[str, Any]) -> str:
    native_sections = ', '.join(f"`{row['section']}`" for row in report['pending_native_sections'])
    lines = [
        '# Rematch-world benchmark world-emission card',
        '',
        f"Focus: {report['focus']}",
        '',
        '## Local result',
        '',
        f"- The standing seed still expects exactly `{report['pending_native_section_count']}` native fills: {native_sections}.",
        f"- The copied contract surface stays frozen across `{report['copied_frozen_section_count']}` sections while the mutation guard still allows only `{report['mutable_prefix_count']}` mutable prefixes against `{report['frozen_prefix_count']}` frozen prefixes.",
        f"- The retained publication bundle already proves `world_emission_ready={str(report['phase3_emission']['world_emission_ready']).lower()}` and emits `{report['phase3_emission']['emitted_question_id_count']}` phase-3 question ids across `delay_contract`, `winner_contract`, and `delta_contract`.",
        f"- The durable publication set is `{report['durable_publication_object_count']}` objects / `{report['durable_publication_bytes']}` bytes; the explicit transient exit set is `{report['transient_exit_object_count']}` objects / `{report['transient_exit_bytes']}` bytes.",
        f"- Important sequencing nuance: the example retention gate still says `retention_exit_ready={str(report['retention_gate']['retention_exit_ready']).lower()}`, but the cleaned-tree authority already lands later at `overall_chain_ready={str(report['chain_status_counts']['overall_chain_ready']).lower()}` and `package_ready={str(report['package_status_counts']['package_ready']).lower()}` once post-prune/package receipts are in hand.",
        '',
        '## Native fill targets',
        '',
        '| order | section | linked questions | status |',
        '|---|---|---|---|',
    ]
    for row in report['pending_native_sections']:
        linked = ', '.join(row['linked_question_ids']) if row['linked_question_ids'] else '—'
        lines.append(f"| {row['fill_order_index']} | `{row['section']}` | {linked} | `{row['status']}` |")
    lines.extend([
        '',
        '## Frozen copied surface that should stay citation-first',
        '',
        '| section | linked questions | source |',
        '|---|---|---|',
    ])
    for row in report['copied_frozen_sections']:
        linked = ', '.join(row['linked_question_ids']) if row['linked_question_ids'] else '—'
        lines.append(f"| `{row['section']}` | {linked} | `{row['source_path']}` |")
    lines.extend([
        '',
        '## Landing ladder',
        '',
        '| step | stage | tool | success witness | receipt |',
        '|---|---|---|---|---|',
    ])
    for row in report['landing_steps']:
        lines.append(f"| {row['order']} | {row['stage']} | `{row['tool_path']}` | {row['success_summary']} | `{row['receipt_path']}` |")
    lines.extend([
        '',
        '## Durable publication objects after successful closeout',
        '',
        '| label | bytes | path |',
        '|---|---|---|',
    ])
    for row in report['durable_publication_objects']:
        lines.append(f"| `{row['label']}` | {row['byte_count']} | `{row['path']}` |")
    lines.extend([
        '',
        '## Package hygiene checks',
        '',
    ])
    for key, value in report['package_policy_checks'].items():
        lines.append(f"- `{key}` = `{str(value).lower()}`")
    lines.extend([
        '',
        '## Implementor takeaway',
        '',
        report['recommended_next_move'],
        '',
    ])
    return '\n'.join(lines)


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(report), encoding='utf-8')
    print(f'rematch-world-benchmark-world-emission-card: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'rematch-world-benchmark-world-emission-card: wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
