#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    'INDEX.md',
    'PRIORITIES.md',
    'RESEARCH_LOG.md',
    'STRATEGIC_FRONTIER.md',
    'AGENTS.md',
    'meta/ACTIVE_FRONTIER.md',
    'meta/AMNESIA_RESISTORS.md',
    'meta/ARCHIVE_DOCTOR_PROTOCOL.md',
    'meta/ARCHIVE_MANIFEST.md',
    'meta/CANONICAL_WORKING_SET.md',
    'meta/REVISION_OPERATING_PROTOCOL.md',
    'design/portfolio-archive-doctor-2026Q1.md',
    'tools/check_cargo_report_pack_contract.py',
    'tools/check_portfolio_envelope_contract.py',
    'meta/PROVING_GROUNDS_PROTOCOL.md',
    'meta/ANCHOR_CORPUS_PROTOCOL.md',
    'meta/EXEMPLAR_FEDERATION_PROTOCOL.md',
    'proofgrounds/README.md',
    'proofgrounds/portfolio-scenario-matrix-v0/scenarios.json',
    'proofgrounds/portfolio-anchor-corpus-v0/anchors.json',
    'proofgrounds/portfolio-exemplar-federation-v0/README.md',
    'proofgrounds/portfolio-exemplar-federation-v0/exemplars.json',
    'design/portfolio-proving-grounds-2026Q1.md',
    'design/portfolio-anchor-corpus-2026Q1.md',
    'design/portfolio-exemplar-federation-2026Q1.md',
    'tools/check_proving_ground_matrix.py',
    'tools/check_anchor_corpus.py',
    'tools/check_exemplar_federation.py',
    'meta/HYPOTHESIS_LEDGER_PROTOCOL.md',
    'meta/LAUNCH_WEDGE_PROTOCOL.md',
    'meta/DECISION_JOURNEY_PROTOCOL.md',
    'meta/KERNEL_SHIPSET_LEDGER_PROTOCOL.md',
    'meta/HANDOFF_GRAPH_PROTOCOL.md',
    'ledgers/top-band-handoff-graph-v0/README.md',
    'ledgers/top-band-handoff-graph-v0/handoffs.json',
    'design/epic-contribution-handoff-graph-2026Q1.md',
    'tools/check_handoff_graph.py',
    'ledgers/top-band-kernel-shipsets-v0/README.md',
    'ledgers/top-band-kernel-shipsets-v0/shipsets.json',
    'design/epic-contribution-kernel-shipset-ledger-2026Q1.md',
    'tools/check_kernel_shipsets.py',
    'ledgers/portfolio-decision-journeys-v0/README.md',
    'ledgers/portfolio-decision-journeys-v0/journeys.json',
    'design/epic-contribution-decision-journeys-2026Q1.md',
    'tools/check_decision_journeys.py',
    'ledgers/README.md',
    'ledgers/portfolio-hypothesis-ledger-v0/hypotheses.json',
    'ledgers/portfolio-launch-wedges-v0/README.md',
    'ledgers/portfolio-launch-wedges-v0/wedges.json',
    'design/portfolio-hypothesis-ledger-2026Q1.md',
    'design/epic-contribution-launch-wedges-2026Q1.md',
    'tools/check_hypothesis_ledger.py',
    'tools/check_launch_wedges.py',
    'meta/SOURCE_ATLAS_PROTOCOL.md',
    'atlases/README.md',
    'atlases/portfolio-source-atlas-v0/sources.json',
    'design/portfolio-source-atlas-2026Q1.md',
    'tools/check_source_atlas.py',
    'meta/KERNEL_FIXTURE_PACK_PROTOCOL.md',
    'meta/KERNEL_ARTIFACT_SCHEMA_PROTOCOL.md',
    'fixtures/README.md',
    'fixtures/top-band-v0/README.md',
    'fixtures/top-band-v0/fixture-pack-hygiene-checks.json',
    'schemas/README.md',
    'schemas/top-band-v0/README.md',
    'schemas/top-band-v0/schema-pack-hygiene-checks.json',
    'tools/check_kernel_fixture_packs.py',
    'tools/check_kernel_artifact_schemas.py',
    'meta/CONTRIBUTION_SHAPE_PROTOCOL.md',
    'morphologies/README.md',
    'morphologies/portfolio-contribution-shapes-v0/shapes.json',
    'design/portfolio-contribution-shapes-2026Q1.md',
    'tools/check_contribution_shapes.py',
]

