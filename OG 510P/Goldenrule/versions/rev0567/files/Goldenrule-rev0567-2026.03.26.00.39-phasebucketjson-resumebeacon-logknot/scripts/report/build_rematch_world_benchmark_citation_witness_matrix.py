#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SPEC_LEDGER_PATH = ROOT / 'docs' / 'spec_ledger.md'
WORLD_EMISSION_DOC = ROOT / 'docs' / 'REMATCH_WORLD_BENCHMARK_WORLD_EMISSION_CARD.md'
NATIVE_FILL_MAP_DOC = ROOT / 'docs' / 'REMATCH_WORLD_BENCHMARK_NATIVE_FILL_MAP.md'
LANDING_LADDER_DOC = ROOT / 'docs' / 'REMATCH_WORLD_BENCHMARK_LANDING_LADDER.md'
EXAMPLE_DELTA_LEDGER_DOC = ROOT / 'docs' / 'REMATCH_WORLD_BENCHMARK_EXAMPLE_DELTA_LEDGER.md'
CLOSEOUT_LIFECYCLE_DOC = ROOT / 'docs' / 'REMATCH_WORLD_BENCHMARK_CLOSEOUT_LIFECYCLE_LEDGER.md'
PUBLICATION_BUNDLE_RECEIPT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_publication_bundle_receipt.json'
PACKAGE_RECEIPT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_package_receipt.json'
WORLD_EMISSION_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_world_emission_card.json'
NATIVE_FILL_MAP_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_native_fill_map.json'
LANDING_LADDER_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_landing_ladder.json'
EXAMPLE_DELTA_LEDGER_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_example_delta_ledger.json'
CLOSEOUT_LIFECYCLE_REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_closeout_lifecycle_ledger.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_citation_witness_matrix.json'
OUT_MD = ROOT / 'docs' / 'REMATCH_WORLD_BENCHMARK_CITATION_WITNESS_MATRIX.md'

TITLE = '# Rematch-world benchmark citation witness matrix'
SUBTITLE = (
    'Generated minimal citation surface for the first endogenous rematch-world benchmark. '
    'Use it to cite the smallest existing control surfaces for each claim family instead of reopening broader artifacts or retaining extra scratch.'
)


