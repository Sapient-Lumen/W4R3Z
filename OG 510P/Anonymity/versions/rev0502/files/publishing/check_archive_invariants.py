#!/usr/bin/env python3
"""Check semantic archive invariants that should survive future refactors."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding='utf-8'))


def record(checks: list[dict], invariant_id: str, ok: bool, details: str):
    checks.append({'id': invariant_id, 'status': 'pass' if ok else 'fail', 'details': details})


def check(root: pathlib.Path) -> dict:
    canonical = load_json(root / 'publishing/CANONICAL_POLICY.json')
    citation_heads = load_json(root / 'published/citation_heads.json')
    legacy_links = load_json(root / 'published/legacy_published_links.json')
    public_surface = load_json(root / 'published/PUBLIC_SURFACE.json')
    release_manifest = load_json(root / 'RELEASE_MANIFEST.json')
    revision_receipt = load_json(root / 'REVISION_RECEIPT.json')
    archive_index = load_json(root / 'ARCHIVE_INDEX.json')
    queue_index = load_json(root / 'release_queue/QUEUE_INDEX.json')
    surface_schema = load_json(root / 'reports/surface_schema_validation.json')
    transient = load_json(root / 'reports/transient_surface_audit.json')
    manifest_verify = load_json(root / 'reports/manifest_sha256_verification.json')
    manifest_coverage = load_json(root / 'reports/manifest_coverage_audit.json')
    context_budget_path = root / 'reports/context_pack_budget.json'
    context_budget = load_json(context_budget_path) if context_budget_path.exists() else {'status': 'missing', 'summary': {'checks_failed': 1}}
    transfer_source_receipt = load_json(root / 'reports/transfer_source_receipt.json')
    version_text = (root / 'VERSION').read_text(encoding='utf-8').strip()
    latest_decision_md = (root / 'release_queue/LATEST_DECISION.md').read_text(encoding='utf-8')
    latest_decision_json = load_json(root / 'release_queue/LATEST_DECISION.json')
    invariants = load_json(root / 'publishing/archive_invariants.json')

    checks = []
    record(
        checks,
        'INV-0001',
        canonical.get('default_release_posture') == 'hold' and canonical.get('allow_zero_publications_in_turn') is True and (latest_decision_json.get('publication_action') == 'none' or 'no publication' in latest_decision_md.lower()),
        f"default_release_posture={canonical.get('default_release_posture')} allow_zero={canonical.get('allow_zero_publications_in_turn')} publication_action={latest_decision_json.get('publication_action')}"
    )
    record(
        checks,
        'INV-0002',
        citation_heads['summary']['legacy_public_head_count'] == len(citation_heads['current_public_citation_heads']) == len(legacy_links.get('canonical_legacy_links', [])) == 5,
        f"citation_legacy_count={citation_heads['summary']['legacy_public_head_count']} current_heads={len(citation_heads['current_public_citation_heads'])} legacy_links={len(legacy_links.get('canonical_legacy_links', []))}"
    )
    frozen = {item['path'] if isinstance(item, dict) else item for item in citation_heads['repo_frozen_noncanonical_entries']}
    current = {item['path'] if isinstance(item, dict) else item for item in citation_heads['current_public_citation_heads']}
    public_frozen = set(public_surface['repo_frozen_noncanonical_entries'])
    record(
        checks,
        'INV-0003',
        frozen.isdisjoint(current) and frozen == public_frozen and citation_heads['summary']['repo_frozen_noncanonical_entry_count'] == len(frozen),
        f"frozen_count={len(frozen)} current_overlap={sorted(frozen & current)} public_surface_frozen_count={len(public_frozen)}"
    )
    all_tex = canonical.get('published_artifact') == 'tex' and all(path.endswith('/paper.tex') for path in current) and all(path.endswith('/paper.tex') for path in public_surface['current_public_citation_heads'])
    record(checks,'INV-0004', all_tex, f"published_artifact={canonical.get('published_artifact')} current_head_count={len(current)}")
    fail_closed_reports = [surface_schema, transient, manifest_verify, manifest_coverage]
    ok_reports = all(r.get('status') == 'pass' for r in fail_closed_reports)
    if context_budget.get('status') != 'missing':
        ok_reports = ok_reports and context_budget.get('status') == 'pass'
        fail_closed_reports = fail_closed_reports + [context_budget]
    record(checks,'INV-0005', ok_reports, 'report_statuses=' + ', '.join(r.get('status','?') for r in fail_closed_reports))
    transient_ok = transient.get('status') == 'pass' and transient.get('summary', {}).get('disallowed_file_count') == 0 and (root / 'PRUNING_POLICY.md').exists() and (root / 'PRUNED_TRANSIENT.paths').exists()
    record(checks,'INV-0006', transient_ok, f"transient_status={transient.get('status')} disallowed={transient.get('summary', {}).get('disallowed_file_count')}")
    receipt_revision = f"rev{int(revision_receipt['revision']):04d}"
    singular = version_text == release_manifest['revision'] == receipt_revision == archive_index['latest_revision'] == queue_index['generated_for_revision']
    record(checks,'INV-0007', singular, f"version={version_text} manifest={release_manifest['revision']} receipt={receipt_revision} archive={archive_index['latest_revision']} queue={queue_index['generated_for_revision']}")
    transfer_ok = transfer_source_receipt.get('status') == 'pass' and transfer_source_receipt.get('summary', {}).get('checks_failed') == 0 and (root / 'TRANSFER_SOURCES.json').exists() and (root / 'TRANSFER_INPUTS.sha256').exists()
    record(checks,'INV-0008', transfer_ok, f"transfer_source_receipt_status={transfer_source_receipt.get('status')} failed={transfer_source_receipt.get('summary', {}).get('checks_failed')}")

    missing_ids = [inv['id'] for inv in invariants.get('invariants', []) if inv['id'] not in {c['id'] for c in checks}]
    if missing_ids:
        for inv_id in missing_ids:
            record(checks, inv_id, False, 'declared in archive_invariants.json but not implemented in checker')

    failures = [c for c in checks if c['status'] == 'fail']
    return {
        'status': 'pass' if not failures else 'fail',
        'checked_revision': release_manifest['revision'],
        'checked_bundle': release_manifest['bundle'],
        'checks': checks,
        'summary': {
            'checks_passed': len(checks) - len(failures),
            'checks_failed': len(failures),
        },
        'fail_closed_rule': 'If an archive invariant fails, default to no publication and repair the violated invariant before trusting the archive state.'
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.')
    parser.add_argument('--write-report', default='')
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = (root / args.write_report).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding='utf-8')
    sys.stdout.write(text)
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