CHECKS = [
    ('cargo_report_pack_contract', [sys.executable, str(ROOT / 'tools' / 'check_cargo_report_pack_contract.py')]),
    ('portfolio_envelope_contract', [sys.executable, str(ROOT / 'tools' / 'check_portfolio_envelope_contract.py')]),
    ('proving_ground_matrix', [sys.executable, str(ROOT / 'tools' / 'check_proving_ground_matrix.py')]),
    ('anchor_corpus', [sys.executable, str(ROOT / 'tools' / 'check_anchor_corpus.py')]),
    ('exemplar_federation', [sys.executable, str(ROOT / 'tools' / 'check_exemplar_federation.py')]),
    ('hypothesis_ledger', [sys.executable, str(ROOT / 'tools' / 'check_hypothesis_ledger.py')]),
    ('launch_wedges', [sys.executable, str(ROOT / 'tools' / 'check_launch_wedges.py')]),
    ('decision_journeys', [sys.executable, str(ROOT / 'tools' / 'check_decision_journeys.py')]),
    ('kernel_shipsets', [sys.executable, str(ROOT / 'tools' / 'check_kernel_shipsets.py')]),
    ('handoff_graph', [sys.executable, str(ROOT / 'tools' / 'check_handoff_graph.py')]),
    ('source_atlas', [sys.executable, str(ROOT / 'tools' / 'check_source_atlas.py')]),
    ('kernel_fixture_packs', [sys.executable, str(ROOT / 'tools' / 'check_kernel_fixture_packs.py')]),
    ('kernel_artifact_schemas', [sys.executable, str(ROOT / 'tools' / 'check_kernel_artifact_schemas.py')]),
    ('contribution_shapes', [sys.executable, str(ROOT / 'tools' / 'check_contribution_shapes.py')]),
]

MANUAL_QUEUE = [
    {
        'name': 'canonical_renewal_queue',
        'path': 'meta/CANONICAL_RENEWAL_QUEUE.md',
        'reason': 'external-evidence freshness remains a human-reviewed task',
    },
    {
        'name': 'default_card_renewal_queue',
        'path': 'meta/DEFAULT_CARD_RENEWAL_QUEUE.md',
        'reason': 'lane-default corpus drift and renewal stay human-reviewed',
    },
    {
        'name': 'active_frontier',
        'path': 'meta/ACTIVE_FRONTIER.md',
        'reason': 'frontier posture and deepening-vs-promotion remain editorial decisions',
    },
    {
        'name': 'canonical_working_set',
        'path': 'meta/CANONICAL_WORKING_SET.md',
        'reason': 'working-set routing still requires human judgment and prioritization',
    },
    {
        'name': 'decision_journeys',
        'path': 'ledgers/portfolio-decision-journeys-v0/journeys.json',
        'reason': 'journey framing and cross-seam composition remain editorial decisions after structural validation',
    },
    {
        'name': 'kernel_shipsets',
        'path': 'ledgers/top-band-kernel-shipsets-v0/shipsets.json',
        'reason': 'first-repo-shape canon and refused-expansion posture remain editorial decisions after structural validation',
    },
    {
        'name': 'handoff_graph',
        'path': 'ledgers/top-band-handoff-graph-v0/handoffs.json',
        'reason': 'producer→consumer edge choice and stable-versus-unstable posture remain editorial decisions after structural validation',
    },
    {
        'name': 'source_atlas',
        'path': 'atlases/portfolio-source-atlas-v0/sources.json',
        'reason': 'source-family scope and caveat coverage still require editorial review after a passing check',
    },
    {
        'name': 'contribution_shapes',
        'path': 'morphologies/portfolio-contribution-shapes-v0/shapes.json',
        'reason': 'shape choice and seam-to-shape mapping remain editorial decisions after structural validation',
    },
]