CLAIM_FAMILY_SPECS = [
    {
        'claim_family_id': 'RWC-001',
        'claim_label': 'editable native-fill surface',
        'posture': 'bridge_ready',
        'minimal_citation_paths': [WORLD_EMISSION_DOC, NATIVE_FILL_MAP_DOC],
        'open_spec_ids': ['SG-003'],
        'summary_builder': lambda ctx: (
            f"The first native rematch-world publication is already narrowed to {ctx['world_emission']['pending_native_section_count']} native sections "
            f"with {ctx['native_fill_map']['minimum_publishable_mutation_set']['explicit_fill_blocker_count']} exact blocker loci, while "
            f"{ctx['world_emission']['copied_frozen_section_count']} copied sections stay frozen and citation-first."
        ),
        'why_it_matters': 'Lets the first Rust-capable inheritor start from one exact edit boundary instead of rediscovering where native work is allowed.',
    },
    {
        'claim_family_id': 'RWC-002',
        'claim_label': 'concrete mutation witness',
        'posture': 'bridge_ready',
        'minimal_citation_paths': [EXAMPLE_DELTA_LEDGER_DOC, NATIVE_FILL_MAP_DOC],
        'open_spec_ids': ['SG-003'],
        'summary_builder': lambda ctx: (
            f"The synthetic compiled example changes exactly {ctx['delta_ledger']['total_changed_path_count']} JSON paths: "
            f"{ctx['delta_ledger']['required_publishable_change_count']} required publication-floor changes plus "
            f"{ctx['delta_ledger']['optional_change_count']} optional row insertions inside already-allowed prefixes."
        ),
        'why_it_matters': 'Gives the implementor one exact mutation witness for the first landing without reopening both the seed and compiled artifact.',
    },
    {
        'claim_family_id': 'RWC-003',
        'claim_label': 'landing order and closeout sequence',
        'posture': 'bridge_ready',
        'minimal_citation_paths': [LANDING_LADDER_DOC, CLOSEOUT_LIFECYCLE_DOC],
        'open_spec_ids': [],
        'summary_builder': lambda ctx: (
            f"The publication floor resolves to {ctx['landing_ladder']['edit_stage_count']} ordered edit stages and "
            f"{ctx['landing_ladder']['closeout_phase_count']} ordered closeout phases rather than an ad hoc bundle/prune/package ritual."
        ),
        'why_it_matters': 'Keeps the first native landing reproducible and small by turning procedure memory into one exact ordered witness.',
    },
    {
        'claim_family_id': 'RWC-004',
        'claim_label': 'phase-3 world emission witness',
        'posture': 'bridge_ready',
        'minimal_citation_paths': [WORLD_EMISSION_DOC, PUBLICATION_BUNDLE_RECEIPT],
        'open_spec_ids': ['SA-003', 'SG-003'],
        'summary_builder': lambda ctx: (
            f"The retained bundle receipt already proves `world_emission_ready={ctx['bundle_receipt']['decision_emission']['world_emission_ready']}` across "
            f"{ctx['bundle_receipt']['decision_emission']['emitted_question_id_count']} emitted question ids while keeping the compiled patch scratch-only."
        ),
        'why_it_matters': 'Preserves one compact proof that the benchmark really emits the copied phase-3 decision contract even before a world-native contract exists.',
    },
    {
        'claim_family_id': 'RWC-005',
        'claim_label': 'role and rematch-state disclosure',
        'posture': 'provisional_interpretation',
        'minimal_citation_paths': [WORLD_EMISSION_DOC],
        'open_spec_ids': ['SA-011', 'SQ-012'],
        'summary_builder': lambda ctx: (
            f"Role assignment and rematch-state carry are still provisional interpretation surfaces: the world card names the copied frozen semantics handoff, "
            f"but asymmetry still requires explicit role policy and a companion role-swapped benchmark when material."
        ),
        'why_it_matters': 'Warns inheritors not to oversell asymmetry-sensitive claims from the bridge benchmark before the open role/state question is resolved.',
    },
    {
        'claim_family_id': 'RWC-006',
        'claim_label': 'delay tax versus efficiency and welfare decomposition',
        'posture': 'provisional_interpretation',
        'minimal_citation_paths': [WORLD_EMISSION_DOC],
        'open_spec_ids': ['SA-012', 'SA-013', 'SQ-013', 'SQ-014'],
        'summary_builder': lambda ctx: (
            f"Delay-tax and welfare claims remain provisional until occupancy accounting is treated as non-optional: the bridge benchmark already exposes "
            f"the relevant copied handoffs, but comparative welfare still depends on matched-vs-searching and occupancy decomposition fields."
        ),
        'why_it_matters': 'Separates what the archive can already publish from the stronger market-efficiency and welfare claims that still need explicit world-native disclosure rules.',
    },
    {
        'claim_family_id': 'RWC-007',
        'claim_label': 'paired leaderboard interpretation',
        'posture': 'provisional_interpretation',
        'minimal_citation_paths': [WORLD_EMISSION_DOC, NATIVE_FILL_MAP_DOC],
        'open_spec_ids': ['SA-015', 'SQ-015', 'SQ-016'],
        'summary_builder': lambda ctx: (
            f"Leaderboard claims are still provisional unless paired occupancy/tempo views remain visible: the native-fill map names the paired-ranking contract as one of the "
            f"{ctx['native_fill_map']['native_section_count']} native sections, but the archive still treats aggregate-only leaderboards as incomplete."
        ),
        'why_it_matters': 'Keeps eventual rankings honest by requiring occupancy-normalized paired views rather than letting aggregate welfare hide tempo artifacts.',
    },
    {
        'claim_family_id': 'RWC-008',
        'claim_label': 'final package-boundary authority',
        'posture': 'final_authority',
        'minimal_citation_paths': [CLOSEOUT_LIFECYCLE_DOC, PACKAGE_RECEIPT],
        'open_spec_ids': [],
        'summary_builder': lambda ctx: (
            f"Final authority is the post-prune -> chain -> package closeout path: the lifecycle ledger names the surviving authority sequence and the package receipt is already "
            f"`package_ready={ctx['package_receipt']['status_counts']['package_ready']}` with "
            f"{ctx['package_receipt']['status_counts']['passed_check_count']}/{ctx['package_receipt']['status_counts']['total_check_count']} policy checks passed."
        ),
        'why_it_matters': 'Prevents the archive from mistaking the pre-prune retention gate for final package authority when cutting a real publication zip.',
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


def parse_spec_ledger(path: Path) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        stripped = line.strip()
        if not stripped.startswith('|'):
            continue
        parts = [part.strip() for part in stripped.strip('|').split('|')]
        if len(parts) != 6:
            continue
        if parts[0] == 'id' or set(parts[0]) == {'-'}:
            continue
        rows[parts[0]] = {
            'id': parts[0],
            'kind': parts[1],
            'status': parts[2],
            'owner': parts[3],
            'review_by': parts[4],
            'summary': parts[5],
        }
    return rows


def surface_kind(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith('docs/'):
        return 'generated_doc'
    if rel.startswith('examples/snapshots/'):
        return 'receipt_snapshot'
    if rel.startswith('artifacts/reports/'):
        return 'generated_report'
    return 'repo_surface'


def build_report() -> dict[str, Any]:
    for path in [
        SPEC_LEDGER_PATH,
        WORLD_EMISSION_DOC,
        NATIVE_FILL_MAP_DOC,
        LANDING_LADDER_DOC,
        EXAMPLE_DELTA_LEDGER_DOC,
        CLOSEOUT_LIFECYCLE_DOC,
        PUBLICATION_BUNDLE_RECEIPT,
        PACKAGE_RECEIPT,
        WORLD_EMISSION_REPORT,
        NATIVE_FILL_MAP_REPORT,
        LANDING_LADDER_REPORT,
        EXAMPLE_DELTA_LEDGER_REPORT,
        CLOSEOUT_LIFECYCLE_REPORT,
    ]:
        if not path.exists():
            raise RuntimeError(f'missing required input: {path.relative_to(ROOT)}')

    ctx = {
        'world_emission': load_json(WORLD_EMISSION_REPORT),
        'native_fill_map': load_json(NATIVE_FILL_MAP_REPORT),
        'landing_ladder': load_json(LANDING_LADDER_REPORT),
        'delta_ledger': load_json(EXAMPLE_DELTA_LEDGER_REPORT),
        'closeout_lifecycle': load_json(CLOSEOUT_LIFECYCLE_REPORT),
        'bundle_receipt': load_json(PUBLICATION_BUNDLE_RECEIPT),
        'package_receipt': load_json(PACKAGE_RECEIPT),
    }
    spec_ledger = parse_spec_ledger(SPEC_LEDGER_PATH)

    claim_rows: list[dict[str, Any]] = []
    cited_surface_rows: dict[str, dict[str, Any]] = {}
    open_spec_touched_by: dict[str, list[str]] = {}
    posture_counts: dict[str, int] = {'bridge_ready': 0, 'provisional_interpretation': 0, 'final_authority': 0}

    for spec in CLAIM_FAMILY_SPECS:
        minimal_paths = [path.relative_to(ROOT).as_posix() for path in spec['minimal_citation_paths']]
        missing_spec_ids = [spec_id for spec_id in spec['open_spec_ids'] if spec_id not in spec_ledger]
        if missing_spec_ids:
            raise RuntimeError(f"missing spec ledger rows for {spec['claim_family_id']}: {missing_spec_ids}")
        posture_counts[spec['posture']] += 1
        open_specs = []
        for spec_id in spec['open_spec_ids']:
            row = spec_ledger[spec_id]
            open_specs.append(
                {
                    'id': spec_id,
                    'kind': row['kind'],
                    'status': row['status'],
                    'summary': row['summary'],
                }
            )
            open_spec_touched_by.setdefault(spec_id, []).append(spec['claim_family_id'])
        claim_rows.append(
            {
                'claim_family_id': spec['claim_family_id'],
                'claim_label': spec['claim_label'],
                'posture': spec['posture'],
                'claim_summary': spec['summary_builder'](ctx),
                'minimal_citation_paths': minimal_paths,
                'minimal_citation_count': len(minimal_paths),
                'open_spec_ids': spec['open_spec_ids'],
                'open_specs': open_specs,
                'why_it_matters': spec['why_it_matters'],
            }
        )
        for path in spec['minimal_citation_paths']:
            rel = path.relative_to(ROOT).as_posix()
            cited_surface_rows.setdefault(
                rel,
                {
                    'path': rel,
                    'surface_kind': surface_kind(path),
                    'byte_count': path.stat().st_size,
                    'sha256': sha256_file(path),
                    'used_by_claim_family_ids': [],
                },
            )
            cited_surface_rows[rel]['used_by_claim_family_ids'].append(spec['claim_family_id'])

    for row in cited_surface_rows.values():
        row['used_by_claim_family_ids'] = sorted(row['used_by_claim_family_ids'])
        row['used_by_claim_family_count'] = len(row['used_by_claim_family_ids'])

    cited_surfaces = sorted(cited_surface_rows.values(), key=lambda row: row['path'])
    open_spec_rows = []
    for spec_id, claim_ids in sorted(open_spec_touched_by.items()):
        row = spec_ledger[spec_id]
        open_spec_rows.append(
            {
                'id': spec_id,
                'kind': row['kind'],
                'status': row['status'],
                'summary': row['summary'],
                'touched_by_claim_family_ids': sorted(claim_ids),
                'touched_by_claim_family_count': len(set(claim_ids)),
            }
        )

    counts = {
        'claim_family_count': len(claim_rows),
        'bridge_ready_count': posture_counts['bridge_ready'],
        'provisional_interpretation_count': posture_counts['provisional_interpretation'],
        'final_authority_count': posture_counts['final_authority'],
        'minimal_unique_surface_count': len(cited_surfaces),
        'open_spec_touchpoint_count': len(open_spec_rows),
    }

    main_findings = [
        f"{counts['claim_family_count']} rematch-world claim families now collapse onto {counts['minimal_unique_surface_count']} small citation surfaces.",
        f"{counts['bridge_ready_count']} families are bridge-ready, {counts['provisional_interpretation_count']} stay explicitly provisional, and {counts['final_authority_count']} carries package-boundary authority.",
        f"The phase-3 bundle still proves `world_emission_ready={ctx['bundle_receipt']['decision_emission']['world_emission_ready']}` while keeping patch retention off (`patch_retention_required={ctx['bundle_receipt']['patch_retention_required']}`).",
        f"Final closeout authority remains the later `post_prune -> chain -> package` path over {ctx['closeout_lifecycle']['lifecycle_counts']['durable_retained_object_count']} durable objects, not the pre-prune retention gate.",
    ]

    return {
        'analysis_script': Path(__file__).relative_to(ROOT).as_posix(),
        'focus': 'map each first-publication rematch-world claim family to the smallest existing citation surfaces and the exact open spec touchpoints that still constrain interpretation',
        'counts': counts,
        'main_findings': main_findings,
        'claim_family_rows': claim_rows,
        'cited_surfaces': cited_surfaces,
        'open_spec_rows': open_spec_rows,
        'recommended_next_move': 'Use this matrix when writing or reviewing the first native rematch-world handoff: cite the named small surfaces instead of reopening broad artifacts, and replace the provisional rows with world-native receipts only when the corresponding open spec questions close.',
    }


def render(report: dict[str, Any]) -> str:
    counts = report['counts']
    lines = [
        TITLE,
        '',
        f"Focus: {report['focus']}",
        '',
        SUBTITLE,
        '',
        '## Main findings',
        '',
    ]
    lines.extend([f"- {row}" for row in report['main_findings']])
    lines.extend(
        [
            '',
            '## Counts',
            '',
            f"- claim_family_count: {counts['claim_family_count']}",
            f"- bridge_ready_count: {counts['bridge_ready_count']}",
            f"- provisional_interpretation_count: {counts['provisional_interpretation_count']}",
            f"- final_authority_count: {counts['final_authority_count']}",
            f"- minimal_unique_surface_count: {counts['minimal_unique_surface_count']}",
            f"- open_spec_touchpoint_count: {counts['open_spec_touchpoint_count']}",
            '',
            '## Claim family matrix',
            '',
            '| claim_family_id | posture | claim_label | minimal_citation_paths | open_spec_ids |',
            '|---|---|---|---|---|',
        ]
    )
    for row in report['claim_family_rows']:
        citation_paths = '<br>'.join(f"`{path}`" for path in row['minimal_citation_paths'])
        open_ids = ', '.join(f"`{spec_id}`" for spec_id in row['open_spec_ids']) if row['open_spec_ids'] else '—'
        lines.append(
            f"| `{row['claim_family_id']}` | `{row['posture']}` | {row['claim_label']} | {citation_paths} | {open_ids} |"
        )

    lines.extend(['', '## Claim family details', ''])
    for row in report['claim_family_rows']:
        lines.extend(
            [
                f"### {row['claim_family_id']} — {row['claim_label']}",
                '',
                f"- posture: `{row['posture']}`",
                f"- claim_summary: {row['claim_summary']}",
                f"- why_it_matters: {row['why_it_matters']}",
                '- minimal_citation_paths:',
            ]
        )
        lines.extend([f"  - `{path}`" for path in row['minimal_citation_paths']])
        if row['open_specs']:
            lines.append('- open_spec_touchpoints:')
            lines.extend(
                [
                    f"  - `{spec['id']}` ({spec['kind']}, {spec['status']}): {spec['summary']}"
                    for spec in row['open_specs']
                ]
            )
        else:
            lines.append('- open_spec_touchpoints: none')
        lines.append('')

    lines.extend(
        [
            '## Cited surfaces',
            '',
            '| path | surface_kind | bytes | sha256_prefix | used_by |',
            '|---|---|---:|---|---|',
        ]
    )
    for row in report['cited_surfaces']:
        lines.append(
            f"| `{row['path']}` | `{row['surface_kind']}` | {row['byte_count']} | `{row['sha256'][:12]}` | {', '.join(f'`{cid}`' for cid in row['used_by_claim_family_ids'])} |"
        )

    lines.extend(
        [
            '',
            '## Open spec touchpoints',
            '',
            '| id | kind | status | touched_by | summary |',
            '|---|---|---|---|---|',
        ]
    )
    for row in report['open_spec_rows']:
        lines.append(
            f"| `{row['id']}` | `{row['kind']}` | `{row['status']}` | {', '.join(f'`{cid}`' for cid in row['touched_by_claim_family_ids'])} | {row['summary']} |"
        )

    lines.extend(['', '## Recommended next move', '', f"- {report['recommended_next_move']}", ''])
    return '\n'.join(lines)


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render(report), encoding='utf-8')
    print(f'wrote {OUT_JSON.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