def extract_revision() -> str:
    match = re.search(r'(rev\d{4})', ROOT.name)
    return match.group(1) if match else 'rev-unknown'


def file_status() -> list[dict[str, object]]:
    status: list[dict[str, object]] = []
    for rel in REQUIRED_FILES:
        path = ROOT / rel
        status.append({'path': rel, 'exists': path.exists()})
    return status


def run_check(name: str, command: list[str]) -> dict[str, object]:
    try:
        proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=90)
        output = (proc.stdout + proc.stderr).strip()
        excerpt = output.splitlines()[:12]
        return {
            'name': name,
            'command': ' '.join(command),
            'status': 'pass' if proc.returncode == 0 else 'fail',
            'returncode': proc.returncode,
            'timed_out': False,
            'output_excerpt': excerpt,
        }
    except subprocess.TimeoutExpired as exc:
        output = ((exc.stdout or '') + (exc.stderr or '')).strip()
        excerpt = output.splitlines()[:12]
        if not excerpt:
            excerpt = [f'Check timed out after {exc.timeout} seconds.']
        return {
            'name': name,
            'command': ' '.join(command),
            'status': 'fail',
            'returncode': None,
            'timed_out': True,
            'output_excerpt': excerpt,
        }


def corpus_counts() -> dict[str, int]:
    return {
        'portfolio_specimens': len(list((ROOT / 'specimens' / 'portfolio-envelope-v0').glob('*.json'))),
        'portfolio_invalid_fixtures': len(list((ROOT / 'fixtures' / 'portfolio-envelope-v0' / 'invalid').glob('*.json'))),
        'design_notes': len(list((ROOT / 'design').glob('*.md'))),
        'meta_files': len(list((ROOT / 'meta').glob('*'))),
        'tool_scripts': len(list((ROOT / 'tools').glob('*.py'))),
        'proving_ground_scenarios': len(json.loads((ROOT / 'proofgrounds' / 'portfolio-scenario-matrix-v0' / 'scenarios.json').read_text(encoding='utf-8')).get('scenarios', [])) if (ROOT / 'proofgrounds' / 'portfolio-scenario-matrix-v0' / 'scenarios.json').exists() else 0,
        'anchor_profiles': len(json.loads((ROOT / 'proofgrounds' / 'portfolio-anchor-corpus-v0' / 'anchors.json').read_text(encoding='utf-8')).get('anchors', [])) if (ROOT / 'proofgrounds' / 'portfolio-anchor-corpus-v0' / 'anchors.json').exists() else 0,
        'federated_exemplars': len(json.loads((ROOT / 'proofgrounds' / 'portfolio-exemplar-federation-v0' / 'exemplars.json').read_text(encoding='utf-8')).get('exemplars', [])) if (ROOT / 'proofgrounds' / 'portfolio-exemplar-federation-v0' / 'exemplars.json').exists() else 0,
        'portfolio_hypotheses': len(json.loads((ROOT / 'ledgers' / 'portfolio-hypothesis-ledger-v0' / 'hypotheses.json').read_text(encoding='utf-8')).get('hypotheses', [])) if (ROOT / 'ledgers' / 'portfolio-hypothesis-ledger-v0' / 'hypotheses.json').exists() else 0,
        'kernel_shipset_cards': len(json.loads((ROOT / 'ledgers' / 'top-band-kernel-shipsets-v0' / 'shipsets.json').read_text(encoding='utf-8')).get('shipsets', [])) if (ROOT / 'ledgers' / 'top-band-kernel-shipsets-v0' / 'shipsets.json').exists() else 0,
        'handoff_graph_cards': len(json.loads((ROOT / 'ledgers' / 'top-band-handoff-graph-v0' / 'handoffs.json').read_text(encoding='utf-8')).get('handoffs', [])) if (ROOT / 'ledgers' / 'top-band-handoff-graph-v0' / 'handoffs.json').exists() else 0,
        'portfolio_launch_wedges': len(json.loads((ROOT / 'ledgers' / 'portfolio-launch-wedges-v0' / 'wedges.json').read_text(encoding='utf-8')).get('wedges', [])) if (ROOT / 'ledgers' / 'portfolio-launch-wedges-v0' / 'wedges.json').exists() else 0,
        'portfolio_decision_journeys': len(json.loads((ROOT / 'ledgers' / 'portfolio-decision-journeys-v0' / 'journeys.json').read_text(encoding='utf-8')).get('journeys', [])) if (ROOT / 'ledgers' / 'portfolio-decision-journeys-v0' / 'journeys.json').exists() else 0,
        'source_atlas_cards': len(json.loads((ROOT / 'atlases' / 'portfolio-source-atlas-v0' / 'sources.json').read_text(encoding='utf-8')).get('sources', [])) if (ROOT / 'atlases' / 'portfolio-source-atlas-v0' / 'sources.json').exists() else 0,
        'kernel_fixture_cards': len(list((ROOT / 'fixtures' / 'top-band-v0').glob('*.fixture.json'))) if (ROOT / 'fixtures' / 'top-band-v0').exists() else 0,
        'kernel_artifact_schemas': len(list((ROOT / 'schemas' / 'top-band-v0').glob('*.schema.json'))) if (ROOT / 'schemas' / 'top-band-v0').exists() else 0,
        'contribution_shape_cards': len(json.loads((ROOT / 'morphologies' / 'portfolio-contribution-shapes-v0' / 'shapes.json').read_text(encoding='utf-8')).get('shapes', [])) if (ROOT / 'morphologies' / 'portfolio-contribution-shapes-v0' / 'shapes.json').exists() else 0,
    }


def build_report() -> tuple[dict[str, object], bool]:
    files = file_status()
    missing = [entry['path'] for entry in files if not entry['exists']]
    checks = [run_check(name, command) for name, command in CHECKS]
    failed_checks = [check['name'] for check in checks if check['status'] != 'pass']
    ok = not missing and not failed_checks

    report: dict[str, object] = {
        'schema_family': 'archive-doctor-report/v0',
        'tool': 'tools/archive_doctor.py',
        'repo_revision': extract_revision(),
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'summary': {
            'status': 'pass' if ok else 'fail',
            'required_files_checked': len(files),
            'checks_passed': sum(1 for check in checks if check['status'] == 'pass'),
            'checks_failed': sum(1 for check in checks if check['status'] != 'pass'),
        },
        'required_files': files,
        'checks': checks,
        'corpus_counts': corpus_counts(),
        'manual_followup_queue': MANUAL_QUEUE,
        'limitations': [
            'This report does not refresh external citations or ecosystem facts.',
            'This report does not rerank seams or promote a new frontier.',
            'This report only validates wired repo-level checks, not every seam-local payload.',
            'Schema validation currently covers the first top-band JSON families only.',
            'Manual renewal queues still require human review after a passing run.',
        ],
    }
    return report, ok


def main() -> int:
    parser = argparse.ArgumentParser(description='Run the archive doctor maintenance pass and emit a JSON report.')
    parser.add_argument('--write', type=Path, help='Optional path to write the JSON report to.')
    args = parser.parse_args()

    report, ok = build_report()
    output = json.dumps(report, indent=2, sort_keys=False)
    print(output)

    if args.write is not None:
        target = args.write if args.write.is_absolute() else ROOT / args.write
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(output + '\n', encoding='utf-8')

    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
